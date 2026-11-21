# 三个开源记忆系统的实体、关系与过期机制调研

[English](memory-systems-survey.en.md) · 中文

Refs #70。本文读三份开源代码的固定快照，回答四个问题：①实体怎么定、怎么去重；②关系怎么建、有没有出处；③事实过期/被取代怎么表示；④冷热分层和按需下钻。每条结论附源码文件与行号（或官方文档链接），并标注置信度：**确定**（源码直接证实）、**推断**（多处代码间接支持）、**猜测**（无直接证据）。

| 系统 | 快照 | 路线 |
| --- | --- | --- |
| Zep / Graphiti | [`9b8a463`](https://github.com/getzep/graphiti/commit/9b8a46300920)（2026-11-20） | 时序知识图谱 |
| Letta | 经典 V1 在 [`archive`](https://github.com/letta-ai/letta/tree/archive) 分支；新版 TS 在 [`letta-ai/letta-code`](https://github.com/letta-ai/letta-code) [`76428c1`](https://github.com/letta-ai/letta-code/commit/76428c1b0ee7)（2026-11-21） | 分层记忆、Agent 自编辑 |
| Memorax | [`89c7c04`](https://github.com/memorax-ai/memorax-code/commit/89c7c041dd56)（2026-11-12） | 文件型编码记忆插件 |

一个前置事实（**确定**）：Letta 主仓 `main` 已只剩说明文件，README 写明当前源码迁到 `letta-ai/letta-code`，经典 Python V1（MemGPT 架构）保留在 `archive` 分支（[letta README](https://github.com/letta-ai/letta/blob/main/README.md)）。因此 Letta 分两代讲。

## 一句话总览

- **Graphiti**：每个事实是一条带双时间轴的边，事实变化时旧边失效而非删除，再写新边；实体和边由 LLM 从消息抽取并做矛盾/重复判定。过期表达最严谨，代价是图库与 LLM 抽取成本。
- **Letta**：核心记忆常驻上下文、其他记忆在外存，Agent 自己调工具换页和改写；新版进一步变成 git 管理的 Markdown 记忆文件系统，出处放提交信息、正文只留结论。没有显式实体/关系层。
- **Memorax**：不建图库，把事实写成带 scope 与出处元数据的扁平条目和 Markdown 侧车文件，靠 hook 自动写回、按配额注入；实体治理最弱，但证据链和误删防护工程化程度高。

## 一、Zep / Graphiti：时序知识图谱

### 1.1 实体怎么定、怎么去重

- 实体是图节点 `EntityNode`，字段只有名称、名称向量、区域摘要和属性字典，没有别名表：`graphiti_core/nodes.py:426-431`【确定】。节点基类的 `created_at` 在创建时写当前 UTC 时间，即「系统何时知道」的事务时间轴：`nodes.py:98-103`【确定】。
- 实体由 LLM 从 episode（一次消息/文档输入）抽取，入口 `extract_nodes`（`utils/maintenance/node_operations.py:76`）与合并抽取 `extract_nodes_and_edges`（`utils/maintenance/combined_extraction.py:58`）【确定】。
- 去重是三级漏斗，注释写明顺序为「identity rule, similarity rule, then LLM」（`node_operations.py:855-857` 与 `resolve_nodes_with_candidates` 函数 docstring，`:882-890`）【确定】：
  1. identity：配置的身份属性精确匹配（`dedup_helpers.py:207-236` 的 identity key 归一化）；
  2. similarity：名称归一化后做 MinHash/LSH 与 Jaccard 相似度（`dedup_helpers.py:89-145`，含名称熵值过滤，避免短名误并）；
  3. LLM：前两级判不了才交模型裁决（`node_operations.py:677 _resolve_with_llm`）。
- 合并时保留胜出节点、合并非空属性（`dedup_helpers.py:171-192`）。没有显式别名机制，同名归一依赖字符串规则与 LLM【推断】。

### 1.2 关系怎么建、有没有出处

- 关系是 `EntityEdge`，一条边就是一句自然语言事实 `fact` 加关系名 `name`，连接两个实体节点；边自带 fact 向量（`graphiti_core/edges.py:228-232`）【确定】。
- **出处回链是一等字段**：每条边带 `episodes: list[str]`，记录引用这条边的所有 episode id（`edges.py:233-236`）；解析新边时把当前 episode 追加进出处列表，已存在则不重复（`utils/maintenance/edge_operations.py:1076-1080` `append_episode_provenance`）【确定】。
- episode 节点本身保存原始内容、来源描述与来源类型（`nodes.py:245-258` `EpisodicNode`），因此可以从任意事实边回溯到原始消息全文【确定】。
- 边也有精确去重：同一对端点加归一化后相同事实文本即判重，反向边同名也算重复（`edge_operations.py:666-694`）【确定】。
- 语义级的重复与矛盾由 LLM 判定，提示词把两类问题分开问：DUPLICATE 问「是否已包含同样信息」，CONTRADICTION 问「两者是否不可能同时为真」，并明确「新进展不构成对角色/归属事实的矛盾」（`llm_client/decision_prompts.py:150-211`）【确定】。

### 1.3 事实过期 / 被取代怎么表示

这是 Graphiti 最核心的设计，**双时间轴四字段**都在 `EntityEdge` 上（`edges.py:236-259`）【确定】：

| 字段 | 语义（字段 docstring 原文要点） |
| --- | --- |
| `valid_at` | 事实何时开始为真；将来时的计划/承诺用 episode 参考时间而非未来发生日 |
| `invalid_at` | 事实何时停止为真；软截止日期不算 invalid_at |
| `expired_at` | Graphiti 何时把这条边标记失效，docstring 明确标注是 **transaction time**，并提示「用 invalid_at 查事实何时停止为真」 |
| `reference_time` | 产生该边的 episode 参考时间戳 |

- 失效是**改时间戳而非删边**。矛盾解决函数 `resolve_edge_contradictions` 把被新事实否定的旧边的 `invalid_at` 设为新边的 `valid_at`、`expired_at` 设为当前时刻，并收入失效列表（`edge_operations.py:795-831`）【确定】。
- `_apply_temporal_invalidation` 还处理反向情形：若候选边比新边更晚生效，则让新边自己失效，并按 `valid_at` 排序找取代点（`edge_operations.py:762-793`）【确定】。
- 物理删除接口虽然存在（`edges.py:57-67` 的 Cypher `DELETE`），但事实演进主路径走失效；增量摄入用 ChangeSet 记录字段级变化，`invalid_at/expired_at` 的变更被显式 diff（`ingestion/change_set.py:261-266,308`）【确定】。
- 一个反直觉但已核实的点：**检索默认并不排除失效边**。`SearchFilters` 的时间条件全是可选过滤（`search/search_filters.py:120-213`），查询会把 `invalid_at` 一起选出（如 `search/search_utils.py:382`）；框架改在给 LLM 的上下文里说明「事实在 valid_at 与 invalid_at 之间有效，invalid_at 为 Present 即仍有效」（`search/search_helpers.py:53-57`），把时序判断交给调用方【确定】。要只取当前有效事实，需要调用方自己传时间过滤。

### 1.4 冷热分层和按需下钻

- Graphiti **没有存储分层**：节点、边、episode 全部在图数据库里，不存在 core/archival 式的冷热介质区别【确定】。
- 「分层」只体现在检索编排：边、节点、社区各自支持 BM25 全文与 cosine 语义两种方法（`search/search_config.py:33-50`），默认融合/重排器是 RRF（`search_config.py:54-82`），官方 hybrid recipe 对边、节点、社区同时跑 BM25+cosine 再 RRF 融合（`search_config_recipes.py:33-50`），另有 MMR 多样性重排与 cross-encoder rerank 组件【确定】。
- 下钻靠图遍历而非分页：支持以节点为中心的 BFS 扩展（`search.py:98-110` 的 `center_node_uuid`/`bfs_origin_node_uuids` 参数）与实体名向量检索（`search_utils.py:607-697`）；每路结果默认上限 10 条（`RELEVANT_SCHEMA_LIMIT`，`search_utils.py:64`）【确定】。
- 写入主流程：`Graphiti.add_episode`（`graphiti.py:1586`）接收带 `reference_time` 的 episode → 抽取节点/边 → 节点三级 resolve → 边的精确去重、LLM 重复/矛盾判定、时间戳抽取 → 时序失效旧边 → 落图库【确定，由上述各函数串联推断整体流程】。
- 成本面：依赖图数据库驱动（Neo4j 等，见 `graphiti_core/driver/`），每次摄入都要多次 LLM 调用做抽取与矛盾判定，这是它相对文件型方案最重的代价【推断】。

## 二、Letta（MemGPT）：分层记忆与 Agent 自编辑

### 2.1 实体怎么定、怎么去重

- V1 没有独立实体模型，最小单位是 **Block**（核心记忆块）与 **Passage**（档案段落）。Block 以 `label`（如 human/persona）标识上下文里的段名并带字符上限，字段见 `letta/schemas/block.py:11-34`（archive 分支）【确定】。
- 去重靠 label 唯一：同一 label 只有一个块；`Memory` 类对 file_blocks 显式按 label 去重，重复即告警丢弃，见 `letta/schemas/memory.py:74-92`【确定】。
- 新版把 Block 文件化，默认只剩 `persona`、`human` 两个标签块（`letta-code/src/agent/memory.ts:16`，注释说明项目级块在 LET-7353 移除）；「一个主题一个家」靠 Skill 提示词约束而非 schema 强制（`src/skills/builtin/maintaining-deferred-memory/SKILL.md`）【确定（提示词层面）】。
- 即 Letta 体系没有实体归一/别名消解的数据模型能力，主题去重是提示词工程【推断】。

### 2.2 关系怎么建、有没有出处

- Block/Passage 之间没有类型化关系边；Passage 带 `tags`、`file_id`、`archive_id` 等归属字段（archive `letta/schemas/passage.py:14-29`），是挂接/标签而非可遍历的边【确定】。
- 新版把出处做到最明确：**记忆正文刻意不写出处，出处进 git 提交信息**。core-memory Skill 要求正文去掉人名、日期、原话，由 commit 的 `Sources:` 段记录会话 ID、消息 ID、URL、PR、commit hash（`maintaining-core-memory/SKILL.md` 的 Commit memory changes 节）【确定】。
- 主题层级用目录树与 `MEMORY.md` 索引链表达，跨主题关联用 Markdown 相对链接；没有关系词表【确定】。

### 2.3 事实过期 / 被取代怎么表示

- V1 核心记忆是**就地改写**：`core_memory_replace` 做字符串替换，删除即把新内容置空（archive `letta/functions/function_sets/base.py:246-281`）；旧值不在记忆层保留版本，历史只在数据库侧（Block 带 ORM 元数据与 `last_updated_by_id`，`block.py:60-62`）【确定】。
- 档案 Passage 用**软删除**：`is_deleted` 布尔标记而非物理删（`passage.py:14`，`letta/services/passage_manager.py:175` 等处读写）【确定】。
- 有整块重写工具 `rethink_memory`/`memory_rethink`，提示词要求整合掉过时与矛盾信息（`base.py:283-309`、`letta/prompts/system_prompts/sleeptime_doc_ingest.py`）【确定】。
- 新版把过期处理交给 git：文件就地修订，历史由 git 保留；多端同步冲突有带租约 token 的专门修复模块（`letta-code/src/agent/memory-conflict-repair.ts:1-40`）【确定】。
- Letta 不区分「事实生效时间」与「系统记录时间」，也没有失效边；git 提供回溯但不提供时序查询【推断】。

### 2.4 冷热分层和按需下钻

V1 经典三层【确定】：

- **core**：常驻系统提示的 Block，persona/human 各 20000 字符、通用块 100000 字符上限（archive `letta/constants.py:433-435`）。
- **recall**：完整对话历史，`conversation_search` 做文本+语义混合检索，支持时间窗与角色过滤（`base.py:87-163`）。
- **archival**：带 embedding 的 Passage 长期库，`archival_memory_insert/search` 语义检索，支持 tags 与时间过滤（`base.py:164-244`）。

换页机制（MemGPT 的「OS 虚拟内存」）【确定】：token 接近窗口上限时注入告警，要求 Agent 先把重要信息存入 core/archival（`constants.py:414-421`）；超限后 summarizer 压缩旧消息（`letta/agents/letta_agent.py:1576-1633`），滑动窗口按百分比驱逐（`letta/services/summarizer/self_summarizer.py:189-231`）。

新版改为 core + deferred 两级文件系统【确定】：

- core 根目录 Markdown 每次进系统提示，总字符默认上限 65536、单文件 20000、目录深度 2，由 pre-commit hook 强制（测试夹具 `src/memory-constraints.test.ts:208`）。
- deferred 子目录在系统提示里只出现路径清单，Agent 必须主动调 `memory()` 工具逐级打开；工具做路径越界校验与单文件大小限制（`src/tools/impl/memory.ts:348-427`）。
- 每个目录必须有 `MEMORY.md` 索引才会被发现，目录列表最多 10 条，靠索引链逐层引导（deferred-memory SKILL 的 Layout/Write the indexes 节）【确定】。
- 新版主流程已无语义向量检索，archival 概念只剩边角残留（`src/cli/helpers/context-chart.ts:98`），冷数据下钻靠索引加文件读取【确定】。

## 三、Memorax：文件型编码记忆插件

### 3.0 产品形态

多编码客户端的记忆插件，架构是「瘦本地 Backend + 托管记忆服务」：本地负责 hook 接入、脱敏、缓冲、scope 解析；embedding、混合检索、RRF、rerank 全部在远端服务（`docs/configuration.md:935-936`、`src/provider/memorax/adapter.ts:316,324`）【确定】。本地另有仓库级 `.repo_memory/`（Markdown+JSON，默认 gitignore）与用户级 personal-memory 两类纯文件记忆。全仓无语义图库或本地向量库，路线是**作用域隔离的扁平事实流加 Markdown 侧车文件**【确定】。

### 3.1 实体怎么定、怎么去重

- 没有显式 entity/relation 领域模型，一等公民是事实条目【确定】。
- 远端条目按 `memory_type` 分桶：core/episodic/semantic/procedural/unclassified（`src/provider/memorax/config.ts:19`，渲染见 `adapter.ts:598-610`）；是否存在实体抽取在黑盒远端，开源代码无法证实【确定（源码缺失）；远端行为只能猜测】。
- 「实体」的替代品是 scope 身份：写入用 `user_id=<base>@<repository-or-folder>` 命名空间，本地项目身份是 git root 路径哈希 `repo:<32hex>`（`src/memory/project.ts:24,53-55`）【确定】。
- 去重全是精确/哈希级、无语义合并，共三层【确定】：① 写入幂等，`idempotency_key` 加 buffer 去重加内容哈希查 pending（`writeback-buffer.ts:170-177,328-331`，pending 为 5 分钟 TTL、上限 1024，`automatic-writeback.ts:127-128`）；② 用户偏好需 description 加两个 scope 字段归一化全等才判重，注释明说「semantic merging belongs to the Skill」（`src/personal-memory/user-profile.ts:308-312`）；③ Repo Memory 按 PR/issue 编号、commit SHA 做 upsert（`repo-memory/detect-updates.ts:559-570,361-385`）。
- 没有别名/归一化词表，唯一归一是路径 realpath 与文本 case folding【确定】。

### 3.2 关系怎么建、有没有出处

- 条目之间没有 link/relation 字段；最接近关系的 heading_path、scope、session/group id 都是归属或分组键，不是可遍历的边【确定】。
- 出处是该项目最实的部分，分两路【确定】：① 远端 writeback 的 metadata 强制带 scope/workspace/session/branch/idempotency_key，业务字段白名单转发（`adapter.ts:35-39,478-491`）；② Repo Memory 是显式证据模型，facet 拉取即含 url/state/evidence/author/sha/files（`repo-memory/github-resource-facets.ts:34-37`、`git-commit-facets.ts:116-143`），原始证据落 `.repo_memory/raw/*.json`，Agent 撰写的 Markdown 必须在 frontmatter 写 source/trust_state/raw_source，校验器强制 raw_source 指向真实存在的原始 JSON（`repo-memory/validate.ts:240-272`）。
- 工具刻意不生成记忆内容，只备证据、建目录、做校验（`repo-memory/prepare.ts:95`），撰写责任留给 Agent 的 Skill【确定】。

### 3.3 事实过期 / 被取代怎么表示

- 客户端没有任何记忆 TTL/失效 API；retention 相关逻辑只针对诊断日志与 trace 的整目录物理清理，不是事实失效【确定】。远端如何淘汰事实不可见【猜测】。
- 本地 trace/事件是 append-only JSONL，只追加不改写（`src/shared/jsonl-append.ts:6-21`）【确定】。
- 一个半成品值得记录：User Profile 的 status 枚举声明了 active/superseded/deleted 三态（`user-profile.ts:22`），但没有任何代码路径写入 superseded——update 原地覆盖、delete 物理移除，三态仅在解析白名单兼容手工或旧文件（`user-profile.ts:176,183,324-337`）。**取代语义声明了但未落地**【确定】。
- Repo Memory 奉行「upsert 加永不默认删除」：增量输出 added/updated/baseline_only，`delete_numbers` 恒为空，理由是有界 provider 窗口无法证明旧资源被删（`detect-updates.ts:711-721`）；rebase 破坏 commit 基线时放弃增量、要求全量 rebuild【确定】。
- 会话层的 supersede 只管 turn 生命周期，被回滚或中断的 turn 不写回，与长期事实无关（`turn-coordinator.ts:78,162`）【确定】。

### 3.4 冷热分层和按需下钻

四层，本地与远端职责分明【确定】：用户全局单文件偏好（64KB 上限，`user-profile.ts:23`）与流程目录（热）；仓库本地 `.repo_memory`（温）；托管事实服务（主存）；append-only JSONL trace（冷）。

- 注入有硬配额：默认 top_k=6、dense/sparse 各 6、上下文预算 4000 字符、单条 1000 字符，均可由环境变量调（`provider/memorax/config.ts:144-152`），结果按类型分桶包进 XML 片段整体截断（`adapter.ts:597-618`）【确定】。
- 下钻两条通道【确定】：① document 模式按 document_ids（1–100 个）精确取原始 chunk，带 heading 与 source_spans，文本视图截断而 JSON 保留全量（`adapter.ts:257-270,621-656`）；② 检索提醒节奏，默认首轮后每 5 轮提醒一次主动搜索（`docs/configuration.md:1162-1166`），另有可选语义判官逐轮判断是否值得搜（`search-guidance.ts:115-134`）。
- 写入侧同样分层缓冲：非代码内容按 8 turn/128KB/10 分钟 idle 聚合 flush，代码内容走 8KB 分片（`writeback-buffer.ts:157-158,225-233`、`writeback-chunk.ts`）【确定】。
- 没有统一的「冷区按 ID 读历史版本」接口，远端旧事实能否召回由服务端排序决定，客户端无法强制读历史版本【推断】。

## 四、横向对比

| 维度 | Graphiti | Letta V1 / 新版 | Memorax |
| --- | --- | --- | --- |
| 实体模型 | EntityNode，三级去重（身份属性→名称相似度→LLM） | 无实体模型；Block label 唯一 / 新版「一主题一文件」靠提示词 | 无实体模型；scope 命名空间即身份，精确键去重 |
| 关系 | 类型化边，一条边一句事实，episodes 字段回链原始出处 | 无类型化关系；标签/目录层级/Markdown 链接 | 无关系字段；只有归属键与文档 heading 路径 |
| 出处 | 边级强制回链 episode，可追到原始全文 | V1 部分归属字段；新版出处强制进 git commit 的 Sources | raw 证据文件 + frontmatter 强制 raw_source 校验，工程化最强 |
| 过期表达 | 双时间轴（valid/invalid 对事实，expired/created 对系统），旧边失效不删 | 就地改写；Passage 软删；新版靠 git 历史，无时序查询 | 三态 status 声明了 superseded 但未实现；证据基线「永不默认删除」 |
| 矛盾消解 | 程序时序规则 + LLM 重复/矛盾双问 | 提示词要求改写时消矛盾，无机制保证 | 不做；语义合并明确「belongs to the Skill」 |
| 冷热分层 | 无介质分层，全部在图库；检索靠 BM25/向量/RRF/BFS | V1 三层 + 换页告警；新版 core/deferred 文件 + 逐级索引 | 四层（偏好/仓库/远端/trace）+ 注入字符配额 |
| 下钻方式 | 图遍历 BFS、实体检索、时间点查询 | 工具调页 / 目录索引逐层打开 | document id 精确取 chunk；周期性检索提醒 |
| 主要代价 | 图库 + 每次摄入多次 LLM 调用 | 治理靠提示词，规模大后一致性存疑 | 关系推理完全依赖 LLM 阅读，核心智能在黑盒服务端 |

## 五、对实体—关系化记忆规则的启发

只做机制层面的抽象对照。

### 5.1 与「实体—关系 + 时间线 + 出处」规则同构的设计（可互相印证）

1. **「旧说法不删除、标注被谁取代」与 Graphiti 边失效同构**。规则里的「移到时间线、标注被哪页取代」对应 Graphiti 的失效边加 `invalid_at`；差异是 Graphiti 还区分事实失效时间与系统处理时间两个时钟，规则目前只有一个生效时间概念。
2. **「每条关系必须带来源」与两套系统的强制出处同构**。Graphiti 用边的 episodes 字段、Memorax 用 frontmatter 的 raw_source 校验，都把出处做成 schema 或校验器强制，而不是写作者自觉。
3. **「移出默认搜索但可按 ID 读回」与 Letta/Memorax 的冷热分层同构**。Letta 新版的 deferred 目录、Memorax 的远端事实与本地 trace，都是「默认不进上下文、需要时按索引精确取」。

### 5.2 值得借鉴的机制（含代价）

1. **双时间轴字段（借鉴 Graphiti）**：给被取代的事实同时记「事实何时失效」与「系统何时处理」。代价是每条边多两个时间字段、写入链路要做时间戳抽取；收益是可以做时间点查询，回答「某时刻系统当时相信什么」，这是单时间线做不到的。
2. **去重三级漏斗（借鉴 Graphiti）**：先确定性规则（身份属性/精确键），再相似度，最后才花 LLM 调用。规则草案目前的「双模型独立判定」相当于直接走最贵的第三级；前两级可以用程序拦掉大部分明显同名/别名。代价是要维护归一化规则和相似度阈值，短名称误并需要额外熵值门槛。
3. **出处与正文分离（借鉴 Letta 新版）**：正文只留现行结论，事件、原话、链接下沉到版本记录。规则现行做法是出处留在页内，可信度更直观但正文会变长；分离的代价是离开版本系统就读不到上下文。
4. **证据侧车与强制校验（借鉴 Memorax）**：原始证据单独落文件、正文用指针引用、校验器验证指针真实存在。代价是多一层文件维护；收益是防止「引用了不存在的证据」。
5. **索引入口用「未来请求的措辞」写（借鉴 Letta 新版 SKILL）**：冷区索引的每一行写成什么场景该打开它，而不是写内容摘要。代价极低，直接针对「冷区等于丢失」的失败模式。

### 5.3 不适合照搬的部分（含理由）

1. **完整时序图库不适合直接引入**：图库运维和每次写入的多次 LLM 抽取成本，对以文档页为单位、写入频率低的团队记忆是过重的；Graphiti 解决的是高频流式事实更新，场景不同。
2. **Letta 的「Agent 自由自编辑核心记忆」不适合直接放权**：其一致性全靠提示词约束，没有 schema 级关系与出处强制；规则草案的双模型判定、待核队列、关系词表收口正是为了避免这种自由放任。
3. **Memorax 的「不做本地实体关系、智能全推服务端」不适合**：其前提是存在托管记忆服务且接受黑盒；规则治理的价值恰恰在本地可审计的实体与关系层，放弃这层等于放弃治理对象。
4. **Memorax 的「有界窗口无法证明删除就永不默认删」要谨慎借鉴**：它防止误删，但会让默认搜索池持续膨胀；规则草案用「移出默认搜索而非物理删除」已经取得类似安全性，同时保住了检索精度，不必再叠加永不淘汰。

## 附：未覆盖项与假设

- 三份代码均为固定时点快照，上游之后的变更不在范围。
- Graphiti 的 MCP server 与服务化封装只做接口级了解，核心分析限于 `graphiti_core`。
- Letta V1 多 Agent 共享 Block 只做字段级确认，未跑通流程。
- Memorax 托管服务端的实体抽取、合并与淘汰逻辑不在其开源仓库内，相关行为不下确定结论。
