# E015 Two-stage reranking across three evaluation sets

- Conclusion: Does not work
- Date: 2026-11-21
- Issue: [#80](https://github.com/yaodiff/memory-lab/issues/80)
- Source: aggregate proportions from small samples. Follow-up to [E003](../E003-llm-rerank-vs-hard-drop/README.md).

## Hypothesis and method

A pointwise relevance floor followed by listwise reranking and a first-rank safeguard can suppress distractors while preserving first-rank accuracy. Compare the frozen original order and the reranked order on the same candidates, repeating the paired replay. Repair identifier matching before scoring so a missing identifier cannot turn a labeled match into a miss. Count answer hits only on questions with a labeled answer page, and track distractors separately on questions with a labeled distractor.

## Results

| Evaluation set | Answer at rank 1 | Answer in first 3 | Answer in first 10 |
| --- | --- | --- | --- |
| Newer retrieval suite | 67.0% → 60.6% | 78.7% → 79.8% | 84.0% → 84.0% |
| Historical candidate pool | 84.9% → 80.6% | 95.7% → 96.8% | 100.0% → 100.0% |
| Earlier frozen suite | 76.8% → 70.7% | 85.9% → 85.9% | 90.9% → 90.9% |

The repeated runs gave the same rank metrics, with 0% fallback due to reranker errors. In the newer suite, distractors in the first three fell from 14.1% to 8.5% among questions with a labeled distractor. Similar pages displaced the best answer at rank one. Some failures appeared in both historical suites, which share questions. In the case used to tune the first-rank safeguard, a later pointwise score fell below the guard threshold and the answer lost first place.

## Decision and limits

Keep this reranker out of rollout. Earlier evidence for mixing similarity and relevance scores evaluated a different ranking method. The prior top-three gain from this reranker came from an earlier candidate sample and did not establish first-rank safety. The replay measures ranking on fixed candidates. It leaves live behavior and the potential of score blending open.
