# Memory Lab：以纠正为驱动的编程 Agent 团队记忆

[English](README.md) · 中文

> 状态：早期草稿，Next-step Replay 已按仓库主人确认的 CLI 配置跑完六个 case。
> 这是小规模合成数据试跑，不是经过校准、可泛化的 benchmark。

**一句话**：评测编程 Agent 的团队记忆，我们问的是「它还会不会被纠正」，而不是「它能不能想起一个事实」。

这个仓库装了三样东西：

1. **文章**：在实际场景里给编程 Agent 做团队记忆的一线笔记，负结果也照写。
2. **评测**：*Next-step Replay*（纠正前那一刻重放）。把一段 Agent 会话（这里用开源仓库上的合成会话）切到人纠正之前，分别在有记忆和无记忆时重放，再由两个独立判官判方案是否仍违反团队约定。
3. **复现**：在公开数据集上复现知名记忆论文（Mem0、A-MEM、Generative Agents、Agent Workflow Memory 等），逐篇和上面的思路对照。

`memlite/` 是一个很小的参考实现，只为让实验能跑起来，不是产品。

## 三道关

一条团队约定要连过三道关才有用：

| 关 | 问题 | 常见失败 |
|---|---|---|
| **写对** | 纠正有没有被记成一条可复用、保住适用范围的规则？ | 被记成进度或一次性要求；「仅首期」这类范围被删；长任务中途顺带的纠正没被记下 |
| **找到** | Agent 有没有在决策点去搜，query 对不对得上规则？ | Agent 搜的是手头的任务，而规则讲的是「这类步骤怎么做」 |
| **用上** | 读到之后照做了没有？ | 读了全文，只照做了一部分 |

详见[第 01 篇](essays/01-three-gates.md)。

## 文章

每篇先写中文，英文版是同一内容的英文写法，不是逐字翻译。

| # | 中文 | English |
|---|---|---|
| 01 | [团队记忆的三道关：写对、搜得到、用得上](essays/01-three-gates.md) | [Three gates for team memory](essays/01-three-gates.en.md) |
| 02 | [用团队记忆的一线数据读 Anthropic 的「记忆组件」](essays/02-reading-the-components.md) | [Reading Anthropic's "components of agent memory" against field data](essays/02-reading-the-components.en.md) |
| 03 | [你的记忆评测可能虚高了：同会话泄漏](essays/03-same-session-leakage.md) | [Your memory eval may be inflated: same-session leakage](essays/03-same-session-leakage.en.md) |
| 04 | [读 Meta 的 Self-Improving Memory：让模型改自己的记忆提示，再蒸馏进权重](essays/04-self-improving-memory.md) | [Reading Meta's Self-Improving Memory: the model rewrites its own memory prompts, then learns them](essays/04-self-improving-memory.en.md) |
| 05 | [让编码 Agent 从手头的仓库找到相关记忆](essays/05-aoci-code.md) | [Finding the right memories from the repository already in view](essays/05-aoci-code.en.md) |
| 06 | [排序没变，Agent 为什么少用了记忆？](essays/06-memory-search-previews.md) | [Why did the agent use less memory when the ranking stayed the same?](essays/06-memory-search-previews.en.md) |
| 07 | [本体化记忆与实体治理](essays/07-typed-memory.md) | [Entity governance and ontology-backed memory](essays/07-typed-memory.en.md) |

## 目录

查看[方案](plans/README.md)、[实验](experiments/README.md)、[经验](lessons/README.md)、[公开交接](handoff/README.md)和[归档](archive/README.md)的索引。

```
essays/            一线笔记：NN-slug.md（中文）+ NN-slug.en.md（英文）
bench/
  next-step-replay/  切会话、出题、重放
  datasets/          公开数据加载器 + 合成会话生成器
  judges/            判官提示、一致率统计
memlite/           最小参考实现：类型化页面、逐句溯源、写入判断、带硬约束的整合、能解释空结果的检索
reproductions/     每篇论文一个目录：README（复现了什么 / 数字 / 和原文差在哪）+ run.sh
docs/              相关工作、CoALA 对照
```

## 路线图

- [x] 第 01 篇：三道关（草稿）
- [x] 第 02 篇：用团队记忆的一线数据读 Anthropic 的记忆组件（草稿）
- [x] 第 03 篇：同会话泄漏让记忆评测虚高（草稿，已补[描述性 demo 结果](essays/03-same-session-leakage.md#评测-demo-结果)）
- [x] 第 04 篇：用团队记忆读 Meta 的 Self-Improving Memory（草稿，配合合成实验 [E004](experiments/E004-meta-optimized-memory-prompts/README.md)）
- [x] 第 05 篇：[读 AOCI-CODE](essays/05-aoci-code.md)
- [ ] 待写文章：步骤级检索
- [ ] 评测：在 Next-step Replay 上加「回看记录、核对记忆」对照组（计划见第 02 篇）
- [ ] 复现：Mem0 与全上下文在 LoCoMo 上的对比
- [ ] 复现：A-MEM 链接演化在 LoCoMo 上的消融
- [x] 评测：[Next-step Replay demo](bench/next-step-replay/README.md)（Click 上六个合成纠正），附 [E001 冒烟测试](experiments/E001-next-step-replay-smoke/README.md)
- [x] 评测：[E002 全部六个 case 的完整试跑](experiments/E002-next-step-replay-full/README.md)（模型和花费已经仓库主人确认）
- [ ] 评测：人工校准、不同模型下的有效性验证

### Timeline（时间线）

- **2026-11-15** — [E001 和 E002](experiments/README.md)：Next-step Replay 冒烟测试和完整试跑。
- **2026-11-20** — [E003–E008、E010–E012](experiments/README.md)：排序、记忆提示、实体检查、页面类型、去重及重放实验。
- **2026-11-20** — [E009](experiments/E009-typed-relation-expansion/README.md)：从搜索结果沿实体关系扩一跳，多页全中率没有提高。
- **2026-11-20** — 方向草案：[从任务上下文找实体](plans/plan-context-anchored-recall.md)，按问题排序实体挂接的记忆，在全局搜索旁边单独展示。
- **2026-11-25** — 固定候选池后做重排，小样本的全局前五目标命中持平，定向收益随题组而变。
- **2026-11-25** — 实体导航能找到搜索列表之外的一些目标。在定向小样本中，导航占用证据名额后，总目标命中反而下降。
- **2026-11-25** — 参考 [Hindsight](https://github.com/vectorize-io/hindsight/blob/main/skills/hindsight-docs/references/developer/retrieval.md) 回放向量、关键词与图混排。自有场景小样本中，定向前五命中从约三成升至约一半。小模型重排提高了全局金标的证据找齐率，定向收益略有回落，默认上线仍缺证据。
- **2026-11-25** — [E020](experiments/E020-structure-retrieval-diagnosis/README.md)：实体整理前后找齐率持平。主结果排序没有用到实体链接，追加子挂载后父实体仍关联很多页，原评测的多页题也偏少。
- **2026-11-25** — [E021](experiments/E021-heldout-retrieval-fusion/README.md)：在扩展的 150 题留出集里，生产结果融合 BM25 后，前五找齐率升约 15 个百分点。参考 Hindsight 的四路页面级适配低于基线。
- **2026-11-25** — [E022](experiments/E022-existing-link-reranking/README.md)：重排已有出链提高了多页证据找齐率，本地回放的 SQL 查询数持平。共享实体扩候选带来更多无关页，多页找齐无净收益。
- **2026-11-25** — [E023](experiments/E023-page-applicability-replay/README.md)：243 题固定召回复验中，适用范围提示减少了观测到的误采纳。正确率差的区间跨零，暂不默认开启。
- **2026-11-25** — [E024](experiments/E024-content-gap-write-guard/README.md)：补写草案在 15 条留出问法中的 14 条进入前五。一次性整理后旧路径仍会回写，因而把校验放到增量写入时。
- **2026-11-25** — [E025](experiments/E025-rollout-checkup-four-arm-replay/README.md)：第二个团队空间的推广体检发现，多数新页没有结构化摘要、不少非叶父实体只有一个子实体，严格叶挂载闸不能直接照搬。76 题四臂重放中，词法融合利好单页题却拖累多页题，出链重排在该空间零增益也零回退。
- **2026-11-25** — [E026](experiments/E026-three-gap-regression/README.md)：50 题回归集上，外部仓作用域守卫把 12 道外部仓题前三的强内部错页降到 0/12，10 道内部护栏题零误伤；置信度加权双路融合在短句题拿到 12/12 前十。克制的回源核实指令只有小幅收益。
- **2026-11-25** — [E027](experiments/E027-live-recall-contract-recheck/README.md)：换成生产真实召回后，新补契约页对 34 道目标题只净增 1 题。并入约 11 KB 实体页的一项契约排到第 13 名甚至更后，大实体页会稀释其中的契约；暂不重跑完整综合评测。
- **2026-11-25** — [E028](experiments/E028-session-memory-v3-retest/README.md)：用生产抽取模板和同款模型复测，原窗与只机械补闭环窗都只有 0/4 产出可复用经验页；同时修好实体字典序截断、路由降级与取代误丢的最小原型达到 4/4，五个回归案例零重复建页、零泄漏。上传溯源还发现归属未解析的会话以退出码 0 结束并写假日志。修复已成草稿，待批合并。
- **2026-11-26** — [E029](experiments/E029-skill-prompt-acceptance-fail/README.md)：统一版和更精简版指令在预登记的 81 题门槛上两轮均未通过：修好一组又在另一组退步，差异落在单次运行波动内。裁定暂停记忆指令的提示词微调，改靠后端检索修复。
- **2026-11-25** — [E030](experiments/E030-link-rerank-production-shadow/README.md)：出链按问题重排的生产影子验收中，10/10 写出影子事件，两阶段共同命中的 49 条出链在用户返回里顺序全部一致，计算耗时中位约 0.17 ms。继续保留影子观察，尚未量到线上效果。
- **2026-11-26** — 30 天零采纳降温离线重放（自有场景小样本）：约 58% 在架页已满 30 天，其中约 85% 窗内零采纳。全库降温可缩减热层约 52%，但目标空间答案页前 1 与前 3 命中各跌 12.5 个百分点（前 10 跌 15 个百分点）、前 3 错页上升，且 25% 检索题失去热层必需金标；稀疏采纳回执误降了近期仍有真实召回的现行页。仅降温事件页可缩减热层约 13% 且答案页召回零回退，抽样历史回执在温层索引与冷归档找回率 100%。结论：全库 30 天零采纳自动降温不可行（Does not work）。
- **2026-11-27** — 仅事件页 30 天冷藏归档草稿与离线复验（自有场景小样本）：落地独立的冷藏归档状态（维护任务默认干跑、夜间默认关闭；移出默认热层索引，同时保留按编号原文回读、实体时间线与按需温层词法检索）。将实装筛选逻辑回放至 30 天基线，冻结默认检索池缩减 12.6%（活跃事件页缩减 41.5%），非事件页与窗内已采纳页误伤率 0%；留出集答案召回持平、目标空间全量前 10 召回升 2.5 个百分点、基准参考页丢失率 0%，按需温层打分器对抽样历史回执实现 100% 前 1 找回，试跑批次写前备份与恢复闭环率 100%。草稿改动待评审批准后再推进试点。
- **2026-11-27** — [E031](experiments/E031-governance-retrieval-recheck/README.md)：**Inconclusive**（内部小样本）。线上留出题前五找齐下降 2.8 个百分点，差异不显著，固定金标整题持平。未找齐题中约 45% 的必要页已在候选池但排在第五位之后。另一路离线补问法使前三实体锚定率从 22.8% 升至 41.0%，下游检索未见增益，未上线。同一判定者复核的前五错页槽位率下降 2.7 个百分点，区间跨零。
- **2026-11-27** — [E032](experiments/E032-keyword-fusion-live/README.md)：**Works**（内部小样本）。上线前离线重算约 +16 个百分点。单范围上线后，冻结留出题取前五判整组找齐，56.9%→71.5%（+14.6 个百分点，配对 95% 区间 +7.6 至 +21.5）；按日常请求上限测的固定金标 +5.7 个百分点，区间跨零。后续线上两小时主命中采纳 22.6%→10.4%，扣同期对照后 −8.2 个百分点（95% 区间 −17.7 至 +1.3）；提前一天切片约 −0.8 个百分点。抽到的超时降级全部成功返回原排序。保留小范围开启，等工作日复测再定推广。
- **2026-11-27** — [E033](experiments/E033-approval-only-ingestion/README.md)：**Works**（内部小样本）。线上发布首小时，纯审批会话新入库较发布前一小时减少 100%，遗留积压全部跳过。存量批次写后读回率 100%，固定探针未见退步。明确的保留例外继续受原准入约束。
- **2026-11-27** — [E034](experiments/E034-event-only-cooling-live/README.md)：**Works**（内部小样本）。事件页专用冷藏由离线方案推进至生产分批写入，在架事件页减少约 43%。抽样冷藏页的原件与温层回找已在试点验过。日常自动运行待生产观察期结束再判。
- **2026-11-27** — [E035](experiments/E035-stale-projection-cleanup/README.md)：**Works**（内部小样本）。只读核对定位到已下架和孤立副本滞留。生产清理后，目标副本移除读回 100%，固定题前 30 位滞留副本槽位降至零。防复发修复上线后，抽到的新下架页全部移除检索副本。
- **2026-11-27** — [E036](experiments/E036-event-weight-cap-replay/README.md)：**Does not work**（内部小样本）。离线仅放宽上限时，原权重下效果持平。减轻降权所得找齐率增益不显著，较激进的变体使前五误入的一次性非金标事件槽位变为约 3–15 倍，挤掉可复用记忆。保留原护栏。本轮降权实验围绕全局调权。冷藏后按问法意图抬权仍无增益，按事件页质量抬权仅保留为离线影子候选，见 [E050](experiments/E050-targeted-event-boost-after-cooling/README.md)。
- **2026-11-27** — [E037](experiments/E037-nightly-curation-readback/README.md)：**Works**（内部小样本）。首个完整生产观察窗中，抽到的新版本未见丢链、摘要退化或触发词丢失。随后拆小并迁移规范页，写后读回 100%，固定探针未见退步。
- **2026-11-27** — [E038](experiments/E038-targeted-content-repair/README.md)：**Inconclusive**（内部小样本）。针对漏召回补正文问法和少量缺页，生产写入后的探针整题找齐净增约 6 个百分点，同期切换了排序。用新融合排序复核归因，固定题前五逐位一致率 100%，未证实补丁单独改善排序。
- **2026-11-27** — [E039](experiments/E039-retrieval-load-isolation/README.md)：**Works**（内部小样本）。上线后一小时，限流响应数较前窗减少约 67%，后台限流响应减少约 94%，线上检索 P99 的窗均值约降 69%。效果来自短窗观察，需继续跟踪高峰期。
- **2026-11-27** — [E040](experiments/E040-cross-category-supersession/README.md)：**Works**（内部小样本）。离线复核的已知冲突均正确判定，相似非冲突误取代率为 0%。跨类取代和证据时间上线后通过定向读回。离线回放否决全局权威加权，证据时间保留给调用方核对。
- **2026-11-27** — [E041](experiments/E041-memory-use-guidance/README.md)：**Inconclusive**（内部小样本）。冻结题中正确处理和必要回源整体持平，生产已读回使用规则。较长的同口径采纳、拒用和纠正变化仍待复核。
- **2026-11-28** — [E042](experiments/E042-workaround-scope-review/README.md)：**Does not work**（内部小样本）。全库活跃页抽样粗估约 4% 需处理，关键词候选的处置建议与人工完全一致约 14%，无法批量执行。改为人工复核常被召回页，整体抽样一致约 94%，含大量无需改动页，不能用作变更准确率。经逐条复核后小批补适用范围，固定题整组找齐持平。
- **2026-11-28** — [E043](experiments/E043-curation-rollout-waves/README.md)：**Inconclusive**（内部小样本）。第二波约四成范围过干跑门槛，实际提交读回 100%，固定探针未见退步。第三波经细化后候选均过 90% 抽检门槛，但次日生产回执中已验收保留约 4%、移除约 7%，约九成仍未完成验收。干跑通过后仍需按线上批次核验。
- **2026-11-28** — [E044](experiments/E044-leaf-coverage-live/README.md)：**Inconclusive**（内部小样本）。生产直挂叶比例由约 80.3% 升至 95.0%，写后读回 100%。留出题前五整组找齐 −1.4 个百分点（配对 95% 区间 −3.5 至 0），固定金标整题找齐和首位持平。前五错页率表面下降 7 个百分点，判定人变化使归因不成立。
- **2026-11-28** — [E045](experiments/E045-entity-structure-ranking/README.md)：**Does not work**（内部小样本）。离线比较叶名扩候选、同叶提权、导航降权加行动页提权、带出处关系一跳扩展。四法均未过影子门槛。最好方案的留出前五找齐仅 +0.7 个百分点，区间触零，且固定金标首位下降约 2.9 个百分点。不开影子。四种做法偏保守且触发有限，向量检索使用归叶前快照，生产实体结构目前仅用于关联页、尚未进入主榜候选生成。两段检索复测显示实体扩候选的上限低，后续优先验证已入池页重排，见 [E049](experiments/E049-entity-index-two-stage/README.md)。
- **2026-11-28** — [E046](experiments/E046-generated-preview-pilot/README.md)：**Inconclusive**（内部小样本）。首个 48 小时窗口排除叠加排序变更后，前三次检索任一采纳为 45.5%，基线 41.1% 落在估计区间内；扣同期对照的 +12.5 个百分点区间也跨零。单条注入长度中位数（按 bytes 计）约减少 83%。保留灰度，待第二窗口确认采纳。首窗样本不足以确认摘要对采纳的影响，效果仍待补样验证。
- **2026-11-28** — [E047](experiments/E047-outgoing-link-live/README.md)：**Inconclusive**（内部小样本）。试点正式开启后的出链查询失败率为 0%，关键词融合仍在影子时，主命中两小时采纳与出链影子期相差约 +0.5 个百分点。正式模式缺逐槽变动和耗时日志，少量可核对案例中约一半变差。维持试点，先补观测再定推广。
- **2026-11-28** — [E048](experiments/E048-ingest-gate-evidence/README.md)：**Inconclusive**（内部小样本）。线上 24 小时新增约降 79%，但比上周同窗高约 10%，暂不能归因于收紧；约 94% 的构建失败发生在外部调用链路，发布点近窗失败率基本持平。离线修复回放中约 54% 的硬拦样本回到原准入，约 13% 仍合理拦截，约 33% 待人工裁决。保留线上准入，补证修复仍是草稿。
- **2026-11-29** — [E049](experiments/E049-entity-index-two-stage/README.md)：**Does not work**（内部小样本）。对线上前五未找齐题，前 2 叶 × 每叶前 2 页理论上可带回约 21% 题的全部缺页，但相对原有前 30 候选，仅约 2% 的题新增可补全；放宽到 8 叶 × 5 页，两项比例分别约 53% 和 9%。锁定配置的救回与退步相当，两种候选基线的前五找齐差值置信区间均跨零。停止推进实体候选扩张，后续优先验证已入池页的重排。
- **2026-11-29** — [E050](experiments/E050-targeted-event-boost-after-cooling/README.md)：**Inconclusive**（内部小样本）。只移除冷藏页后，最激进配置下留出题前五的单次非金标事件占槽减少约 20%，全局抬权仍会挤占可复用结果。按问法意图触发无找齐增益；按事件页质量分层抬权并保留事件上限 2，留出题前五整组找齐提高约 0.7 个百分点（配对 95% 区间 0 至 +2.2 个百分点）。仅保留为离线影子候选，暂不启用。
- **2026-11-29** — [E051](experiments/E051-question-and-scope-enrichment/README.md)：**Works**（内部小样本，离线回放）。已有页补常见问法和适用范围，前五整组找齐约 +4.9 个百分点（配对 95% 区间 +1.5 至 +8.6）；仅用同版正文约 +2.8 个百分点。独立金标与错页率持平，待新留出复验。
- **2026-11-29** — 记录[源码与论文精读](docs/agent-memory-deep-reading.md)和[实体治理综合分析](essays/07-typed-memory.md)。[里程碑](plans/team-memory-quality/README.md)将池内选齐证据和定点补内容排在前面；类型化、写入绑定、有效期和实体下钻用独立的证据与导航评测验证。

## 数据政策

只用公开数据集，以及在公开开源仓库上合成的会话。不放任何专有代码、会话或文档。文章里的例子都经过改写或是合成的；内部测量只写比例或粗粒度描述，不放原始数据，并注明是我们自己场景下的小样本。

## 参与贡献

所有改动都走 issue → PR → 检查 → squash 合并，`main` 受保护，不能直接推送。流程见 [CONTRIBUTING.md](CONTRIBUTING.md)（英文）。

## 许可证

Apache-2.0
