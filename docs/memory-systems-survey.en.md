# Entity, relation, and expiry mechanisms in three open-source memory systems

[中文](memory-systems-survey.md) · English

Refs #70. This note reads three open-source codebases at pinned commits and answers four questions about each: (1) how entities are defined and deduplicated; (2) how relations are built and whether they carry provenance; (3) how fact expiry and supersession are represented; (4) cold/hot tiering and on-demand drill-down. Every claim cites a source file with line numbers (or an official doc link) and carries a confidence label: **confirmed** (directly visible in code), **inferred** (supported indirectly by several code paths), or **speculation** (no direct evidence).

| System | Snapshot | Approach |
| --- | --- | --- |
| Zep / Graphiti | [`9b8a463`](https://github.com/getzep/graphiti/commit/9b8a46300920) (2026-11-20) | Temporal knowledge graph |
| Letta | Classic V1 on the [`archive`](https://github.com/letta-ai/tree/archive) branch; current TS code in [`letta-ai/letta-code`](https://github.com/letta-ai/letta-code) [`76428c1`](https://github.com/letta-ai/letta-code/commit/76428c1b0ee7) (2026-11-21) | Tiered memory, agent self-editing |
| Memorax | [`89c7c04`](https://github.com/memorax-ai/memorax-code/commit/89c7c041dd56) (2026-11-12) | File-based coding memory plugin |

One prerequisite fact (**confirmed**): the `main` branch of the Letta repo now contains only a pointer README; the current source moved to `letta-ai/letta-code`, while the classic Python V1 (the MemGPT architecture) is preserved on the `archive` branch ([letta README](https://github.com/letta-ai/letta/blob/main/README.md)). Letta is therefore covered in two generations.

## At a glance

- **Graphiti**: every fact is an edge on a bi-temporal axis. When a fact changes, the old edge is invalidated, not deleted, and a new edge is written; an LLM extracts entities and edges and judges duplicates and contradictions. It has the most rigorous expiry model, at the cost of a graph database and LLM calls on every ingestion.
- **Letta**: core memory stays in context while other memory lives outside it; the agent pages and rewrites memory through its own tools. The new generation turns memory into a git-backed Markdown filesystem, with provenance moved into commit messages and only conclusions kept in the text. There is no explicit entity/relation layer.
- **Memorax**: no graph and no database. Facts are flat records with scope and provenance metadata, plus Markdown sidecar files, written back through hooks and injected under fixed quotas. Its entity governance is the weakest of the three, but its evidence chain and anti-deletion safeguards are the most engineered.

## 1. Zep / Graphiti: the temporal knowledge graph

### 1.1 Entity definition and deduplication

- An entity is an `EntityNode` graph node carrying only a name, a name embedding, a regional summary, and an attribute dict; there is no alias table (`graphiti_core/nodes.py:426-431`) [confirmed]. The base node's `created_at` is set to UTC now at construction, i.e. the transaction-time axis of "when the system knew this" (`nodes.py:98-103`) [confirmed].
- Entities are LLM-extracted from an episode (one message/document input): `extract_nodes` (`utils/maintenance/node_operations.py:76`) and the combined path `extract_nodes_and_edges` (`utils/maintenance/combined_extraction.py:58`) [confirmed].
- Deduplication is a three-stage funnel whose documented order is "identity rule, similarity rule, then LLM" (docstring of `resolve_nodes_with_candidates`, `node_operations.py:855-890`) [confirmed]:
  1. identity: exact matching on configured identity properties, with normalized identity keys (`dedup_helpers.py:207-236`);
  2. similarity: MinHash/LSH and Jaccard over normalized names, including a name-entropy guard against merging short generic names (`dedup_helpers.py:89-145`);
  3. LLM: only unresolved cases reach the model (`node_operations.py:677`, `_resolve_with_llm`).
- Merges keep the winning node and union non-empty attributes (`dedup_helpers.py:171-192`). There is no explicit alias mechanism; name normalization rests on string rules plus the LLM [inferred].

### 1.2 Relations and provenance

- A relation is an `EntityEdge`: one edge expresses one natural-language `fact` plus a relation `name` between two entity nodes, and carries its own fact embedding (`graphiti_core/edges.py:228-232`) [confirmed].
- **Provenance is a first-class field**: every edge holds `episodes: list[str]`, the ids of all episodes referencing it (`edges.py:233-236`). Edge resolution appends the current episode to that list without duplicates (`utils/maintenance/edge_operations.py:1076-1080`, `append_episode_provenance`) [confirmed].
- The episode node itself stores raw content, source description, and source type (`nodes.py:245-258`, `EpisodicNode`), so any fact edge can be traced back to the full original message [confirmed].
- Exact edge deduplication is also structural: the same endpoint pair plus the same normalized fact text is a duplicate, and a reverse-direction edge with the same name counts too (`edge_operations.py:666-694`) [confirmed].
- Semantic duplicate/contradiction decisions are LLM prompts that ask the two questions separately. DUPLICATE asks whether the existing fact already contains the same information; CONTRADICTION asks whether both facts cannot be true at once, explicitly noting that new progress about the same entities does not contradict a role or ownership fact (`llm_client/decision_prompts.py:150-211`) [confirmed].

### 1.3 Expiry and supersession

This is Graphiti's central design. **Four fields on two time axes** live on `EntityEdge` (`edges.py:236-259`) [confirmed]:

| Field | Meaning (from the field docstrings) |
| --- | --- |
| `valid_at` | When the fact became true; future-tense plans/promises use the episode reference time, not the future occurrence date |
| `invalid_at` | When the fact stopped being true; soft deadlines are not `invalid_at` |
| `expired_at` | When Graphiti marked the edge invalidated, explicitly labelled **transaction time**, with the hint to use `invalid_at` for when the fact itself stopped being true |
| `reference_time` | Reference timestamp from the episode that produced the edge |

- Invalidation means **rewriting timestamps, not deleting edges**. `resolve_edge_contradictions` sets an old edge contradicted by a new fact to `invalid_at = new edge's valid_at`, stamps `expired_at` with now, and collects it into the invalidated list (`edge_operations.py:795-831`) [confirmed].
- `_apply_temporal_invalidation` also handles the reverse case: when a candidate becomes valid later than the new edge, the new edge itself is expired, with candidates sorted by `valid_at` to find the superseding point (`edge_operations.py:762-793`) [confirmed].
- Physical delete methods exist (Cypher `DELETE`, `edges.py:57-67`), but the main fact-evolution path is invalidation. Incremental ingestion diffs field-level changes through a ChangeSet that explicitly tracks `invalid_at/expired_at` changes (`ingestion/change_set.py:261-266,308`) [confirmed].
- A counter-intuitive but verified point: **search does not exclude invalidated edges by default**. The temporal conditions on `SearchFilters` are all optional (`search/search_filters.py:120-213`), and queries select `invalid_at` alongside the edge (e.g. `search/search_utils.py:382`). Instead, the LLM-facing context states that "facts are considered valid between their valid_at and invalid_at dates" and that an `invalid_at` of "Present" means still valid (`search/search_helpers.py:53-57`), leaving point-in-time judgment to the caller [confirmed]. Callers that want only currently valid facts must pass their own time filters.

### 1.4 Tiering and drill-down

- Graphiti has **no storage tiering**: nodes, edges, and episodes all live in the graph database; there is no core/archival media split [confirmed].
- "Tiering" appears only in retrieval orchestration. Edges, nodes, and communities each support BM25 full-text and cosine semantic search (`search/search_config.py:33-50`); the default fusion/reranker is RRF (`search_config.py:54-82`), and the official hybrid recipe runs BM25+cosine over edges, nodes, and communities before RRF fusion (`search_config_recipes.py:33-50`), with MMR diversity reranking and a cross-encoder component available [confirmed].
- Drill-down is graph traversal rather than paging: node-centric BFS expansion (`center_node_uuid`/`bfs_origin_node_uuids` in `search.py:98-110`) and entity-name vector search (`search_utils.py:607-697`); each retrieval path defaults to a 10-result cap (`RELEVANT_SCHEMA_LIMIT`, `search_utils.py:64`) [confirmed].
- The write path: `Graphiti.add_episode` (`graphiti.py:1586`) takes an episode with a `reference_time`, extracts nodes/edges, runs the three-stage node resolution, then exact edge dedup, LLM duplicate/contradiction decisions, timestamp extraction, temporal invalidation of old edges, and persistence [confirmed for each stage; the end-to-end ordering is inferred from how the functions chain].
- Cost: a graph database driver (Neo4j and others under `graphiti_core/driver/`) plus multiple LLM calls per ingestion for extraction and contradiction decisions — its heaviest trade-off versus file-based designs [inferred].

## 2. Letta (MemGPT): tiered memory and agent self-editing

### 2.1 Entity definition and deduplication

- V1 has no standalone entity model. The smallest units are the **Block** (core memory section) and the **Passage** (archival paragraph). A Block is identified by a `label` (e.g. human/persona) inside the context and carries a character limit; see the fields at `letta/schemas/block.py:11-34` on the archive branch [confirmed].
- Dedup relies on unique labels: one block per label, and the `Memory` class explicitly dedupes file blocks by label, warning and dropping repeats (`letta/schemas/memory.py:74-92`) [confirmed].
- The new generation file-ifies blocks: only the `persona` and `human` labels remain by default (`letta-code/src/agent/memory.ts:16`, whose comment notes project blocks were removed in LET-7353). "One home per subject" is enforced by Skill prompt wording, not by the schema (`src/skills/builtin/maintaining-deferred-memory/SKILL.md`) [confirmed at the prompt level].
- In short, the Letta family offers no entity resolution or alias-deduplication data model; subject dedup is prompt engineering [inferred].

### 2.2 Relations and provenance

- There are no typed relation edges between blocks or passages. Passages carry `tags`, `file_id`, and `archive_id` attachment fields (archive `letta/schemas/passage.py:14-29`): grouping keys, not traversable edges [confirmed].
- The new generation makes provenance maximally explicit: **the memory text deliberately omits provenance, and provenance goes into git commit messages**. The core-memory Skill requires stripping names, dates, and quotes from the text and recording conversation ids, message ids, URLs, PRs, and commit hashes in the commit's `Sources:` section (Commit memory changes in `maintaining-core-memory/SKILL.md`) [confirmed].
- Subject hierarchy is expressed through directory trees and `MEMORY.md` index chains, and cross-subject links through relative Markdown links; there is no relation vocabulary [confirmed].

### 2.3 Expiry and supersession

- V1 core memory is **edited in place**: `core_memory_replace` does string replacement, and deletion means replacing with an empty string (archive `letta/functions/function_sets/base.py:246-281`). Old values are not versioned inside the memory layer; history exists only database-side via ORM metadata and `last_updated_by_id` (`block.py:60-62`) [confirmed].
- Archival passages use **soft delete**: an `is_deleted` boolean rather than physical removal (`passage.py:14`; read and written across `letta/services/passage_manager.py:175` and peers) [confirmed].
- Dedicated whole-block rewrite tools `rethink_memory`/`memory_rethink` consolidate outdated and contradictory information, with prompts explicitly asking for blocks free of stale content (`base.py:283-309`; `letta/prompts/system_prompts/sleeptime_doc_ingest.py`) [confirmed].
- The new generation delegates expiry to git: files are revised in place and history is naturally retained; multi-device sync conflicts have a dedicated lease-token-based repair worker (`letta-code/src/agent/memory-conflict-repair.ts:1-40`) [confirmed].
- Letta does not distinguish "when the fact was true" from "when the system recorded it" and has no invalidated-edge construct; git offers rollback but not point-in-time querying [inferred].

### 2.4 Tiering and drill-down

The classic V1 three tiers [confirmed]:

- **core**: blocks always rendered into the system prompt, with 20,000-character limits for persona/human and 100,000 for generic blocks (archive `letta/constants.py:433-435`).
- **recall**: the full conversation history, searched through `conversation_search` with hybrid text/semantic retrieval plus time-window and role filters (`base.py:87-163`).
- **archival**: embedding-backed passages in long-term storage, written and searched through `archival_memory_insert/search` with tags and time filters (`base.py:164-244`).

The paging mechanism (MemGPT's "OS virtual memory") [confirmed]: when tokens approach the window limit, a warning is injected telling the agent to save important information into core/archival first (`constants.py:414-421`); past the limit, a summarizer compresses old messages (`letta/agents/letta_agent.py:1576-1633`), and a sliding-window mode evicts a percentage of history (`letta/services/summarizer/self_summarizer.py:189-231`).

The new generation uses a two-level core/deferred filesystem [confirmed]:

- Root Markdown in core enters every system prompt, with default caps of 65,536 total characters, 20,000 per file, and directory depth 2, enforced by a pre-commit hook (fixture `src/memory-constraints.test.ts:208`).
- Deferred subdirectories appear in the prompt only as a path list; the agent must call the `memory()` tool to open them level by level, with path-traversal checks and per-file size limits (`src/tools/impl/memory.ts:348-427`).
- A directory is discoverable only when it has a `MEMORY.md` index, listings cap at ten entries, and discovery runs through the index chain (Layout/Write the indexes in the deferred-memory Skill) [confirmed].
- The main flow no longer has semantic vector retrieval; archival survives only in edge remnants (`src/cli/helpers/context-chart.ts:98`), and cold-data drill-down works through indexes plus file reads [confirmed].

## 3. Memorax: the file-based coding memory plugin

### 3.0 Product shape

A memory plugin for many coding clients, built as a thin local backend plus a hosted memory service. The local side handles hooks, redaction, buffering, and scope resolution; embedding, hybrid retrieval, RRF, and reranking all live in the remote service (`docs/configuration.md:932`, `src/provider/memorax/adapter.ts:316,324`) [confirmed]. Locally there are also two pure-file memory stores: repo-level `.repo_memory/` (Markdown plus JSON, gitignored by default) and user-level personal memory. No graph store or local vector database exists anywhere in the repo. The approach is **scope-isolated flat fact streams plus Markdown sidecar files** [confirmed].

### 3.1 Entity definition and deduplication

- There is no explicit entity/relation domain model; the first-class citizen is the fact record [confirmed].
- Remote records are bucketed by `memory_type`: core/episodic/semantic/procedural/unclassified (`src/provider/memorax/config.ts:19`; rendering at `adapter.ts:598-610`). Whether entity extraction exists at all is hidden inside the remote service and cannot be established from the open-source client [the absence of source is confirmed; remote behavior is speculation].
- The substitute for an entity is a scope identity: writes use the `user_id=<base>@<repository-or-folder>` namespace, and the local project id is a hash of the git root path, `repo:<32 hex chars>` (`src/memory/project.ts:24`, with the id shape validated at `:53-55`) [confirmed].
- All deduplication is exact/hash-level with no semantic merging, in three layers [confirmed]: (1) write idempotency through `idempotency_key`, buffer turn-key dedup, and content-hash pending lookup (`writeback-buffer.ts:170-177`; the pending cache is a five-minute TTL bounded map capped at 1024, `automatic-writeback.ts:127-128`); (2) user preferences count as duplicates only when description plus both scope fields match after Unicode normalization, with the comment "semantic merging belongs to the Skill" (`src/personal-memory/user-profile.ts:308-312`); (3) Repo Memory upserts PRs/issues by number and commits by SHA (`repo-memory/detect-updates.ts:361,559-570`).
- There is no alias or normalization vocabulary; the only normalization is path realpath and text case folding [confirmed].

### 3.2 Relations and provenance

- Records have no link/relation fields. The closest things — `heading_path`, scope, and session/group ids — are ownership or grouping keys, not traversable edges [confirmed].
- Provenance is the project's strongest area, on two tracks [confirmed]. First, remote writeback metadata is required to carry scope/workspace/session/branch/idempotency key, and business fields are forwarded through a whitelist (`adapter.ts:35-39,478-491`). Second, Repo Memory is an explicit evidence model: fetched facets already include url/state/evidence/author/sha/files (`repo-memory/github-resource-facets.ts:34-37`, `git-commit-facets.ts:116-143`); raw evidence lands in `.repo_memory/raw/*.json`, and agent-authored Markdown must declare source/trust_state/raw_source in frontmatter, with a validator requiring raw_source to point at an actually existing raw JSON file (`repo-memory/validate.ts:240-272`).
- Tooling deliberately does not generate memory content; it only prepares evidence, creates directories, and validates (`repo-memory/prepare.ts:95`), leaving authoring to the agent's Skill [confirmed].

### 3.3 Expiry and supersession

- The client exposes no memory TTL or invalidation API; every retention mechanism found concerns diagnostic logs and traces being physically purged as whole directories, not fact expiry [confirmed]. How the remote service retires facts is invisible [speculation].
- Local traces and events are append-only JSONL, never rewritten in place (`src/shared/jsonl-append.ts:6-21`) [confirmed].
- A notable half-built feature: the User Profile status enum declares active/superseded/deleted (`user-profile.ts:22`), yet no code path ever writes `superseded` — updates overwrite in place and deletes physically remove the entry, while the enum only survives in the parser whitelist for hand-edited or legacy files (`user-profile.ts:176,324-337`). **Supersession is declared but not implemented** [confirmed].
- Repo Memory follows "upsert plus never delete by default": incremental output is added/updated/baseline_only and `delete_numbers` is always empty, because a bounded provider window cannot prove that an older resource was deleted (`detect-updates.ts:705-721`); when rebases break the commit baseline, it abandons incremental mode and demands a full rebuild [confirmed].
- Session-level supersede exists but only governs turn lifecycle: interrupted, rolled-back, or superseded turns are not written back, unrelated to long-term facts (`turn-coordinator.ts:78,162`) [confirmed].

### 3.4 Tiering and drill-down

Four tiers with a clear local/remote split [confirmed]: a single global user preference file (64 KB cap, `user-profile.ts:23`) plus procedure docs (hot); repo-local `.repo_memory` (warm); the hosted fact service (primary store); and append-only JSONL traces (cold).

- Injection has hard quotas: defaults of top_k=6, dense/sparse 6 each, a 4000-character context budget, and 1000 characters per item, all overridable by environment variables (`provider/memorax/config.ts:144-152`); results are bucketed by type into an XML fragment and truncated as a whole (`adapter.ts:597-618`) [confirmed].
- Two real drill-down channels [confirmed]: (1) document mode fetches original chunks precisely by document ids (1–100), with heading and source spans, truncated in the text view but complete in JSON output (`adapter.ts:257-270,621-656`); (2) search reminders run on a rhythm — by default on turns 1, 6, and 11 (`docs/configuration.md:1162-1166`) — with an optional semantic judge deciding per turn whether a search is worth it (`search-guidance.ts:115-134`).
- The write side is also buffered in tiers: non-code content flushes after eight turns / 128 KB / ten idle minutes, while code content goes through 8 KB chunks (`writeback-buffer.ts:157-158,225-233`, `writeback-chunk.ts`) [confirmed].
- There is no unified "read a historical version by id" interface; whether an old remote fact is recallable depends entirely on server-side ranking, and the client cannot force a historical read [inferred].

## 4. Cross-system comparison

| Dimension | Graphiti | Letta V1 / new generation | Memorax |
| --- | --- | --- | --- |
| Entity model | EntityNode with three-stage dedup (identity property, name similarity, LLM) | No entity model; unique block labels / "one subject one file" by prompt | No entity model; scope namespace as identity, exact-key dedup |
| Relations | Typed edges, one fact per edge, episodes field links source provenance | No typed relations; tags, directory hierarchy, Markdown links | No relation fields; ownership keys and document heading paths only |
| Provenance | Mandatory edge-to-episode links, traceable to raw text | Partial ownership fields in V1; new generation forces sources into git commits | Raw evidence files plus frontmatter raw_source validation; most engineered |
| Expiry | Bi-temporal (valid/invalid for facts, expired/created for the system), edges invalidated not deleted | In-place rewrite; passage soft delete; new generation relies on git history, no temporal query | Three-state status declares superseded but never writes it; evidence baseline never deleted by default |
| Contradiction handling | Programmatic temporal rules plus LLM duplicate/contradiction prompts | Prompt-only instruction to resolve contradictions; no mechanism guarantee | None; semantic merging explicitly "belongs to the Skill" |
| Tiering | No media tiering, everything in the graph; retrieval via BM25/vector/RRF/BFS | V1 three tiers plus paging warnings; new core/deferred files with level-by-level indexes | Four tiers (preferences/repo/remote/trace) plus character injection quotas |
| Drill-down | BFS graph traversal, entity search, point-in-time queries | Tool paging / directory index walk | Precise chunk fetch by document id; periodic search reminders |
| Main cost | Graph database plus multiple LLM calls per ingestion | Governance rests on prompts; consistency at scale is uncertain | Relation reasoning fully depends on LLM reading; core intelligence sits in a black-box service |

## 5. Lessons for entity-relation memory rules

Mechanism-level comparison only.

### 5.1 Designs isomorphic to an "entity-relation plus timeline plus provenance" rule set

1. **"Keep superseded statements, mark what replaced them" is isomorphic to Graphiti edge invalidation.** Moving a statement to a timeline with a replacement marker corresponds to an invalidated edge with `invalid_at`; the difference is that Graphiti keeps two clocks (fact expiry versus system processing time), while a single effective-time concept is the norm in simpler rules.
2. **"Every relation must carry a source" is isomorphic to the mandatory provenance in two systems.** Graphiti enforces it through the edge episodes field and Memorax through a frontmatter validator — both make provenance a schema or checker requirement rather than author discipline.
3. **"Remove from default search but keep readable by id" is isomorphic to the tiering in Letta and Memorax.** Deferred directories and remote/trace stores both default out of context and are fetched precisely through indexes when needed.

### 5.2 Mechanisms worth borrowing, with their costs

1. **Bi-temporal fields (from Graphiti)**: record both when a fact stopped being true and when the system processed it. Cost: two extra fields per fact plus timestamp extraction in the write path. Benefit: point-in-time queries answering "what did the system believe at time T", impossible with a single timeline.
2. **Three-stage dedup funnel (from Graphiti)**: deterministic rules first, similarity second, LLM last. A dual-model independent judgment effectively starts at the most expensive stage; the first two stages can remove obvious same-name/alias cases programmatically. The cost is maintaining normalization rules and similarity thresholds, including entropy guards for short names.
3. **Separating provenance from the body (from new Letta)**: keep current conclusions in the page and push events, quotes, and links into version history. In-page provenance is more directly auditable but lengthens the body; separation makes the body unreadable outside the version system.
4. **Evidence sidecars with mandatory validation (from Memorax)**: store raw evidence in separate files, reference them from the body, and validate that every pointer exists. The cost is an extra layer of file maintenance; the benefit is preventing citations to nonexistent evidence.
5. **Index entries written in the wording of future requests (from Letta's Skill)**: each cold-area index line says when to open it, rather than summarizing contents. Near-zero cost, directly targeting the "cold area is effectively lost" failure mode.

### 5.3 Parts not worth copying

1. **A full temporal graph database is too heavy**: graph operations and multiple extraction LLM calls per write suit high-frequency streaming facts, not low-frequency document-page team memory.
2. **Letta's free agent self-editing of core memory should not be delegated wholesale**: consistency rests entirely on prompts with no schema-level relation or provenance enforcement; dual-model judgment, review queues, and a closed relation vocabulary exist precisely to avoid that laissez-faire behavior.
3. **Memorax's "no local entity relations, intelligence in the hosted service" does not transfer**: it assumes a hosted service and accepts a black box; the value of rule-based governance lies in a locally auditable entity/relation layer, and abandoning it means abandoning the object being governed.
4. **"Never delete by default because a bounded window cannot prove deletion" needs caution**: it prevents mistakes but inflates the default search pool. Removing pages from default search without physically deleting them already obtains the same safety while preserving retrieval precision, so adding never-retire on top is unnecessary.

## Appendix: gaps and assumptions

- All three codebases are fixed snapshots; later upstream changes are out of scope.
- Graphiti's MCP server and service wrappers were read only at the interface level; core analysis is limited to `graphiti_core`.
- Letta V1 multi-agent shared blocks were confirmed only at the field level; no end-to-end flow was run.
- Memorax's server-side entity extraction, merging, and retirement logic is not in the open-source repository, so no definitive claims are made about it.
