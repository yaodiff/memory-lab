"""Run the five E012 arms on the E010 questions with local inference."""

import argparse
from concurrent.futures import ThreadPoolExecutor, as_completed
from importlib.metadata import version
import json
import math
import os
from pathlib import Path
from statistics import median
from time import perf_counter

from audit_judge import e010, is_abstention, model_grade

# Prevent upstream defaults from sending telemetry or choosing a hosted provider.
os.environ["MEM0_TELEMETRY"] = "false"
os.environ["HF_HUB_OFFLINE"] = "1"
os.environ.pop("OPENROUTER_API_KEY", None)

from mem0 import Memory
from qdrant_client import QdrantClient

from prepare_embeddings import ASSETS


COMPONENT = "mem0"
ARMS = (*e010.ARMS, COMPONENT)
PACKAGES = ("mem0ai", "fastembed", "qdrant-client", "onnxruntime")


def timed(function, *args):
    start = perf_counter()
    value = function(*args)
    return value, round(1000 * (perf_counter() - start), 3)


def mem0_index(port, chunks):
    store = Memory.from_config({
        "vector_store": {
            "provider": "qdrant",
            "config": {"client": QdrantClient(":memory:"), "embedding_model_dims": 384},
        },
        "embedder": {"provider": "fastembed", "config": {"model": "BAAI/bge-small-en-v1.5",
                                                       "embedding_dims": 384}},
        "llm": {"provider": "openai", "config": {
            "model": e010.CONFIG["model_alias"],
            "api_key": "local",
            "openai_base_url": f"http://localhost:{port}/v1",
        }},
        "history_db_path": ":memory:",
    })
    messages = [{"role": "user", "content": chunk.text, "name": str(i)}
                for i, chunk in enumerate(chunks)]
    inserted = store.add(messages, user_id="question", infer=False)["results"]
    if len(inserted) != len(chunks):
        raise ValueError(f"Mem0 inserted {len(inserted)} of {len(chunks)} chunks")
    return store


def mem0_retrieve(store, chunks, question):
    hits = store.search(question, filters={"user_id": "question"},
                        top_k=e010.CONFIG["top_k"], threshold=0.1, rerank=False)["results"]
    indices = sorted(int(hit["actor_id"]) for hit in hits)
    return e010.format_chunks([chunks[index] for index in indices]), len(hits)


def prepare_memories(item, port):
    (chunks, excluded), cut_ms = timed(e010.cut_history, item)
    weights, weight_ms = timed(e010.document_weights, chunks)
    question = item["question"]
    query = sorted(set(e010.terms(question)))
    retrieved, retrieval_ms = timed(e010.retrieve, chunks, query, weights)
    summary, summary_ms = timed(e010.summarize, port, chunks, weights)
    pages, page_ms = timed(e010.build_pages, port, retrieved, question)
    (fact_memory, gate), select_ms = timed(e010.select_pages, pages, retrieved,
                                          query, weights, len(chunks))
    bm25_memory, format_ms = timed(e010.format_chunks, retrieved)
    store, index_ms = timed(mem0_index, port, chunks)
    (mem0_memory, hits), mem0_retrieval_ms = timed(mem0_retrieve, store, chunks, question)
    return {
        "no_memory": ("", False, 0, None),
        "summary": (summary, False, cut_ms + weight_ms + summary_ms, None),
        "bm25": (bm25_memory, False, cut_ms + weight_ms, retrieval_ms + format_ms),
        "fact_pages": (fact_memory, gate, cut_ms + weight_ms + page_ms + select_ms, retrieval_ms),
        "mem0": (mem0_memory, False, cut_ms + index_ms, mem0_retrieval_ms),
    }, {"chunks": len(chunks), "excluded_future_sessions": excluded,
        "fact_pages": len(pages), "gate_fired": gate, "mem0_hits": hits}


def answer_question(item, stratum, port):
    memories, counts = prepare_memories(item, port)
    rows = {}
    for arm, (memory, gate, prep_ms, retrieval_ms) in memories.items():
        repeats = []
        for seed in e010.SEEDS:
            candidate, answer_ms = timed(e010.answer, port, item["question"], item["question_date"],
                                         memory, seed, gate)
            repeats.append({"seed": seed, "answer": candidate, "answer_ms": answer_ms})
        rows[arm] = {"prep_ms": round(prep_ms, 3), "retrieval_ms": retrieval_ms, "repeats": repeats}
    return {"id": item["question_id"], "stratum": stratum, "arms": rows, **counts}


def score_question(question, by_id, port):
    item = by_id[question["id"]]
    abstention = question["stratum"] == "abstention"
    for cells in question["arms"].values():
        for row in cells["repeats"]:
            candidate = row.pop("answer")
            row["correct"] = (is_abstention(candidate) if abstention
                              else model_grade(port, item["question"], item["answer"], candidate))
    return question


def summarize_scores(questions):
    by_stratum = {}
    for stratum in (*e010.STRATA, "balanced"):
        selected = [q for q in questions if stratum == "balanced" or q["stratum"] == stratum]
        by_stratum[stratum] = {}
        for arm in ARMS:
            scores = [[r["correct"] for r in q["arms"][arm]["repeats"]] for q in selected]
            counts = [sum(repeat) for repeat in zip(*scores, strict=True)]
            by_stratum[stratum][arm] = {
                "questions": len(scores),
                "correct_by_repeat": counts,
                "mean_accuracy_pct": round(100 * sum(counts) / (len(scores) * len(counts)), 4),
                "absolute_seed_spread_pp": round(100 * (max(counts) - min(counts)) / len(scores), 4),
                "correctness_flips": sum(len(set(pair)) > 1 for pair in scores),
            }
    return by_stratum


def distribution(values):
    if not values:
        return None
    ordered = sorted(values)
    return {"n": len(values), "p50_ms": round(median(values), 3),
            "p95_ms": round(ordered[math.ceil(0.95 * len(values)) - 1], 3)}


def summarize_latency(questions):
    latency = {}
    for arm in ARMS:
        rows = [question["arms"][arm] for question in questions]
        latency[arm] = {
            "prep": distribution([row["prep_ms"] for row in rows]),
            "retrieval": distribution([row["retrieval_ms"] for row in rows
                                       if row["retrieval_ms"] is not None]),
            "answer": distribution([r["answer_ms"] for row in rows for r in row["repeats"]]),
            "cold": distribution([row["prep_ms"] + (row["retrieval_ms"] or 0) + r["answer_ms"]
                                   for row in rows for r in row["repeats"]]),
            "amortized": distribution([
                (row["prep_ms"] + (row["retrieval_ms"] or 0)) / len(row["repeats"]) + r["answer_ms"]
                for row in rows for r in row["repeats"]
            ]),
        }
    return latency


def compare(scores):
    balanced = scores["balanced"]
    baseline = max(e010.ARMS, key=lambda arm: balanced[arm]["mean_accuracy_pct"])
    repeat_gains = [round(100 * (a - b) / balanced[baseline]["questions"], 4)
                    for a, b in zip(balanced[COMPONENT]["correct_by_repeat"],
                                    balanced[baseline]["correct_by_repeat"], strict=True)]
    stratum_gains = {s: round(scores[s][COMPONENT]["mean_accuracy_pct"]
                              - scores[s][baseline]["mean_accuracy_pct"], 4)
                      for s in e010.STRATA}
    mean_gain = sum(repeat_gains) / len(repeat_gains)
    if mean_gain >= e010.CONFIG["minimum_gain_pp"] and min(repeat_gains) > 0 and min(stratum_gains.values()) >= 0:
        conclusion = "Works"
    elif max(repeat_gains) <= 0:
        conclusion = "Does not work"
    else:
        conclusion = "Inconclusive"
    return {"baseline": baseline, "mean_gain_pp": mean_gain, "repeat_gain_pp": repeat_gains,
            "stratum_gain_pp": stratum_gains, "conclusion": conclusion}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("dataset", type=Path)
    parser.add_argument("--judge-audit", type=Path, required=True)
    parser.add_argument("--checkpoint", type=Path, required=True,
                        help="Local-only JSONL of timed answer outputs.")
    parser.add_argument("--out", type=Path, required=True)
    parser.add_argument("--port", type=int, default=18754)
    parser.add_argument("--workers", type=int, default=4)
    args = parser.parse_args()

    repo = Path(__file__).resolve().parents[2]
    if args.checkpoint.resolve().is_relative_to(repo):
        parser.error("Keep answer outputs outside the repository")
    gate = json.loads(args.judge_audit.read_text())
    audit = gate["knowledge_update_audit"]
    if (not gate["gate_passed"] or audit["total"] != 20
            or audit["matched"] / audit["total"] < e010.CONFIG["minimum_judge_agreement"]):
        parser.error("The preregistered judge gate did not pass")
    if e010.digest(args.dataset) != e010.CONFIG["dataset"]["sha256_base64"]:
        parser.error("Dataset checksum does not match E010")
    selected, pool = e010.sample(json.loads(args.dataset.read_text()))
    by_id = {item["question_id"]: item for item, _ in selected}

    started = e010.utc()
    start = perf_counter()
    completed = []
    with args.checkpoint.open("x") as checkpoint, ThreadPoolExecutor(max_workers=args.workers) as workers:
        futures = [workers.submit(answer_question, item, stratum, args.port)
                   for item, stratum in selected]
        for future in as_completed(futures):
            result = future.result()
            checkpoint.write(json.dumps(result, ensure_ascii=False) + "\n")
            checkpoint.flush()
            completed.append(result)
            print(f"Timed questions: {len(completed)}/{len(selected)}", flush=True)
    answer_wall_seconds = round(perf_counter() - start, 3)

    indexed = {question["id"]: question for question in completed}
    ordered = [indexed[item["question_id"]] for item, _ in selected]
    with ThreadPoolExecutor(max_workers=args.workers) as workers:
        questions = list(workers.map(lambda row: score_question(row, by_id, args.port), ordered))

    scores = summarize_scores(questions)
    result = {
        "started_utc": started, "ended_utc": e010.utc(), "workers": args.workers,
        "answer_wall_seconds": answer_wall_seconds, "wall_seconds": round(perf_counter() - start, 3),
        "answer_model": e010.CONFIG["model_alias"], "packages": {p: version(p) for p in PACKAGES},
        "embedding_revisions": ASSETS, "pool_questions": pool, "seeds": e010.SEEDS,
        "scores": scores, "latency": summarize_latency(questions),
        "comparison": compare(scores), "per_question": questions,
    }
    args.out.write_text(json.dumps(result, indent=2) + "\n")
    print(f'{result["comparison"]["conclusion"]}; scored {len(questions)} questions', flush=True)


if __name__ == "__main__":
    main()
