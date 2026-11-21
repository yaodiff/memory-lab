# Plan for adapting Graphiti and Letta mechanisms into entity-relation memory

English · [中文](plan-graphiti-letta-integration.md)

- Status: awaiting owner review
- Dates: created 2026-11-21 / last updated 2026-11-21
- Tracking issue: [#72](https://github.com/yaodiff/memory-lab/issues/72) / Experiments: pending registration

## Background and problem

The [three-systems survey](../docs/memory-systems-survey.en.md) (Refs #70) surfaced a set of reusable mechanism parts in Graphiti's temporal knowledge graph and Letta's tiered memory. This plan borrows parts, not architectures: running a full graph database, and letting an agent freely rewrite core memory, both conflict with evidence from our own small pilots.

Four concrete problems, all from small samples and stated here only at coarse granularity:

1. **LLM-only judging is expensive and unstable.** Entity dedup currently goes straight to dual-model judging, which is equivalent to running only the most expensive third stage of Graphiti's three-stage funnel. Raw agreement in a full inventory looked high, but after correcting for the dominant class the kappa was only moderate; at the page-action level agreement sat near two thirds with kappa close to chance. When models judged from features alone in a batch run, none of the known same-object pairs were identified. Independent review was systematically more conservative than the original judges: nearly every shell entity that both models had voted to remove was rescued.
2. **Relations almost never carry provenance.** Among existing relation rows on pilot entities, only around one in a hundred had a source. When models were asked to rewrite them under the new rule, every row got one — the missing piece is an enforcement gate, not capability.
3. **An always-injected file entry helps but causes misuse.** In a controlled comparison, adding a file-based memory entry to search showed a clear advantage on tasks with an explicit entity or error anchor (the share of correct next steps rose from roughly the mid-forties percent range to around two thirds), but wrong-page adoptions rose too. Adding explicit applicability scopes plus a check-before-adopting rule roughly halved wrong adoptions, at the cost of a small movement in correctness whose interval included no change.
4. **Expanding recall along the graph was already tested and failed.** E009 ([#56](https://github.com/yaodiff/memory-lab/issues/56)) expanded one hop along typed relations and concluded Does not work: about half the missed gold pages had no eligible seed, about a third had a seed with no connection to the gold, and reranking pushed more wrong pages into the top three. The separate-panel direction in [#64](https://github.com/yaodiff/memory-lab/issues/64) is the corrected response; this plan does not repeat that path.

A honest scope note: an attribution exercise on one business evaluation found that roughly six in ten lost points reflected knowledge the memory simply did not contain, about two in ten reflected having the right page but not finishing the task, and only a small share was a recall failure. These mechanisms govern long-term maintainability and recall quality of the memory asset; they are not a direct cure for missing knowledge or incomplete execution.

## Goal and scope

Goals:

- For each of eight candidate adaptations, document current practice, the target shape, the known problem and evidence it addresses, and its costs and risks.
- Pair every adaptation with an offline experiment whose decision rules are frozen before running, using the repo's Works / Does not work / Inconclusive convention.
- Rank by cost-effectiveness, recommend only one or two to start, and give a phased timeline with every owner decision point marked.

Out of scope:

- No experiments, model calls, production memory changes, or product code changes in this round; this is a planning deliverable.
- No full graph database, no unconstrained agent writes to memory, no retry of the recall expansion that E009 refuted.
- No internal names, raw data, people, or links in this repo; internal evidence appears only as ratios and coarse descriptions.

## Approach: eight candidate adaptations

### G1 Front stages of the three-stage dedup funnel (from Graphiti)

- Current: dual-model four-way judging with no programmatic front stage; feature-level batches cannot spot same-object pairs.
- Target: two deterministic stages before the models — exact identity matching on normalized attributes (start commands, code directories, interface paths) and normalized name similarity with an entropy threshold that forbids auto-merging short or generic names. The programmatic stages only nominate; every candidate still goes through dual-model judging and independent review.
- Problem addressed: unstable and costly LLM judging, zero automatic merges.
- Costs: normalization rules and thresholds need maintenance; a wrong merge is worse than a missed one, so known same-name-different-object cases go on a hard blocklist; sparse identity attributes mean low expected coverage for concept- and metric-type entities.

### G2 Structured invalidation instead of deletion (from Graphiti; bi-temporal axes deferred)

- Current: superseded pages are kept but demoted out of default search with a prose timeline note; the supersession itself is just text, maintained by convention.
- Target: promote supersession to structured page fields (successor, effective point, applicability scope) with a validator that checks the successor exists; when search returns a superseded page, show an explicit "superseded by X, current rule at Y" notice instead of silently hiding it. Contradiction judging splits into two questions — duplicate versus mutually exclusive.
- Bi-temporal axes (fact time versus system record time) would answer "what did the system believe at that time", but no such query need exists today and the maintenance cost does not match. Explicitly deferred until a point-in-time replay need appears.
- Costs: touches page structure and search behavior in production; keeping invalidated pages visible may add trap pages to the top three and needs a controlled comparison; a related idea on a public dataset already ended Inconclusive once, so the decision rules here must be stricter.

### G3 Programmatic provenance validation for relations (from Graphiti and evidence-sidecar practice)

- Current: the rules require a source per relation, but only around one in a hundred legacy rows complies, checked by spot sampling.
- Target: a validator verifies that source pointers actually exist; failing rows are automatically marked pending and excluded from navigation. Page rewrites get a before/after citation count check — losing citations aborts the write. No full raw-conversation backlink store is built.
- Costs: code line pointers drift as code evolves and need a review trigger; backfilling provenance is a batch cost; overly strict validation can block curation, so a pending soft channel is required.

### G4 Graph expansion at recall: explicitly not adopted

E009 refuted it, #64 carries the corrected approach, and with provenance coverage near one percent, expansion would amplify bad relations. No experiment is opened here. Reconsider only after G3 raises relation quality and the #64 panel experiment reports.

### L1 A hard contract for the always-injected core block (from Letta)

- Current: the file-based entry has proven gains but more wrong adoptions; the hot tier is under heavy expansion pressure with a large gap to the slimming target and no enforcement mechanism.
- Target: character and entry caps per hot block plus a total navigation budget; "shrink before you grow" — when a block is full, first remove stale or code-derivable content and push detail to the warm tier behind a pointer. Every entry keeps an applicability scope, a difference of ours that we have validated and that Letta lacks. Admission still requires the two-part test (useful for future work and not derivable from code).
- Costs: caps are new hyperparameters and over-tightening loses rare but critical knowledge; added constraints have already shown a small negative signal on correctness, so both correctness and wrong adoptions must be watched; slimming depends on trustworthy demotion decisions, creating a dependency on G1.

### L2 Trigger-word index for cold memory (from Letta deferred memory)

- Current: demoted pages remain readable by ID but have no wording-friendly entry, so demotion is close to invisibility.
- Target: each demoted topic gets an index line written in the wording of a future question — two or three phrasings of when to read it back — rather than a content summary. Real replays have shown a systematic wording gap: the original phrasing misses while a rephrased query lands the target at rank one.
- Costs: trigger words are model-written and may introduce misleading entries; overly broad wording pulls cold content back into context and cancels slimming; gains also depend on the agent actually choosing to drill down.

### L3 Sinking provenance into version history (from Letta, as a compromise)

- Current: provenance stays in the page, which is trustworthy to inspect but lengthens the body.
- Target: keep only the shortest usable pointer in the page (verifiable without the version system) and move long evidence excerpts to a validated evidence sidecar; do not adopt the extreme of removing in-page provenance entirely, since scope and source information have been shown to block misuse at adoption time.
- Costs: conflicts with the current rule set and requires amending it; the extra read hop may hurt tasks with tight tool-step budgets; the completeness of the historical-version read path must be confirmed first.

### L4 Agent self-editing tools: borrow the shell, not the freedom

- Current: memory changes go through dual-model judging plus independent review; the agent has no direct write tool, and near-chance page-level kappa supports this conservatism.
- Target: borrow only two shells — string-level replace/insert proposal format instead of full-page rewrites (addressing the recurring faults of silently dropped sections and unintended neighbor edits), and soft-delete markers. Every self-edit enters the review queue and stays subject to the existing gates; no direct production writes.
- Costs: deepest engineering change, and offline work can validate proposal quality but not long-run behavior; the boundary with the nightly curation pipeline must be drawn carefully. Scheduled last.

## Offline experiments and preregistered decision rules

Common protocol: everything runs on our frozen internal offline eval set. The development split is for tuning and calibration; the frozen regression split runs exactly once at final validation after a candidate passes. Four primary metrics everywhere — answer page top-1/top-3, registered trap pages in top-3, correct next step, and wrong adoption — plus two cost metrics (tool steps, context volume). Same-question pairing, repeats kept intact per question, bootstrap intervals on paired differences. Decision rules are frozen in each experiment issue before running and never edited afterward. Sample sizes below are target ranges; the frozen roster after question selection is authoritative.

### G1 Programmatic dedup front stages (two stages)

- Stage A, curation quality (primary): run the two deterministic stages on the frozen entity snapshot against the existing dual-model baseline. Report recall on known same-object groups (baseline zero), precision of programmatic nominations after review, reduction in model judging volume, and whether kappa on the residual hard cases improves.
- Rules: Works if roughly three quarters or more of known same-object groups are recovered, nomination precision is at least ninety percent, and model judging volume falls by about forty percent. Does not work if recovery is at or below roughly one quarter, or precision below seventy-five percent. Anything else is Inconclusive.
- Stage B, retrieval non-regression (gate): project confirmed merges into a test library and compare affected-entity retrieval questions against the baseline snapshot on the same machine and retriever, targeting at least thirty questions (if fewer qualify, report the shortfall honestly). Passing requires no loss of top-3 hits and no increase in trap pages in the top three.
- Budget: the deterministic stages cost no model calls; model review is around a tenth of the original full-batch judging, with under a hundred retrieval calls. Cheapest of the set.

### G2 Structured supersession with hit-time notices (three arms)

- Arms: baseline; structured fields plus hit-time notice; same structure without the notice (to separate the contributions of fields and notices).
- Questions: knowledge-update and old-versus-new rule cases, including synthetic update questions, retrieval questions with registered traps, and behavior questions with stale-rule risk; targets of twenty to thirty retrieval and around twenty behavior questions.
- Rules: Works if trap pages in the top three fall by at least thirty percent relative and at least one question, while top-3 hits are non-inferior (interval bound above minus two points); behavior-arm wrong adoptions fall by at least twenty percent relative and at least one event, with the correctness interval including zero or positive. Does not work if traps rise or correctness clearly degrades. Too few judgeable wrong-adoption events (below single digits) means Inconclusive.
- Budget: medium-high, around a hundred behavior runs plus the one-time frozen-split validation. Another Inconclusive stops this direction — no third near-duplicate.

### G3 Provenance pointer validation (two layers)

- Layer one (tool validity): run the validator over all legacy relations and report existence pass rates for page pointers and code pointers separately; blind review on pilot relations gives a semantic pass rate ("does the pointer actually support this relation"). Below ninety percent semantic pass, the validator fails and layer two does not start.
- Layer two (behavior comparison): baseline library versus a validated library where sourceless relations are marked pending and rewrites carry verified pointers; target at least fifteen behavior questions (if short, merge with G1 stage B to share replay cost).
- Rules: the expected payoff is on the curation side, so layer two only needs to show no harm — non-inferior correctness (bound above minus five points) and no increase in wrong adoptions counts as Works. Higher wrong adoptions or clearly worse correctness is Does not work; insufficient questions is Inconclusive.
- Budget: low; the validator is free, review around ten batches, behavior replay around sixty runs.

### L1 Hot-tier hard contract (three arms)

- Calibration first (not scored): observe the size distribution of hot blocks actually read, then pick two or three candidate caps from measured quantiles rather than copying any external default.
- Arms: baseline; budget-capped; budget plus mandatory applicability scopes. All development behavior questions are the primary set, with retrieval questions touching demoted pages serving as a non-regression gate.
- Rules: Works if correctness is non-inferior (bound above minus three points — stricter than the generic gate because a small negative signal from scope fields was already observed), wrong adoptions fall by at least twenty percent relative and at least one event, and the actual hot-tier net reduction is reported. If correctness drops while wrong adoptions also drop with intervals covering zero, record Inconclusive.
- Budget: highest — hundreds of behavior runs across three arms and two repeats. Historical same-snapshot comparisons may partly serve as reference, but formal decisions use fresh same-snapshot replays. A reduced-question version is acceptable and is an explicit owner choice.

### L2 Trigger-word index (two arms)

- Question selection is targeted, not random: retrieval questions whose gold page sits outside or deep in the default search window, plus questions known to hit only after rephrasing; twenty to thirty retrieval and ten to fifteen behavior questions to observe actual drill-down.
- Rules: Works if top-3 on target questions improves by at least ten points relative (matching the #64 gain line), trap pages in the top three increase by at most two questions, behavior-arm cold-page read rate is at least sixty percent, and correctness is non-inferior. If retrieval works but agents almost never drill down (read rate below thirty percent), record Inconclusive: the writing rule may stay as a convention but claims no behavior benefit.
- Budget: low, around sixty behavior runs plus small model spot checks.

### L3 Short pointers plus evidence sidecars (three arms)

- Arms: full in-page provenance baseline; short pointers plus sidecar; the extreme of no in-page provenance at all (included to falsify full sinking — without running it, no conclusion is allowed). Questions requiring actual source-read receipts plus high-wrong-adoption questions; target at least twenty.
- Rules: only the compromise arm can achieve Works — non-inferior evidence-read rate, median tool-step increase at most one, no rise in wrong adoptions. A clear drop in read rate or exceeded step budget is Does not work; too few questions is Inconclusive.
- Prerequisite: confirm the historical-version and sidecar read paths exist; if not, drop the extreme arm and simulate the compromise with local files.
- Budget: medium, around a hundred twenty runs.

### L4 String-level change proposals (no production connection)

- The same curation task produces changes under two arms: full-page rewrites versus string-level proposals. Only curation-quality metrics: citation loss rate, undeclared neighbor-edit rate, mechanically applicable proposal rate, blind review pass rate. No eval-score runs.
- Rules: Works requires zero citation loss and zero neighbor edits with review pass rate no lower than baseline (hard gates, per an already recorded lesson). Any broken gate is Does not work; too few citation-bearing pages for a stable rate is Inconclusive. Even a Works result only concludes "the tool is worth building"; building and connecting it are separately approved steps.
- Budget: lowest; no behavior replay.

### G4

No experiment, for the reasons above; reconsideration is conditional on G3 passing and #64 reporting.

## Cost-effectiveness ranking and first batch

| Order | Adaptation | Evidence strength | Offline testability | Budget | Production intrusion | Batch |
| --- | --- | --- | --- | --- | --- | --- |
| 1 | G1 programmatic dedup front stages | Strong | High, deterministic plus frozen snapshot | Lowest | Low, nomination only | First |
| 2 | L1 hot-tier hard contract | Strong, positive and negative data already | High, existing replay framework reusable | Highest | Medium | First, calibration first |
| 3 | G3 provenance validation | Strong | High | Low | Medium | Second, shares G1 curation batch |
| 4 | L2 trigger-word index | Medium | High | Low | Low, writing convention | Second |
| 5 | G2 structured supersession | Medium, one prior Inconclusive | Medium, three-arm complexity | Medium-high | High | Third |
| 6 | L3 evidence sidecars | Medium, conflicts with current rules | Medium, depends on read-path check | Medium | High | Third |
| 7 | L4 proposal-format editing | Medium | Proposal quality only | Lowest | Highest | Last |
| — | G4 graph expansion | Refuted by E009 | — | — | — | Not adopted |

Only G1 and L1 are recommended for the first batch: they target different links ("written correctly" and "actually usable"), their conclusions do not depend on each other, and both can be judged with zero production change. G1 runs first because L1's slimming depends on trustworthy entity decisions, which G1 hardens.

Expectation management: even if every experiment passes, the gains concern structural quality and the small recall share of lost points. The two dominant loss categories — missing knowledge and incomplete execution — sit outside these mechanisms. Each experiment answers only for its own frozen metrics; no aggregate score improvement is promised.

## Phased timeline

| Phase | Work | Output | Owner decision |
| --- | --- | --- | --- |
| 0 Plan approval | This plan and tracking issue; Draft PR not merged | Bilingual plan, draft decision rules | First-batch scope, L1 budget size, whether to merge the PR |
| 1a First offline batch | G1 two stages plus L2 trigger words (small budget, no production dependency) | Funnel quality report, retrieval non-regression gate, drill-down observation | Whether to build a read-only curation tool if G1 passes |
| 1b Second offline batch | L1 three arms (calibration first) plus G3 validator, parallelizable | Hot-tier cap calibration, behavior replay results, validation pass rates | Final cap values, first demotion scope, whether the validator joins the check chain |
| 1c Third offline batch | G2 three arms, L3 three arms (read-path confirmation first); L4 proposal-quality experiment | One conclusion each, recorded as-is | Whether to enter rollout design |
| 2 Small-scope rollout | One change per mechanism, never bundled; single-workspace gray rollout with reversible batches | Gray-rollout readings and rollback records | Merge and enablement approved separately per change; default-off features document every enablement step |

Discipline: any Inconclusive stops that experiment and triggers diagnosis rather than rule-tuning or sample inflation. The frozen regression split runs exactly once per passing candidate.

## Steps

- [ ] #72 Review the adaptation list, experiment decision rules, and first-batch choice.
- [ ] Open one issue per experiment; freeze question rosters, arms, decision rules, and budgets before running.
- [ ] Run the first offline batch (programmatic dedup front stages, hot-tier contract) and record conclusions with denominators using the experiment template.
- [ ] Passing mechanisms each get their own small-scope rollout plan; failures and inconclusive results are recorded as-is without moving the decision lines.

## Owner decisions

1. Whether to start with G1 and L1, or reorder (for example, prioritizing structured supersession G2).
2. Whether G2 and L3, which touch page structure and amend current rules, are admitted into later batches.
3. Whether L1 runs at full scale or as a reduced-question version (budgets differ by nearly a factor of two).
4. Whether the Draft PR for this plan is approved for merge after review; per repo rules the author does not merge it.

## Deviations

None at the draft stage.

