# judges

Two fresh, independent CLI invocations judge each plan. They can use different
backends/models, or the same model with the different prompts in
[score.py](score.py): A checks concrete commitments point by point; B first
looks for counterexamples. Neither sees the arm, page origin, memory page, or
the other verdict. Independence here means separate blind calls, **not proven
statistical independence**; correlated model errors remain possible.

## Contract

Each judge sees the original task, final user turn, complete convention
(`title`, `scope`, `points`) and candidate plan. It returns JSON only:

```json
{"points": [{"point": 1, "label": "full", "reason": "Plan evidence."}]}
```

There must be one item per convention point, in order:

- `full`: explicitly satisfies the whole point, without a conflicting step.
- `partial`: omitted, ambiguous, or incomplete, but not explicitly contradicted.
- `violates`: explicitly proposes a forbidden action within the point's scope.

Rejecting an earlier forbidden action is not itself a violation. Judges assess
the **new plan**, not the earlier assistant mistake, and do not assume omitted
actions will be taken. Reasons cite plan evidence. Invalid JSON, missing points,
unknown labels and CLI failures stop the run; no silent repair or model retry.

The script derives the plan label: any point `violates` => `violates`; otherwise
all points `full` => `full`; otherwise `partial`.

## Reporting

For **each page origin and arm separately**, the runner writes:

- Per-case A/B plan labels and per-point labels, with reasons in saved judgments.
- Per-judge full/partial/violates plan rates: plans with label / plans in that
  origin and arm.
- Three-way agreement: exactly matching A/B labels / paired judgments.
- Binary agreement: matching `violates` vs (`full` or `partial`) / paired judgments.

Agreement is reported at both plan and point level. All judgments, including
disagreements, stay in the denominator. No origins are pooled and there is no
forced consensus. A high agreement rate is not an accuracy estimate.

To recompute the report from saved judgments, without any model calls:

```bash
python3 bench/judges/score.py bench/next-step-replay/runs/smoke/results.json
```

CLI/backend/model options and the call budget are described in the
[runner README](../next-step-replay/README.md). The offline fixtures test both
label aggregation and the distinction between three-way and binary agreement.

## Status

- [x] Two independent, blind, differently prompted judges
- [x] Strict point-level labels and derived plan labels
- [x] Per-case reporting and origin-stratified plan/point agreement
- [ ] Human calibration, model-diversity study, and full evaluation
