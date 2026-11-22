# E017 Programmatic screening for duplicate entities

- Conclusion: Does not work
- Date: 2026-11-22
- Issue: [#80](https://github.com/yaodiff/memory-lab/issues/80)
- Source: aggregate proportions from a small sample. Tests the duplicate-screening idea in [the mechanism plan](../../plans/plan-graphiti-letta-integration.en.md).

## Hypothesis and method

A programmatic funnel based on normalized names and related signals can find sufficiently precise same-object candidates while reducing model review effort. Compare review batches with the baseline. Inspect known similar-but-distinct pairs and adjudicate proposed candidates. The automatic-action gate requires at least 90% merge precision, and the cost gate requires at least 40% fewer model-review batches.

## Results and decision

Merge precision was 0.29%. Even counting useful look-alikes together with true duplicates, candidate precision was 46.42%. The automatic-action gate failed. Model-review batches fell by 77.6%, and the known look-alike check observed a 0% false-merge rate. Use the funnel to reduce review workload and flag ambiguous names. Keep merge decisions under review. The observations come from one snapshot and do not estimate the false-merge rate for unseen look-alikes.
