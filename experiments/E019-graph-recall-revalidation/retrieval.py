"""Offline retrieval and deterministic evaluation. Models read local files only."""
import argparse
from collections import Counter, defaultdict
import hashlib
import json
import math
from pathlib import Path
import re

import numpy as np
import onnxruntime as ort
from tokenizers import Tokenizer

from fixture import cases

HERE = Path(__file__).resolve().parent
CONFIG = json.loads((HERE / "config.json").read_text())
P = CONFIG["retrieval"]
ARMS = ("A_global", "B_append", "C_boost", "R_no_graph", "H_graph", "X_context")
INVERSE = {"part-of": "contains", "contains": "part-of", "implements": "implemented-by",
           "implemented-by": "implements", "depends-on": "depended-on-by",
           "depended-on-by": "depends-on"}
WEIGHT = {"part-of": .95, "implements": .90, "implemented-by": .90, "contains": .85,
          "depends-on": .80, "depended-on-by": .80}
PRIORITY = {key: i for i, group in enumerate(
    (("part-of",), ("contains",), ("implements", "implemented-by"), ("depends-on", "depended-on-by"))
) for key in group}


class OnnxModel:
    def __init__(self, folder, threads):
        options = ort.SessionOptions()
        options.intra_op_num_threads = threads
        options.inter_op_num_threads = 1
        self.session = ort.InferenceSession(str(folder / "model.onnx"), options,
                                            providers=["CPUExecutionProvider"])
        self.inputs = {arg.name for arg in self.session.get_inputs()}
        self.tokenizer = Tokenizer.from_file(str(folder / "tokenizer.json"))
        self.tokenizer.enable_padding(pad_id=self.tokenizer.token_to_id("[PAD]")
                                      or self.tokenizer.token_to_id("<pad>") or 0)
        self.tokenizer.enable_truncation(max_length=256)

    def predict(self, texts, embeddings=False):
        output = []
        for offset in range(0, len(texts), 32):
            tokens = self.tokenizer.encode_batch(texts[offset:offset + 32])
            mask = np.array([item.attention_mask for item in tokens], dtype=np.int64)
            tensors = {
                "input_ids": np.array([item.ids for item in tokens], dtype=np.int64),
                "attention_mask": mask,
                "token_type_ids": np.array([item.type_ids for item in tokens], dtype=np.int64),
            }
            values = self.session.run(None, {k: v for k, v in tensors.items() if k in self.inputs})[0]
            if embeddings:
                values = (values * mask[..., None]).sum(axis=1) / mask.sum(axis=1, keepdims=True)
                values /= np.maximum(np.linalg.norm(values, axis=1, keepdims=True), 1e-12)
            else:
                values = values.reshape(len(tokens), -1)
                if values.shape[1] != 1:
                    raise ValueError("expected one cross-encoder logit per pair")
                values = values[:, 0]
            output.extend(values)
        return np.asarray(output)


def text(page):
    return f"{page['title']}\n{page['text']}"


def tokens(s):
    return re.findall(r"[a-z0-9]+|[\u3400-\u9fff]", s.lower())


def bm25(query, documents):
    terms = {key: Counter(tokens(value)) for key, value in documents.items()}
    q = set(tokens(query))
    n = len(terms)
    lens = {k: sum(tf.values()) for k, tf in terms.items()}
    average = max(sum(lens.values()) / n, 1)
    df = Counter(term for tf in terms.values() for term in q.intersection(tf))
    idf = {term: math.log1p((n - count + .5) / (count + .5)) for term, count in df.items()}
    return {k: sum(idf[term] * freq * 2.2 / (freq + 1.2 * (.25 + .75 * lens[k] / average))
                   for term in sorted(q.intersection(tf)) for freq in (tf[term],))
            for k, tf in terms.items()}


def ranked(scores):
    return sorted(scores, key=lambda key: (-scores[key], key))


def rrf(*legs):
    scores = defaultdict(float)
    for leg in legs:
        for rank, uid in enumerate(leg, 1):
            scores[uid] += 1 / (P["rrf_k"] + rank)
    return scores


def grounded_edges(case):
    pages, sources = case["pages"], case["sources"]
    seen = set()
    for link in case["edges"]:
        a, kind, b = (link[k] for k in ("a", "kind", "b"))
        triple = (a, kind, b)
        evidence = link.get("source")
        if (a != b and a in pages and b in pages and evidence
                and (list(triple) == sources.get(evidence)) and triple not in seen):
            seen.add(triple)
            yield triple


def legacy(case, global_ids, raw_scores, edges, weak):
    pages = case["pages"]
    ranks = {uid: i for i, uid in enumerate(global_ids)}
    seeds = [uid for uid in global_ids[:5] if pages[uid]["kind"] == "entity" and uid not in weak]
    neighbors = defaultdict(set)
    for a, kind, b in edges:
        if kind in INVERSE and pages[a]["kind"] == pages[b]["kind"] == "entity":
            neighbors[a].add((kind, b))
            neighbors[b].add((INVERSE[kind], a))
    append = []
    scores = {uid: raw_scores[uid] for uid in global_ids}
    plus = Counter()
    for seed in seeds:
        for kind, uid in sorted(neighbors[seed], key=lambda item: (PRIORITY[item[0]], item[1])):
            if uid not in ranks:
                if uid not in append:
                    append.append(uid)
                scores[uid] = max(scores.get(uid, 0.0), raw_scores[seed] * WEIGHT[kind])
            elif ranks[seed] < ranks[uid]:
                plus[uid] += .03
    for uid, bonus in plus.items():
        scores[uid] += min(bonus, .06)
    # E009 C rebuilds the global order from raw scores, including without neighbors.
    return global_ids + append[:5], ranked(scores)[:P["global_depth"]], seeds


def diffuse(seeds, edges):
    weights = {**WEIGHT, "attachment": 1, "semantic": .75, "temporal": .45, "causal": 1}
    adjacency = defaultdict(dict)
    for a, kind, b in edges:
        if kind in weights:
            weight = weights[kind]
            adjacency[a][b] = max(weight, adjacency[a].get(b, 0))
            adjacency[b][a] = max(weight, adjacency[b].get(a, 0))
    activation = defaultdict(float)
    wave = {uid: 1 / math.sqrt(rank) for rank, uid in enumerate(seeds, 1)}
    for _ in range(P["graph_steps"]):
        next_wave = defaultdict(float)
        for a, mass in wave.items():
            for b, weight in adjacency[a].items():
                next_wave[b] += P["graph_decay"] * mass * weight / sum(adjacency[a].values())
        for uid, mass in next_wave.items():
            activation[uid] += mass
        wave = next_wave
    return ranked(activation)[:P["leg_depth"]]


def find_anchor(case):
    context = case["context"]
    keys = {str(context.get(key, "")).casefold() for key in ("repo", "mentioned_system")}
    keys.update(path.split("/", 1)[0].casefold() for path in context.get("paths", []))
    hits = [uid for uid, page in case["pages"].items()
            if page["kind"] == "entity" and keys.intersection(a.casefold() for a in page.get("aliases", []))]
    return hits[0] if len(hits) == 1 else None


def assemble_panel(global_ids, panel, limit):
    return list(dict.fromkeys([*global_ids[:3], *panel, *global_ids[3:]]))[:limit]


def evaluate_case(case, embedding, cross_encoder, captured=None):
    pages, query = case["pages"], case["query"]
    documents = {uid: text(page) for uid, page in pages.items()}
    uid_list = list(documents)
    vectors = embedding.predict([query, *documents.values()], embeddings=True)
    cosine = dict(zip(uid_list, (vectors[1:] @ vectors[0]).tolist(), strict=True))
    dense = ranked(cosine)[:P["leg_depth"]]
    sparse = ranked({k: v for k, v in bm25(query, documents).items() if v > 0})[:P["leg_depth"]]
    global_scores = rrf(dense, sparse)
    baseline = ranked(global_scores)[:P["global_depth"]]
    raw = {uid: score * (P["rrf_k"] + 1) / 2 for uid, score in global_scores.items()}
    weak = {uid for uid in baseline if cosine[uid] < P["weak_seed_cosine_floor"]}
    if captured is not None:
        baseline, raw, weak = captured
    edges = list(grounded_edges(case))
    append, boost, seeds = legacy(case, baseline, raw, edges, weak)
    graph_seeds = [uid for uid in dense[:P["graph_seed_depth"]]
                   if cosine[uid] >= P["weak_seed_cosine_floor"]]
    graph = diffuse(graph_seeds, edges)
    r_pool = ranked(global_scores)[:P["rerank_depth"]]
    h_pool = ranked(rrf(dense, sparse, graph))[:P["rerank_depth"]]

    anchor = find_anchor(case)
    attachments = [(a, b) for a, kind, b in edges if kind == "attachment"]
    panel_pool = [b for a, b in attachments if a == anchor and b not in baseline[:3]]
    oracle = case.get("target_entity")
    oracle_pool = [b for a, b in attachments if a == oracle and b not in baseline[:3]]
    pair_ids = list(dict.fromkeys(r_pool + h_pool + panel_pool))
    cross_scores = dict(zip(pair_ids, cross_encoder.predict([(query, documents[k]) for k in pair_ids]),
                            strict=True))

    def rerank(pool):
        return sorted(pool, key=lambda uid: -cross_scores[uid])

    panel = rerank(panel_pool)[:P["panel_depth"]]
    oracle_panel = panel
    if oracle != anchor:
        oracle_scores = cross_encoder.predict([(query, documents[uid]) for uid in oracle_pool])
        oracle_panel = ranked(dict(zip(oracle_pool, oracle_scores, strict=True)))[:P["panel_depth"]]
    orders = dict(zip(ARMS, (baseline, append, boost, rerank(r_pool), rerank(h_pool),
                             assemble_panel(baseline, panel, P["read_budget"])), strict=True))
    return dict(orders=orders, legacy_seeds=seeds, graph_seeds=graph_seeds, graph=graph,
                anchor=anchor, panel=panel, global_for_panel=baseline.copy(),
                oracle_read=assemble_panel(baseline, oracle_panel, P["read_budget"]),
                accepted_edges=len(edges), rejected_edges=len(case["edges"]) - len(edges),
                required_attachments=sum(a == oracle and b in case["gold"] for a, b in attachments))


def verify_models(assets):
    for name in ("embedding", "reranker"):
        for filename, expected in CONFIG[name]["sha256"].items():
            with (assets / name / filename).open("rb") as f:
                actual = hashlib.file_digest(f, "sha256").hexdigest()
            if not actual.startswith(expected):
                raise ValueError(f"model hash mismatch for {name}/{filename}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--assets", type=Path, required=True)
    parser.add_argument("--out", type=Path, required=True)
    parser.add_argument("--threads", type=int, default=4)
    args = parser.parse_args()
    verify_models(args.assets)
    embedding = OnnxModel(args.assets / "embedding", args.threads)
    reranker = OnnxModel(args.assets / "reranker", args.threads)
    output = {case["id"]: evaluate_case(case, embedding, reranker) for case in cases()}
    args.out.write_text(json.dumps(output, indent=2) + "\n")
