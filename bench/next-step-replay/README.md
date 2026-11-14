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
- `page_origin` is one of `other_session`, `same_session` or `after_correction`. **Report results separately for each value**: same-session pages leak the answer (see essays/02).

## Arms
`no_memory` · `memory_search` (agent decides when to search) · `oracle_page` (the page is put in front of the agent) · `step_conditioned` (search takes a "next step" field)

## Scoring
- Two independent judges score each plan as `full` / `partial` / `violates`, based on `convention.points`.
- Report agreement on all three labels and on violates vs not.
- Funnel: searched → right page found → read in full → followed.

## Status
- [ ] 5–10 synthetic cases on one public repo
- [ ] runner (any coding agent CLI that runs non-interactively)
- [ ] judges and agreement stats
