# Agent 记忆系统精读

2026-11-29 · 上游实现固定到所链接提交。论文分数来自作者的协议，本轮只做静态阅读。实验编号链接到本 Lab 的小样本证据。[综合分析](../essays/07-typed-memory.md)

## 1. OpenAI Codex

- **机制与位置**。Phase 1 每次领取会话任务并提取经验，无输出仍可成功。Phase 2 先同步入选产物，再按旧基线算 Git diff，输入无变化且产物校验通过就跳过整理。SQLite 用最近使用或来源更新时间决定保留，再用使用次数和最近使用排整理批次。读取有短摘要及本地行级字面搜索，返回片段按路径和行号排序。 [抽取](https://github.com/openai/codex/blob/065e18b04021008e/codex-rs/memories/write/src/phase1.rs#L54) · [整理](https://github.com/openai/codex/blob/065e18b04021008e/codex-rs/memories/write/src/phase2.rs#L125) · [保留 SQL](https://github.com/openai/codex/blob/065e18b04021008e/codex-rs/state/src/runtime/memories.rs#L446) · [摘要](https://github.com/openai/codex/blob/065e18b04021008e/codex-rs/ext/memories/src/prompts.rs#L31) · [搜索](https://github.com/openai/codex/blob/065e18b04021008e/codex-rs/ext/memories/src/local/search.rs#L52)
- **差异与用法**。本地经验优化会话启动与回读。团队页还要维护共享版本和范围。借成功基线、无信号跳过和正文窗，分别对照 [E037](../experiments/E037-nightly-curation-readback/README.md)、[E048](../experiments/E048-ingest-gate-evidence/README.md) 和 [E046](../experiments/E046-generated-preview-pilot/README.md)。使用次数适合作为整理预算信号，规范有效性仍靠出处和取代证据。

## 2. Anthropic Claude

- **机制与位置**。API memory tool 将文件操作分派给客户端。Python 参考后端的替换要求旧文本唯一命中，以临时文件原子换入。Claude Code 的 auto memory 用短入口索引引导按需读文件。研究文章另展示后台 dreaming 回看 transcript 校错、补 wiki 断链与少量预注入。 [SDK 分派](https://github.com/anthropics/anthropic-sdk-python/blob/f1edcd7d751a4cd6/src/anthropic/lib/tools/_beta_builtin_memory_tool.py#L103) · [原子写](https://github.com/anthropics/anthropic-sdk-python/blob/f1edcd7d751a4cd6/src/anthropic/lib/tools/_beta_builtin_memory_tool.py#L283) · [唯一命中](https://github.com/anthropics/anthropic-sdk-python/blob/f1edcd7d751a4cd6/src/anthropic/lib/tools/_beta_builtin_memory_tool.py#L507) · [研究案例](https://www.anthropic.com/research/components-of-agent-memory)
- **差异与用法**。文件操作提供持久读写。团队记忆还需证据权限和多人共同维护。让整理先回源，再按预期版本补问法或范围，对照 [E037](../experiments/E037-nightly-curation-readback/README.md)、[E038](../experiments/E038-targeted-content-repair/README.md)、[E048](../experiments/E048-ingest-gate-evidence/README.md)。原子替换只防部分写，共享事实仍需审阅；文章任务跑分无法估算团队检索增益。

## 3. Hindsight

- **机制与位置**。Retain 将文档拆成事实，解析实体并建立事实链接。Consolidation 维护事实支撑的 observations。Recall 并行跑语义、词法、图和明确约束下的时间路，融合后可重排。图传播起点是事实，限制单实体扇出，共享实体加分做饱和处理。 [方法 §4](https://arxiv.org/html/2512.12818v1#S4) · [ACL 基准](https://aclanthology.org/2026.acl-demo.27/) · [落库](https://github.com/vectorize-io/hindsight/blob/c828c7e41527d0c4/hindsight-api-slim/hindsight_api/engine/retain/orchestrator.py#L891) · [实体解析](https://github.com/vectorize-io/hindsight/blob/c828c7e41527d0c4/hindsight-api-slim/hindsight_api/engine/retain/entity_processing.py#L157) · [图扩展](https://github.com/vectorize-io/hindsight/blob/c828c7e41527d0c4/hindsight-api-slim/hindsight_api/engine/memories/pg/link_expansion.py#L118) · [并行检索](https://github.com/vectorize-io/hindsight/blob/c828c7e41527d0c4/hindsight-api-slim/hindsight_api/engine/search/retrieval.py#L192) · [融合](https://github.com/vectorize-io/hindsight/blob/c828c7e41527d0c4/hindsight-api-slim/hindsight_api/engine/search/fusion.py#L112)
- **差异与用法**。短事实可连接事件和时间，我们的候选是页，共挂叶只表达组织归属。保留 [E032](../experiments/E032-keyword-fusion-live/README.md) 的词法＋向量对照。依据 [E019](../experiments/E019-graph-recall-revalidation/README.md) 和 [E049](../experiments/E049-entity-index-two-stage/README.md)，把同池证据组合和明确日期单测。论文结果同时受 reader、候选粒度及 token 预算影响。整体复刻四路会混合这些效应。

## 4. Mem0 OSS

- **机制与位置**。论文 §2 描述事实抽取后选择增、改、删或跳过，另有图变体。固定提交的普通增量写使用近邻上下文和文本哈希，显式更新另记历史。论文 §4.3 的长上下文对照还有更高的判官分，换来较高时延。同步向量检索过量取语义候选，在其 ID 上融合 BM25 和实体分数，结合有效期和阈值过滤；词法独有项进不了这条函数的候选。 [论文方法](https://arxiv.org/html/2504.19413v1#S2) · [质量与时延 §4.3](https://arxiv.org/html/2504.19413v1#S4.SS3) · [增量写](https://github.com/mem0ai/mem0/blob/cae3d8cda8943786/mem0/memory/main.py#L881) · [候选构造](https://github.com/mem0ai/mem0/blob/cae3d8cda8943786/mem0/memory/main.py#L1680) · [显式更新](https://github.com/mem0ai/mem0/blob/cae3d8cda8943786/mem0/memory/main.py#L2052)
- **差异与用法**。其小粒度增量维护及 ID 对齐可借给池内匹配，对照 [E045](../experiments/E045-entity-structure-ranking/README.md)。保留 [E032](../experiments/E032-keyword-fusion-live/README.md) 中能独立补召回的词法路。哈希可识别原文重复，同一事实的改写或范围冲突需要另判。

## 5. Letta / MemGPT

- **机制与位置**。MemGPT 将工作上下文与外部存储分层，让 agent 用工具查归档和改核心块。论文用深历史召回和嵌套键查找检验主动换入上下文。归档 V1 可按 tag、时间查 passages；当前 Letta Code 的 memfs 维护 Markdown 树与 Git checkout，区分系统内存路径和按需浏览材料。 [论文上下文](https://arxiv.org/html/2310.08560v2#S2) · [论文实验](https://arxiv.org/html/2310.08560v2#S3) · [归档工具](https://github.com/letta-ai/letta/blob/56ba9c25552605ee/letta/functions/function_sets/base.py#L192) · [当前 checkout](https://github.com/letta-ai/letta-code/blob/120685984d8f132a/src/agent/memory-filesystem.ts#L219) · [树渲染](https://github.com/letta-ai/letta-code/blob/120685984d8f132a/src/agent/memory-filesystem.ts#L252)
- **差异与用法**。核心索引解决每轮容量问题，团队页要能下钻验证适用范围。用短实体卡指向出处，与 [E041](../experiments/E041-memory-use-guidance/README.md)、[E046](../experiments/E046-generated-preview-pilot/README.md) 对照回读和采纳。Git 历史帮助定位改动，事实生效须另记。

## 6. Zep / Graphiti

- **机制与位置**。独立保存原 episode，解析实体并抽带方向和谓词的事实边。相同端点和规范事实可快速去重，疑似冲突另行核对。按有效时间关闭旧边，保留历史和来源。边检索可混合词法、语义和种子 BFS，并按配置重排、过滤时间。作者的 LongMemEval 对照取事实边及节点，主要与全上下文比较。 [论文构建](https://arxiv.org/html/2501.13956v1#S2) · [论文实验](https://arxiv.org/html/2501.13956v1#S4) · [边解析与去重](https://github.com/getzep/graphiti/blob/343a7bb1fa950946/graphiti_core/utils/maintenance/edge_operations.py#L429) · [关闭区间](https://github.com/getzep/graphiti/blob/343a7bb1fa950946/graphiti_core/utils/maintenance/edge_operations.py#L762) · [检索](https://github.com/getzep/graphiti/blob/343a7bb1fa950946/graphiti_core/search/search.py#L259) · [过滤器](https://github.com/getzep/graphiti/blob/343a7bb1fa950946/graphiti_core/search/search_filters.py#L55)
- **差异与用法**。它核对某条关系的成立区间和出处。我们已有页取代 [E040](../experiments/E040-cross-category-supersession/README.md)，可给可变事实补范围和时间，再测当前、历史、时间未知三类。[E050](../experiments/E050-targeted-event-boost-after-cooling/README.md) 的泛事件抬权未覆盖明确时间查询。父子和普通出链保留导航含义。

## 7. LangMem

- **机制与位置**。热路径在指定 namespace 管理增删改。后台 MemoryStoreManager 查旧记忆，通过稳定 ID 应用整理结果，公开工厂默认关闭后台删除。多搜索根据会话生成查询，以 namespace 和 key 聚合，实际检索能力取决于注入的 store。 [管理工具](https://github.com/langchain-ai/langmem/blob/4beb9c36a40953f0/src/langmem/knowledge/tools.py#L271) · [多搜索](https://github.com/langchain-ai/langmem/blob/4beb9c36a40953f0/src/langmem/knowledge/extraction.py#L695) · [旧条目查找](https://github.com/langchain-ai/langmem/blob/4beb9c36a40953f0/src/langmem/knowledge/extraction.py#L937) · [工厂](https://github.com/langchain-ai/langmem/blob/4beb9c36a40953f0/src/langmem/knowledge/extraction.py#L1666)
- **差异与用法**。团队共享页已有准入与出处。借按问项检索，先用冻结人工拆分在同池选证据。保留 [E024](../experiments/E024-content-gap-write-guard/README.md)、[E048](../experiments/E048-ingest-gate-evidence/README.md) 的准入对照，后台整理建议先审阅再应用。

## 8. A-MEM

- **机制与位置**。写 note 时提取关键词、标签、语境，用语义邻居让模型判断连边与演进。检索从 Chroma 先取最多 k 个种子，再追加至多 k 个去重邻居。论文 §4.4 在会话问答上消融连边和演进。 [论文方法](https://arxiv.org/html/2502.12110v11#S3) · [消融](https://arxiv.org/html/2502.12110v11#S4.SS4) · [写入](https://github.com/agiresearch/A-mem/blob/ceffb860f0712bba/agentic_memory/memory_system.py#L233) · [邻居检索](https://github.com/agiresearch/A-mem/blob/ceffb860f0712bba/agentic_memory/memory_system.py#L509) · [演进](https://github.com/agiresearch/A-mem/blob/ceffb860f0712bba/agentic_memory/memory_system.py#L590)
- **差异与用法**。note 邻接解决分散线索查找。我们已有出链重排 [E047](../experiments/E047-outgoing-link-live/README.md)，以它作对照，固定五槽单测已核证的互补关系是否补齐证据、是否挤掉准确结果；生成的邻接先作待核线索。

## 9. Cognee

- **机制与位置**。从 chunk 抽图，按节点 ID、有向端点和标签去重。cognify 维护来源投影。检索从命中节点和边对局部三元组打分。子问路径允许逐问消费结果或合并三元组后回答。 [抽取](https://github.com/topoteretes/cognee/blob/dbc515bdcde72691/cognee/tasks/graph/extract_graph_from_data_v2.py#L18) · [去重](https://github.com/topoteretes/cognee/blob/dbc515bdcde72691/cognee/modules/graph/utils/deduplicate_nodes_and_edges.py#L4) · [投影](https://github.com/topoteretes/cognee/blob/dbc515bdcde72691/cognee/api/v1/cognify/cognify.py#L1107) · [三元组](https://github.com/topoteretes/cognee/blob/dbc515bdcde72691/cognee/modules/retrieval/utils/brute_force_triplet_search.py#L128) · [子问](https://github.com/topoteretes/cognee/blob/dbc515bdcde72691/cognee/modules/retrieval/graph_completion_decomposition_retriever.py#L135)
- **差异与用法**。它提供 chunk 级可检索结构，我们已有页投影和链接。借用子问证据合并与投影重建，分别对照 [E049](../experiments/E049-entity-index-two-stage/README.md) 和 [E035](../experiments/E035-stale-projection-cleanup/README.md)。结构去重只解结构重复，矛盾、过期与权限仍要由源记录判断。

## 10. WorldDB

- **机制与证据**。嵌套 world 节点用内容寻址连接。写时依次用精确名、模糊、音形、向量等信号解析，疑似同一身份可提案，确认后才进同一身份视图。事实有效时间与系统获知时间分别可查。作者在 LongMemEval-S 报 96.4%。迭代同时改 reader、摘要和 k；同 reader 消融同时关闭事实抽取、实体解析和引用边，差值反映这一组机制的贡献。 [数据模型 §2](https://arxiv.org/html/2604.18478v1#S2) · [写时协调 §3](https://arxiv.org/html/2604.18478v1#S3) · [结果与消融 §7](https://arxiv.org/html/2604.18478v1#S7)
- **差异与用法**。我们的归叶定位文档，跨类取代落在页上。借写时身份确认、待审和双时间，先测同名与版本变化，以 [E044](../experiments/E044-leaf-coverage-live/README.md)、[E048](../experiments/E048-ingest-gate-evidence/README.md)、[E040](../experiments/E040-cross-category-supersession/README.md) 为对照。内容寻址存储和通用模糊合并需独立论证。

## 11. OntoKG

- **机制与证据**。声明式 gate 用可信类型值匹配类别。内在模块选择标量属性，关系模块产出有方向及限定符的边。未归类和未激活模块分别进入下一轮修订。Wikidata 验分类覆盖并审 NER 标签。BLINK 消歧对照固定共同候选，实验改的是实体画像。20 个以上候选的优势基于很小的分组。 [方法 §3](https://arxiv.org/html/2604.02618v1#S3) · [分类 §4](https://arxiv.org/html/2604.02618v1#S4) · [类型 gate](https://github.com/Prorata-ai/OntoKG/blob/c2906a4281d4388c/src/rust/src/loader.rs#L91) · [声明分桶](https://github.com/Prorata-ai/OntoKG/blob/c2906a4281d4388c/src/rust/src/bin/classify_dump.rs#L695) · [节点与边导出](https://github.com/Prorata-ai/OntoKG/blob/c2906a4281d4388c/src/rust/src/bin/export_neo4j.rs#L548) · [消歧 §5.3](https://arxiv.org/html/2604.02618v1#S5.SS3)
- **差异与用法**。叶节点先服务导航，页类型不能说明引用对象是什么。用少数实体类型和内在字段做固定候选消歧，保留未知，关系与导航边分开。对照 [E044](../experiments/E044-leaf-coverage-live/README.md)、[E045](../experiments/E045-entity-structure-ranking/README.md)。Wikidata 已有类型值，团队自然语言来源需要验证字段覆盖和抽取噪声。

## 12. EnSIMem

- **机制与证据**。划分主题连贯 episode 并保留原文，写入类型、实体及属性索引。查询拆为原子证据要求，依据点查、时间、复合或聚合决定证据配额，最后回 episode 读上下文。LongMemEval 两个判官均为 92.8%；LoCoMo 固定设置消融段落粒度、属性粒度、结构与稠密匹配及固定／自适应预算。论文指出在线规划延迟。 [方法 §3](https://arxiv.org/html/2609.27279v2#S3) · [消融 §4](https://arxiv.org/html/2609.27279v2#S4) · [限制 §5](https://arxiv.org/html/2609.27279v2#S5)
- **差异与用法**。[E031](../experiments/E031-governance-retrieval-recheck/README.md) 的叶名锚定提升未传到下游。先用冻结问项、同版正文窗口和固定五槽量证据找齐。属性只有能明确消歧时才加入；在线模型规划和全量 episode 化各需验证成本。

## 13. Graph-Based Personalized Memory for LLM Agents

- **机制与证据**。综述拆开事实、关系与证据表示，及准入、整合、冲突、巩固、移除。区分随时间变化、纠正错误、不同范围并存。图检索可由相似性锚定，再结构扩展和预算控制。§VI 比较会话、状态更新、偏好和行动等评测目标，未跑统一实验臂。 [表示 §III](https://arxiv.org/html/2609.08599v1#S3) · [演进 §IV](https://arxiv.org/html/2609.08599v1#S4) · [评测 §VI](https://arxiv.org/html/2609.08599v1#S6)
- **差异与用法**。共享技术约束和个人偏好适用范围不同。用三类冲突各做用例，对照 [E040](../experiments/E040-cross-category-supersession/README.md)、[E042](../experiments/E042-workaround-scope-review/README.md)，按被误取代的有效证据计错。选图形状前先确认所需的证据关系。

## 14. MemForest v4

- **机制与证据**。独立抽事实，再规范化和放置，按 dirty 节点及受影响祖先刷新视图。事实与可重建视图分开，发布需要核验刷新。代码提供根摘要向下、事实近邻反查树及两路并集。§8.4 同事实底座的视图对照增加构建成本，点查和固定预算下总体差未显著。反向召回对短根摘要更稳。 [写入与查询 §4–7](https://arxiv.org/html/2605.23986v4#S4) · [查询消融 §8.4](https://arxiv.org/html/2605.23986v4#S8.SS4) · [刷新](https://github.com/Concyclics/MemForest/blob/864fbdf20d304816/src/build/tree_builder.py#L347) · [两向召回](https://github.com/Concyclics/MemForest/blob/864fbdf20d304816/src/query/retriever.py#L69)
- **差异与用法**。[E049](../experiments/E049-entity-index-two-stage/README.md) 测了先找实体再找页。可在独立导航面板测正文证据反查实体，再按对象、范围回到原文。在 [E037](../experiments/E037-nightly-curation-readback/README.md) 基础上检查局部刷新与重建，不引入主榜扩池。

## 15. Engineering Reliable Coding Agents

- **机制与证据**。第 15 章建议保持可重建源记录、按已观察的查找失败补索引，并以实际压缩失误确定该保留的约束、工具证据和决策。专著把检索基础设施的工程建议标为方向性证据，压缩相关受控证据来自其他任务类型。 [证据分级](https://arxiv.org/html/2608.13867v1#Chx2.Sx3.SSx3) · [第 15 章](https://arxiv.org/html/2608.13867v1#Ch15)
- **差异与用法**。我们已有 [E032](../experiments/E032-keyword-fusion-live/README.md) 向量＋词法基线，[E046](../experiments/E046-generated-preview-pilot/README.md) 观察到压缩降低注入量。用可逐页回退的证据补丁，把真实使用和找齐分开量。可逆性只证明能安全恢复。

## 16. Memory in the Age of AI Agents

- **机制与证据**。综述按形式、功能、动态组织系统，把事实与工作记忆的功能分类和形成、演进、取回的生命周期交叉。§5.3.4 分开重排过滤与聚合压缩，§6 按任务覆盖归纳基准。没有统一 reader 和预算的效果对比。 [分类 §3–4](https://arxiv.org/html/2512.13564v2#S3) · [动态 §5](https://arxiv.org/html/2512.13564v2#S5) · [评测 §6](https://arxiv.org/html/2512.13564v2#S6)
- **差异与用法**。用该分类给实验设可归因阶段。维护 [E037](../experiments/E037-nightly-curation-readback/README.md)、找齐 [E032](../experiments/E032-keyword-fusion-live/README.md)、展示 [E046](../experiments/E046-generated-preview-pilot/README.md)、调用动作 [E041](../experiments/E041-memory-use-guidance/README.md) 分开。跨论文成绩用于理解不同协议。

## 阅读后落点

先做[同池证据重排和定点补内容](../plans/team-memory-quality/m2-findability.md)。[实体类型与写入绑定](../plans/team-memory-quality/m4-structure.md) 先测消歧、出处、范围及导航。取代、冷藏与投影更新沿用现有[整理计划](../plans/team-memory-quality/m3-consolidation.md)。

## 补充阅读

### REALM

把召回轨迹中的证据聚合反馈用于局部边调整，更新幅度受置信度和上下界约束。论文 §4 消融检索与重整组件，仍是在作者整套图表示上测。对照 [E047](../experiments/E047-outgoing-link-live/README.md)，可把反复误召回的关系列为审阅候选。实际召回频率只能定位问题，事实正确性仍由出处决定。 [方法 §3](https://arxiv.org/html/2609.16053#S3) · [实验 §4](https://arxiv.org/html/2609.16053#S4)

### agentmemory

技术标识的前缀评分原会累加多个扩展词。修复后每个查询词只取最强前缀命中；已精确命中不再加前缀分。作者在检查过的清洗版数据上比较相同协议的修前、修后和 grep，属于开发集结果。对照 [E032](../experiments/E032-keyword-fusion-live/README.md)，先用短前缀和同名不同范围的合成反例守住词法精确性，只有观察到池外缺证据才试一个字面槽。 [前缀打分](https://github.com/rohitg00/agentmemory/blob/949bbfa5623f9885/src/state/search-index.ts#L230) · [可复查的作者记录](https://github.com/rohitg00/agentmemory/blob/949bbfa5623f9885/docs/benchmarks/2026-10-09-evaluation-baseline.md#L47)

### MGMem

把提及对原 episode 的关联做成索引。以主语解歧，先精确候选，再看邻域及全局候选，最终返回源 episode。作者 §4 同时检查问答、episode 取回和出处。我们的实体叶连到文档而非原始 mention，可在 [E049](../experiments/E049-entity-index-two-stage/README.md) 后用审核过的别名和固定候选测试端点消歧，避免把共同提及写成事实边。 [论文方法与实验](https://arxiv.org/html/2611.33174#S3) · [解析](https://github.com/junhong-h/MGMem/blob/67c53a283f553c82/src/mgmem/retrieval/resolver.py#L52) · [回传原证据](https://github.com/junhong-h/MGMem/blob/67c53a283f553c82/src/mgmem/retrieval/standard.py#L33)

### AgentMemRec

把取候选、学习排序、有限上下文的组装拆开，使用组内证据找齐衡量最后一段。作者在 LongMemEval 的特征消融显示 turn 上下文特征贡献明显。我们以页为单位，沿 [E049](../experiments/E049-entity-index-two-stage/README.md) 固定候选，先用问项覆盖替代单页打分的贪心选法，再决定是否需要训练排序。 [组装 §4](https://arxiv.org/html/2610.34673v1#S4) · [结果 §6](https://arxiv.org/html/2610.34673v1#S6)

### SoMem

把可核验来源与可编辑主题文档分层，运行时从文档派生关系、时间线和最近视图。事务校验版本；论文在固定 LoCoMo 记忆和 reader 下做读取组件消融。对照 [E037](../experiments/E037-nightly-curation-readback/README.md) 和 [E035](../experiments/E035-stale-projection-cleanup/README.md)，可验证重建和回滚时源证据仍可回读。生成的派生链接仍需验证是否真的支持事实。 [方法 §2](https://arxiv.org/html/2611.11929#S2) · [实验 §3](https://arxiv.org/html/2611.11929#S3) · [事务](https://github.com/Qi202/SoMem/blob/8846a91616e55c38/code/src/management/transaction.py#L81) · [派生视图](https://github.com/Qi202/SoMem/blob/8846a91616e55c38/code/src/runtime/derived_views.py#L78)

### BRIDGE

自然边界切块、词法与余弦召回，再按时间呈现摘要和少量原文。作者还测了在任务中应用规则或归纳做法，发现同一表示的相对表现随任务改变。对照 [E041](../experiments/E041-memory-use-guidance/README.md) 和 [E046](../experiments/E046-generated-preview-pilot/README.md)，复用相同取回结果分测引用证据与执行约束，保留简单召回基线，避免用问答准确率代替编码任务结果。 [方法 §2](https://arxiv.org/html/2611.22179v1#S2) · [应用探针 §4.2](https://arxiv.org/html/2611.22179v1#S4.SS2)

### LongMemEval

原版为问题标支持会话，分别评价问答与检索；源码区分 recall-any、recall-all 和 nDCG，turn 级结果还可折叠到 session 再计分。该折叠会改变分母和预算，不能直接拿来和我们的五页槽比较。以 [E019](../experiments/E019-graph-recall-revalidation/README.md)、[E049](../experiments/E049-entity-index-two-stage/README.md) 为起点，另列候选上界和实际读到的整组证据，并保留时间、更新和应弃答案例。V2 的轨迹及任务结果用于后续使用层设计。 [评测 §3](https://arxiv.org/html/2410.10813#S3) · [计分](https://github.com/xiaowu0162/LongMemEval/blob/9e0b455f4ef0e2ab/src/retrieval/eval_utils.py#L24) · [V2 协议](https://github.com/xiaowu0162/LongMemEval-V2/blob/2cc8c540bdb87fe6/README.md)
