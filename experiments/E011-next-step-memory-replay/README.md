# E011 Next-step replay with historical and current memory

- Conclusion: Inconclusive
- Date: 2026-11-20
- Issue / PR: [#59](https://github.com/yaodiff/memory-lab/issues/59) / this change
- Source: small internal sample of previously reported retrieval mismatches
- Follow-up: none

## Hypothesis

Current retrieval should give the assistant useful grounds for its immediate next action, improve the case-level safe next-step rate over no memory, and avoid increasing the rate of influence from an irrelevant result.

## Method

Following [E001](../E001-next-step-replay-smoke/README.md) and [E002](../E002-next-step-replay-full/README.md), freeze the context before the target search and withhold the reference next step. The planner receives historical results, a current read-only retrieval result, or no memory. Current retrieval is frozen before generating repeated plans. The historical arm retains any relevant results that were already present. A proxy with partial historical evidence accounts for 11.1% of cases.

Generate independent text-only plans. A separate blind call scores each plan for use of a relevant result, influence from an incorrect result, and whether the first action is on target. A fixed underlying model serves both roles. The rubric and case references were frozen before generation. The references were drafted by an assistant using the available source evidence.

A case passes the next-step criterion when at least two thirds of its plans are on target and none follows a wrong result. Current memory counts as helpful on a case when it passes that criterion, a returned page can answer the question, and at least two thirds of its plans use a relevant result. A page can qualify by directing the assistant to the requested primary source. Ranking passes when a relevant page appears in the short high-rank window without a recorded wrong match.

The frozen decision rule called for a helpful-case rate of at least two thirds, a case-level next-step rate improvement of at least one ninth over no memory, and no higher wrong-result influence than historical retrieval. A helpful-case rate at most one third with no increase in first-action correctness over no memory would fail. Other outcomes are inconclusive. [Configuration](config.json)

## Results

All planned generations and paired judgments completed (100.0%). The plan rates use all plans in the relevant arm as the denominator. The case rates use the same selected cases in each arm.

| Arm | Relevant result used | Wrong result influenced plan | First action on target | Case passes next-step criterion |
| --- | ---: | ---: | ---: | ---: |
| Historical results | 51.9% | 0.0% | 100.0% | 100.0% |
| Current results | 85.2% | 3.7% | 100.0% | 88.9% |
| No memory | Not applicable | Not applicable | 100.0% | 100.0% |

For current retrieval, 33.3% of cases passed the ranking criterion, 100.0% contained a page with a usable answer or direct primary-source navigation, and memory helped in 77.8% of cases. Current memory increased the count of on-target first actions in 0.0% of cases compared with no memory.

## Conclusion

The current results gave the planner more usable references. First-action direction was already at the ceiling without memory, and wrong-result influence occurred in a small share of the current-result plans. The frozen decision rule yields **Inconclusive**.

## Limits

The sample was selected for known problems. Some requirements already described the intended action. The planner saw an abridged prefix and the actual search excerpts. The page audit could also use the corresponding full text, which explains how answerability and adoption can differ. Model judgments were not human-calibrated. Repeated plans share a frozen retrieval result and do not measure ranking variance. No tools or generated changes were executed. Only aggregate ratios and method are published.
