# Plan for context-anchored entity recall

English · [中文](plan-context-anchored-recall.md)

- Status: awaiting owner review
- Dates: created 2026-11-20 / last updated 2026-11-20
- Tracking issue: [#64](https://github.com/yaodiff/memory-lab/issues/64) / Experiments: pending registration

## Background and problem

[E009](../experiments/E009-typed-relation-expansion/README.md) picked entity seeds from the top five global results and followed typed relations one hop. Its conclusion was **Does not work**. In a small internal sample, about 48% of missed gold entity pages had no eligible seed and about 36% had a seed with no connection to the gold page. Complete multi-page recall stayed flat. Reranking put wrong pages in the top three for more cases.

In small internal sample reviews, roughly three quarters to four fifths of the model's proposed attachments were judged correct. Mechanical matching on code symbols yielded almost no correct attachments. These observations concern attachment quality. Recall effectiveness still needs a controlled comparison.

## Goal and scope

Test whether a separate panel helps readers find all the memory pages they need under the same reading budget when the task context identifies the right entities and the pages are correctly attached. This round is an offline recall evaluation using public or synthetic material. Global results keep their original contents and order.

## Approach

1. Identify entity anchors from context available before search: the active repository, files being changed, and systems named in the task brief.
2. Collect the lessons, decisions, and conventions directly attached to those entities, deduplicate them, and rank them by semantic relevance to the question. Cap the panel at three pages and leave it empty when there is no suitable anchor or attached page.
3. Put the panel beside global search. E009 depended on search finding an entity first and tried promoting its neighbors into the global results. A separate panel lets us measure both additional recall and wrong pages under a fixed reading budget.

### AOCI-CODE reference

The [AOCI-CODE reading note](../essays/05-aoci-code.en.md) explains the inspiration for this plan. It covers upstream commit [`5f68ace`](https://github.com/aoci-spec/aoci-code/commit/5f68ace), licensed under [FSL-1.1-MIT](https://github.com/aoci-spec/aoci-code/blob/5f68ace/LICENSE).

- **Object identity.** Identify entities by repository and by path or symbol within it so that objects with the same name in different repositories or modules stay distinct. See the [object contract](https://github.com/aoci-spec/aoci-code/blob/5f68ace/spec/public/aoci-object-fras-v2.txt).
- **Verifiable evidence.** Keep revision-specific source references on attachments so reviewers can inspect the cited evidence. Reviewers still need to check that the page's topic and scope fit the entity. See the [System Cognition contract](https://github.com/aoci-spec/aoci-code/blob/5f68ace/spec/public/aoci-system-cognition-runtime-v1.txt).
- **Review on source change.** Adapt the upstream source change detection to mark affected attachments for review when their cited source changes. See the [refresh workflow](https://github.com/aoci-spec/aoci-code/blob/5f68ace/docs/cognition-refresh.md).

### Draft decision rules to preregister before running

- **Sample.** Freeze the held-out public or synthetic tasks, gold anchors, required pages, wrong-page labels, ranking method, and cap of three panel pages. Include multi-page cases and cases with no suitable anchor. Retrieval sees only context available before search. Reserve gold labels for scoring and diagnosis. Set a sample size that can resolve the proposed margins before viewing outcomes.
- **Attachment gate.** Independently review the frozen links. Require at least 90% precision (correct links / evaluated links) and 80% coverage (present gold links / all gold links for required pages on tasks with gold anchors). Report anchor precision and coverage separately. If the gate fails, record **Inconclusive** and distinguish missing links from incorrect links.
- **Comparison at a fixed budget.** Use the same questions and snapshot, with up to six unique pages read per case. The baseline reads the first six global pages. Treatment reads the first three global pages, then up to three unique panel pages, then fills unused slots from the remaining global order. Complete recall uses all multi-page cases, including misses and empty panels. The wrong-page rate is the share of all cases with at least one judged wrong page among the pages read. Verify that global result IDs and order match for every case.
- **Works** if the gate passes, complete recall improves by at least 10 percentage points, the wrong-page rate rises by at most 5 points, and global results match in every case.
- **Does not work** if the gate passes and global results match, but complete recall fails to improve or the wrong-page rate rises by more than 5 points.
- **Inconclusive** if the gate fails, global results change and invalidate the comparison, or the result falls between the decision lines. Run a gold-anchor diagnostic on the same links to distinguish anchor detection, attachment, and ranking failures.

## Steps

- [ ] #64 Review the direction and draft decision rules.
- [ ] Open a separate experiment issue, freeze the tasks, labels, method, and decision rules, and review attachment quality.
- [ ] Run the offline comparison and gold-anchor diagnostic on the same snapshot. Record the conclusion, denominators, and failure causes in the experiment template.

## Owner decisions

Approve the separate panel direction and draft decision rules. Register the sample size and labeling details before the experiment runs.

## Deviations

None at the draft stage.
