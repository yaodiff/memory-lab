# E019 preregistration

[Issue #85](https://github.com/yaodiff/memory-lab/issues/85) · [E009](../E009-typed-relation-expansion/README.md) · [Context-anchored recall plan](../../plans/plan-context-anchored-recall.md)

## Hypotheses

Provenance-backed graph candidates can increase all-required-page recall compared with the same pipeline without graph candidates. Resolving an entity from task context and exposing its attached pages in a separate panel can increase all-required-page recall compared with global search. Each claim requires a gain of at least 10 percentage points at six pages and no more than a five-point increase in wrong-page exposure. E009's original expansion mechanisms are comparison arms.

## Sample and measurements

Freeze [fixture.py](fixture.py), its generated JSON hash and all fixed parameters in [config.json](config.json) before any case retrieval. Use all 120 synthetic tasks, 30 each for object ambiguity, action ambiguity, both, and no usable context anchor. Each task has two required pages and explicit wrong-object and wrong-action distractors. There are ten domain clusters of 12 tasks. All tiers use the same corpus within each task and no task is excluded. Cluster resampling reflects shared scenario templates. This fixed design has 12 task changes per 10 points overall and 3 per 10 points within a stratum. As an illustrative planning calculation, at 20% paired discordance an independent-task 95% half-width is about eight points. Clustering may widen it. Strata are diagnostic and the sample can only resolve sizable effects.

Use frozen source registry rows to validate each edge's typed endpoints. Keep unsupported edges in the input as negative controls and exclude them from every graph arm. The synthetic registry encodes author-supplied ground truth for graph links. Panel attachment precision is the fraction of direct attachments whose subject is corroborated by the linked page body, using the synthetic declared service names. Attachment recall is the number of required owner-to-page attachments present divided by all required owner-to-page attachments across anchorable tasks (180). Wrong-action pages can be valid attachments for an entity while still being wrong for a question. Report context anchor precision and coverage, oracle anchor diagnostics, no-anchor behavior, and how many cases have no E009 seed.

Primary metrics are tasks retrieving both required page IDs in the first six and tasks exposed to at least one labeled wrong-object or wrong-action page in those six. Report wrong-page exposure at three, split error types, per-stratum results and E009 native cutoffs as secondary metrics. The denominator is all tasks in the stated group. Graph and panel get no gold inputs. Oracle output is diagnostic only.

## Arms

| Arm | Behavior |
| --- | --- |
| A global | Fuse top 12 dense cosine candidates and up to 12 positive BM25 candidates by RRF with k=60. Keep a global list of 10. |
| B E009 append | Pick non-weak entities in A's first five. Follow one hop over E009 types with inverse edges. Append at most five absent entity neighbors in seed and relation priority order. |
| C E009 boost | Same seeds and typed neighbors; apply E009's weights and 0.03 per relation with a 0.06 cap for existing later-ranked neighbors. Rebuild by global numeric score and keep ten. Scale A's raw fusion score by 30.5 to give it a unit maximum. A cosine below 0.25 stands in for the unavailable production weakness flag. |
| R no graph | Cross-encode the first 12 candidates from the dense and keyword RRF. |
| H graph fusion | Seed a separate graph leg with up to eight dense results above the common cosine floor. Propagate two degree-normalized steps through evidence-backed edges, with decay 0.55. Fuse dense, keyword and graph legs with RRF, then use the same cross-encoder and candidate cap as R. This is inspired by the Hindsight architecture. |
| X context panel | Resolve the entity using exact, unique matches from repository, path prefix or mentioned-system aliases in pre-search context. Score direct attached pages against the original query with the same cross-encoder. Apply the #64 six-page read order: A's first three, up to three distinct panel pages, then A in its existing order to fill any unused slots. Audit the original global ID order for every task. |

Dense and cross-encoder weights and software are fixed in config. Stable ID sorts break score ties and RRF order breaks cross-encoder ties. R and H receive the same search query with no task context. X uses context for the entity lookup. E009's original live back end and original corpus are outside this synthetic reproduction.

Run the deterministic gold score and two separate GPT-6.2 Sol passes on each arm. Randomize task order and blind arm and page labels. Give the judge the task description, the two requirements and the ordered page text. Use one frozen rubric for all calls. Require all 1,440 case-arm-pass verdicts, log requested and resolved model names and usage, and report exact two-round agreement for each arm and metric. No voting-based replacement for the gold score.

## Decision rule

Compare H with R and X with A as the two confirmatory comparisons. H versus A, B versus A, C versus A and the oracle are descriptive. Use 10,000 paired percentile bootstrap draws by domain cluster (seed 190056). Report 95% intervals as sampling uncertainty conditional on the synthetic design. For judge noise, bootstrap each arm's signed pass-2 minus pass-1 task score difference, and report the central 95% interval and the 95th percentile of the absolute difference. For a pair, the noise boundary is the sum of the two arms' absolute radii. Also report the min and max over all four cross-pass arm deltas. A claimed positive gain must exceed the noise boundary in all four combinations. For wrong-page non-regression require the upper bound of the four crossed deltas plus the noise boundary to be at most five points.

- **Works** if either confirmatory pair reaches a gold gain of at least 10 points, its gold gain interval excludes zero, the upper 95% gold interval for wrong-page increase is at most five points, and both repeated-judge conditions pass. A panel claim additionally requires the 90% attachment precision and 80% coverage floors and identical global rankings for all tasks.
- **Does not work** if both confirmatory pairs are ruled out. A pair is ruled out for gain when its upper gold interval is below 10 and the best crossed judge gain plus noise is below 10. It is ruled out for harm when the lower gold interval for wrong-page increase exceeds five and the smallest crossed judge harm minus noise exceeds five. The panel must pass the attachment and ranking gates to be ruled out.
- **Inconclusive** otherwise, including incomplete judging or a panel failing its attachment gate with no supported graph claim. Gains within the judge noise are inconclusive.

## Scope

This is a controlled mechanism test with authored gold and graph links. It measures finding evidence, not whether an agent follows it, how often good links exist in a live system, or the effect of running Hindsight in production. B's native extra slots are an explicit descriptive comparison. A separate frozen offline case study, if available, is reported as a coarse observation with coverage limits.
