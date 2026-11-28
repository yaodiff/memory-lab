# 本体化记忆与实体治理

[English](07-typed-memory.en.md) · [源码与论文精读](../docs/agent-memory-deep-reading.md)

实体治理解决了「这页应该挂在哪」。本体化记忆要进一步回答「这条事实在说哪个对象、在哪个条件下成立、依据是什么」。已有叶节点适合作为导航。近期最有实测支持的做法是从真实漏题回源，给相关页面补常见问法和适用范围。

## 我们做对了什么

- **改善归属，保留出处。** 主要试点的直挂叶比例约从 80% 升至 95%。夜间整理的抽样读回保住了链接和触发词，跨类取代和证据时间也通过了定向读回。这些是结构和维护证据。 [E037](../experiments/E037-nightly-curation-readback/README.md) · [E040](../experiments/E040-cross-category-supersession/README.md) · [E044](../experiments/E044-leaf-coverage-live/README.md)
- **把取回和使用分别验证。** 词法＋向量在单范围线上对照中提高前五整组找齐，真实会话采纳的调整后差值区间跨零。已确认的找齐改善和实际采纳属于两份证据。 [E032](../experiments/E032-keyword-fusion-live/README.md)

## 实验支持哪条路线

以下均为内部小样本。

| 问题 | 观测 | 决定 |
| --- | --- | --- |
| 原池缺证据吗 | 线上前五未找齐的问题中，约 65% 的必找页已全部进入原前 30。实体扩池对同批未找齐题的新增可补全上限约 2% 和 9%，分别对应小配置和放宽配置，锁定配置的净效应区间跨零。 [E049](../experiments/E049-entity-index-two-stage/README.md) | 两种规则重排均未救回。定点补内容后仍有可重复的池内漏题，再评估模型重排。 [E053](../experiments/E053-rule-based-in-pool-reranking/README.md) |
| 给哪类内容补什么 | 定点补内容线上前五整组找齐约 +5.6 个百分点，整题零退步。第二轮离线约 +1.4 个百分点，区间触零。脱离漏题、按召回频率批量补问法的离线变化约 −1.4 个百分点。 [E052](../experiments/E052-targeted-content-enrichment-live/README.md) · [E056](../experiments/E056-blind-faq-enrichment/README.md) | 从真实漏题回源核查适用范围，另用新留出复验。线上首批包含少量新页，改动由同批漏题诊断得来。 |
| 归叶以后能直接用来排吗 | 四种实体入榜方法都没过影子门槛；较准的叶名锚定也未带来下游收益。 [E031](../experiments/E031-governance-retrieval-recheck/README.md) · [E045](../experiments/E045-entity-structure-ranking/README.md) | 为消歧、证据回读和导航单建面板。页级扩池的负结果界定了这条实现的上限，事实级方案仍待验证。 |

## 本体化缺的五层

| 缺口 | 最小改动 |
| --- | --- |
| 实体类型 | 在现有稳定 ID 上为少数高歧义对象加类型，例如组件、环境、接口。区分主题、别名与身份；保留未知。见 [OntoKG §3](https://arxiv.org/html/2604.02618v1#S3)。 |
| 内在属性 | 在对象上只保留可证、能消歧的字段，例如组件职责或接口协议。对象自身的属性与带方向的关系分别表达。字段随范围或版本变化时，作为带限定的事实保存。 [OntoKG §5.3](https://arxiv.org/html/2604.02618v1#S5.SS3) |
| 写入时绑定 | 新增或改版时为证据片段解析对象。唯一的类型和范围匹配可做绑定提案，多解或出处不足待审。记录来源版本，重复回放幂等，保留原始页面。 [WorldDB §3](https://arxiv.org/html/2604.18478v1#S3) |
| 有效期与取代边 | 从页级取代细化到可变事实。分别保留证据时间、事实生效区间和记录时间，冷藏状态另计。只在同对象、同属性、同范围有明确取代证据时关闭旧区间。历史可回读，未知维持未知。 [Zep §2.2.3](https://arxiv.org/html/2501.13956v1#S2.SS2.SSS3) · [Graph-Based Personalized Memory §IV](https://arxiv.org/html/2609.08599v1#S4) |
| 实体路由下钻 | 提供「识别对象 → 看适用事实 → 回原文」的显式路径，也允许正文命中后反向进入对象导航。验证对象定位、出处可读和下钻步数；同名多解允许回退全文搜。 [EnSIMem §3](https://arxiv.org/html/2609.27279v2#S3) · [MemForest §6](https://arxiv.org/html/2605.23986v4#S6) |

例如，两套部署环境可以在同一时期有不同的重试策略。来源证实某环境升级后改变策略时，只关闭该环境旧事实的有效期，仍能回答升级前的问题。主题节点组织文档，实体 ID 标明对象，事实名下保留策略、范围和证据。这个例子是合成的。

继续从真实漏题回源，每批留一套新题复验。补内容后若仍有可复现的池内同版证据漏排，再评估模型重排。实体侧先补少量类型、可核查日期和版本，随后测显式历史查询及预算内的问题相关下钻。固定目录在测试预算内没有整题增益，时间／版本规则回放受缺字段限制。 [E054](../experiments/E054-entity-drilldown-navigation/README.md) · [E055](../experiments/E055-dedup-time-and-literal-replay/README.md) · [路线图](../plans/team-memory-quality/README.md)
