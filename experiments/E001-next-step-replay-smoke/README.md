# E001 Next-step Replay bounded CLI smoke

- 结论：说不清
- 日期：开始 2026-11-15 / 结束 2026-11-15
- Issue / PR：[#3](https://github.com/yaodiff/memory-lab/issues/3) / [#6](https://github.com/yaodiff/memory-lab/pull/6)
- 来源：[Next-step Replay demo](../../bench/next-step-replay/README.md)
- 交接：无
- 迁移：[#11](https://github.com/yaodiff/memory-lab/issues/11) / [#13](https://github.com/yaodiff/memory-lab/pull/13)

## 假设

The exploratory comparison asks whether supplying the oracle page helps the
independent-origin plan state the required synthetic rule.

## 做法

This historical smoke checks wiring, not benchmark effectiveness. A later
owner-approved [E002 complete shipped-case pilot](../E002-next-step-replay-full/README.md)
is now available. For this smoke, only the first sorted cases were selected,
covering independent `other_session` memory and the `same_session` prior-exposure
control.

The [synthetic Click dataset](../../bench/datasets/click-synthetic/README.md)
was replayed with `no_memory` and `oracle_page`. The published setup supplies
[the frozen parameters](config.json). The exact evaluated commit and a pre-run
effectiveness threshold are unrecorded.

### Command and environment

Run from the repository root with an existing first-party OAuth CLI login:

```bash
bench/next-step-replay/run.sh --cases 2 \
  --planner-backend claude --planner-model haiku \
  --judge-a-model haiku --judge-b-model haiku \
  --out bench/next-step-replay/runs/smoke --timeout 180
```

- CLI: Claude Code `2.1.325`.
- Requested planner and judge model alias: `haiku`.
- Resolved model in every raw CLI response: `claude-haiku-5-5`.
- Judges: independent blind calls with point-first and counterexample-first
  prompts; the same underlying model, so correlated mistakes remain possible.
- No new API key, extra API client, session resume, fallback, or harness retry.
- Manifest status: `complete`; planned CLI invocation completion rate: **100.0%**.

## 数据

### Ratio-only output excerpt

The per-judge label rate is plans assigned that label / all completed plans
**within the same origin and arm**. A and B gave the same label rates here; they
are shown once, not pooled into an accuracy estimate.

| Page origin | Arm | Full (each judge) | Partial (each judge) | Violates (each judge) | Plan three-way agreement | Plan violates-vs-not agreement |
| --- | --- | --- | --- | --- | --- | --- |
| other_session | no_memory | 0.0% | 100.0% | 0.0% | 100.0% | 100.0% |
| other_session | oracle_page | 100.0% | 0.0% | 0.0% | 100.0% | 100.0% |
| same_session | no_memory | 100.0% | 0.0% | 0.0% | 100.0% | 100.0% |
| same_session | oracle_page | 100.0% | 0.0% | 0.0% | 100.0% | 100.0% |

Point-level three-way and violates-vs-not agreement were also **100.0%** in
every origin/arm. Agreement denominator is all corresponding A/B judgment pairs,
not just the agreed or non-violating subset. The observed violation rate is
**0.0%** for both arms; this does not establish a reduction in violations.

The independent-origin no-memory plan used a different filesystem-isolation
mechanism but omitted the exact synthetic team convention, so both judges marked
that point partial. The oracle plan explicitly used the requested context.
The same-session prefix already stated its rule in both arms; its results are
not independent transfer evidence and must stay separate.

## 结论

The replay and scoring checks completed, and the saved and rescored reports
matched. The small sample and the absence of observed violations in either arm
leave effectiveness and violation reduction unresolved.

## 没覆盖的

### Retained evidence and limitations

Raw stdout/stderr, prompts, extracted plans and judge reasons are retained
locally under the ignored run directory. They are not published because CLI
envelopes may contain account or session metadata. The runner itself prints the
per-case and point labels in addition to the rates.

The saved and independently recomputed Markdown reports matched:

```bash
python3 bench/judges/score.py \
  bench/next-step-replay/runs/smoke/results.json \
  > bench/next-step-replay/runs/smoke/rescored.md
cmp bench/next-step-replay/runs/smoke/summary.md \
  bench/next-step-replay/runs/smoke/rescored.md
```

Exit status was successful. This is a text-only CLI demo, so no UI screenshot,
patch execution, deployment or live-service verification is applicable.
Codex is only offline-tested, not live-smoked.

A full six-case run uses `6 * 2 * (1 + 2) = 36` CLI invocations, before
provider-internal retries. The later pilot used that owner-approved budget.
Any expanded run still needs a model/spending decision; do not infer a price
or general effectiveness from this smoke.
