"""Offline tests. Fake CLIs never contact a model or require credentials."""

import contextlib
import importlib.util
import io
import json
import os
from pathlib import Path
import sys
import tempfile
from types import SimpleNamespace
import unittest
from unittest.mock import patch

HERE = Path(__file__).resolve().parent
SPEC = importlib.util.spec_from_file_location("replay", HERE / "run.py")
replay = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(replay)
import score  # noqa: E402


def sample_case(case_id="example-001", origin="other_session"):
    return {
        "id": case_id,
        "repo": "https://github.com/pallets/click",
        "repo_revision": "934813e4d421",
        "prefix": [
            {"role": "user", "content": "Add a synthetic command test."},
            {"role": "assistant", "content": "I drafted a direct callback call."},
            {"role": "user", "content": "What is your next concrete plan?"},
        ],
        "last_user_turn": "What is your next concrete plan?",
        "convention": {
            "title": "GOLD_TITLE_ONLY",
            "scope": "GOLD_SCOPE_ONLY",
            "points": ["GOLD_POINT_ONE_ONLY", "GOLD_POINT_TWO_ONLY"],
        },
        "memory_pages": ["pages/example.md"],
        "page_origin": origin,
        "held_out_correction": "HELD_OUT_ONLY",
    }


def verdict(labels):
    return score.parse_judgment(json.dumps({"points": [
        {"point": i, "label": label, "reason": "Explicit plan evidence."}
        for i, label in enumerate(labels, 1)
    ]}), len(labels))


class DatasetTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.dataset = Path(self.temp.name)
        (self.dataset / "cases").mkdir()
        (self.dataset / "pages").mkdir()
        self.page = "MEMORY_BEGIN_ONLY\n\nScoped synthetic rule.\n\nMEMORY_END_ONLY\n"
        (self.dataset / "pages" / "example.md").write_text(self.page, encoding="utf-8")
        self.case = sample_case()
        self.save_case()

    def save_case(self):
        replay.write_json(self.dataset / "cases" / "example.json", self.case)

    def test_shipped_cases(self):
        cases = replay.load_cases(replay.BENCH / "datasets" / "click-synthetic")
        self.assertTrue(5 <= len(cases) <= 10)
        self.assertGreaterEqual(sum(c["page_origin"] == "same_session" for c in cases), 2)
        for case in cases:
            self.assertEqual(case["repo"], "https://github.com/pallets/click")
            self.assertEqual(case["last_user_turn"], case["prefix"][-1]["content"])
            self.assertNotIn(case["held_out_correction"], json.dumps(case["prefix"]))

    def test_no_memory_has_no_gold_or_held_out_correction(self):
        prompt = replay.planner_prompt(self.case, "no_memory", self.dataset)
        for hidden in (
            "GOLD_TITLE_ONLY", "GOLD_SCOPE_ONLY", "GOLD_POINT", "HELD_OUT_ONLY",
            "MEMORY_BEGIN_ONLY", "page_origin", "other_session", "memory_pages",
        ):
            self.assertNotIn(hidden, prompt)
        self.assertIn(self.case["last_user_turn"], prompt)

    def test_oracle_gets_complete_page_not_gold(self):
        prompt = replay.planner_prompt(self.case, "oracle_page", self.dataset)
        self.assertIn(self.page, prompt)
        self.assertNotIn("GOLD_POINT", prompt)
        self.assertNotIn("HELD_OUT_ONLY", prompt)

    def test_future_arms_do_not_silently_fall_back(self):
        for arm in ("memory_search", "step_conditioned"):
            with self.assertRaises(NotImplementedError):
                replay.planner_prompt(self.case, arm, self.dataset)

    def test_invalid_case_fields_are_rejected(self):
        mutations = (
            lambda c: c.update(id="../escape"),
            lambda c: c.update(repo="https://example.org/private"),
            lambda c: c.update(page_origin="unknown"),
            lambda c: c.update(last_user_turn="not the final user turn"),
            lambda c: c.update(prefix=[{"role": "system", "content": "bad"}]),
            lambda c: c["convention"].update(points=[]),
            lambda c: c.update(memory_pages=[]),
            lambda c: c.update(held_out_correction=c["prefix"][0]["content"]),
        )
        for mutate in mutations:
            with self.subTest(mutation=mutate):
                self.case = sample_case()
                mutate(self.case)
                self.save_case()
                with self.assertRaises(ValueError):
                    replay.load_cases(self.dataset)

    def test_missing_fields_and_duplicate_ids(self):
        del self.case["convention"]
        self.save_case()
        with self.assertRaises(ValueError):
            replay.load_cases(self.dataset)
        self.case = sample_case()
        self.save_case()
        replay.write_json(self.dataset / "cases" / "duplicate.json", self.case)
        with self.assertRaises(ValueError):
            replay.load_cases(self.dataset)

    def test_page_traversal_absolute_paths_and_symlinks(self):
        with tempfile.TemporaryDirectory() as external:
            outside = Path(external) / "outside.md"
            outside.write_text("not dataset context", encoding="utf-8")
            (self.dataset / "pages" / "link.md").symlink_to(outside)
            for page in ("../outside.md", str(outside), "pages/link.md"):
                self.case["memory_pages"] = [page]
                with self.subTest(page=page), self.assertRaises(ValueError):
                    replay.read_pages(self.case, self.dataset)

    def test_empty_and_missing_pages(self):
        (self.dataset / "pages" / "example.md").write_text("", encoding="utf-8")
        with self.assertRaises(ValueError):
            replay.load_cases(self.dataset)
        (self.dataset / "pages" / "example.md").unlink()
        with self.assertRaises(OSError):
            replay.load_cases(self.dataset)


class JudgeTests(unittest.TestCase):
    def test_overall_is_derived_from_points(self):
        for labels, expected in (
            (["full", "full"], "full"),
            (["full", "partial"], "partial"),
            (["partial", "violates"], "violates"),
            (["full", "violates"], "violates"),
        ):
            with self.subTest(labels=labels):
                self.assertEqual(verdict(labels)["label"], expected)

    def test_invalid_judge_outputs_fail_closed(self):
        invalid = [
            "not json", "[]", '{"points":[]}',
            '{"points":[{"point":1,"label":"maybe","reason":"x"}]}',
            '{"points":[{"point":true,"label":"full","reason":"x"}]}',
            '{"points":[{"point":2,"label":"full","reason":"x"}]}',
            '{"points":[{"point":1,"label":"full","reason":""}]}',
            '{"points":[{"point":1,"label":"full"}]}',
            '{"points":[{"point":1,"label":"full","reason":"x"}],"label":"full"}',
        ]
        for answer in invalid:
            with self.subTest(answer=answer), self.assertRaises(ValueError):
                score.parse_judgment(answer, 1)

    def test_fenced_json_and_no_keyword_heuristic(self):
        answer = '{"points":[{"point":1,"label":"full","reason":"Rejects threads."}]}'
        parsed = score.parse_judgment("```json\n" + answer + "\n```", 1)
        self.assertEqual(parsed["label"], "full")

    def test_independent_blind_prompts(self):
        case = sample_case()
        a = score.judge_prompt(case, "A plan mentioning oracle_page as data.", "a")
        b = score.judge_prompt(case, "A plan mentioning oracle_page as data.", "b")
        self.assertNotEqual(a, b)
        for prompt in (a, b):
            self.assertIn("GOLD_POINT_ONE_ONLY", prompt)
            self.assertNotIn("HELD_OUT_ONLY", prompt)
            self.assertNotIn("page_origin", prompt)
            self.assertNotIn("other_session", prompt)
            self.assertNotIn("memory_pages", prompt)

    def test_three_way_and_binary_agreement_are_different(self):
        stats = score.agreement([
            ("full", "full"), ("full", "partial"), ("violates", "partial")
        ])
        self.assertEqual(stats["denominator"], 3)
        self.assertAlmostEqual(stats["three_way"], 1 / 3)
        self.assertAlmostEqual(stats["violates_vs_not"], 2 / 3)

    def test_summary_stratifies_origins_and_arms(self):
        rows = [
            {"case_id": "one", "page_origin": "other_session", "arm": "no_memory",
             "judges": {"a": verdict(["full", "full"]), "b": verdict(["full", "partial"])}},
            {"case_id": "two", "page_origin": "same_session", "arm": "no_memory",
             "judges": {"a": verdict(["violates", "full"]), "b": verdict(["violates", "full"])}},
            {"case_id": "one", "page_origin": "other_session", "arm": "oracle_page",
             "judges": {"a": verdict(["full", "full"]), "b": verdict(["full", "full"])}},
        ]
        report = score.summarize(rows)
        self.assertEqual(set(report), {"by_origin"})
        other = report["by_origin"]["other_session"]["no_memory"]
        self.assertEqual(other["plan_agreement"]["three_way"], 0)
        self.assertEqual(other["plan_agreement"]["violates_vs_not"], 1)
        self.assertEqual(other["point_agreement"]["three_way"], 0.5)
        self.assertEqual(other["plan_label_rates"]["a"]["full"], 1)
        self.assertEqual(report["by_origin"]["same_session"]["no_memory"][
            "plan_label_rates"]["a"]["violates"], 1)
        summary = score.render_summary(rows, report)
        self.assertIn("100.0%", summary)
        self.assertIn("0.0%", summary)
        self.assertIn("not accuracy", summary)

    def test_duplicate_missing_judge_or_inconsistent_label_rejected(self):
        row = {
            "case_id": "one", "page_origin": "other_session", "arm": "no_memory",
            "judges": {"a": verdict(["full"]), "b": verdict(["full"])},
        }
        for rows in (
            [row, row],
            [{**row, "judges": {"a": verdict(["full"])}}],
            [{**row, "judges": {
                "a": {**verdict(["full"]), "label": "violates"},
                "b": verdict(["full"]),
            }}],
        ):
            with self.assertRaises(ValueError):
                score.summarize(rows)


FAKE_CLAUDE = '''#!/usr/bin/env python3
import json, os, sys, time
if "--version" in sys.argv:
    print("fake-claude-offline-test")
    sys.exit(0)
prompt = sys.stdin.read()
if os.environ.get("FAKE_TIMEOUT"):
    print("partial output", flush=True)
    time.sleep(10)
if "CONVERSATION" in prompt:
    answer = "Use the scoped fixture and verify the command output."
elif os.environ.get("FAKE_BAD_JUDGE"):
    answer = "not JSON"
else:
    evidence = json.loads("{" + prompt.split("\\n\\n{", 1)[1])
    answer = json.dumps({"points": [
        {"point": i, "label": "full", "reason": "Offline fixture only."}
        for i, _ in enumerate(evidence["convention"]["points"], 1)
    ]})
print(json.dumps({"subtype": "success", "is_error": False, "result": answer}))
'''


class RunnerTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.directory = Path(self.temp.name)
        executable = self.directory / "claude"
        executable.write_text(FAKE_CLAUDE, encoding="utf-8")
        executable.chmod(0o755)
        self.env = patch.dict(os.environ, {
            "PATH": str(self.directory) + os.pathsep + os.environ["PATH"],
        })
        self.env.start()
        self.addCleanup(self.env.stop)

    def run_main(self, *arguments):
        with patch.object(sys, "argv", ["run.py", *arguments]):
            with contextlib.redirect_stdout(io.StringIO()), contextlib.redirect_stderr(io.StringIO()):
                replay.main()

    def test_fake_cli_end_to_end_both_arms_and_independent_judges(self):
        out = self.directory / "results"
        self.run_main("--cases", "2", "--out", str(out))
        manifest = json.loads((out / "manifest.json").read_text())
        self.assertEqual(manifest["status"], "complete")
        self.assertEqual(manifest["completed_cli_invocations"], 12)
        self.assertEqual(manifest["expected_cli_invocations"], 12)
        results = json.loads((out / "results.json").read_text())["results"]
        self.assertEqual(len(results), 4)
        self.assertEqual({r["arm"] for r in results}, set(replay.IMPLEMENTED))
        for result in results:
            path = out / result["case_id"] / result["arm"]
            for stage in ("planner", "judge-a", "judge-b"):
                for filename in ("prompt.txt", "stdout.txt", "stderr.txt", "response.txt", "call.json"):
                    self.assertTrue((path / stage / filename).is_file())
            self.assertIsNone(result["memory_delivery"]["read_in_full"])
        self.assertEqual((out / "summary.md").read_text(), score.render_summary(
            results, score.summarize(results)
        ))

    def test_dry_run_and_validate_do_not_invoke_cli(self):
        with patch.object(replay, "invoke") as invoke:
            self.run_main("--validate-only")
            out = self.directory / "dry"
            self.run_main("--cases", "6", "--dry-run", "--out", str(out))
            invoke.assert_not_called()
            self.assertEqual(json.loads((out / "manifest.json").read_text())["status"], "dry_run")
            self.assertFalse((out / "summary.md").exists())

    def test_full_run_and_todo_arms_are_guarded_before_calls(self):
        for arguments in (
            ["--cases", "3"],
            ["--cases", "3", "--allow-full-run"],
            ["--arms", "memory_search"],
            ["--arms", "step_conditioned"],
            ["--arms", "no_memory", "no_memory"],
            ["--cases", "0"],
            ["--cases", "999"],
        ):
            with self.subTest(arguments=arguments), patch.object(replay, "invoke") as invoke:
                with self.assertRaises(SystemExit):
                    self.run_main(*arguments)
                invoke.assert_not_called()

    def test_invalid_judge_stops_without_retry_and_retains_raw_output(self):
        out = self.directory / "bad"
        with patch.dict(os.environ, {"FAKE_BAD_JUDGE": "1"}):
            with self.assertRaises(SystemExit):
                self.run_main("--out", str(out))
        manifest = json.loads((out / "manifest.json").read_text())
        self.assertEqual(manifest["status"], "failed")
        self.assertEqual(manifest["completed_cli_invocations"], 2)
        self.assertEqual(len(list(out.glob("*/*/judge-a/stdout.txt"))), 1)
        self.assertFalse(list(out.glob("*/*/judge-b")))
        self.assertFalse((out / "summary.md").exists())

    def test_existing_output_is_not_overwritten(self):
        out = self.directory / "existing"
        out.mkdir()
        sentinel = out / "sentinel.txt"
        sentinel.write_text("keep", encoding="utf-8")
        with patch.object(replay, "invoke") as invoke:
            with self.assertRaises(SystemExit):
                self.run_main("--out", str(out))
            invoke.assert_not_called()
        self.assertEqual(sentinel.read_text(), "keep")

    def test_timeout_retains_partial_output(self):
        destination = self.directory / "timeout"
        with patch.dict(os.environ, {"FAKE_TIMEOUT": "1"}):
            with self.assertRaises(RuntimeError):
                replay.invoke("claude", None, "test", destination, 0.5)
        metadata = json.loads((destination / "call.json").read_text())
        self.assertTrue(metadata["timed_out"])
        self.assertIn("partial output", (destination / "stdout.txt").read_text())

    def test_codex_response_and_any_tool_event_contamination(self):
        def fake_process(command, **kwargs):
            output = Path(command[command.index("--output-last-message") + 1])
            output.write_text("A bounded plan.", encoding="utf-8")
            self.assertFalse(Path(kwargs["cwd"]).is_relative_to(replay.BENCH.parent))
            self.assertNotIn("OPENAI_API_KEY", kwargs["env"])
            self.assertNotIn("ANTHROPIC_API_KEY", kwargs["env"])
            self.assertTrue(kwargs["start_new_session"])
            return SimpleNamespace(
                returncode=0,
                communicate=lambda prompt, timeout: (
                    json.dumps({"type": "item.completed", "item": {"type": item_type}}),
                    "",
                ),
            )

        with patch.dict(os.environ, {
            "OPENAI_API_KEY": "offline-placeholder",
            "ANTHROPIC_API_KEY": "offline-placeholder",
        }), patch.object(replay.subprocess, "Popen", side_effect=fake_process):
            for item_type in ("agent_message", "reasoning", "command_execution", "unknown_tool"):
                destination = self.directory / item_type
                with self.subTest(item_type=item_type):
                    if item_type in ("agent_message", "reasoning"):
                        self.assertEqual(replay.invoke(
                            "codex", "example-model", "A prompt", destination, 1
                        ), "A bounded plan.")
                    else:
                        with self.assertRaises(RuntimeError):
                            replay.invoke("codex", None, "A prompt", destination, 1)
                        self.assertTrue((destination / "stdout.txt").is_file())

    def test_no_tool_fresh_session_command_configuration(self):
        command = replay.command_for("claude", "haiku", self.directory)
        self.assertEqual(command[command.index("--tools") + 1], "")
        self.assertIn("--no-session-persistence", command)
        self.assertEqual(command[command.index("--setting-sources") + 1], "")
        self.assertNotIn("--resume", command)
        codex = replay.command_for("codex", "example-model", self.directory)
        for flag in ("--ephemeral", "--ignore-user-config", "--ignore-rules"):
            self.assertIn(flag, codex)
        for override in (
            "features.shell_tool=false", "features.apply_patch_freeform=false",
            "project_doc_max_bytes=0", "mcp_servers={}",
        ):
            self.assertIn(override, codex)
        self.assertEqual(codex[codex.index("--sandbox") + 1], "read-only")


if __name__ == "__main__":
    unittest.main()
