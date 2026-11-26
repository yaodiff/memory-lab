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

## 数据政策

只用公开数据集，以及在公开开源仓库上合成的会话。不放任何专有代码、会话或文档。文章里的例子都经过改写或是合成的；内部测量只写比例或粗粒度描述，不放原始数据，并注明是我们自己场景下的小样本。

## 参与贡献

所有改动都走 issue → PR → 检查 → squash 合并，`main` 受保护，不能直接推送。流程见 [CONTRIBUTING.md](CONTRIBUTING.md)（英文）。

## 许可证

Apache-2.0
