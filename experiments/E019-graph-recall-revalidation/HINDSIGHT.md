# Hindsight 图检索源码笔记

范围是 [Hindsight `937886199e0e`](https://github.com/vectorize-io/hindsight/commit/937886199e0e) 的 PostgreSQL 记忆单元召回（`retain` → `recall`）。下列链接指向这一版本。Hindsight 的文档级 Pages 搜索是另一个入口，有自己的稠密与全文融合。 [Pages 文档](https://github.com/vectorize-io/hindsight/blob/937886199e0e/hindsight-docs/docs/developer/pages.mdx#L52-L67)

## 写入与实体身份

1. Retain 按块用模型提取事实、实体名、事件时间、有限的事实因果关系。事实入库时保留文档和块的关联。实体名从事实取出，做清洗、规范化和批量消歧，再写入事实与实体的多对多表 `unit_entities`。消歧在 memory bank 内找同名及近名候选。PostgreSQL 用名称索引和 trigram 候选，近名须先过 trigram 与词兼容门槛，再用名称相似度、和邻近实体的共现、最近见到的时间消歧。没有达标候选时建立实体。 [事实提取结构和提示](https://github.com/vectorize-io/hindsight/blob/937886199e0e/hindsight-api-slim/hindsight_api/engine/retain/fact_extraction.py#L1348-L1382) · [名称清洗与收集](https://github.com/vectorize-io/hindsight/blob/937886199e0e/hindsight-api-slim/hindsight_api/engine/retain/entity_processing.py#L57-L137) · [候选查询](https://github.com/vectorize-io/hindsight/blob/937886199e0e/hindsight-api-slim/hindsight_api/engine/memories/pg/entity_resolver.py#L830-L929) · [候选打分与创建](https://github.com/vectorize-io/hindsight/blob/937886199e0e/hindsight-api-slim/hindsight_api/engine/memories/pg/entity_resolver.py#L1319-L1383) · [落库关联](https://github.com/vectorize-io/hindsight/blob/937886199e0e/hindsight-api-slim/hindsight_api/engine/retain/orchestrator.py#L928-L983)
2. 同一事实里的实体对积累共现统计，供后续实体消歧。召回里的「实体共现边」指两个记忆单元共享实体，从 `unit_entities` 自连接即时计算。显式物化的 `entity` links 服务图形展示；默认召回直接使用关联表。 [共现统计写入](https://github.com/vectorize-io/hindsight/blob/937886199e0e/hindsight-api-slim/hindsight_api/engine/memories/pg/entity_resolver.py#L1635-L1693) · [召回 SQL](https://github.com/vectorize-io/hindsight/blob/937886199e0e/hindsight-api-slim/hindsight_api/engine/db/ops_postgresql.py#L1070-L1110) · [物化用途](https://github.com/vectorize-io/hindsight/blob/937886199e0e/hindsight-api-slim/hindsight_api/engine/retain/orchestrator.py#L974-L976)

## 链接、入口与遍历

| 信号 | 写入时的依据 | PostgreSQL 召回 |
| --- | --- | --- |
| 共享实体 | 事实携带的实体提及，经归一和消歧 | 默认图路按共享实体数计分，把计数经 `tanh(count × 0.5)` 压到 0–1。每个实体限制展开量，默认 200。 |
| 语义 | 新事实与同批或存量记忆的向量近邻，余弦阈值和数量受限 | 默认图路沿已存语义边双向找候选，取相似度权重。 |
| 因果 | 提取时的事实关系及批内事实索引，新写入使用 `caused_by`，导入还可恢复旧类型 `causes`、`enables`、`prevents` | 默认图路和时间路都可以利用因果链接。 |
| 时间 | 相同 bank 和事实类型的近时间事件，默认窗口 24 小时，越近权重越高 | 解析出时间范围时由独立时间路使用。先取满足时间及语义条件的入口，再沿时间和因果边做带衰减的有界 BFS。 |
| 归纳观察的来源 | Observation 保留支持它的源事实 ID | 观察类图召回还可通过源事实和实体关联抵达观察。 |

[语义近邻计算](https://github.com/vectorize-io/hindsight/blob/937886199e0e/hindsight-api-slim/hindsight_api/engine/memories/pg/links.py#L570-L655) · [同批语义边](https://github.com/vectorize-io/hindsight/blob/937886199e0e/hindsight-api-slim/hindsight_api/engine/memories/pg/links.py#L752-L850) · [因果写入与恢复](https://github.com/vectorize-io/hindsight/blob/937886199e0e/hindsight-api-slim/hindsight_api/engine/memories/pg/links.py#L935-L1045) · [时间边](https://github.com/vectorize-io/hindsight/blob/937886199e0e/hindsight-api-slim/hindsight_api/engine/memories/pg/links.py#L446-L545) · [观察展开](https://github.com/vectorize-io/hindsight/blob/937886199e0e/hindsight-api-slim/hindsight_api/engine/memories/pg/link_expansion.py#L373-L444)

默认图实现为 `link_expansion`。每个事实类型先从向量池取至多 20 个超过阈值的事实单元，默认阈值 0.30。SQL 池能覆盖图路阈值时复用候选，否则图路独立做向量种子查询。实体一侧走「种子事实 → 共享实体 → 邻居事实」，另一侧直接沿语义和因果链接展开。Python 将各信号的分数相加，截成一份独立的图路排名。实体展开超时可退回语义和因果。这是有界邻接扩展。多轮、带衰减的传播在时间路中，受节点预算、语义阈值、访问集合和最多五轮等约束。 [默认配置](https://github.com/vectorize-io/hindsight/blob/937886199e0e/hindsight-api-slim/hindsight_api/config.py#L1939-L1946) · [种子数量](https://github.com/vectorize-io/hindsight/blob/937886199e0e/hindsight-api-slim/hindsight_api/engine/memories/base.py#L834-L844) · [相似度阈值](https://github.com/vectorize-io/hindsight/blob/937886199e0e/hindsight-api-slim/hindsight_api/config.py#L1557-L1566) · [默认图路种子与计分](https://github.com/vectorize-io/hindsight/blob/937886199e0e/hindsight-api-slim/hindsight_api/engine/memories/pg/link_expansion.py#L166-L276) · [超时分支](https://github.com/vectorize-io/hindsight/blob/937886199e0e/hindsight-api-slim/hindsight_api/engine/memories/pg/link_expansion.py#L326-L365) · [时间路入口与有界传播](https://github.com/vectorize-io/hindsight/blob/937886199e0e/hindsight-api-slim/hindsight_api/engine/memories/pg/recall.py#L451-L515) · [时间路衰减与截断](https://github.com/vectorize-io/hindsight/blob/937886199e0e/hindsight-api-slim/hindsight_api/engine/memories/pg/recall.py#L529-L694)

## 融合与重排

稠密路按向量余弦取候选。关键词路由后端的文本搜索实现，PG 将它与稠密路放进同一批 SQL，回传独立排名。图路以事实类型并发执行。识别到时间约束时才纳入时间候选。候选按 ID 去重，默认用 RRF，分数为每路 `1/(60 + 名次)` 的和，图路的激活值只决定其在这一路的名次。可显式选择 round-robin interleave，例如合并重复观察的召回。 [稠密与关键词 SQL](https://github.com/vectorize-io/hindsight/blob/937886199e0e/hindsight-api-slim/hindsight_api/engine/memories/pg/recall.py#L164-L222) · [PostgreSQL 各路调度](https://github.com/vectorize-io/hindsight/blob/937886199e0e/hindsight-api-slim/hindsight_api/engine/memories/postgres.py#L185-L255) · [RRF](https://github.com/vectorize-io/hindsight/blob/937886199e0e/hindsight-api-slim/hindsight_api/engine/search/fusion.py#L29-L109) · [融合入口](https://github.com/vectorize-io/hindsight/blob/937886199e0e/hindsight-api-slim/hindsight_api/engine/memory_engine.py#L10820-L10859)

默认正常召回会在融合后按候选预算截断、补齐文本，再用交叉编码器直接给查询和候选文本配对打分。普通交叉编码器分支按归一化重排分乘以时效、时间匹配与证据数量系数形成最终分。决策模型分支有专门的排序路径，也可以配置跳过重排。 [候选预算和重排调用](https://github.com/vectorize-io/hindsight/blob/937886199e0e/hindsight-api-slim/hindsight_api/engine/memory_engine.py#L10868-L10964) · [查询与候选配对打分](https://github.com/vectorize-io/hindsight/blob/937886199e0e/hindsight-api-slim/hindsight_api/engine/search/reranking.py#L480-L522) · [最终分与模式分流](https://github.com/vectorize-io/hindsight/blob/937886199e0e/hindsight-api-slim/hindsight_api/engine/search/reranking.py#L259-L312) · [决策模型分流](https://github.com/vectorize-io/hindsight/blob/937886199e0e/hindsight-api-slim/hindsight_api/engine/memory_engine.py#L10995-L11047)

## 和 E009 的关键差异

| 决策 | E009 | Hindsight | E019 对照 |
| --- | --- | --- | --- |
| 从哪里进图 | 只用全局合并结果前五条里的非弱相关实体页 | 独立向量种子是事实单元，可通过其实体或已有事实链接展开 | B/C 保留旧入口。H 用独立向量种子。X 从任务仓库、路径或提及的系统定位锚点。 |
| 扩到什么 | 只在实体页间走一跳，从属于、包含、实现、依赖及其反向中选边 | 事实级共享实体、语义、因果及独立时间路；观察还可接来源事实 | B/C 保留实体类型。H 在有出处的页面边上做两次度归一化传播。X 取一层有出处的经验/规范等挂接页。 |
| 结果怎么进入阅读范围 | 追加在原榜单后，或用种子查找分数乘关系权重、对已有页加分后全榜重排 | 图路单独排名，同向量和关键词等先融合，再在受控预算中重排 | H/R 用同一交叉编码器和上限，只改变候选路。X 保留全局名次并单列实体候选，使用等阅读预算。 |
| 如何知道关系可信 | E009 对各边没有强制单独校验出处 | 事实可追至 document/chunk，边由提取的因果、共享实体、时间或向量相似生成；这些生成依据的含义各异 | 只遍历可验证到明确写入该关系的来源记录。公开夹具主动放入无出处边检验排除。 |

E009 在原试验里发现首轮种子欠缺，且数值重排会改变原有按页型混排。Hindsight 给出了不同的候选入口和竞争机制。源码还说明，自动近邻、共现或时间关联各自只表达一种信号。它们可以扩候选，无法单靠结构证明一条领域关系。E019 把这些机制借到页面检索，省略 Hindsight 的写入、观察生成和独立时间路。 [E009 原实验](../E009-typed-relation-expansion/README.md) · [#64 上下文锚定方案](../../plans/plan-context-anchored-recall.md) · [E019 配置](config.json)
