# E014 Memory usage instructions and held-out regression

- Conclusion: Inconclusive
- Date: 2026-11-22
- Issue: [#75](https://github.com/yaodiff/memory-lab/issues/75)
- Source: small internal sample. Results below are aggregate proportions.

## Hypothesis

Specific search wording, full-page reading for relevant matches, and a final check of each applicable requirement can improve plan completion without reducing held-out performance.

## Method

The baseline and revised instructions used the same model, cases, memory contents, retrieval service and read-only tools. A separate blind call rated whether the first action was correct, whether the plan covered every required item, and whether it adopted unsuitable material. We fixed the grading rules before replay, reused a prior development pilot, and kept the held-out set out of instruction tuning. Retrieval and behavior were evaluated separately. Repeated held-out behavior attempts were grouped by case.

The development threshold required at least a 10 percentage point gain on completion or next-step accuracy, a positive lower bound from paired resampling, and tolerances on the other metrics. The held-out check required stable or better labeled rankings and empty-response frequency, limited next-step loss, and no increase in mistaken adoption. The run prioritized the entire held-out set, then development behavior, then stratified paired development retrieval within a fixed token budget.

## Results

We completed 100.0% of held-out cases, 100.0% of development behavior cases, and 87.5% of development retrieval cases. The retrieval denominator below is the paired cases with a labeled answer or source entry. Behavior rates use completed plans.

| Measure | Baseline | Revised |
| --- | ---: | ---: |
| Held-out labeled retrieval at 1 | 66.7% | 66.7% |
| Held-out labeled retrieval at 3 | 80.0% | 80.0% |
| Held-out labeled retrieval at 10 | 100.0% | 100.0% |
| Held-out correct next step | 72.2% | 77.8% |
| Held-out all requirements covered | 66.7% | 66.7% |
| Held-out mistaken adoption | 0.0% | 0.0% |
| Development correct next step | 90.8% | 93.4% |
| Development all requirements covered | 56.6% | 59.2% |
| Development mistaken adoption | 0.0% | 0.0% |
| Development labeled retrieval at 3, observed pairs only | 78.8% | 80.0% |

Mean token use per new paired case changed by +3.8% for held-out retrieval and +0.4% for held-out behavior. It changed by -0.2% for development retrieval and +0.4% for development behavior. Estimates include cached input in both arms and exclude reused pilot usage.

## Conclusion

**Inconclusive.** The held-out check passed. Development retrieval coverage was incomplete under the token budget. The observed paired subset is descriptive. The evaluation used text-only plans and a model judge. It provides no evidence about actual task execution after release.
