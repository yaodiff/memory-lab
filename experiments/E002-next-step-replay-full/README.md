# E002 Next-step Replay complete shipped-case pilot

- 结论：说不清
- 日期：开始 2026-11-15 / 结束 2026-11-15
- Issue / PR：[#7](https://github.com/yaodiff/memory-lab/issues/7) / [#8](https://github.com/yaodiff/memory-lab/pull/8)
- 来源：[Next-step Replay demo](../../bench/next-step-replay/README.md)
- 交接：无
- 迁移：[#11](https://github.com/yaodiff/memory-lab/issues/11) / [#13](https://github.com/yaodiff/memory-lab/pull/13)

## 假设

The exploratory comparison asks whether supplying the complete oracle page
improves plan labels on the independent-origin cases across the shipped dataset.

## 做法

The owner authorized merging the demo and running the complete shipped dataset
with the existing smoke configuration. This is **all six synthetic demo cases**,
not a representative or human-calibrated benchmark. No wider model matrix was
run, and the same-session exposure controls are never pooled with independent
origins. This full pilot is separate from the earlier
[E001 bounded smoke](../E001-next-step-replay-smoke/README.md).

The [frozen parameters](config.json) come from the published run. A pre-run
effectiveness threshold is unrecorded.

### Frozen setup and observation window

- Evaluated source on `main`: [`bb43d1a755f7`](https://github.com/yaodiff/memory-lab/commit/bb43d1a755f7),
  published by [PR #6](https://github.com/yaodiff/memory-lab/pull/6).
- Dataset: [synthetic Click cases](../../bench/datasets/click-synthetic/README.md), based on
  public Click 8.1.8. Cases, pages, planner prompt and judge rules were unchanged
  throughout evaluation. No case was removed after observing its result.
- All cases were freshly replayed in both `no_memory` and `oracle_page`; no
  smoke result was reused. Plan replay only: no generated patch was executed.
- CLI: claude: `2.1.325 (Claude Code)`. Existing first-party OAuth login; no new paid API key.
- Planner and both judges requested `haiku`; every response reported the resolved
  model `claude-haiku-5-5`. The two judges used separate blind calls and different
  prompts, not different underlying models; correlated errors remain possible.
- Window: `2026-11-15T04:53:58Z` through `2026-11-15T04:57:55Z` (UTC, first launch through last
  recorded CLI response). No harness retries, fallback models or extra arms.

### Exact command

From the repository root, after explicit owner approval:

```bash
bench/next-step-replay/run.sh --cases 6 --allow-full-run \
  --planner-backend claude --planner-model haiku \
  --judge-a-model haiku --judge-b-model haiku \
  --out bench/next-step-replay/runs/full-20261115 --timeout 180
```

Manifest status: `complete`; planned invocation completion rate: **100.0%**.
The run used the authorized `6 * 2 * (1 + 2) = 36` CLI-invocation budget.
That is a harness call count, not a claim about provider-internal attempts or
billable requests. CLI usage estimates are not a verified subscription bill;
no monetary-cost claim is made here.

## 数据

### Descriptive readout

Within `other_session`, both judges assigned a **25.0%** violates rate to
`no_memory` and **0.0%** to `oracle_page`. Full-plan rates were **50.0%** for
both no-memory judges, versus **75.0%** for oracle judge A and **100.0%** for
oracle judge B. The oracle plans were **not unanimously full**.

The oracle disagreement concerns `click-004`'s optional verification with a
different `COLUMNS` value after explicitly using `terminal_width=48`. Judge A
considered that environment mutation ambiguous under the scope; judge B treated
it as an independence diagnostic, not a dependency of the test. Both original
verdicts are retained: no adjudication, rubric change, or selective rerun.
This makes oracle plan three-way agreement **75.0%**, while binary agreement
remains **100.0%**; point-level three-way agreement is **90.9%**.

The `same_session` controls were **100.0%** full in both arms for each judge.
Their rule reminder was already visible in both prefixes; do not mix them into
a cross-session score or claim an incremental memory benefit from saturation.
These descriptive ratios do not establish general effectiveness.

### Recorded output

The following is the saved, independently recomputed report. Plan labels are
derived from all point labels: any `violates` wins; otherwise every point must be
`full` for a full plan. No forced judge consensus or discarded disagreements.
See the [judge contract](../../bench/judges/README.md).

### Per-case labels

| Case | Page origin | Arm | Judge A | Judge B | Point labels A / B |
| --- | --- | --- | --- | --- | --- |
| click-001 | other_session | no_memory | partial | partial | partial, full, full / partial, full, full |
| click-001 | other_session | oracle_page | full | full | full, full, full / full, full, full |
| click-002 | same_session | no_memory | full | full | full, full, full / full, full, full |
| click-002 | same_session | oracle_page | full | full | full, full, full / full, full, full |
| click-003 | other_session | no_memory | full | full | full, full, full / full, full, full |
| click-003 | other_session | oracle_page | full | full | full, full, full / full, full, full |
| click-004 | other_session | no_memory | violates | violates | partial, violates, full / partial, violates, full |
| click-004 | other_session | oracle_page | partial | full | full, partial, full / full, full, full |
| click-005 | same_session | no_memory | full | full | full, full, full / full, full, full |
| click-005 | same_session | oracle_page | full | full | full, full, full / full, full, full |
| click-006 | other_session | no_memory | full | full | full, full / full, full |
| click-006 | other_session | oracle_page | full | full | full, full / full, full |

### Rates (origins never pooled)

Each label rate = that judge's plans with the label / all plans in the
same origin and arm. Agreement = matching labels / paired judgments in
that origin and arm, separately at plan and point level.
Violates-vs-not collapses full and partial into not; this is not accuracy.

| Origin | Arm | A full / partial / violates | B full / partial / violates | Plan 3-way / binary | Point 3-way / binary |
| --- | --- | --- | --- | --- | --- |
| other_session | no_memory | 50.0% / 25.0% / 25.0% | 50.0% / 25.0% / 25.0% | 100.0% / 100.0% | 100.0% / 100.0% |
| other_session | oracle_page | 75.0% / 25.0% / 0.0% | 100.0% / 0.0% / 0.0% | 75.0% / 100.0% | 90.9% / 100.0% |
| same_session | no_memory | 100.0% / 0.0% / 0.0% | 100.0% / 0.0% / 0.0% | 100.0% / 100.0% | 100.0% / 100.0% |
| same_session | oracle_page | 100.0% / 0.0% / 0.0% | 100.0% / 0.0% / 0.0% | 100.0% / 100.0% | 100.0% / 100.0% |

## 结论

Both judges observed a lower violation rate with the oracle page on the
independent-origin cases, and they assigned different full-plan rates to that
arm. The synthetic cases and shared model with no human calibration leave
general effectiveness unresolved.

## 没覆盖的

### Interpretation and limits

- Treat each origin/arm as its own result stratum. `same_session` pages summarize
  an earlier rule reminder already visible in both arms' target prefix; their
  results are not independent cross-session memory-transfer evidence.
- These are hand-written synthetic conventions inspired by public APIs, not
  actual upstream maintainer policies. The cases are small and deliberately
  chosen for demo coverage rather than representative sampling.
- Agreement measures judge consistency, not label correctness. The same model
  produced plans and judgments; there is no independent human reference set.
- A complete page being supplied proves delivery, not actual reading. Retrieval,
  search behavior, patch correctness and real task completion are not measured.
- An observed change in full-plan rate is descriptive, not a causal estimate or
  evidence of a general reduction in future human corrections. Do not combine
  these fresh generations with the earlier smoke as if they were one run.
- `memory_search`, `step_conditioned`, human calibration and a model-diversity
  study remain pending. Any expanded run needs a new model/spending decision.

### Reproduction and retained evidence

Raw stdout/stderr, original prompts, extracted plans, judge reasons and run
metadata stay locally in the ignored run directory. They are not published:
CLI envelopes can contain account/session identifiers. The public tables above
contain only synthetic case labels and ratios, with no raw account metadata.

Recompute without any model calls:

```bash
python3 bench/judges/score.py \
  bench/next-step-replay/runs/full-20261115/results.json \
  > bench/next-step-replay/runs/full-20261115/rescored.md
cmp bench/next-step-replay/runs/full-20261115/summary.md \
  bench/next-step-replay/runs/full-20261115/rescored.md
```

Both commands exited successfully. An integrity audit also verified every
raw-to-parsed judgment, the complete case/arm matrix, point counts, resolved
models, successful call metadata, complete oracle pages and absence of held-out
corrections from planner prompts. This is a CLI experiment: no UI screenshot or
service deployment applies. The separate Codex backend is still offline-tested
only.
