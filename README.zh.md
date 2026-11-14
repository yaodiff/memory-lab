# Memory Lab：以纠正为驱动的编程 Agent 团队记忆

[English](README.md) · 中文

> 状态：早期草稿，还没有任何东西跑过 benchmark。

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

## 目录

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
- [ ] 第 03 篇：同会话泄漏让记忆评测虚高
- [ ] 第 04 篇：步骤级检索
- [ ] 评测：在 Next-step Replay 上加「回看记录、核对记忆」对照组（计划见第 02 篇）
- [ ] 复现：Mem0 与全上下文在 LoCoMo 上的对比
- [ ] 复现：A-MEM 链接演化在 LoCoMo 上的消融
- [ ] 评测：Next-step Replay 在一个开源仓库上的 demo（5–10 个合成纠正）

## 数据政策

只用公开数据集，以及在公开开源仓库上合成的会话。不放任何专有代码、会话或文档。文章里的例子都经过改写或是合成的；内部测量只写比例或粗粒度描述，不放原始数据，并注明是我们自己场景下的小样本。

## 参与贡献

所有改动都走 issue → PR → 检查 → squash 合并，`main` 受保护，不能直接推送。流程见 [CONTRIBUTING.md](CONTRIBUTING.md)（英文）。

## 许可证

Apache-2.0
