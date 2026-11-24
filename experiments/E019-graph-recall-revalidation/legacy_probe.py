"""Supplemental legacy opportunity probe, separate from the decision suite."""
import argparse
from collections import Counter
from concurrent.futures import ThreadPoolExecutor
import hashlib
import json
from pathlib import Path

import numpy as np

from fixture import DOMAINS, world
from judge import Judge, METRICS, jobs
from retrieval import CONFIG, OnnxModel, evaluate_case, verify_models

ARMS = ("A_global", "B_append", "C_boost")
GROUPS = ("named_supported", "named_unsupported", "generic_supported")


def fixture():
    result = []
    for i, domain in enumerate(DOMAINS):
        for variant in range(6):
            case = world(i, variant)
            case["id"] = "probe-" + case["id"]
            group = GROUPS[variant // 2]
            case["stratum"] = group
            owner = case["target_entity"] or next(uid for uid, p in case["pages"].items()
                                                    if p["aliases"] and len(p["aliases"]) == 3)
            first, second = case["gold"]
            subject = case["pages"][owner]["title"]
            case["pages"][second].update(kind="entity", aliases=[], title=f"Timing coordinator for {subject.split()[0]}")
            case["pages"][first]["title"] = f"{domain[0]} approval checklist"
            case["pages"][owner]["text"] += (
                f" This is the identity entry for {subject}. Use this registry for {domain[0]} approvals and sequence."
            )
            if group != "generic_supported":
                case["query"] = f"{subject}: for {domain[0]}, what needs approval and what is the sequence?"
            else:
                case["query"] = f"For {domain[0]}, what needs approval and what is the sequence?"
            ref = f"{case['id']}/registry/legacy"
            edge = dict(a=owner, b=second, kind="contains",
                        source="" if group == "named_unsupported" else ref)
            if edge["source"]:
                case["sources"][ref] = [owner, "contains", second]
            case["edges"].append(edge)
            case["legacy_probe_owner"] = owner
            result.append(case)
    return result


def probe_summary(data, orders, judge_dir, commit):
    size = len(data)
    draws = np.random.default_rng(190057).integers(0, len(DOMAINS), (10000, len(DOMAINS)))
    ledger = [json.loads(line) for line in (judge_dir / "usage.jsonl").open()]
    run = dict(preregistered_commit=commit, n=size, groups={}, arms={},
               judge_usage=dict(attempts=len(ledger), successful=sum(r["error"] is None for r in ledger),
                                total_reported=sum(r["usage"]["total_tokens"] for r in ledger if r["usage"]),
                                accounted=sum(r["accounted"] for r in ledger)))
    for group in GROUPS:
        subset = [case for case in data if case["stratum"] == group]
        run["groups"][group] = dict(
            cases=len(subset),
            intended_owner_seed=sum(c["legacy_probe_owner"] in orders[c["id"]]["legacy_seeds"] for c in subset),
            entity_gold_outside_a_top10=sum(c["gold"][1] not in orders[c["id"]]["orders"]["A_global"]
                                           for c in subset))
    for arm in ARMS:
        metrics = Counter()
        for c in data:
            order = orders[c["id"]]["orders"][arm]
            gold = set(c["gold"])
            outcome = dict(all_top6=gold.issubset(order[:6]), all_native=gold.issubset(order),
                           entity_top6=c["gold"][1] in order[:6], entity_native=c["gold"][1] in order,
                           wrong_top3=bool(set(c["wrong"]).intersection(order[:3])),
                           wrong_top6=bool(set(c["wrong"]).intersection(order[:6])))
            metrics.update(k for k, v in outcome.items() if v)
            metrics.update(f"{c['stratum']}/{k}" for k, v in outcome.items() if v)
        scores = [{}, {}]
        for repeat in range(2):
            for path in judge_dir.glob(f"{repeat}-{arm}-*.json"):
                scores[repeat].update(json.loads(path.read_text()))
            assert set(scores[repeat]) == {c["id"] for c in data}
        agreement, noise, totals = {}, {}, [{}, {}]
        for m in METRICS:
            first, second = (np.array([int(s[c["id"]][m]) for c in data]) for s in scores)
            agreement[m] = int((first == second).sum())
            totals[0][m], totals[1][m] = int(first.sum()), int(second.sum())
            dist = (second - first).reshape(len(DOMAINS), -1).mean(axis=1)[draws].mean(axis=1) * 100
            noise[m] = dict(interval_pp=np.percentile(dist, [2.5, 97.5]).tolist(),
                            radius_pp=float(np.percentile(np.abs(dist), 95)))
        run["arms"][arm] = dict(gold=dict(metrics), judge_totals=totals, judge_agreement=agreement, judge_noise=noise)
    return run


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--assets", type=Path, required=True)
    parser.add_argument("--out", type=Path, required=True)
    parser.add_argument("--endpoint", required=True)
    parser.add_argument("--commit", required=True)
    args = parser.parse_args()
    data = fixture()
    serialized = json.dumps(data, ensure_ascii=False, sort_keys=True, separators=(",", ":"))
    if not hashlib.sha256(serialized.encode()).hexdigest().startswith(PROBE_SHA256):
        raise ValueError("probe fixture differs from preregistered digest")
    args.out.mkdir(mode=0o700, exist_ok=True, parents=True)
    path = args.out / "orders.json"
    if path.exists():
        orders = json.loads(path.read_text())
    else:
        verify_models(args.assets)
        dense = OnnxModel(args.assets / "embedding", 4)
        cross = OnnxModel(args.assets / "reranker", 4)
        orders = {c["id"]: evaluate_case(c, dense, cross) for c in data}
        path.write_text(json.dumps(orders) + "\n")
    judge = Judge(args.endpoint, args.out / "judge")
    with ThreadPoolExecutor(8) as pool:
        list(pool.map(judge.call, jobs(orders, data, ARMS)))
    result = probe_summary(data, orders, judge.out, args.commit)
    (args.out / "legacy-probe-results.json").write_text(json.dumps(result, indent=2) + "\n")


PROBE_SHA256 = "ce9a6c5b3448"

if __name__ == "__main__":
    main()
