# E012 · Local memory retrieval on LongMemEval

[Preregistration](https://github.com/yaodiff/memory-lab/issues/62) and [frozen Mem0 settings](https://github.com/yaodiff/memory-lab/issues/62#issuecomment-7038461925).

## Judge calibration

Qwen and Granite agreed on **19/20 (95.0%)**, above the 18/20 gate. The audit ranks the 20 E010 knowledge-update questions by the preregistered hash and cycles through the eight arm/seed cells. The independent reviewer sees only the question, reference and response. Both judges failed all 18 refusals. They agreed on one of the two substantive outputs. The other was failed by Qwen and passed by Granite. The small number of substantive responses limits what this audit establishes about semantic grading.

The deterministic abstention rule passed 143 of 160 archived abstention responses, all with an explicit `UNKNOWN` marker. It disagreed with 32 E010 primary labels (20 refusals recovered and 12 guesses rejected) and 88 alternate labels (78 refusals recovered and 10 guesses rejected). Abstention uses no model grader. Unit tests exercise affirmative answers, `UNKNOWN` variants and explicit English refusals. The [audit results](judge_results.json) contain IDs, cells and verdicts.

## Comparison design

The [E010 configuration](../E010-longmemeval-supersession/config.json) fixes the LongMemEval cleaned S revision, sample, Qwen2.5-1.5B-Instruct Q4_K_M weights, llama.cpp build b12560, and answer seeds 101 and 202. The sample has 20 knowledge-update and 20 abstention questions. The comparison imports E010's sample, cutoff, four original memory arms and answer function. Post-question sessions are excluded from every history and gold answers are reserved for scoring.

The extra arm is Mem0 OSS 2.2.1 with local Qdrant and FastEmbed. It indexes the same dated 160-word chunks used by E010 BM25 with `Memory.add(infer=False)`. Each question has a fresh in-memory store. `Memory.search` scores dense candidates with dense similarity and a sparse BM25 boost. The retriever returns up to six chunks with its default 0.1 semantic threshold and the reader sees them chronologically. spaCy is absent, so Mem0's lexical fallback uses the original text. The optional model reranker is disabled. This evaluates Mem0's raw-ingest retrieval path. Generative extraction, consolidation, and lifecycle behavior are outside the experiment. [Mem0 license](https://github.com/mem0ai/mem0/blob/v2.2.1/LICENSE) · [Mem0 search](https://github.com/mem0ai/mem0/blob/v2.2.1/mem0/memory/main.py) · [Hybrid scoring](https://github.com/mem0ai/mem0/blob/v2.2.1/mem0/utils/scoring.py)

Graphiti and Letta were screened with official sources. Graphiti is Apache-2.0 and needs a graph backend, a structured-output LLM and an embedder. Its search recipes allow BM25, dense and graph traversal with rank fusion, diversity, or an optional reranker. Letta Code is Apache-2.0. Its local mode uses the Node.js 22.19+ CLI and can connect to a local inference endpoint. Current MemFS uses file search by default and offers optional QMD-backed semantic/hybrid search with model reranking disabled by the official extension. The legacy self-hosted V1 server uses Docker/PostgreSQL and can use Ollama for inference. The archive search uses an embedding backend. These two components were not timed. [Graphiti local setup](https://github.com/getzep/graphiti/blob/9b8a46300920/README.md#using-graphiti-with-openai-compatible-providers-and-local-llms) · [Graphiti search recipes](https://github.com/getzep/graphiti/blob/9b8a46300920/graphiti_core/search/search_config_recipes.py) · [Letta Code license](https://github.com/letta-ai/letta-code/blob/758735789b96/LICENSE) · [Letta CLI requirements](https://docs.letta.com/quickstart) · [Letta V1 Docker](https://docs.letta.com/v1-sdk/docker) · [MemFS](https://github.com/letta-ai/letta-docs-md/blob/44776b832935/concepts/memfs/index.md) · [MemFS search implementation](https://github.com/letta-ai/mods/blob/e49df6715cb3/packages/memfs-search/mods/index.mjs#L332-L345)

A local synthetic smoke test indexed two chunks, found the expected chunk and verified one sparse BM25 hit. The comparison uses only loopback inference and predownloaded public embedding assets with telemetry disabled. It runs four concurrent questions on the devbox CPU. Judge calls run after timing.

Latency is client wall-clock time measured with a monotonic clock. Preparation includes the arm's share of standalone history processing and any summary/extraction/indexing. Retrieval measures top-k selection where applicable. Both seeds use the same prepared memory. Cold totals assign the entire preparation and retrieval once to each answer. Amortized totals assign half of that shared work to each answer. Component timings include shared CPU and answer-server contention. Cold totals are sums of stages, excluding gaps spent on other arms. The p95 is the nearest-rank quantile.

## Reproduction

Keep all model weights, downloaded data and answer traces outside the checkout. Use the [E010 download and llama-server instructions](../E010-longmemeval-supersession/README.md) for the primary model and dataset. The optional E010 `--trace` writes an answer archive. This audit used the original run's local archive and matched its question IDs, cells and two original score fields to published E010 results. Regenerating an answer trace can change local model outputs.

For independent review, serve [IBM Granite 4.0 Micro GGUF](https://huggingface.co/ibm-granite/granite-4.0-micro-GGUF/tree/55cded3dcb8a) revision `55cded3dcb8a`, Q4_K_M on loopback port 18755 with alias `granite-4.0-micro-q4_k_m` using llama.cpp b12560, CPU, 8 threads, one slot and context size 4096.

```bash
exp=experiments/E012-local-memory-components
python3 -m venv "$DATA_DIR/e012-venv"
source "$DATA_DIR/e012-venv/bin/activate"
pip install mem0ai==2.2.1 fastembed==0.9.1 qdrant-client==1.20.0 onnxruntime==1.32.0
export FASTEMBED_CACHE_PATH="$DATA_DIR/e012-embeddings" MEM0_DIR="$DATA_DIR/e012-mem0"
python "$exp/prepare_embeddings.py"
python -m unittest discover -s "$exp"
python "$exp/audit_judge.py" "$DATA_DIR/e010-answers.json" --out "$DATA_DIR/e012-audit.json"
python "$exp/run_comparison.py" "$DATA_DIR/longmemeval_s_cleaned.json" \
  --judge-audit "$DATA_DIR/e012-audit.json" --workers 4 \
  --checkpoint "$DATA_DIR/e012-timed-answers.jsonl" --out "$DATA_DIR/e012-results.json"
```

## Results

**Inconclusive**. Mem0 scored 21/40 in each repeat (52.5%). No memory and summary tied as the strongest E010 arms at 20/40 (50.0%) per repeat. The preregistered order selects no memory for the comparison. Mem0 gained 2.5 percentage points in both repeats, below the +10 pp target. Against no memory it gained 15 pp on knowledge updates and lost 10 pp on abstention.

Local CPU run from 2026-11-20T11:34:22+00:00 to 2026-11-20T12:03:04+00:00. Timed answering took 1620.6 s and the full run took 1721.2 s. All 400 responses were scored. The timed runner was `8d4fbf64bfbf`. A refusal-format test extension run during answering changed zero labels when checked across all 200 scored abstention outputs.

| Arm | Balanced 101 / 202 | Knowledge update 101 / 202 | Abstention 101 / 202 | Mean balanced | Repeat gap | Score flips |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| No memory | 20/40 / 20/40 | 0/20 / 0/20 | 20/20 / 20/20 | 50.00% | 0.0 pp | 0/40 |
| Summary | 20/40 / 20/40 | 0/20 / 0/20 | 20/20 / 20/20 | 50.00% | 0.0 pp | 0/40 |
| BM25 | 19/40 / 19/40 | 3/20 / 4/20 | 16/20 / 15/20 | 47.50% | 0.0 pp | 2/40 |
| Fact pages + gate | 18/40 / 17/40 | 2/20 / 2/20 | 16/20 / 15/20 | 43.75% | 2.5 pp | 1/40 |
| Mem0 OSS | 21/40 / 21/40 | 3/20 / 3/20 | 18/20 / 18/20 | 52.50% | 0.0 pp | 0/40 |

Repeat gap is the absolute difference between aggregate seed scores. A flip is a different correctness verdict on the same question. Scores by stratum and per-question timings are in the [numeric results](results.json).

| Arm | Prepare p50 / p95 (s) | Retrieve p50 / p95 (ms) | Answer p50 / p95 (s) | Cold total p50 / p95 (s) | Amortized total p50 / p95 (s) |
| --- | ---: | ---: | ---: | ---: | ---: |
| No memory | 0.00 / 0.00 | — | 0.73 / 5.01 | 0.73 / 5.01 | 0.73 / 5.01 |
| Summary | 33.41 / 145.29 | — | 1.22 / 4.22 | 36.14 / 147.16 | 19.63 / 74.51 |
| BM25 | 0.05 / 0.13 | 1.94 / 3.15 | 3.29 / 10.75 | 3.33 / 10.81 | 3.31 / 10.78 |
| Fact pages + gate | 45.22 / 110.84 | 1.92 / 3.14 | 1.22 / 8.24 | 49.06 / 111.69 | 26.87 / 57.31 |
| Mem0 OSS | 14.24 / 45.87 | 39.12 / 105.60 | 3.45 / 11.43 | 19.41 / 53.79 | 12.46 / 29.97 |

This is a balanced pilot using 40 public questions. No memory refused every abstention question and answered no update questions correctly. Its balanced score therefore reflects the equal weight assigned to both strata. E012 scores use the new grading scheme. The E010 report uses its original judges. The measurement supports a latency and QA comparison for the frozen raw-ingest Mem0 configuration on this host.
