# E010: Supersession and abstention on LongMemEval

- Conclusion: Inconclusive
- Date: 2026-11-20
- Issue: [#58, preregistration](https://github.com/yaodiff/memory-lab/issues/58)
- Source: [LongMemEval, ICLR 2025](https://arxiv.org/abs/2410.10813)
- Handoff: none

## Hypothesis

On LongMemEval v1 cleaned S, date-ordered fact pages with explicit supersession and a low-evidence gate improve balanced QA accuracy by at least 10 percentage points over keyword retrieval. The preregistration requires strictly positive gains in both repeats and no drop within either stratum for the improvement claim. Gains at or below zero in both repeats falsify the claim under this protocol. All other outcomes, incomplete answers, or judge-prompt agreement below 90% leave the claim unresolved.

## Method

[LongMemEval v1 cleaned S](https://huggingface.co/datasets/xiaowu0162/longmemeval-cleaned) is MIT-licensed. We select 20 answerable knowledge-update and 20 abstention questions using the lowest SHA-256 hashes of `20261120:<question_id>` in each stratum. The abstention stratum uses the `_abs` suffix. All four arms see the same question and its date. All memory arms ignore sessions dated after that question and use the remaining S history, including distractors. Answer and evidence labels are held out from memory construction and answering.

| Arm | Memory supplied |
| --- | --- |
| No memory | Empty memory field |
| Summary | One question-blind summary. Score chunks across the full eligible timeline, select one representative per chronological bin, and ask the model to compress the representatives together. |
| BM25 | Top six keyword-ranked 160-word chunks with 32-word overlap, displayed chronologically |
| Fact pages | Extract dated facts from the same six chunks at query time. For the same mutable slot, a later chunk marks earlier records superseded. Put active pages before superseded pages and give active pages precedence. Require `UNKNOWN` if no active source covers at least 35% of the query's IDF-weighted vocabulary. |

All stages run on local CPU with the official [Qwen2.5-1.5B-Instruct Q4_K_M](https://huggingface.co/Qwen/Qwen2.5-1.5B-Instruct-GGUF) weights, served by [llama.cpp b12560](https://github.com/ggml-org/llama.cpp/releases/tag/b12560). The answer API reported `qwen2.5-1.5b-instruct-q4_k_m`. Each question-arm pair uses two independent answer calls with seeds 101 and 202 at temperature 0.4 and the same frozen memory. The gate constrains the answer to `UNKNOWN` in those calls. The same local model scores each answer with a binary rubric, blind to arm and seed. A second prompt with a different field order grades every answer again to measure judge-prompt agreement.

Reproduce from the repository root with Python 3.11+, curl, and the pinned llama.cpp release. Use a data directory outside this checkout.

```bash
exp=experiments/E010-longmemeval-supersession
python3 "$exp/download.py" "$DATA_DIR"
llama-server --model "$DATA_DIR/qwen2.5-1.5b-instruct-q4_k_m.gguf" \
  --alias qwen2.5-1.5b-instruct-q4_k_m --host 127.0.0.1 --port 18754 \
  --ctx-size 32768 --parallel 4 --threads 8 --threads-batch 12 --no-webui
```

In a second shell, with the same variables set:

```bash
timeout 2h python3 "$exp/run.py" "$DATA_DIR/longmemeval_s_cleaned.json" \
  --workers 4 --out "$exp/results.json"
```

The [config](config.json) pins dataset and model revisions and their SHA-256 checksums, encoded in base64. The [runner](run.py) includes answer and judge prompts. [Results](results.json) contain only question IDs, scores and counters.

## Results

Run window `2026-11-20T10:02:27+00:00` to `2026-11-20T10:22:53+00:00` (1226.2 s). Runner commit `ccd42b1a36a5`. The [issue](https://github.com/yaodiff/memory-lab/issues/58) froze the plan at 09:43:10 UTC before this run. All 320 of 320 answers have both judge scores. No sampled question was dropped. Local inference used no paid API.

Before the scored run, synthetic controls exercised summary construction, supersession and the gate. The original Boolean-response judge failed an exact-match control. A PASS/FAIL response format and calibrated prompts passed 16 of 16 synthetic judge checks.
An initial scored attempt at 09:58 UTC stopped when truncation left an unterminated JSON answer. The runner then used bounded plain text for ordinary answers and summaries, and retained the structured gate and grading. All questions and both seeds were rerun from scratch under the same preregistered decision rule. The table uses the complete rerun.

Cells show correct answers over unique questions in that stratum. A score flip means the same question was correct with one seed and incorrect with the other. The absolute gap can be zero even when individual questions flip.

### Balanced sample (40 questions)

| Arm | Seed 101 | Seed 202 | Mean accuracy | Absolute repeat gap | Score flips |
| --- | ---: | ---: | ---: | ---: | ---: |
| No memory | 17/40 (42.5%) | 17/40 (42.5%) | 42.5% | 0.0 pp | 0/40 |
| Summary | 17/40 (42.5%) | 17/40 (42.5%) | 42.5% | 0.0 pp | 0/40 |
| BM25 | 22/40 (55.0%) | 20/40 (50.0%) | 52.5% | 5.0 pp | 4/40 |
| Fact pages | 20/40 (50.0%) | 20/40 (50.0%) | 50.0% | 0.0 pp | 0/40 |

### Knowledge update (20 questions)

| Arm | Seed 101 | Seed 202 | Mean accuracy | Absolute repeat gap | Score flips |
| --- | ---: | ---: | ---: | ---: | ---: |
| No memory | 0/20 (0.0%) | 0/20 (0.0%) | 0.0% | 0.0 pp | 0/20 |
| Summary | 0/20 (0.0%) | 0/20 (0.0%) | 0.0% | 0.0 pp | 0/20 |
| BM25 | 5/20 (25.0%) | 4/20 (20.0%) | 22.5% | 5.0 pp | 1/20 |
| Fact pages | 3/20 (15.0%) | 3/20 (15.0%) | 15.0% | 0.0 pp | 0/20 |

### Abstention (20 questions)

| Arm | Seed 101 | Seed 202 | Mean accuracy | Absolute repeat gap | Score flips |
| --- | ---: | ---: | ---: | ---: | ---: |
| No memory | 17/20 (85.0%) | 17/20 (85.0%) | 85.0% | 0.0 pp | 0/20 |
| Summary | 17/20 (85.0%) | 17/20 (85.0%) | 85.0% | 0.0 pp | 0/20 |
| BM25 | 17/20 (85.0%) | 16/20 (80.0%) | 82.5% | 5.0 pp | 3/20 |
| Fact pages | 17/20 (85.0%) | 17/20 (85.0%) | 85.0% | 0.0 pp | 0/20 |

Fact pages minus BM25 was **-2.5 pp** across the two repeats (-5.0 and +0.0 pp). The mean gaps were **-7.5 pp** for knowledge update and **+2.5 pp** for abstention. The alternate judge gave repeat gaps of -2.5 and -2.5 pp. Judge-prompt agreement was **250/320 (78.1%)**.

The gate fired on 4/20 update questions and 7/20 abstention questions. At least one earlier page was marked superseded on 14/20 update questions and 6/20 abstention questions. The time filter omitted 78 post-question sessions. No annotated answer session was after the cutoff.

Among 283 literal `UNKNOWN` responses (ignoring case and trailing punctuation), the primary/alternate judges disagreed with the expected category on 20/78 responses respectively. This is a narrow scoring check and does not measure all semantic errors.

## Interpretation

The 78.1% judge-prompt agreement fell below the preregistered 90% floor, so the result is **Inconclusive**. The primary judge's observed gains are descriptive. It also rejected some literal refusals that should have received credit. The gap between the two judges and their errors on literal refusals limit the evidence for either intervention.

## Scope

- This is a balanced 40-question pilot of two abilities from the S split. Knowledge-update questions can ask for the most recent event as well as the current value of a mutable fact. Its QA accuracy uses a local judge and a custom protocol. The official full-benchmark scores use a different denominator and judge.
- The fact-page arm combines extraction, supersession and gating. The design measures their joint effect. It uses query-time materialization and does not measure persistent indexing, memory writes, or long-running updates.
- The two answer seeds measure answer/score variation with the same constructed memory. The summary and extracted pages are frozen across repeats. The two grading prompts share one small model, so their agreement measures sensitivity to wording and field order.
