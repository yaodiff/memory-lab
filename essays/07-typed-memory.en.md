# Entity governance and ontology-backed memory

[中文](07-typed-memory.md) · [Source and paper notes (Chinese)](../docs/agent-memory-deep-reading.md)

Entity governance tells us where a page belongs. An ontology-backed memory also needs to tell us which object a statement refers to, when and where it applies, and what supports it. The existing leaves are a useful navigation layer. The strongest near-term retrieval result came from diagnosing real misses and adding question wording and scope to relevant pages.

## What the governance work achieved

- **Clearer attachment and preserved evidence.** In the main pilot, direct attachment to leaves rose from about 80% to 95%. Sampled overnight edits preserved links and trigger terms. Targeted readback also verified cross-category supersession and evidence dates. These are results about structure and maintenance. [E037](../experiments/E037-nightly-curation-readback/README.md) · [E040](../experiments/E040-cross-category-supersession/README.md) · [E044](../experiments/E044-leaf-coverage-live/README.md)
- **Separate evidence for retrieval and use.** Keyword and vector fusion improved complete top-five coverage in a single-scope live comparison. The control-adjusted interval for adoption in real sessions crossed zero. [E032](../experiments/E032-keyword-fusion-live/README.md)

## What the experiments support

These observations come from small internal samples.

| Question | Observation | Decision |
| --- | --- | --- |
| Is evidence missing from the pool? | About 65% of queries missing evidence in the live top five already had every required page in the original top 30. Entity expansion made newly complete coverage possible for about 2% or 9% of that same set, depending on budget. The locked configuration had a net interval crossing zero. [E049](../experiments/E049-entity-index-two-stage/README.md) | Two rule-based rerankers recovered no held-out queries. Consider a model reranker only if reproducible in-pool misses remain after content edits. [E053](../experiments/E053-rule-based-in-pool-reranking/README.md) |
| Which content is worth adding? | Targeted edits raised complete top-five coverage by about 5.6 points in the live before/after, with no complete-query regressions. Round two added about 1.4 points in offline replay, with an interval touching zero. Frequency-based bulk edits changed coverage by about −1.4 points offline. [E052](../experiments/E052-targeted-content-enrichment-live/README.md) · [E056](../experiments/E056-blind-faq-enrichment/README.md) | Start from actual misses, verify the applicable scope in the source, and replicate on a fresh holdout. The live batch included a few new pages and used the same questions that informed the edits. |
| Can we rank directly from the leaves? | Four structure-based ranking variants missed the shadow gate. Better leaf-name anchoring also failed to improve downstream retrieval. [E031](../experiments/E031-governance-retrieval-recheck/README.md) · [E045](../experiments/E045-entity-structure-ranking/README.md) | Evaluate disambiguation, evidence readback, and navigation directly. The failed page-level expansion bounds that implementation. Statement-level designs remain to be tested. |

## Five gaps an ontology could fill

| Gap | Smallest testable change |
| --- | --- |
| Entity types | Add types to existing stable IDs for a few frequently confused objects, such as components, environments, and interfaces. Keep identity, aliases, and topics distinct, with an explicit unknown state. [OntoKG §3](https://arxiv.org/html/2604.02618v1#S3) |
| Intrinsic attributes | Record a few sourced properties that can distinguish objects, such as a component's responsibility or an interface's protocol. Keep a node attribute distinct from a directed relation. Represent properties that vary with scope or version as qualified statements. [OntoKG §5.3](https://arxiv.org/html/2604.02618v1#S5.SS3) |
| Binding at write time | Resolve the object for an evidence span when a page is created or revised. A unique, type- and scope-consistent match can become a binding proposal. Ambiguous matches or weak sources go to review. Store the source version and make replays idempotent while preserving the page. [WorldDB §3](https://arxiv.org/html/2604.18478v1#S3) |
| Validity and supersession | Extend page-level supersession to statements that can change. Store evidence time, the interval when the statement applies, and when it was recorded. Track cooling separately. Close the old interval only with evidence of replacement for the same object, attribute, and scope. Keep past evidence addressable and unknown values explicit. [Zep §2.2.3](https://arxiv.org/html/2501.13956v1#S2.SS2.SSS3) · [Graph-Based Personalized Memory §IV](https://arxiv.org/html/2609.08599v1#S4) |
| Entity navigation | Offer an explicit route from a resolved object to scoped statements and their source text. Also let a body-text hit lead back to the object. Measure correct resolution, readable evidence, and steps to the source. Fall back to ordinary search on ambiguous names. [EnSIMem §3](https://arxiv.org/html/2609.27279v2#S3) · [MemForest §6](https://arxiv.org/html/2605.23986v4#S6) |

For a synthetic example, two deployment environments can have different retry policies at the same time. If a source confirms that an upgrade changes the policy in one environment, close the old interval only there and keep it accessible for pre-upgrade questions. The topic organizes the documents, the entity ID names the object, and the statement keeps the policy, scope, and evidence together.

Keep working from real retrieval misses and use a fresh holdout to check each batch. Evaluate model reranking only if reproducible misses with matching-version evidence remain in the pool. Start the entity work with a few types and verifiable dates and versions. Then test explicit historical queries and question-specific navigation against a fixed read budget. The fixed directory added no complete coverage under the tested budgets, and the time/version replay lacked usable fields. [E054](../experiments/E054-entity-drilldown-navigation/README.md) · [E055](../experiments/E055-dedup-time-and-literal-replay/README.md) · [Roadmap](../plans/team-memory-quality/README.md)
