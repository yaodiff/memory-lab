# Next-step Replay

Evaluate memory at the moment it should matter: **right before a human correction**.

## Case format (one JSON per case)
```json
{
  "id": "repo-x-0001",
  "repo": "https://github.com/<public-org>/<public-repo>",
  "prefix": [{"role": "user", "content": "..."}, {"role": "assistant", "content": "..."}],
  "last_user_turn": "...",
  "convention": {"title": "...", "points": ["...", "..."], "scope": "..."},
  "memory_pages": ["pages/....md"],
  "page_origin": "other_session"
}
```
- `prefix` stops at the last user message before the correction. Nothing after it is kept.
- `page_origin` is one of `other_session`, `same_session` or `after_correction`. **Report results separately for each value**: same-session pages leak the answer (see [essay 03](../../essays/03-same-session-leakage.en.md)).
- `last_user_turn` must exactly match the final `prefix` message, whose role is
  `user`. An earlier assistant step must be present. The final user request
  asks for the next plan; it is not the withheld human correction.
- `memory_pages` paths are relative to the dataset root, not the JSON file.
  Each path must resolve to a complete, nonempty Markdown page within that root.
- The demo adds optional `repo_revision` (a public pinned commit) and
  `held_out_correction` (synthetic audit metadata). The runner never sends
  `convention`, `page_origin`, or `held_out_correction` to the planner.
  Only the oracle arm gets memory-page text.

The [Click dataset](../datasets/click-synthetic/README.md) contains six synthetic
cases. Two are intentional `same_session` exposure controls: their pages summarize
an earlier rule reminder already in the target prefix, not independent prior
knowledge. The held-out target correction is absent from every prefix; deriving
a page from that future correction would instead require `after_correction`.
Other-session pages describe fictional independent earlier corrections.
Nothing is a private or real session.

## Arms
`no_memory` · `memory_search` (agent decides when to search) · `oracle_page` (the page is put in front of the agent) · `step_conditioned` (search takes a "next step" field)

Implemented: `no_memory` and `oracle_page`. The other names are reserved CLI
interfaces and fail before any calls, with an explicit TODO. No retrieval or
`oracle_page + verify` / `dream_verify` experiment is implemented yet.

## Scoring
- Two independent judges score each plan as `full` / `partial` / `violates`, based on `convention.points`.
- Report agreement on all three labels and on violates vs not.
- Funnel: searched → right page found → read in full → followed.

See the [judge contract](../judges/README.md) for precise labels, deterministic
plan aggregation, and agreement denominators. Injecting a complete page proves
delivery, **not that the model read it**. Saved results record page delivery;
search, retrieval success and actual reading remain `null` (unobserved), not
fabricated funnel successes.

## Run

Requirements: Python 3.10+, Bash, and a locally installed, already authenticated
`claude` or `codex` CLI. No Python packages or new API keys are needed.
The real smoke uses existing first-party Claude CLI login. Model aliases and
availability depend on the logged-in account.

Recorded commands, resolved models and ratio-only metrics:
[E001 bounded smoke](../../experiments/E001-next-step-replay-smoke/README.md) and the
[E002 complete shipped-case pilot](../../experiments/E002-next-step-replay-full/README.md).
The latter covers all six demo cases, not a representative or human-calibrated benchmark.

From the repository root, run the bounded smoke:

```bash
bench/next-step-replay/run.sh --cases 2 \
  --planner-backend claude --planner-model haiku \
  --judge-a-model haiku --judge-b-model haiku \
  --out bench/next-step-replay/runs/smoke
```

The default is **one case**, both arms. Cases are sorted by filename; the first
two deliberately cover both `other_session` and `same_session`. Judge backends
default to the planner backend; judge models independently default to their CLI's
own model default. Set `--judge-a-backend`, `--judge-b-backend`,
`--judge-a-model` and `--judge-b-model` explicitly to compare different models.
No sessions are resumed or shared between arms or judges.

For Codex, use `--planner-backend codex` and an available `--planner-model`;
each judge can also choose `codex`. This backend is covered by offline command
tests but has not been live-smoked. It ignores user configuration to avoid
loading hidden project instructions, hooks or tools, while reusing CLI auth.
Custom provider routing from user configuration is therefore not supported.
See the official [Claude CLI reference](https://code.claude.com/docs/en/cli-reference)
and [Codex non-interactive guide](https://developers.openai.com/codex/noninteractive/).

Every CLI call gets a fresh empty working directory, a bounded text-only system
prompt, no resume state, and disabled tools, MCP, hooks and automatic memory.
Claude's user/project/local settings and Codex's user configuration and project
instructions are disabled. API-key environment variables are removed from child
processes. Managed account policies may still apply: review your CLI setup before
using this for a controlled evaluation. This is plan replay, not a patch-execution
or repository-navigation benchmark.

No-cost inspection and offline tests:

```bash
bench/next-step-replay/run.sh --validate-only
bench/next-step-replay/run.sh --cases 2 --dry-run
python3 -m unittest discover -s bench/next-step-replay -p 'test_*.py'
scripts/check.sh
```

`--dry-run` writes planner prompts and a manifest only; it never calls a CLI or
fabricates scores. `scripts/check.sh` includes the offline fake-CLI tests; it
does not run a real evaluation.

## Artifacts and spending gate

Each run uses a **new** directory under `runs/` (gitignored), or `--out PATH`.
Existing directories are never overwritten. Per case/arm it preserves:

- Planner and judge inputs, complete raw stdout/stderr, extracted responses.
- Strictly parsed judge point labels, plan labels, reasons and call metadata.
- `manifest.json` (configuration, CLI versions, call budget, completion/failure).
- `results.json`, `summary.json` and ratio-only `summary.md`.

Raw CLI output may include account/session metadata; it stays local. Inspect
before sharing, publish only the synthetic ratio report, and never commit
credentials or blindly upload a custom output directory. A failed call or invalid
judge output stops immediately, retaining diagnostics; no harness retries or
automatic fallback. A failed manifest and any partial results are not a completed
evaluation. `--timeout` limits each CLI process group (default 180 seconds).

**Call budget:** each case uses two arms, each with one planner and two judge
calls: `N * 2 * (1 + 2) = 6N` CLI invocations. The shipped six-case dataset needs
36 invocations for a full run, excluding any provider-internal retries. Token
usage and money depend on the chosen models, CLI subscription/quotas and answer
length; this demo does not estimate a price or promise free quota.

**Do not run a full evaluation before the owner chooses models and spending.**
More than two cases requires both `--allow-full-run` and explicit
`--planner-model`, `--judge-a-model`, `--judge-b-model`. That flag is an operator
acknowledgment, not a substitute for owner approval. An owner-approved complete
run with the smoke configuration is recorded in
[E002](../../experiments/E002-next-step-replay-full/README.md).
Expanded runs still require a new model/spending decision.

## Status
- [x] Six synthetic cases on one permissively licensed public repo
- [x] Non-interactive CLI runner for `no_memory` and `oracle_page`
- [x] Two blind judges, point labels and origin-stratified agreement
- [x] Offline validation, leakage guards and fake-CLI integration tests
- [x] Bounded real-Claude CLI smoke, with ratio-only public evidence
- [x] Complete shipped-case pilot with owner approval and preserved judge disagreements
- [ ] `memory_search` and `step_conditioned` (reserved interfaces only)
- [ ] Human-calibrated, representative evidence of effectiveness
