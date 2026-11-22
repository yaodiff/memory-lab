# E016 Evidence-backed entity attachment changes

- Conclusion: Inconclusive
- Date: 2026-11-22
- Issue: [#80](https://github.com/yaodiff/memory-lab/issues/80)
- Source: aggregate proportions from small samples.

## Hypothesis and method

Attaching a page to the entity its body actually describes can improve subject organization without degrading retrieval. Apply changes in an evidence-backed batch and verify every stored record with an independent readback. Compare frozen retrieval questions with the earlier baseline and inspect changed rankings to see whether the edited pages affected the scoring positions. For a broader model-proposed batch, have a separate judge blind-review a sample against a 90% accuracy gate.

## Results

The evidence-backed batch had 100% successful write verification and preserved all secondary links. The frozen replay showed no regression attributable to these edits. Some unrelated rankings moved between snapshots. The ranking function did not consume the edited links, and the only edited page in a changed result was below the scored positions. Blind review of the broader proposals found 76.7% correct attachments.

## Decision and limits

Retain the verified edits. Keep broader proposals in review because the accuracy gate failed. The frozen replay checks retrieval safety for this batch. It leaves any downstream benefit from navigating the entity links unmeasured.
