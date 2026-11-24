"""Audit retrieval and judge artifacts and apply the frozen decision rules."""
import argparse
from collections import Counter
import json
from pathlib import Path

import numpy as np

from fixture import cases
from judge import J, METRICS
from retrieval import ARMS, CONFIG, P, grounded_edges

D = CONFIG["decision"]


def metrics(ids, case):
    wrong = set(case["wrong"])
    return dict(all_required=set(case["gold"]).issubset(ids),
                wrong_top3=bool(wrong.intersection(ids[:3])), wrong_top6=bool(wrong.intersection(ids)),
                wrong_object=any(case["wrong_kinds"].get(k) == "object" for k in ids),
                wrong_action=any(case["wrong_kinds"].get(k) == "action" for k in ids))


def pp(values):
    return round(float(np.mean(values) * 100), 6)


def summary(rows):
    return {m: sum(row[m] for row in rows) for m in rows[0]}


def main(orders, judge_dir, out, commit):
    fixture = cases()
    by_id = {case["id"]: case for case in fixture}
    if set(orders) != set(by_id):
        raise ValueError("retrieval artifact does not match the frozen sample")
    native = {arm: {} for arm in ARMS}
    gold = {arm: {} for arm in ARMS}
    oracle, attachment_total, attachment_correct = [], 0, 0
    for uid, item in orders.items():
        case = by_id[uid]
        for arm in ARMS:
            ids = item["orders"][arm]
            if len(set(ids)) != len(ids) or not set(ids).issubset(case["pages"]):
                raise ValueError(f"invalid rank list {uid}/{arm}")
            native[arm][uid] = set(case["gold"]).issubset(ids)
            gold[arm][uid] = metrics(ids[:P["read_budget"]], case)
        oracle.append(metrics(item["oracle_read"], case))
        for a, kind, b in grounded_edges(case):
            if kind != "attachment" or a != case["target_entity"]:
                continue
            attachment_total += 1
            attachment_correct += case["pages"][a]["title"].casefold() in case["pages"][b]["text"].casefold()
    judges = [{arm: {} for arm in ARMS} for _ in range(J["rounds"])]
    for path in sorted(judge_dir.glob("*.json")):
        run, arm, _ = path.stem.split("-")
        seen = judges[int(run)][arm]
        found = json.loads(path.read_text())
        if seen.keys() & found.keys():
            raise ValueError(f"duplicate judge verdicts: {path}")
        seen.update(found)
    for run in judges:
        for arm in ARMS:
            if set(run[arm]) != set(by_id):
                raise ValueError(f"incomplete judge coverage: {arm}, {len(run[arm])}/{len(by_id)}")

    cluster_count = CONFIG["sample"]["clusters"]
    groups = np.array([[c["id"] for c in fixture if c["cluster"] == i] for i in range(cluster_count)])
    draws = np.random.default_rng(D["bootstrap_seed"]).integers(
        0, cluster_count, (D["bootstrap_draws"], cluster_count))

    def matrix(rows, arm, metric):
        return np.array([[rows[arm][uid][metric] for uid in group] for group in groups], dtype=float)

    def distribution(values):
        return values.mean(axis=1)[draws].mean(axis=1) * 100

    def interval(distribution):
        return np.percentile(distribution, [2.5, 97.5]).round(6).tolist()

    report = dict(preregistered_commit=commit, total=len(by_id), per_arm={}, paired={}, case_rows={})
    radii = {}
    for arm in ARMS:
        noise, agreement = {}, {}
        for m in METRICS:
            first, second = (matrix(run, arm, m) for run in judges)
            dist = distribution(second - first)
            width = float(np.percentile(np.abs(dist), 95))
            radii[arm, m] = width
            noise[m] = dict(signed_interval_pp=interval(dist), absolute_radius_pp=round(width, 6))
            agreement[m] = int(np.sum(first == second))
        report["per_arm"][arm] = dict(
            gold_top6=summary(list(gold[arm].values())), native_all_required=sum(native[arm].values()),
            native_depths=dict(Counter(len(v["orders"][arm]) for v in orders.values())),
            by_stratum={s: summary([gold[arm][uid] for uid, c in by_id.items() if c["stratum"] == s])
                        for s in sorted({c["stratum"] for c in fixture})},
            judge_passes=[summary(list(run[arm].values())) for run in judges],
            judge_agreement=agreement, judge_noise=noise)
    report["native_E009"] = {
        "A_top10_both": sum(native["A_global"].values()),
        "B_first10_both": sum(set(case["gold"]).issubset(orders[uid]["orders"]["B_append"][:10])
                              for uid, case in by_id.items()),
        "B_full_both": sum(native["B_append"].values()),
        "C_top10_both": sum(native["C_boost"].values()),
    }
    selected = sum(row["anchor"] is not None for row in orders.values())
    anchorable = sum(case["target_entity"] is not None for case in fixture)
    exact = sum(row["anchor"] is not None and row["anchor"] == by_id[uid]["target_entity"]
                for uid, row in orders.items())
    required = sum(item["required_attachments"] for item in orders.values())
    global_same = sum(item["global_for_panel"] == item["orders"]["A_global"] for item in orders.values())
    report["coverage"] = dict(
        e009_no_seed=sum(not item["legacy_seeds"] for item in orders.values()),
        graph_no_seed=sum(not item["graph_seeds"] for item in orders.values()),
        graph_empty=sum(not item["graph"] for item in orders.values()),
        anchor_selected=selected, anchor_exact=exact, anchorable=anchorable,
        attachment_correct=attachment_correct, attachment_total=attachment_total,
        required_attachments=required, required_attachment_total=2 * anchorable,
        global_order_identical=global_same, panel_nonempty=sum(bool(v["panel"]) for v in orders.values()),
        accepted_edges=sum(item["accepted_edges"] for item in orders.values()),
        rejected_edges=sum(item["rejected_edges"] for item in orders.values()), oracle=summary(oracle))
    attachment_gate = (attachment_correct >= D["attachment_precision_floor"] * attachment_total
                       and attachment_total > 0 and required >= D["attachment_recall_floor"] * 2 * anchorable
                       and global_same == len(fixture))
    statuses = []
    for arm, base in (("H_graph", "R_no_graph"), ("X_context", "A_global"),
                      ("H_graph", "A_global"), ("B_append", "A_global"), ("C_boost", "A_global")):
        evidence = {}
        for m in METRICS:
            values = matrix(gold, arm, m) - matrix(gold, base, m)
            crossed = [pp(matrix(j, arm, m) - matrix(k, base, m)) for j in judges for k in judges]
            evidence[m] = dict(gold_delta_pp=pp(values), gold_interval_pp=interval(distribution(values)),
                               judge_crossed_pp=[min(crossed), max(crossed)],
                               judge_pair_noise_pp=round(radii[arm, m] + radii[base, m], 6))
        report["paired"][f"{arm}_vs_{base}"] = evidence
        if (arm, base) not in {("H_graph", "R_no_graph"), ("X_context", "A_global")}:
            continue
        gain, harm = (evidence[m] for m in ("all_required", "wrong_top6"))
        bar, guard = D["gain_pp"], D["wrong_page_max_increase_pp"]
        works = (gain["gold_delta_pp"] >= bar and gain["gold_interval_pp"][0] > 0
                 and harm["gold_interval_pp"][1] <= guard
                 and gain["judge_crossed_pp"][0] > gain["judge_pair_noise_pp"]
                 and harm["judge_crossed_pp"][1] + harm["judge_pair_noise_pp"] <= guard)
        ruled = ((gain["gold_interval_pp"][1] < bar
                  and gain["judge_crossed_pp"][1] + gain["judge_pair_noise_pp"] < bar)
                 or (harm["gold_interval_pp"][0] > guard
                     and harm["judge_crossed_pp"][0] - harm["judge_pair_noise_pp"] > guard))
        if arm == "X_context" and not attachment_gate:
            works, ruled = False, False
        status = "Works" if works else ("Does not work" if ruled else "Inconclusive")
        evidence["decision"] = status
        statuses.append(status)
    report["decision"] = ("Works" if "Works" in statuses else
                          "Does not work" if statuses == ["Does not work"] * 2 else "Inconclusive")

    for uid in by_id:
        report["case_rows"][uid] = {
            "orders": orders[uid]["orders"],
            "gold_top6": {arm: gold[arm][uid] for arm in ARMS},
            "judge_passes": [{arm: j[arm][uid] for arm in ARMS} for j in judges],
        }
    ledger = [json.loads(line) for line in (judge_dir / "usage.jsonl").open()]
    received = [r["usage"] for r in ledger if r["usage"]]
    report["judge_usage"] = dict(
        requested=J["model"], resolved=sorted({r["model"] for r in ledger if r["model"]}),
        attempts=len(ledger), successful_batches=sum(r["error"] is None for r in ledger),
        failures=sum(r["error"] is not None for r in ledger),
        input_tokens=sum(r["prompt_tokens"] for r in received),
        cached_input_tokens=sum(r.get("prompt_tokens_details", {}).get("cached_tokens", 0) for r in received),
        output_tokens=sum(r["completion_tokens"] for r in received),
        total_reported_tokens=sum(r["total_tokens"] for r in received),
        total_accounted_tokens=sum(r["accounted"] for r in ledger))
    out.write_text(json.dumps(report, separators=(",", ":"), ensure_ascii=False) + "\n")
    print(json.dumps({k: v for k, v in report.items() if k not in {"case_rows", "per_arm"}}, indent=2))


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--orders", type=Path, required=True)
    parser.add_argument("--judge-dir", type=Path, required=True)
    parser.add_argument("--out", type=Path, required=True)
    parser.add_argument("--commit", required=True)
    args = parser.parse_args()
    main(json.loads(args.orders.read_text()), args.judge_dir, args.out, args.commit)
