# Agent notes

Public repository: anything you write here (files, commit messages, issues, PR text) is published and stays in history.

**Every change ships through a PR** — `main` rejects direct pushes. Follow `CONTRIBUTING.md` in order: issue → `Claim:` comment → branch `<type>/<issue>-<slug>` → PR with `Fixes #N` → green `checks` and `pr-links-issue` → `scripts/merge-pr.sh <PR>`. Done means the PR is merged and its issue closed, not that the branch is pushed.

Before opening a PR, run `scripts/check.sh` and fix every hit. When an essay changes, change its other-language version in the same PR.
