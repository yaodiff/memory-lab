#!/usr/bin/env python3
"""E004: do meta-optimized LOAD/OFFLOAD memory prompts beat generic ones on an unseen world?

A small, synthetic analogue of the harness-optimization half of Self-Improving Memory
(https://facebookresearch.github.io/RAM/blogs/self_improving_memory/). No fine-tuning.

World: shop groups whose order rows store price in cents or dollars and quantity in
units or dozens. The question shows raw fields only; the units are learnable only from
feedback on earlier subtasks. Memory is a small directory of text files that the model
rewrites after each subtask (OFFLOAD) and sees before the next one (LOAD).

Stdlib only. Model calls go through the Claude Code CLI (`claude -p`).
"""
import argparse
import json
import random
import re
import subprocess
import sys
import time
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

HERE = Path(__file__).resolve().parent
MEMORY_CAP = 2000  # characters across all memory files; the harness truncates beyond it
STREAM_LEN = 14
N_GROUPS = 5
DRIFT_FROM = 9
TRAIN_NAMES = ["amber", "birch", "cobalt", "dune", "ember"]
TEST_NAMES = [["fjord", "garnet", "hollow", "iris", "juniper"],
              ["kelp", "lumen", "moss", "nectar", "onyx"],
              ["pebble", "quartz", "reed", "sable", "tundra"]]

SYSTEM = ("You work through a stream of small tasks. Each task starts with a fresh context; "
          "the only thing that carries over between tasks is a persistent memory directory of "
          "text files. Follow the memory instructions you are given.")

TASK_RULES = ("Answer the question. End your reply with one line `ANSWER: <number>` "
              "(a plain number, no units or commas).")

OFFLOAD_FORMAT = ("Reply with JSON only: {{\"files\": {{\"<FILENAME>.md\": \"<full content>\", ...}}}}. "
                  "The JSON replaces the whole directory: omit a file to delete it. "
                  "Total size across files is capped at {cap} characters; text beyond the cap is cut.")

SEEDS = {
    "generic": {
        "load": "Read your memory directory before you start; how you organize it is your decision.",
        "offload": "After the task, update the memory directory, deciding yourself what to keep.",
    },
    "summary": {
        "load": "Read your one running summary and check each step against it.",
        "offload": "Fold what this task taught you into that single running summary.",
    },
    "skill": {
        "load": "Read SKILLS.md and apply any procedure whose trigger matches this task before answering.",
        "offload": ("Keep SKILLS.md as a list of reusable procedures, each with a trigger and steps. "
                    "Add or fix a procedure when this task showed one was missing or wrong."),
    },
}

# The Database prompt shown in the paper's Figure 1, copied as published (not selected here).
TRANSPLANT = {
    "load": ("Read GUARDRAILS.md, then SCHEMA.md. Before answering, check price unit and "
             "timestamp type; target <=5 queries."),
    "offload": ("Record each group's price unit and timestamp format (CONFIRMED/UNTESTED); "
                "log failures as IF->THEN rules."),
}


def make_world(names, seed):
    rng = random.Random(seed)
    combos = [("cents", "units"), ("cents", "dozens"), ("dollars", "units"), ("dollars", "dozens")]
    units = combos + [rng.choice(combos)]
    rng.shuffle(units)
    return {n: {"price": p, "qty": q} for n, (p, q) in zip(names, units)}


def make_stream(world, seed):
    rng = random.Random(seed)
    names = list(world)
    order = names[:]
    rng.shuffle(order)
    while len(order) < STREAM_LEN:
        order.append(rng.choice(names))
    head, tail = order[:N_GROUPS], order[N_GROUPS:]
    rng.shuffle(tail)
    order = head + tail
    # Drift: from task DRIFT_FROM on, one group's price unit flips (cents <-> dollars). The
    # question never says so; only feedback shows it. The drift group is the one seen most
    # often after the switch, so the flip is observable and then reusable.
    late = [g for g in order[DRIFT_FROM:]]
    drift_group = max(sorted(set(late)), key=late.count)
    tasks, seen = [], set()
    for i, g in enumerate(order):
        price, qty = rng.randint(120, 1980), rng.randint(1, 9)
        unit = world[g]["price"]
        drifted = g == drift_group and i >= DRIFT_FROM
        if drifted:
            unit = "dollars" if unit == "cents" else "cents"
        dollars = price / 100 if unit == "cents" else price
        count = qty * 12 if world[g]["qty"] == "dozens" else qty
        tasks.append({
            "i": i, "group": g, "first_visit": g not in seen, "drifted": drifted,
            "question": (f"Order #{1000 + i} from shop group `{g}`. Raw fields: price={price}, "
                         f"quantity={qty}. What is the order revenue in dollars?"),
            "gold": round(dollars * count, 2),
        })
        seen.add(g)
    return tasks


def call_model(prompt, model, timeout, system=SYSTEM):
    command = [
        "claude", "-p", "--output-format", "json",
        "--tools", "", "--disable-slash-commands",
        "--strict-mcp-config", "--mcp-config", '{"mcpServers":{}}',
        "--setting-sources", "", "--settings", '{"disableAllHooks":true}',
        "--no-session-persistence", "--system-prompt", system, "--model", model,
    ]
    last = None
    for attempt in range(3):
        try:
            out = subprocess.run(command, input=prompt, capture_output=True, text=True,
                                 timeout=timeout, check=True).stdout
            data = json.loads(out)
            if data.get("is_error"):
                raise RuntimeError(f"cli error: {data.get('result')!r}")
            return {"text": data.get("result", ""),
                    "models": sorted((data.get("modelUsage") or {}).keys()),
                    "cost_usd": data.get("total_cost_usd"), "attempts": attempt + 1}
        except (subprocess.SubprocessError, json.JSONDecodeError, RuntimeError) as err:
            last = err
            # Keep the original failure on stderr; the call is retried, then the run aborts.
            print(f"call_model attempt {attempt + 1} failed: {err!r}", file=sys.stderr)
            time.sleep(2 * (attempt + 1))
    raise RuntimeError(f"model call failed after retries: {last!r}")


def render_memory(files):
    if not files:
        return "(the memory directory is empty)"
    return "\n\n".join(f"--- {name} ---\n{body}" for name, body in sorted(files.items()))


def cap_memory(files):
    out, used, cut = {}, 0, False
    for name, body in sorted(files.items()):
        room = MEMORY_CAP - used
        if room <= 0:
            cut = True
            break
        if len(body) > room:
            body, cut = body[:room], True
        out[name] = body
        used += len(body)
    return out, cut


def parse_answer(text):
    found = re.findall(r"ANSWER\W{0,4}\s*\$?\s*(-?[\d,]*\.?\d+)", text)
    if not found:
        return None
    try:
        return float(found[-1].replace(",", ""))
    except ValueError:
        return None


def parse_files(text):
    match = re.search(r"\{.*\}", text, re.S)
    if not match:
        return None
    try:
        files = json.loads(match.group(0)).get("files")
    except (json.JSONDecodeError, AttributeError):
        return None
    if not isinstance(files, dict):
        return None
    return {str(k): str(v) for k, v in files.items()}


def correct(answer, gold):
    return answer is not None and abs(answer - gold) <= max(0.01, 0.005 * abs(gold))


def run_stream(harness, tasks, model, timeout, use_memory=True):
    files, log = {}, []
    for task in tasks:
        parts = []
        if use_memory:
            parts += [f"Memory instructions (LOAD): {harness['load']}",
                      "Memory directory:\n" + render_memory(files)]
        parts += [f"Task: {task['question']}", TASK_RULES]
        reply = call_model("\n\n".join(parts), model, timeout)
        answer = parse_answer(reply["text"])
        ok = correct(answer, task["gold"])
        step = {"i": task["i"], "group": task["group"], "first_visit": task["first_visit"],
                "drifted": task["drifted"],
                "gold": task["gold"], "answer": answer, "correct": ok,
                "reply": reply["text"], "models": reply["models"], "cost_usd": reply["cost_usd"]}
        if use_memory:
            feedback = (f"Your answer {answer} was {'correct' if ok else 'wrong'}. "
                        f"The correct revenue was {task['gold']} dollars.")
            prompt = "\n\n".join([
                f"Memory instructions (OFFLOAD): {harness['offload']}",
                "Current memory directory:\n" + render_memory(files),
                f"The task you just finished: {task['question']}",
                "Your reply:\n" + reply["text"], "Feedback: " + feedback,
                OFFLOAD_FORMAT.format(cap=MEMORY_CAP)])
            off = call_model(prompt, model, timeout)
            new = parse_files(off["text"])
            step["offload_parse_ok"] = new is not None
            if new is not None:
                files, step["memory_cut"] = cap_memory(new)
            step["memory_after"] = dict(files)
            step["offload_cost_usd"] = off["cost_usd"]
        log.append(step)
    return log


def score(log):
    rep = [s for s in log if not s["first_visit"] and not s["drifted"]]
    dri = [s for s in log if s["drifted"]]
    return {"all": sum(s["correct"] for s in log) / len(log),
            "repeat_visits": sum(s["correct"] for s in rep) / len(rep) if rep else None,
            "drifted": sum(s["correct"] for s in dri) / len(dri) if dri else None,
            "no_answer": sum(s["answer"] is None for s in log),
            "n": len(log), "n_repeat": len(rep), "n_drifted": len(dri)}


META_SYSTEM = ("You improve the memory instructions of a task agent. You read its runs and "
               "propose better LOAD and OFFLOAD instructions. Reply with JSON only.")


def report(log):
    lines = []
    for s in log:
        mark = "OK " if s["correct"] else "BAD"
        lines.append(f"{mark} task {s['i']} order=#{1000 + s['i']} group={s['group']} "
                     f"first_visit={s['first_visit']} "
                     f"answer={s['answer']} gold={s['gold']}")
    last = log[-1].get("memory_after", {})
    return "\n".join(lines) + "\nFinal memory directory:\n" + render_memory(last)


def revise(parent, logs, model, timeout):
    runs = "\n\n".join(f"## Run {k + 1}\n{report(log)}" for k, log in enumerate(logs))
    prompt = "\n\n".join([
        "The task agent solves a stream of order-revenue questions. Each task starts with an "
        "empty context; only the memory directory carries over. Before each task it gets the "
        "LOAD instruction plus the whole memory directory; after each task it gets feedback "
        "with the correct value and rewrites the directory following the OFFLOAD instruction. "
        f"Memory is capped at {MEMORY_CAP} characters.",
        f"Current LOAD: {parent['load']}\nCurrent OFFLOAD: {parent['offload']}",
        f"Mean score of these instructions: {parent['score']:.3f}",
        "Runs (one line per task, then the final memory):\n" + runs,
        "Find where memory use fell short (what was not written, written badly, or not used) "
        "and rewrite both instructions. The new instructions will be used on future streams of "
        "the same kind of task, where the specific groups and their properties may differ, so "
        "do not copy facts about particular groups into the instructions.",
        'Reply with JSON only: {"diagnosis": "<two sentences>", "load": "<new LOAD>", '
        '"offload": "<new OFFLOAD>"}'])
    reply = call_model(prompt, model, timeout, system=META_SYSTEM)
    match = re.search(r"\{.*\}", reply["text"], re.S)
    data = json.loads(match.group(0)) if match else {}
    if not data.get("load") or not data.get("offload"):
        raise RuntimeError(f"meta agent returned no usable prompts: {reply['text'][:400]!r}")
    return {"load": data["load"], "offload": data["offload"],
            "diagnosis": data.get("diagnosis", ""), "parent": parent["name"]}


def mean(xs):
    xs = [x for x in xs if x is not None]
    return sum(xs) / len(xs) if xs else None


def evaluate(pool, names, jobs, args, logf):
    """jobs: list of (label, tasks, use_memory). Runs every (harness, job) pair in parallel."""
    work = [(n, label, tasks, mem) for n in names for (label, tasks, mem) in jobs]

    def one(item):
        name, label, tasks, mem = item
        log = run_stream(pool[name], tasks, args.model, args.timeout, use_memory=mem)
        return name, label, log

    out = {}
    with ThreadPoolExecutor(max_workers=args.workers) as ex:
        for name, label, log in ex.map(one, work):
            logf.write(json.dumps({"harness": name, "stream": label, "log": log}) + "\n")
            logf.flush()
            out.setdefault(name, {})[label] = score(log)
            print(f"{name:<12} {label:<10} {score(log)}", flush=True)
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--model", default="haiku")
    ap.add_argument("--timeout", type=float, default=180)
    ap.add_argument("--workers", type=int, default=8)
    ap.add_argument("--iterations", type=int, default=2)
    ap.add_argument("--parents", type=int, default=2)
    ap.add_argument("--train-repeats", type=int, default=2)
    ap.add_argument("--out", type=Path, required=True)
    a = ap.parse_args()
    a.out.mkdir(parents=True, exist_ok=False)
    logf = (a.out / "logs.jsonl").open("w")
    started = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())

    train_world = make_world(TRAIN_NAMES, 11)
    train_jobs = [(f"train-{r}", make_stream(train_world, 101 + r), True) for r in range(a.train_repeats)]
    pool = {k: dict(v, name=k) for k, v in SEEDS.items()}
    search = evaluate(pool, list(pool), train_jobs, a, logf)
    for name in pool:
        pool[name]["score"] = mean(s["all"] for s in search[name].values())
    logs_by = {}
    for line in (a.out / "logs.jsonl").read_text().splitlines():
        rec = json.loads(line)
        logs_by.setdefault(rec["harness"], []).append(rec["log"])

    for it in range(1, a.iterations + 1):
        parents = sorted(pool.values(), key=lambda h: -h["score"])[:a.parents]
        new = []
        for k, parent in enumerate(parents):
            child = revise(parent, logs_by[parent["name"]], a.model, a.timeout)
            child["name"] = f"meta-i{it}-{k}"
            pool[child["name"]] = child
            new.append(child["name"])
            print(f"{child['name']} from {parent['name']}: {child['diagnosis']}", flush=True)
        res = evaluate(pool, new, train_jobs, a, logf)
        search.update(res)
        for name in new:
            pool[name]["score"] = mean(s["all"] for s in res[name].values())
        for line in (a.out / "logs.jsonl").read_text().splitlines():
            rec = json.loads(line)
            if rec["harness"] in new:
                logs_by.setdefault(rec["harness"], []).append(rec["log"])

    best = max(pool.values(), key=lambda h: h["score"])
    pool["optimized"] = dict(best, name="optimized", selected_from=best["name"])
    pool["transplant"] = dict(TRANSPLANT, name="transplant")
    pool["no_memory"] = {"name": "no_memory", "load": "", "offload": ""}

    test_jobs = [(f"test-{k}", make_stream(make_world(TEST_NAMES[k], 200 + k), 300 + k), True)
                 for k in range(len(TEST_NAMES))]
    arms = ["generic", "summary", "skill", "transplant", "optimized"]
    test = evaluate(pool, arms, test_jobs, a, logf)
    nomem_jobs = [(label, tasks, False) for label, tasks, _ in test_jobs]
    test.update(evaluate(pool, ["no_memory"], nomem_jobs, a, logf))

    summary = {name: {"all": mean(s["all"] for s in runs.values()),
                      "repeat_visits": mean(s["repeat_visits"] for s in runs.values()),
                      "drifted": mean(s["drifted"] for s in runs.values()),
                      "no_answer": sum(s["no_answer"] for s in runs.values()),
                      "per_world": runs} for name, runs in test.items()}
    result = {
        "started": started, "finished": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "model_requested": a.model, "stream_len": STREAM_LEN, "memory_cap": MEMORY_CAP,
        "drift_from": DRIFT_FROM,
        "train_world": train_world,
        "test_worlds": [make_world(TEST_NAMES[k], 200 + k) for k in range(len(TEST_NAMES))],
        "search": {n: {"score": pool[n]["score"], "runs": search[n],
                       "load": pool[n]["load"], "offload": pool[n]["offload"],
                       "parent": pool[n].get("parent"), "diagnosis": pool[n].get("diagnosis")}
                   for n in search},
        "selected": best["name"], "test": summary,
    }
    (a.out / "results.json").write_text(json.dumps(result, indent=2, ensure_ascii=False) + "\n")
    print(json.dumps({n: (round(v["all"], 3), v["repeat_visits"] and round(v["repeat_visits"], 3))
                      for n, v in summary.items()}), flush=True)


if __name__ == "__main__":
    main()
