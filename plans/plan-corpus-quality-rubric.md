# Evaluate the quality of the stored memory corpus

- Status: Draft proposal
- Issue: [#80](https://github.com/yaodiff/memory-lab/issues/80)
- Scope: Assess the stored pages and relationships directly and check whether maintenance improves them.

The reviewed Zep and Mem0 papers emphasize downstream question answering. Letta also describes grading the accuracy of memory edits. These sources leave room for a repeatable baseline of the whole stored corpus. [Zep paper](https://arxiv.org/abs/2501.13956) · [Mem0 paper](https://arxiv.org/abs/2504.19413) · [Letta Context-Bench](https://www.letta.com/blog/evaluating-memory-in-production-agents/)

| Layer | Measurement |
| --- | --- |
| L0 Corpus-wide lint | Count deterministic issues such as truncated summaries, dangling replacements, and orphaned pages. |
| L1 Page semantics | Blind-grade a stratified sample for scope, usefulness and factual accuracy against sources. Track unsupported and contradicted claims independently. |
| L2 Entities and relationships | Review attachment correctness and provenance. Track valid, dead, missing and unverifiable pointers. [W3C PROV-O](https://www.w3.org/TR/prov-o/) |
| L3 Corpus health | Track staleness using explicit proxies, potentially conflicting pairs, and the page-type distribution. |

Calibrate on a human-labeled sample, have independent judges grade blind, adjudicate disagreements, and report inter-rater agreement alongside the raw agreement rate. Freeze a panel for repeated scoring. Pair the corpus scores with a frozen retrieval and behavior replay to test whether maintenance improves both. Validate the rubric on a small sample before scaling. Acceptance thresholds and measured costs remain to be established.
