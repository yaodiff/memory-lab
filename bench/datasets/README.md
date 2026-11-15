# datasets

## Available data

[click-synthetic](click-synthetic/README.md): six synthetic pre-correction sessions
on the public BSD-3-Clause project `pallets/click`, pinned to release 8.1.8
(commit `934813e4d421`). Each case has a scoped, point-based team convention,
a complete Markdown memory page, and a held-out synthetic human correction.
These are benchmark-defined conventions inspired by public APIs, **not claims
about actual Click maintainer policies or actual conversations**.

There are independent-origin `other_session` cases and deliberate `same_session`
exposure controls. The latter pages summarize a rule reminder already present
earlier in the target prefix, not the future target correction. Their pages are
supplied only in the oracle arm, but both arms already see the reminder.
Do not pool these controls with independent origins. Neither is a real session.

## Loading and validation

The [runner](../next-step-replay/README.md) loads sorted JSON files from
`click-synthetic/cases/` and resolves `memory_pages` relative to
`click-synthetic/`. Filesystem traversal and symlink escapes are rejected.
It validates all cases and pages before starting any CLI call:

```bash
bench/next-step-replay/run.sh --validate-only
```

Use `--dataset PATH` for another dataset with the same `cases/` and `pages/`
layout. Do not put the withheld correction or grading rubric in planner context.

## Status

- [x] Six public, synthetic Click cases and their memory pages
- [x] Explicit page-origin and pinned-source provenance
- [x] Standard-library loader and offline validation
- [ ] Public-session importers and synthetic case generator
