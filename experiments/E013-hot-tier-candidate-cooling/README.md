# E013 Hot-tier candidate cooling — retrieval non-regression gate

- Conclusion: Works
- Date: 2026-11-22
- Issue / PR: [#77](https://github.com/yaodiff/memory-lab/issues/77) / this change
- Source: small internal frozen-snapshot experiment, abstracted to ratios
- Follow-up: a larger-scale value adjudication before any behavior-arm claim (see Scope)

## Hypothesis

Demoting pages already adjudicated as having no reusable value out of the default search candidate set shrinks the hot-tier surface without hurting retrieval. This is the operational form of the "shrink before you grow" hot-tier contract in plan [#72](https://github.com/yaodiff/memory-lab/issues/72). A preceding read-volume calibration motivated the change of leverage point: in hundreds of completed trials, agents never read a large navigation block wholesale — essentially every navigation open covered only the short head — while the context actually consumed on each task arrived through a small set of search results. File-block character caps therefore had no causal path to behavior; the candidate set does.

## Method

Two offline stores built from one frozen snapshot, sharing the same lexical retriever, tokenizer and ranking function. The baseline store is unchanged. The cooled store removes a small set of pages — already judged "no reusable value" by an independent dual-model review in earlier work — from the full-text search index only. Their summary rows and original page files are retained, so each page stays readable by its exact identifier; nothing is physically deleted.

The full held retrieval question set was replayed identically against both stores. About two thirds of the questions carry an answer gold label and a large majority carry a registered trap (wrong-page) label. Development and frozen-regression splits were scored separately, and the single affected workspace was also reported on its own.

Decision rules were frozen before the run:

- **Works (gate to any behavior arm)**: answer-page top-1 and top-3 counts do not decrease and trap-pages-in-top-3 does not increase.
- **Does not work**: any gold drops out of top-1/top-3 or trap-in-top-3 rises.
- **Inconclusive**: retriever differences make the two arms non-comparable.

The local lexical retriever is a proxy for the production hybrid retriever, so absolute scores are not compared across snapshots; only the same-machine, same-snapshot arm contrast is interpreted.

## Results

The gate passed with identical metrics across arms.

- Answer-page top-1, top-3 and trap-in-top-3 were unchanged on both the development and the frozen-regression splits, and unchanged on the affected workspace considered alone.
- Only a small handful of questions showed any difference in their top-ten ordering. Inspection showed identical page sets with a benign internal tie-break reorder; their top-1, top-3 and trap outcomes were all unchanged.
- The demoted pages had **zero** appearances in any question's result window on the baseline arm — a pure noise-removal, zero-recall-impact outcome, consistent with an earlier one-page demotion pilot reported in the same setting.
- The demoted set was a tiny fraction of the affected library, well below one percent of its indexed pages.

## Why no behavior arm at this scale

Before spending model budget, the demoted pages were traced across a large body of already-completed historical trials. Only a few of the demoted pages had ever been returned by search, and the trials that touched any of them contained **no** wrong-adoption event. At this sample size a behavior arm cannot satisfy a pre-registered "reduce wrong adoptions by a relative margin with at least one fewer event" bar — the relevant baseline is zero — so running it would produce an unavoidable Inconclusive at a non-trivial token cost. The measurable behavior benefit of cooling requires applying the value adjudication over a much larger page set first; that scale and its model budget are a separate, explicitly approved decision.

## What this establishes

A narrow, safe mechanism: adjudicated low-value pages can be removed from the default search index while their originals remain readable by identifier, with no measurable retrieval cost on the held set. It validates the projection method for a future larger cooling campaign, not the campaign's target reduction. It does not establish any behavior-metric gain, and it does not touch production memory or product code.

## Not covered

- The demoted labels are reused from an earlier independent dual-model review and were not re-adjudicated here; any label error is inherited.
- The lexical proxy cannot reproduce production semantic ranking; known proxy limitations (some gold pages never reach the short window under the proxy) apply equally to both arms.
- No production traffic, model calls, or writes were made in this stage; all scoring was local and deterministic.
