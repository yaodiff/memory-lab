# Plan：团队记忆质量治理（写对、搜得到、用得上）

[← 方案索引](../README.md)

- 状态：草案
- 日期：创建 2026-11-19 / 最后更新 2026-11-19
- 总 issue：#17 / 拆出的实验：见下方各 milestone 的 issue（相关：E003 / #16）

## 背景与问题

团队记忆要帮到编码 Agent，要过三道关：[写对、搜得到、用得上](../../essays/01-three-gates.md)。我们在一个内部场景里用大约两周集中治理了这三道关。这份 plan 只写通用做法、取舍和步骤状态，结论是粗粒度的，来自小样本，不代表通用结论。

总体状态：

| 关 | 状态 |
| --- | --- |
| 写对 | 改善明显，主要来自写入规则和写后检查 |
| 搜得到 | 改善很小。多数想法没有越过事先定好的门槛 |
| 用得上 | 搜到之后基本会照做，但「搜到」本身是瓶颈，这一关几乎没有单独改善 |
| 少被纠正 | 尚未证实，要等足够长的观察窗口 |

另一个发现：我们自己的评测设置多次高估或掩盖了效果。这些失败方式单独记在 [评测教训](../../lessons/memory-eval.md)，写入与整理方面的在 [整理教训](../../lessons/memory-curation.md)。

## 目标 / 不做什么

目标：

- 让 Agent 在真实开发中少被纠正，而不是让记忆条数更多。
- 把「哪些做法有效、哪些无效、为什么」写成别人可以复用的取舍。

不做什么：

- 不在 Lab 里放内部系统的名字、数字、样例和链接。内部明细留在内部文档。
- 不把内部小样本结论包装成通用结论。需要数字的结论，用合成或公开数据在实验 issue 里复现。
- 不在这份 plan 里决定产品改动。需要交接时，走 `handoff/` 的公开交接卡。

## 方案

组织方式：Plan（本文）、Milestone（每个一个文件）、Issue、Task 四层。

- **Milestone**：对应 GitHub 上的 milestone，写目标、退出条件、状态。
- **Issue**：一个具体问题或假设，写结论（行 / 不行 / 说不清）。尚未做完或待验证的有真实 GitHub issue，链接写在标题里。已经做完的历史尝试不开 issue，只留在 task 里（标「无 issue」）。
- **Task**：issue 下的一次尝试，只写通用做法、结果、失败或放弃的原因。失败的尝试保留。

结论里的「行 / 不行」来自内部小样本，只代表那个场景；「说不清」表示样本太小、判官意见不一或效果混杂。

## 步骤：Milestone 总览

每个 milestone 一个文件，文件内按 目标与退出条件、Issue、Task 组织。

| Milestone | 状态 | Lab issue（未完成或待验证） | 文件 |
| --- | --- | --- | --- |
| [M1 写入质量](https://github.com/yaodiff/memory-lab/milestone/1) | 内部大部分达成，剩余是在公开或合成数据上的验证。 | [#19](https://github.com/yaodiff/memory-lab/issues/19)、[#20](https://github.com/yaodiff/memory-lab/issues/20) | [m1-write-quality.md](m1-write-quality.md) |
| [M2 让 Agent 搜得到](https://github.com/yaodiff/memory-lab/milestone/2) | 未达成。想法很多，越过门槛的很少。 | [#21](https://github.com/yaodiff/memory-lab/issues/21)、[#22](https://github.com/yaodiff/memory-lab/issues/22) | [m2-findability.md](m2-findability.md) |
| [M3 规范整合与去重](https://github.com/yaodiff/memory-lab/milestone/3) | 进行中。整合已做，数量没有稳定下降。 | [#23](https://github.com/yaodiff/memory-lab/issues/23)、[#24](https://github.com/yaodiff/memory-lab/issues/24) | [m3-consolidation.md](m3-consolidation.md) |
| [M4 结构：个人偏好与实体关系](https://github.com/yaodiff/memory-lab/milestone/4) | 进行中。 | [#25](https://github.com/yaodiff/memory-lab/issues/25)、[#26](https://github.com/yaodiff/memory-lab/issues/26) | [m4-structure.md](m4-structure.md) |
| [M5 评测与度量](https://github.com/yaodiff/memory-lab/milestone/5) | 进行中。 | [#27](https://github.com/yaodiff/memory-lab/issues/27)、[#28](https://github.com/yaodiff/memory-lab/issues/28)、[#29](https://github.com/yaodiff/memory-lab/issues/29) | [m5-evaluation.md](m5-evaluation.md) |
| [M6 检索门控](https://github.com/yaodiff/memory-lab/milestone/6) | 进行中。 | [#16](https://github.com/yaodiff/memory-lab/issues/16)、[#30](https://github.com/yaodiff/memory-lab/issues/30)、[#31](https://github.com/yaodiff/memory-lab/issues/31) | [m6-retrieval-gating.md](m6-retrieval-gating.md) |

## 待用户决定

- 是否继续把 milestone 里的待办升成实验（目前每个都是一个 issue，尚未开始）。
- 两份 lessons 是否要写成 essay（中英成对）。

## 偏差记录

- 2026-11-19：初版，按时间组织。
- 2026-11-19：按用户要求重组为 Plan、Milestone、Issue、Task；并按 milestone 建立了 GitHub milestone 与尚未完成事项的 issue（#19 至 #31，加上已有的 #16）。内部结论来自小样本，评测标注和判官都是模型，没有逐题人工校准。
- 2026-11-19：单文件过大，拆成 README 加每个 milestone 一个文件，内容不变。
