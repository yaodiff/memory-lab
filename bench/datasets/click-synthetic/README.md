# Synthetic Click corrections

Six hand-written, synthetic pre-correction cases on
[pallets/click](https://github.com/pallets/click), a focused Python command-line
library. API behavior is pinned to release **8.1.8**, commit `934813e4d421`.
There is no checkout or dependency installation during replay.

## Provenance and license

All tasks, assistant drafts, human corrections and memory pages are invented for
this benchmark. The team conventions are **synthetic benchmark conventions**,
inspired by the documented APIs, not asserted to be actual Click maintainer
policies. No proprietary code, real conversations, or copied issue discussions
are included.

Public sources:

- [Testing guide](https://github.com/pallets/click/blob/934813e4d421/docs/testing.rst):
  invocation, filesystem isolation, input emulation, terminal width, thread safety.
- [Testing tests](https://github.com/pallets/click/blob/934813e4d421/tests/test_testing.py):
  concrete public behavior including color preservation.
- [Upstream license](https://github.com/pallets/click/blob/934813e4d421/LICENSE.txt):
  BSD-3-Clause, retained in [CLICK-LICENSE.txt](CLICK-LICENSE.txt).

The new synthetic sessions and memory prose use this repository's
[Apache-2.0 license](../../../LICENSE). Small API-call examples are explanatory,
not copied upstream implementations.

## Contents

| Case | Synthetic convention | Page origin |
| --- | --- | --- |
| [click-001](cases/click-001.json) | Fixture creation and invocation inside filesystem isolation | other_session |
| [click-002](cases/click-002.json) | Ordinary prompt input and emulated echo | same_session |
| [click-003](cases/click-003.json) | Invoke the root group to test subcommand context | other_session |
| [click-004](cases/click-004.json) | Explicit invocation width for help wrapping | other_session |
| [click-005](cases/click-005.json) | Preserve ANSI at the runner boundary | same_session |
| [click-006](cases/click-006.json) | No concurrent in-interpreter runner threads | other_session |

Each case includes the initial task, a mistaken assistant draft, and a neutral
user request for the next plan. `prefix` ends there, **before** the held-out human
correction. `last_user_turn` repeats that final user request exactly.
`held_out_correction` is audit metadata, never a planner input.
`convention.points` are the scoring rubric; `scope` preserves exclusions.
`memory_pages` resolves from this dataset directory, not from `cases/`.

### Page origins

- `other_session`: a fictional independent earlier session's correction.
- `same_session`: the initial rule reminder already in the target prefix, before
  its task and erroneous draft. The memory page summarizes **that earlier
  reminder**, not the future held-out target correction. Both arms already see
  the reminder. This intentional same-session rule exposure can inflate apparent
  performance and is not clean other-session transfer evidence.
- `after_correction`: reserved by the format for future-correction-derived pages;
  none are shipped here. A page derived from the held-out correction belongs
  here, not under `same_session`.

These provenance labels describe the synthetic evidence source, not real
extraction timestamps. Every page records the origin, scope and points. Report
the origins separately: the same-session controls must not inflate a pooled
headline score.

## Status

- [x] Six cases, complete pages, permissive source license and pinned references
- [x] Two same-session exposure controls, with their source visible in the prefix
- [ ] Real-session extraction or a representative public benchmark
