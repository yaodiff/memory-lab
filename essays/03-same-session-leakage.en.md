# Your memory eval may be inflated: same-session leakage

English · [中文](03-same-session-leakage.md)

> Draft v0. Observations attributed to "us" come from running a team memory system internally. We describe them only in coarse terms, with no raw data or examples. The sample is small, and the setting is team conventions for coding agents. All examples are rewritten or synthetic. The Next-step Replay results at the end come from the complete public synthetic pilot: they are descriptive, not evidence of memory effectiveness.

## In one paragraph

When you evaluate memory, the memory arm may read pages that **came from the session under test**, or that were **written or edited after the correction**. Either way it has seen the answer, and the gain is overstated. So results have to be reported separately by page origin (`page_origin`). Only pages from other sessions, which already existed before the correction, can back the claim that memory helps.

## How we walked into it

[Essay 01](01-three-gates.en.md) described the setup: take the step right before a real correction, have the agent plan it with and without memory, and judge the plans. Overall, memory cut the violation rate clearly. Going through the cases one by one, we found that many of them used pages **learned from that very session**, some updated only after the correction. On the clean cases alone (page from another session, untouched after the correction) **the gain was close to zero**.

It is hard to spot because each step is reasonable on its own:

- The memory system extracts corrections from every session each night and writes them up as pages. That is its job.
- The eval set is drawn from sessions that contain a correction. That is the cheapest way to get items.
- Replay runs against the current memory store. That is the cheapest environment.

Put the three together and you have trained on the answer to a question and then tested on the same question. Machine learning calls this **leakage**, and it is an old problem. Kapoor and Narayanan surveyed 329 papers across 17 fields affected by leakage, gave a taxonomy of 8 types, and found conclusions optimistic enough that they failed to reproduce ([arXiv:2207.07048](https://arxiv.org/abs/2207.07048)). In LLM evaluation the same thing goes by **test-set contamination**: a model that saw the test split in training scores too high (Sainz et al., [arXiv:2310.18018](https://arxiv.org/abs/2310.18018)). Memory leakage is the same disease with "training" replaced by "writing memory", and it spreads faster. You don't wait for the next model release; it leaks in overnight.

## What leakage looks like

The examples are synthetic. Setting: the repository of an open-source web framework, with the team convention "a public API change gets a line under Unreleased in `CHANGELOG`, committed together with the code". In the session, the agent finishes an interface change and is about to commit. The user cuts in: "What about the changelog? We always write one for public API changes."

**1. Same session (`same_session`)**

The nightly extractor ran over this session and wrote the correction up as a page: "public API changes must update CHANGELOG". At eval time the session is cut right before the correction and replayed. The page is sitting in the store; the agent finds it, follows it, and the judge scores the plan as compliant.

Every sentence on that page cites the session under test. It shows that the extractor can turn a correction into a page. It does not show that a convention learned elsewhere takes effect here.

**2. After the correction (`after_correction`)**

The page was originally written from another session and only said "public API changes must be announced to downstream users". After the correction in the session under test, consolidation folded "and update CHANGELOG" into it. Replay reads the merged version.

The page is labelled "other session", yet it carries the answer from the session under test. Looking at who created the page won't catch this. You need **when each version was written and what each sentence cites**.

**3. Laundered by consolidation**

Subtler than case 2. Nightly consolidation merges and rewrites a few similar pages and drops the citations along the way (the "a merge must not drop any citation" constraint in [essay 02](02-reading-the-components.en.md) exists for this reason). The merged page has no traceable source and looks like an old, generic convention, but one of its sentences came from the session under test. Without sentence-level provenance this kind can't be labelled at all.

**4. In the item, not in memory**

Some leaks never touch a memory page and do the same damage:

- **The prefix is cut too late.** It runs past the correction, or the last user message already carries a hint ("hold off on the commit, think about what's missing"). Essay 02 noted that a sizable share of our items were misaligned, with the correction and the last user message before it about different things. A wrong cut point produces both leakage and misalignment.
- **The repository is checked out after the fact.** Replay checks out the commit where the fix already landed, so `CHANGELOG` already has the line and the agent only has to copy the neighbouring format. This lifts the no-memory arm too, so the gap between arms may even shrink, and looking at the gap alone won't reveal it.
- **The same thing was corrected earlier in the session.** The answer is already in the prefix. That tests in-context memory, not cross-session memory. Label it and report it separately; don't count it as a memory gain.

**5. Selection bias in the items**

If you only build items from corrections that have a matching page in the store, you only test items that already passed gate 1 (written right). That isn't leakage, but it flatters gates 2 and 3. At minimum, report what share of the corrections worth remembering made it into the item set.

## Why public benchmarks and team setups both invite it

**Fact-recall benchmarks: same session is the task**

In [LoCoMo](https://arxiv.org/abs/2402.17753), each conversation averages about 300 turns and 9K tokens over up to 35 sessions, and the benchmark covers question answering, event summarization and multimodal dialogue generation. [LongMemEval](https://arxiv.org/abs/2410.10813) embeds 500 questions in freely scalable chat histories and tests five abilities: information extraction, multi-session reasoning, temporal reasoning, knowledge updates and abstention. In both, memory is built from **this history** and the questions ask about **this history**.

That is not a flaw. It is what they set out to measure: can a system recover a fact from a long history. The trouble is in how results get read. Systems like [Mem0](https://arxiv.org/abs/2504.19413) report gains on LoCoMo against RAG and full context, which are other ways of reading the same history. The gain says that memory reads that history more accurately or more cheaply. Read it as "team memory makes an agent err less on a different task" and you are using a `same_session` number as if it were an `other_session` one.

How the two settings differ:

| | Fact-recall benchmark | Team convention |
|---|---|---|
| Where memory comes from | The history being asked about | Other people, other sessions, often long ago |
| When it is used | Someone asks directly | Nobody asks; the agent is about to take a step |
| Where the answer lives | In the history (except abstention items) | Only in memory; if it wasn't kept, it's gone |
| Is same session a leak? | No, it's the task | Yes |

LongMemEval's knowledge-update category looks a lot like `after_correction`: a new fact overrides an old one, and the test is whether the system uses the new one. That is a fair test of fact recall. In a correction-driven eval, a page updated after the correction *is* the answer. [inference]

**Team setups: leakage is the default**

- **Corrections are what memory is made of.** The extractor's most important input is corrections, and so is the eval's. The more valuable the item, the more likely it has already leaked into memory.
- **Consolidation keeps editing pages.** Merging, rewriting and splitting all push new content into old pages. Labelling origin by "who created the page" marks cases 2 and 3 as clean.
- **The store is shared and keeps growing.** Evals usually run against today's store, not the store as it was at the moment of correction. In between, someone else may have been corrected for the same thing and written another page.
- **Every shortcut leaks.** Drawing items from logs, connecting to the live store, checking out the latest code: each one lets leakage in, and cutting cases clean means doing a bit more at each step.

## Cutting cases clean

**1. The cut: stop before the correction**

- The prefix ends at the last user message before the correction. Everything after it goes, including the agent's later tool calls.
- Check that the last user message is about the same thing as the correction and carries no hint. Drop items that don't line up rather than keeping them anyway (this is the cleaning step from essay 02).
- If the same thing was already corrected inside the prefix, label the item in-context and report it separately.

**2. Snapshots: roll everything back to the moment of correction**

- **Repository**: check out the commit that was current when the correction happened, not the one with the fix.
- **Memory store**: include only page versions that existed before the correction. Ideally the store is versioned and can be replayed to a point in time. If it isn't, at least record when each version of each page was written, and block versions newer than the correction during replay.

**3. Label page origin per sentence, not per page**

`page_origin` takes three values. Apply the rules in order and stop at the first match:

1. Any sentence on the page cites a message from the session under test → `same_session`.
2. The current version of the page was written after the correction, wherever its citations point → `after_correction`.
3. Everything else → `other_session`.

Two additions:

- **A page with no traceable source is not clean.** Once citations are gone you can't rule out case 3, so treat it as `after_correction`. This is conservative: it can undercount the gain, but it won't overcount it.
- **Label the pages the replay actually read**, not just the pages listed in the case. In the `memory_search` arm the agent searches on its own and may read pages the case never listed. A run's origin is the dirtiest origin among all pages it read.

All of this assumes **every sentence can be traced back to a source message**. That is one reason this repository's `memlite/` (not written yet) lists sentence-level provenance and consolidation with hard constraints as requirements. A memory system without sentence-level provenance is very hard to evaluate cleanly.

**4. Plant leaks on purpose in synthetic data**

The public version uses synthetic sessions on open-source repositories. A clean `other_session` page is written from a different synthetic session, deliberately worded differently from the session under test, so neither the agent nor the judge can match on surface wording. For some cases we also build `same_session` and `after_correction` variants on purpose, as controls. The gap on the same item across the three origins is how much leakage can inflate the gain.

## How Next-step Replay will report

The case format and arms are in [bench/next-step-replay](../bench/next-step-replay/README.md). Reporting rules:

- **The headline uses `other_session` only.** "Does memory reduce violations?" is answered from that column alone.
- **The other two columns are listed separately and never pooled.** `same_session` and `after_correction` are leakage references: how much better they do than `other_session` is how much a pooled number would be inflated.
- **Every cell gives its n.** Clean cases are usually the fewest. When n is small we say "no measurable difference" rather than pooling to reach significance.
- **Report the origin mix**: how many items fall under each origin, and how many untraceable pages were treated as `after_correction`.
- **Split the funnel and judge agreement by origin too.** Leakage doesn't just lift the final violation rate. It also lifts the "found the right page" step, since the session's own wording naturally resembles the agent's query at that moment. [inference]

Full reporting template (the demo below covers only some of these cells):

| Arm \ page origin | `other_session` | `same_session` | `after_correction` |
|---|---|---|---|
| `no_memory` | violation rate (n) | violation rate (n) | violation rate (n) |
| `memory_search` | … | … | … |
| `oracle_page` | … | … | … |
| `step_conditioned` | … | … | … |

In principle `no_memory` doesn't depend on pages at all. If it varies a lot across the three columns, the item groups differ in difficulty, and comparisons should be paired by item rather than made column against column.

## Eval demo results

The [E002 complete Next-step Replay pilot](../experiments/E002-next-step-replay-full/README.md) on 2026-11-15 covered all six synthetic Click cases, running only `no_memory` and `oracle_page`. These are plan-level ratios split by `page_origin`; origins are never pooled, nor are these results combined with the earlier [E001 bounded smoke](../experiments/E001-next-step-replay-smoke/README.md).

Each label rate is that judge's plans with the label divided by all plans in the same origin and arm. `full` means fully compliant, `partial` means partially compliant, and `violates` means a violation; each cell's n is the number of plans judged. Agreement uses paired judgments in that same origin and arm as its denominator. Three-way agreement compares the original labels; binary agreement compares only violates versus not. Neither is accuracy.

| `page_origin` | Arm | Judge A: full / partial / violates | Judge B: full / partial / violates | Plan agreement: three-way / binary |
|---|---|---|---|---|
| `other_session` | `no_memory` | 50.0% / 25.0% / 25.0% (n=4) | 50.0% / 25.0% / 25.0% (n=4) | 100.0% / 100.0% (n=4) |
| `other_session` | `oracle_page` | 75.0% / 25.0% / 0.0% (n=4) | 100.0% / 0.0% / 0.0% (n=4) | 75.0% / 100.0% (n=4) |
| `same_session` | `no_memory` | 100.0% / 0.0% / 0.0% (n=2) | 100.0% / 0.0% / 0.0% (n=2) | 100.0% / 100.0% (n=2) |
| `same_session` | `oracle_page` | 100.0% / 0.0% / 0.0% (n=2) | 100.0% / 0.0% / 0.0% (n=2) | 100.0% / 100.0% (n=2) |

Within `other_session`, both judges' violates rates went from 25.0% for `no_memory` to 0.0% for `oracle_page`, but **the oracle plans were not unanimously judged full**. The disagreement concerns an optional verification step: after explicitly using `terminal_width=48`, the plan also suggested checking with a different `COLUMNS` value. Judge A found that environment mutation ambiguous under the rule's scope and assigned `partial`; judge B treated it as an independence diagnostic, not a test dependency, and assigned `full`. Both original verdicts are retained, with no adjudication, rubric change, or selective rerun.

**Both `same_session` arms were fully compliant for both judges, but the rule reminder was already in both prefixes.** The no-memory arm was therefore already at the ceiling; saturation is not an incremental memory benefit. Pooling these controls would lift judge A's memory-arm full-plan rate; judge B's is already at the ceiling in `other_session`. This illustrates why the essay requires origin-stratified reporting, not that cross-session memory works.

**Limits: six hand-written synthetic cases, one model, descriptive results only.** The planner and both judges used `claude-haiku-5-5`; separate blind calls with different prompts do not provide model diversity, and there is no independent human calibration. Only plans were scored; no patch was executed. Supplying a complete page proves delivery, not reading, and retrieval and real task completion were not measured. `after_correction`, `memory_search`, and `step_conditioned` were not run. These ratios are not a causal estimate or **evidence of memory effectiveness**. The [E002 full report](../experiments/E002-next-step-replay-full/README.md) records the setup, original labels, and limitations.

## Summary

| Problem | What to do |
|---|---|
| Page came from the session under test | Trace per sentence; any citation into that session means `same_session` |
| Page was edited after the correction | Judge by version time; newer than the correction means `after_correction`, or replay the store as of that moment |
| Consolidation dropped citations | Untraceable is not clean; merges must keep citations |
| Prefix or repository state carries the answer | Cut at the last user message before the correction; check out the commit current at that time |
| How to report | Headline from `other_session` only; three columns, each with n; never pooled |

Next: "Step-conditioned retrieval".
