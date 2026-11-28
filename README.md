# Memory Lab: correction-driven team memory for coding agents

English · [中文](README.zh.md)

> Status: early draft. The complete six-case Next-step Replay pilot has run with
> an owner-approved CLI setup. These are small synthetic results, not a validated
> general benchmark.

**One line**: we evaluate team memory for coding agents by asking *"does the agent still get corrected?"*, not *"can it recall a fact?"*.

Memory Lab is three things in one repo:

1. **Essays**: field notes from running team memory for coding agents in practice, including the negative results.
2. **Bench**: *Next-step Replay*. Cut a real (here: synthetic, open-source-repo) agent session just before a human correction, replay it with and without memory, and let two independent judges score whether the plan still violates the team convention.
3. **Reproductions** of well-known memory papers (Mem0, A-MEM, Generative Agents, Agent Workflow Memory…) on public datasets, each compared against the ideas above.

A small reference implementation (`memlite/`) exists only to make the experiments runnable. It is not a product.

## The three gates

A team convention only helps if it passes three gates:

| Gate | Question | Typical failure |
|---|---|---|
| **Written right** | Was the correction captured as a reusable rule with its scope intact? | Captured as progress or a one-off; scope ("first phase only") dropped; mid-task side remarks never captured |
| **Found** | Does the agent search *at the decision point*, with a query that matches the rule? | Agent searches for the task at hand, while the rule is about "how we do this kind of step" |
| **Used** | Having read it, does the agent follow it? | Read in full, then partially followed |

Details: [essay 01](essays/01-three-gates.en.md).

## Essays

Each essay is written in Chinese first, with an English version covering the same content.

| # | English | 中文 |
|---|---|---|
| 01 | [Three gates for team memory: written right, found, used](essays/01-three-gates.en.md) | [团队记忆的三道关：写对、搜得到、用得上](essays/01-three-gates.md) |
| 02 | [Reading Anthropic's "components of agent memory" against field data from team memory](essays/02-reading-the-components.en.md) | [用团队记忆的一线数据读 Anthropic 的「记忆组件」](essays/02-reading-the-components.md) |
| 03 | [Your memory eval may be inflated: same-session leakage](essays/03-same-session-leakage.en.md) | [你的记忆评测可能虚高了：同会话泄漏](essays/03-same-session-leakage.md) |
| 04 | [Reading Meta's Self-Improving Memory: the model rewrites its own memory prompts, then learns them](essays/04-self-improving-memory.en.md) | [读 Meta 的 Self-Improving Memory：让模型改自己的记忆提示，再蒸馏进权重](essays/04-self-improving-memory.md) |
| 05 | [Finding the right memories from the repository already in view](essays/05-aoci-code.en.md) | [让编码 Agent 从手头的仓库找到相关记忆](essays/05-aoci-code.md) |
| 06 | [Why did the agent use less memory when the ranking stayed the same?](essays/06-memory-search-previews.en.md) | [排序没变，Agent 为什么少用了记忆？](essays/06-memory-search-previews.md) |

## Layout

Browse the indexes for [plans](plans/README.md), [experiments](experiments/README.md), [lessons](lessons/README.md), [public handoffs](handoff/README.md), and [archived records](archive/README.md).

```
essays/            field notes: NN-slug.md (zh) + NN-slug.en.md (en)
bench/
  next-step-replay/  session cutting, case building, replay runner
  datasets/          loaders for public data + synthetic session generator
  judges/            judge prompts, agreement stats
memlite/           minimal reference memory: typed pages, sentence-level provenance,
                   write decisions, consolidation with hard constraints, retrieval that explains empty results
reproductions/     one folder per paper: README (what / numbers / gaps vs paper) + run.sh
docs/              related work, CoALA mapping
```

## Roadmap

- [x] Essay 01: the three gates (draft)
- [x] Essay 02: reading Anthropic's components of agent memory against our field data (draft)
- [x] Essay 03: same-session leakage inflates memory evals (draft; [descriptive demo results](essays/03-same-session-leakage.en.md#eval-demo-results) added)
- [x] Essay 04: reading Meta's Self-Improving Memory against team memory (draft; with the synthetic [E004](experiments/E004-meta-optimized-memory-prompts/README.md))
- [x] Essay 05: [reading AOCI-CODE](essays/05-aoci-code.en.md)
- [ ] Essay: step-conditioned retrieval
- [ ] Bench: "look back and verify memory" arms on Next-step Replay (planned in essay 02)
- [ ] Repro: Mem0 vs full context on LoCoMo
- [ ] Repro: A-MEM link evolution ablation on LoCoMo
- [x] Bench: [Next-step Replay demo](bench/next-step-replay/README.md) on Click (six synthetic corrections), with [E001 bounded smoke evidence](experiments/E001-next-step-replay-smoke/README.md)
- [x] Bench: [E002 complete shipped-case pilot](experiments/E002-next-step-replay-full/README.md) with owner-approved models and spending
- [ ] Bench: human-calibrated, model-diverse effectiveness evaluation

### Timeline

- **2026-11-15** — [E001 and E002](experiments/README.md): Next-step Replay smoke test and full pilot.
- **2026-11-20** — [E003–E008 and E010–E012](experiments/README.md): studies on ranking, memory prompts, entity checks, page types, deduplication, and replay.
- **2026-11-20** — [E009](experiments/E009-typed-relation-expansion/README.md): one-hop expansion from search results did not improve complete multi-page recall.
- **2026-11-20** — Proposed: [context-anchored entity recall](plans/plan-context-anchored-recall.en.md). Rank memory attached to entities identified from the task context and show it in a separate panel alongside global search.
- **2026-11-25** — Fixed-pool reranking left overall top-five target recall unchanged in a small sample from our own setting. Targeted gains varied by query group.
- **2026-11-25** — Entity navigation reached some targets outside the search list. Spending evidence slots on navigation lowered total target recall in a small targeted sample.
- **2026-11-25** — A [Hindsight-inspired](https://github.com/vectorize-io/hindsight/blob/main/skills/hindsight-docs/references/developer/retrieval.md) replay fused dense, lexical, and graph results. In a small sample from our own setting, targeted top-five hits rose from about three in ten to about half. A small-model reranker helped complete evidence retrieval on the general gold set and gave back some of the targeted gain. The mixed results leave default rollout inconclusive.
- **2026-11-25** — [E020](experiments/E020-structure-retrieval-diagnosis/README.md): entity cleanup left complete recall unchanged. Ranking never consulted the links, adding child attachments left parent fan-out high, and the evaluation had few multi-page cases.
- **2026-11-25** — [E021](experiments/E021-heldout-retrieval-fusion/README.md): on an expanded 150-question holdout, fusing production results with BM25 improved complete top-five recall by about 15 points. A four-route page-level adaptation of Hindsight underperformed the baseline.
- **2026-11-25** — [E022](experiments/E022-existing-link-reranking/README.md): ranking existing outgoing links improved multi-page evidence coverage with no additional SQL queries in a local replay. Shared-entity expansion added noise without a net multi-page gain.
- **2026-11-25** — [E023](experiments/E023-page-applicability-replay/README.md): applicability notes reduced observed misuse in a 243-question fixed-retrieval replay. The correctness interval crossed zero, so the replay did not support enabling the notes by default.
- **2026-11-25** — [E024](experiments/E024-content-gap-write-guard/README.md): new drafts reached the top five for 14 of 15 held-out phrasings. Write-time validation addressed regressions that a one-off cleanup could not prevent.
- **2026-11-25** — [E025](experiments/E025-rollout-checkup-four-arm-replay/README.md): a rollout checkup of a second team space found most new pages lacked the structured summary and many non-leaf parents had only one child, so the strict leaf-attachment gate could not be copied over directly. In a 76-question four-arm replay, lexical fusion helped single-page cases but hurt multi-page ones; outgoing-link reranking was a zero gain, zero regression there.
- **2026-11-25** — [E026](experiments/E026-three-gap-regression/README.md): in a 50-question regression set, an external-repo scope guard removed strong internal look-alike pages from the top three for 12 of 12 external-repo questions with zero false demotions on 10 internal controls, and confidence-weighted dual-query fusion reached 12/12 top-ten on short queries. A concise verify-at-source instruction gave a small gain.
- **2026-11-25** — [E027](experiments/E027-live-recall-contract-recheck/README.md): under real production recall, newly added contract pages improved the 34 target questions by only one. One contract merged into an 11 KB entity page ranked 13th or worse; large entity pages dilute the contracts inside them. Rerunning the full composite benchmark was not justified yet.
- **2026-11-25** — [E028](experiments/E028-session-memory-v3-retest/README.md): with the production extraction template and model, both the original window and a mechanical closure backfill stayed at 0/4 reusable pages. A minimal prototype that also fixed lexicographic entity truncation and route/supersede handling reached 4/4, with zero duplicate pages or leakage across five regression cases. Upload tracing found unresolved-workspace sessions exiting 0 while writing fake uploaded logs. Fixes are drafted but await merge approval.
- **2026-11-26** — [E029](experiments/E029-skill-prompt-acceptance-fail/README.md): neither the consolidated nor the slimmer instruction edit passed the pre-registered 81-question bar: each fixed some groups and regressed others, and run-to-run variation covered the differences. Prompt tuning for memory instructions is paused in favor of backend retrieval fixes.
- **2026-11-25** — [E030](experiments/E030-link-rerank-production-shadow/README.md): production shadow verification of query-ranked outgoing links logged 10/10 shadow events with 49/49 shared outgoing-link orders unchanged in the user response and about 0.17 ms median compute. Shadow stays on for observation; no effect on production outcomes has been measured yet.
- **2026-11-26** — 30-day zero-adoption cooling replay (small internal sample): about 58% of active pages reached 30-day age and roughly 85% of them had zero observed adoption. Blanket cooling shrank the hot tier by about 52% but lowered target-space answer top-1 and top-3 recall by 12.5 points each (top-10 by 15 points), raised top-3 traps, and removed required hot-tier gold for 25% of retrieval queries; sparse adoption telemetry mis-demoted actively recalled durable pages. Cooling event pages alone shrank the hot tier by about 13% with zero answer-recall loss and 100% warm-index and cold-archive recovery on sampled historical receipts. Blanket 30-day zero-adoption cooling does not work.
- **2026-11-27** — Event-only 30-day cooling draft and offline verification (small internal sample): drafted a dedicated cooled archive status (default-off dry-run maintenance job; excluded from default hot-tier search while preserving direct-ID readback, entity timelines, and on-demand warm lexical search). Replaying the implemented selector against the 30-day baseline shrank the frozen default pool by 12.6% (41.5% of active events) with 0% non-event or recently adopted leakage, kept held-out answer recall flat while lifting target-space full-set top-10 recall by 2.5 points, lost 0% of benchmark reference pages, and recovered 100% of sampled cooled receipts at top-1 via the warm scorer; pilot write-backup-restore verified 100% round-trip. Draft changes await review before rollout.
- **2026-11-27** — [E031](experiments/E031-governance-retrieval-recheck/README.md): **Inconclusive** (small internal sample). Complete evidence in the first five results fell 2.8 percentage points on live held-out queries, without a significant difference. The fixed reference set was flat. About 45% of misses had the needed pages in the pool below rank five. Adding common phrasings offline raised top-three entity anchoring from 22.8% to 41.0% without a downstream gain and stayed offline. With the same reviewer, the top-five wrong-slot rate fell 2.7 points, with an interval crossing zero.
- **2026-11-27** — [E032](experiments/E032-keyword-fusion-live/README.md): **Works** (small internal sample). Offline readiness replay gained about 16 percentage points. In one live scope, full evidence coverage in the first five results rose from 56.9% to 71.5% on frozen held-out queries (+14.6 points, paired 95% CI +7.6 to +21.5). At the normal request limit the fixed reference set gained 5.7 points, with an interval crossing zero. Two-hour adoption of primary hits later fell from 22.6% to 10.4%. The control-adjusted change was −8.2 points (95% CI −17.7 to +1.3), and shifting the split one day earlier gave about −0.8 points. All sampled timeout fallbacks returned the original order successfully. Keep the pilot on and retest on weekdays before expanding.
- **2026-11-27** — [E033](experiments/E033-approval-only-ingestion/README.md): **Works** (small internal sample). In the first live hour, new ingestion of approval-only sessions fell 100% versus the previous hour, and the backlog was skipped. Stock cleanup had 100% readback and no regression on fixed probes. Explicit exceptions remain subject to the existing gates.
- **2026-11-27** — [E034](experiments/E034-event-only-cooling-live/README.md): **Works** (small internal sample). Event-only cooling moved from offline validation to a staged production write, reducing active event pages by about 43%. The pilot verified direct and warm-tier retrieval of sampled archived pages. Automated operation awaits the end of live observation.
- **2026-11-27** — [E035](experiments/E035-stale-projection-cleanup/README.md): **Works** (small internal sample). A read-only reconciliation found lingering copies of withdrawn and orphaned pages. Production cleanup verified 100% of targeted removals and reduced stale slots in the first 30 positions to zero on fixed queries. After the prevention fix shipped, all sampled new withdrawals removed their retrieval copies.
- **2026-11-27** — [E036](experiments/E036-event-weight-cap-replay/README.md): **Does not work** (small internal sample). Relaxing the cap alone was neutral in offline replay at the original weight. Reducing the penalty did not yield a significant coverage gain. More aggressive variants produced roughly 3–15 times as many top-five slots filled by non-reference, one-off events and displaced reusable memory. Retain the guardrails.
- **2026-11-27** — [E037](experiments/E037-nightly-curation-readback/README.md): **Works** (small internal sample). The first full live window showed no lost links, degraded summaries, or missing trigger phrases in reviewed versions. Subsequent rule-page splits and moves had 100% readback and no regression on fixed probes.
- **2026-11-27** — [E038](experiments/E038-targeted-content-repair/README.md): **Inconclusive** (small internal sample). Targeted edits added missing phrasings and a missing page. Complete coverage rose about 6 percentage points in the post-write probes during a ranking change. Under the new fusion ranking, the fixed queries had 100% position-by-position agreement in the top five, leaving a standalone ranking benefit unconfirmed.
- **2026-11-27** — [E039](experiments/E039-retrieval-load-isolation/README.md): **Works** (small internal sample). In the first live hour versus the prior window, throttled responses fell about 67%, background throttles fell about 94%, and mean window-level retrieval P99 fell about 69%. Peak-period performance still needs a longer observation.
- **2026-11-27** — [E040](experiments/E040-cross-category-supersession/README.md): **Works** (small internal sample). Offline replay classified all known conflicts correctly and falsely superseded 0% of similar non-conflicts. Targeted live readback verified cross-category supersession and evidence dates. Replay rejected a global authority boost and kept evidence dates available for source checking.
- **2026-11-27** — [E041](experiments/E041-memory-use-guidance/README.md): **Inconclusive** (small internal sample). Correct actions and required source checks were flat on frozen tasks. Live readback verified the guidance. Adoption, rejection, and corrections still need a longer like-for-like window.
- **2026-11-28** — [E042](experiments/E042-workaround-scope-review/README.md): **Does not work** (small internal sample). Sampling suggested roughly 4% of active pages needed attention, but keyword-generated dispositions agreed with manual review only about 14% of the time and could not be applied in bulk. Human review of frequently retrieved pages reached about 94% overall agreement, including many unchanged pages. A small, individually approved scope edit left complete coverage flat on fixed probes.
- **2026-11-28** — [E043](experiments/E043-curation-rollout-waves/README.md): **Inconclusive** (small internal sample). About 40% of scopes cleared the second-wave dry-run gate. Applied edits had 100% readback and no regression on fixed probes. Refined third-wave candidates all cleared the 90% review threshold. The next day’s live report showed about 4% accepted and retained, 7% removed, and roughly 90% still awaiting acceptance. Verify live batches after dry-run approval.
- **2026-11-28** — [E044](experiments/E044-leaf-coverage-live/README.md): **Inconclusive** (small internal sample). Direct leaf attachment rose from about 80.3% to 95.0% in production with 100% readback. Held-out full coverage in the top five fell 1.4 percentage points (paired 95% CI −3.5 to 0), with fixed-reference full coverage and first-rank hits flat. The top-five wrong-page rate appeared to fall 7 points, but a reviewer change prevented attribution.
- **2026-11-28** — [E045](experiments/E045-entity-structure-ranking/README.md): **Does not work** (small internal sample). Offline variants tried leaf-name expansion, same-leaf boosts, demoting navigation while promoting action pages, and one-hop expansion along sourced relations. All failed the shadow gate. The best gained only 0.7 percentage points in held-out top-five coverage with its interval touching zero, and fixed-reference first-rank hits fell about 2.9 points. Keep these variants out of shadow.
- **2026-11-28** — [E046](experiments/E046-generated-preview-pilot/README.md): **Inconclusive** (small internal sample). In the first 48-hour window, excluding overlapping ranking changes, adoption from any of the first three searches was 45.5%, with the 41.1% baseline inside the interval. The control-adjusted +12.5 percentage points also had an interval crossing zero. Median injected bytes per hit fell about 83%. Keep the pilot and verify adoption in another window.
- **2026-11-28** — [E047](experiments/E047-outgoing-link-live/README.md): **Inconclusive** (small internal sample). In the active pilot, outgoing-link lookups had a 0% failure rate. While keyword fusion was still in shadow, two-hour adoption of primary hits was about 0.5 percentage points above the link-shadow window. Active mode lacked per-position change and latency logs, and about half the few verified reorders were worse. Keep the pilot and add instrumentation before expansion.
- **2026-11-28** — [E048](experiments/E048-ingest-gate-evidence/README.md): **Inconclusive** (small internal sample). New writes fell about 79% over the previous 24-hour window, but were about 10% higher than the same window a week before. The gate's effect remains unconfirmed. About 94% of build failures arose in an upstream call path, and the failure rate near release was roughly flat. Offline replay of a draft evidence fix returned about 54% of hard-blocked samples to the original gate, kept about 13% blocked, and left about 33% for manual review. The tighter gate remains live; the evidence fix is still a draft.

## Data policy

Only public datasets and synthetic sessions on public open-source repositories. No proprietary code, sessions, or documents. Examples in the essays are rewritten or synthetic; internal measurements are given only as ratios or in coarse terms, with no raw data, and are labelled as small samples from our own setting.

## Contributing

Every change goes issue → PR → checks → squash merge; `main` is protected. See [CONTRIBUTING.md](CONTRIBUTING.md).

## License

Apache-2.0
