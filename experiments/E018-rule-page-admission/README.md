# E018 Adding rule pages and repeating the behavior evaluation

- Conclusion: Inconclusive
- Date: 2026-11-22
- Issue: [#80](https://github.com/yaodiff/memory-lab/issues/80)
- Source: aggregate proportions from a small sample.

## Hypothesis and method

Adding rule pages to a frozen retrieval corpus can make execution plans more complete. Compare the same cases, prompts, inputs and judge rubric with and without the draft pages. Repeat on the same cases and blind-grade the plans. For the additional behavior runs, require a gain in each repeat, at least a ten percentage point pooled improvement and a positive lower bound from paired resampling clustered by question. Also require stable next-step accuracy and labeled top-three retrieval, no increase in mistaken adoption, and token use within budget.

## Results

Across all attempts, complete plans rose from 69.6% to 75.5%. In the additional behavior runs, completeness rose from 40.6% to 50.0%, with a paired 95% interval of −12.5 to +31.3 percentage points. This missed the stability gate. The frozen comparison found identical retrieval rankings in the covered scope. The frozen cases came from outside the affected corpus.

## Decision and limits

Keep the pages as drafts. Admit durable, evidenced cross-task contracts when the agent cannot reliably recover them from a single authoritative source. Leave code-derivable details with their sources and put reusable search, reading and verification steps in the usage instructions. See [E014](../E014-memory-instruction-regression/README.md) for the separate instruction regression. This replay rated plans and leaves actual execution unmeasured.
