#!/usr/bin/env python3
"""Replay synthetic cases using an existing authenticated coding-agent CLI."""

import argparse
from datetime import datetime, timezone
import json
import os
from pathlib import Path
import re
import shutil
import signal
import subprocess
import sys
import tempfile
import time

BENCH = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(BENCH / "judges"))
from score import judge_prompt, parse_judgment, render_summary, summarize  # noqa: E402


ARMS = ("no_memory", "oracle_page", "memory_search", "step_conditioned")
IMPLEMENTED = ("no_memory", "oracle_page")
ORIGINS = ("other_session", "same_session", "after_correction")
SYSTEM = (
    "You are a coding assistant in a bounded, text-only replay. All necessary "
    "context is in the input. Do not use tools, inspect files, browse, or edit. "
    "Return only the requested plan or judgment."
)


def write_json(path, value):
    path.write_text(json.dumps(value, indent=2, ensure_ascii=True) + "\n", encoding="utf-8")


def text(value):
    return isinstance(value, str) and bool(value.strip())


def read_pages(case, dataset):
    pages = []
    for relative in case["memory_pages"]:
        path = (dataset / relative).resolve()
        if Path(relative).is_absolute() or not path.is_relative_to(dataset.resolve()):
            raise ValueError("memory page must stay within the dataset")
        if path.suffix != ".md":
            raise ValueError("memory pages must be Markdown")
        content = path.read_text(encoding="utf-8")
        if not content.strip():
            raise ValueError("empty memory page")
        pages.append(content)
    return pages


def load_cases(dataset):
    cases = []
    seen = set()
    for path in sorted((dataset / "cases").glob("*.json")):
        case = json.loads(path.read_text(encoding="utf-8"))
        required = {
            "id", "repo", "prefix", "last_user_turn", "convention",
            "memory_pages", "page_origin",
        }
        if not isinstance(case, dict) or not required <= case.keys():
            raise ValueError(f"{path.name}: missing case fields")
        if not text(case["id"]) or not re.fullmatch(r"[a-z0-9][a-z0-9-]*", case["id"]):
            raise ValueError(f"{path.name}: invalid case id")
        if case["id"] in seen:
            raise ValueError("duplicate case id")
        seen.add(case["id"])
        if not text(case["repo"]) or not re.fullmatch(
            r"https://github\.com/[A-Za-z0-9_.-]+/[A-Za-z0-9_.-]+", case["repo"]
        ):
            raise ValueError(f"{case['id']}: expected a public GitHub repo URL")
        prefix = case["prefix"]
        if not isinstance(prefix, list) or not prefix:
            raise ValueError(f"{case['id']}: prefix must be nonempty")
        for turn in prefix:
            if (
                not isinstance(turn, dict) or set(turn) != {"role", "content"}
                or turn["role"] not in ("user", "assistant") or not text(turn["content"])
            ):
                raise ValueError(f"{case['id']}: invalid prefix turn")
        if prefix[0]["role"] != "user" or prefix[-1]["role"] != "user":
            raise ValueError(f"{case['id']}: prefix must start and end with user")
        if not any(turn["role"] == "assistant" for turn in prefix):
            raise ValueError(f"{case['id']}: prefix needs an earlier agent step")
        if case["last_user_turn"] != prefix[-1]["content"]:
            raise ValueError(f"{case['id']}: last_user_turn must equal final prefix turn")
        convention = case["convention"]
        if (
            not isinstance(convention, dict)
            or not {"title", "points", "scope"} <= convention.keys()
            or not text(convention["title"]) or not text(convention["scope"])
            or not isinstance(convention["points"], list) or not convention["points"]
            or not all(text(point) for point in convention["points"])
        ):
            raise ValueError(f"{case['id']}: invalid convention")
        if case["page_origin"] not in ORIGINS:
            raise ValueError(f"{case['id']}: invalid page_origin")
        if (
            not isinstance(case["memory_pages"], list) or not case["memory_pages"]
            or not all(text(page) for page in case["memory_pages"])
        ):
            raise ValueError(f"{case['id']}: memory_pages must be a nonempty path list")
        read_pages(case, dataset)
        correction = case.get("held_out_correction")
        if correction is not None and (
            not text(correction) or any(correction in turn["content"] for turn in prefix)
        ):
            raise ValueError(f"{case['id']}: held-out correction must not be in prefix")
        cases.append(case)
    if not cases:
        raise ValueError("no case JSON files found in dataset/cases")
    return cases


def planner_prompt(case, arm, dataset):
    if arm not in IMPLEMENTED:
        # TODO: implement agent-driven search and next-step-conditioned retrieval.
        raise NotImplementedError(f"{arm} is reserved, not implemented")
    context = {"repo": case["repo"], "prefix": case["prefix"]}
    if "repo_revision" in case:
        context["repo_revision"] = case["repo_revision"]
    prompt = (
        "Continue this synthetic coding conversation at its final user turn. "
        "Return a concrete next-step plan in at most 220 words, not code edits. "
        "The earlier assistant step may need revising. Do not invent a later "
        "human correction. Use supplied memory only within its stated scope.\n\n"
        "CONVERSATION\n" + json.dumps(context, indent=2, ensure_ascii=True)
    )
    if arm == "oracle_page":
        prompt += "\n\nREFERENCE MEMORY (complete pages)\n" + "\n\n---\n\n".join(
            read_pages(case, dataset)
        )
    return prompt + "\n"


def command_for(backend, model, workspace):
    if backend == "claude":
        command = [
            "claude", "-p", "--output-format", "json",
            "--tools", "", "--disable-slash-commands",
            "--strict-mcp-config", "--mcp-config", '{"mcpServers":{}}',
            "--setting-sources", "", "--settings", '{"disableAllHooks":true}',
            "--no-session-persistence", "--system-prompt", SYSTEM,
        ]
    else:
        instructions = workspace / "instructions.txt"
        instructions.write_text(SYSTEM, encoding="utf-8")
        command = [
            "codex", "exec", "--skip-git-repo-check", "--ephemeral",
            "--ignore-user-config", "--ignore-rules", "--sandbox", "read-only",
            "--color", "never", "--json", "--output-last-message",
            str(workspace / "response.txt"),
        ]
        overrides = {
            "approval_policy": "never",
            "project_doc_max_bytes": 0,
            "model_instructions_file": str(instructions),
            "web_search": "disabled",
            "mcp_servers": {},
            "features.shell_tool": False,
            "features.apply_patch_freeform": False,
            "features.memories": False,
            "features.memory_tool": False,
            "features.multi_agent": False,
            "features.hooks": False,
            "features.plugins": False,
            "features.skip_host_skill_discovery": True,
        }
        for key, value in overrides.items():
            # The only mapping is the empty MCP table; TOML uses {} for it too.
            command += ["-c", f"{key}={json.dumps(value)}"]
    if model:
        command += ["--model", model]
    return command


def invoke(backend, model, prompt, destination, timeout):
    destination.mkdir()
    (destination / "prompt.txt").write_text(prompt, encoding="utf-8")
    env = os.environ.copy()
    for key in (
        "ANTHROPIC_API_KEY", "ANTHROPIC_AUTH_TOKEN", "OPENAI_API_KEY",
        "CLAUDE_CODE_USE_BEDROCK", "CLAUDE_CODE_USE_VERTEX",
        "CLAUDE_CODE_USE_FOUNDRY", "CLAUDECODE",
    ):
        env.pop(key, None)
    env["CLAUDE_CODE_DISABLE_AUTO_MEMORY"] = "1"
    started = time.monotonic()
    with tempfile.TemporaryDirectory(prefix="memlab-replay-") as directory:
        workspace = Path(directory)
        command = command_for(backend, model, workspace)
        process = subprocess.Popen(
            command, stdin=subprocess.PIPE, stdout=subprocess.PIPE,
            stderr=subprocess.PIPE, text=True, encoding="utf-8",
            cwd=workspace, env=env, start_new_session=True,
        )
        timed_out = False
        try:
            stdout, stderr = process.communicate(prompt, timeout=timeout)
        except subprocess.TimeoutExpired:
            timed_out = True
            os.killpg(process.pid, signal.SIGKILL)
            stdout, stderr = process.communicate()
        (destination / "stdout.txt").write_text(stdout, encoding="utf-8")
        (destination / "stderr.txt").write_text(stderr, encoding="utf-8")
        metadata = {
            "backend": backend, "requested_model": model,
            "returncode": process.returncode, "timed_out": timed_out,
            "elapsed_seconds": round(time.monotonic() - started, 3),
        }
        write_json(destination / "call.json", metadata)
        if timed_out or process.returncode:
            raise RuntimeError(f"CLI call failed; inspect {destination}")
        if backend == "claude":
            response = json.loads(stdout)
            if response.get("is_error") or response.get("subtype") != "success":
                raise RuntimeError(f"CLI returned an error; inspect {destination}")
            output = response.get("result")
        else:
            for line in stdout.splitlines():
                event = json.loads(line)
                item = event.get("item", {})
                if item and item.get("type") not in ("agent_message", "reasoning"):
                    raise RuntimeError("Codex used a tool; discard this contaminated run")
            output = (workspace / "response.txt").read_text(encoding="utf-8")
        if not text(output):
            raise RuntimeError(f"CLI returned no text; inspect {destination}")
        (destination / "response.txt").write_text(output, encoding="utf-8")
        return output


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--dataset", type=Path, default=BENCH / "datasets" / "click-synthetic",
        help="directory containing cases/ and pages/",
    )
    parser.add_argument("--cases", type=int, default=1, help="first N sorted cases (default: 1)")
    parser.add_argument("--arms", nargs="+", choices=ARMS, default=list(IMPLEMENTED))
    parser.add_argument("--planner-backend", choices=("claude", "codex"), default="claude")
    parser.add_argument("--planner-model", help="default: CLI's own model default")
    for judge in ("a", "b"):
        parser.add_argument(f"--judge-{judge}-backend", choices=("claude", "codex"))
        parser.add_argument(f"--judge-{judge}-model", help="default: CLI's own model default")
    parser.add_argument("--timeout", type=float, default=180, help="seconds per CLI invocation")
    parser.add_argument("--out", type=Path, help="new output directory; never overwritten")
    parser.add_argument("--dry-run", action="store_true", help="save planner prompts; no CLI calls")
    parser.add_argument("--validate-only", action="store_true", help="validate the whole dataset; no calls")
    parser.add_argument(
        "--allow-full-run", action="store_true",
        help="allow >2 cases ONLY after the owner approves models and spending",
    )
    args = parser.parse_args()
    if args.cases < 1 or args.timeout <= 0:
        parser.error("--cases and --timeout must be positive")
    if len(set(args.arms)) != len(args.arms):
        parser.error("duplicate arms")
    if any(arm not in IMPLEMENTED for arm in args.arms):
        parser.error("memory_search and step_conditioned are TODO; no calls made")
    try:
        cases = load_cases(args.dataset)
    except (ValueError, OSError) as exc:
        parser.error(str(exc))
    if args.validate_only:
        print(f"Valid dataset: {len(cases)} cases; origins: "
              + ", ".join(sorted({case["page_origin"] for case in cases})))
        return
    if args.cases > len(cases):
        parser.error("--cases exceeds the dataset size")
    if args.cases > 2 and not args.dry_run and (
        not args.allow_full_run
        or not all((args.planner_model, args.judge_a_model, args.judge_b_model))
    ):
        parser.error(">2 cases requires --allow-full-run and explicit planner/judge models")
    cases = cases[:args.cases]
    configuration = {
        "planner": {"backend": args.planner_backend, "model": args.planner_model},
        "judges": {
            judge: {
                "backend": getattr(args, f"judge_{judge}_backend") or args.planner_backend,
                "model": getattr(args, f"judge_{judge}_model"),
                "prompt": judge,
            }
            for judge in ("a", "b")
        },
    }
    if not args.dry_run:
        for backend in {
            configuration["planner"]["backend"],
            *(entry["backend"] for entry in configuration["judges"].values()),
        }:
            if not shutil.which(backend):
                parser.error(f"{backend} CLI not found; install and log in first")
    out = args.out or BENCH / "next-step-replay" / "runs" / datetime.now(
        timezone.utc
    ).strftime("%Y%m%dT%H%M%S%fZ")
    out = out.resolve()
    if out.exists():
        parser.error("output directory already exists; choose a new --out")
    out.mkdir(parents=True, exist_ok=False)
    manifest = {
        "status": "dry_run" if args.dry_run else "running",
        "configuration": configuration, "arms": args.arms,
        "cases": [{"id": c["id"], "page_origin": c["page_origin"]} for c in cases],
        "expected_cli_invocations": len(cases) * len(args.arms) * 3,
        "completed_cli_invocations": 0,
        "cli_versions": {},
    }
    if not args.dry_run:
        for backend in {entry["backend"] for entry in [
            configuration["planner"], *configuration["judges"].values()
        ]}:
            version = subprocess.run(
                [backend, "--version"], capture_output=True, text=True, check=True
            ).stdout.strip()
            manifest["cli_versions"][backend] = version
    write_json(out / "manifest.json", manifest)
    results = []
    write_json(out / "results.json", {"results": results})
    try:
        for case in cases:
            for arm in args.arms:
                directory = out / case["id"] / arm
                directory.mkdir(parents=True)
                prompt = planner_prompt(case, arm, args.dataset)
                if args.dry_run:
                    (directory / "planner.prompt.txt").write_text(prompt, encoding="utf-8")
                    continue
                print(f"{case['id']} {arm}: planner", flush=True)
                plan = invoke(
                    args.planner_backend, args.planner_model, prompt,
                    directory / "planner", args.timeout,
                )
                manifest["completed_cli_invocations"] += 1
                write_json(out / "manifest.json", manifest)
                judges = {}
                for judge in ("a", "b"):
                    print(f"{case['id']} {arm}: judge {judge}", flush=True)
                    config = configuration["judges"][judge]
                    answer = invoke(
                        config["backend"], config["model"], judge_prompt(case, plan, judge),
                        directory / f"judge-{judge}", args.timeout,
                    )
                    manifest["completed_cli_invocations"] += 1
                    write_json(out / "manifest.json", manifest)
                    judges[judge] = parse_judgment(answer, len(case["convention"]["points"]))
                    write_json(directory / f"judge-{judge}" / "judgment.json", judges[judge])
                results.append({
                    "case_id": case["id"], "page_origin": case["page_origin"],
                    "arm": arm, "judges": judges,
                    "memory_delivery": {
                        "page_supplied_in_full": arm == "oracle_page",
                        "searched": None, "right_page_found": None, "read_in_full": None,
                    },
                })
                write_json(out / "results.json", {"results": results})
        if not args.dry_run:
            report = summarize(results)
            write_json(out / "summary.json", report)
            summary = render_summary(results, report)
            (out / "summary.md").write_text(summary, encoding="utf-8")
            manifest["status"] = "complete"
            print(summary, end="")
    except (ValueError, OSError, RuntimeError) as exc:
        manifest["status"] = "failed"
        write_json(out / "manifest.json", manifest)
        print(f"Replay stopped without retries: {exc}", file=sys.stderr)
        raise SystemExit(1) from exc
    write_json(out / "manifest.json", manifest)
    print(f"Artifacts: {out}")


if __name__ == "__main__":
    main()
