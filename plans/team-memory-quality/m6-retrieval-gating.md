# M6 检索门控

[← 总览](README.md) · [GitHub milestone](https://github.com/yaodiff/memory-lab/milestone/6)

## 目标与退出条件


- 目标：低相关和「相似但错」的结果不误导 Agent。
- 退出条件：在留出的探针上测过拒答或弱相关门控，并报告误拒率和错误断言率。
- 状态：事件护栏保留，滞留检索副本已清理并上线防复发修复。错误断言和误拒的退出条件待验证。

## Issue：事件护栏、时效与降级（[#99](https://github.com/yaodiff/memory-lab/issues/99)）

- [x] Task：[E036](../../experiments/E036-event-weight-cap-replay/README.md)（内部小样本）。放宽上限在原权重下无增益，激进减轻降权后非金标的一次性事件占位约增至 3–15 倍。本轮降权实验围绕全局调权。冷藏后按问法意图抬权仍无增益，按事件页质量抬权仅保留为离线影子候选，见 [E050](../../experiments/E050-targeted-event-boost-after-cooling/README.md)。
- [x] Task：[E035](../../experiments/E035-stale-projection-cleanup/README.md)（内部小样本）。清理后固定探针的前 30 位滞留副本占槽归零，抽到的新下架页均已移除检索副本。
- [x] Task：[E040](../../experiments/E040-cross-category-supersession/README.md)（内部小样本）。跨类取代和证据时间完成定向线上验证。
- [x] Task：[E039](../../experiments/E039-retrieval-load-isolation/README.md)（内部小样本）。后台限流隔离后的首小时，线上检索 P99 窗均值约降 69%。关键词支路另有原序回退，见 E032。
- [ ] Task：保留降权与上限。用留出近似错页、应拒答、应保留的事件和新旧冲突探针核验误拒与错误断言，同时跟踪高峰降级率。

## Issue：相关度下限（[E003 / #16](https://github.com/yaodiff/memory-lab/issues/16)）

- 结论：说不清（实验尚未跑）。
- [x] Task：相关度很低的结果直接不返回，不再保底返回前几条。结果：行（内部上线）。门槛过高会误杀边缘正例，退回后靠排序让位。
- [ ] Task：#16 合成语料上复现下限的效果。

## Issue：相似但错的结果（无 issue，已完成的尝试）与门控（[#30](https://github.com/yaodiff/memory-lab/issues/30)）

- 假设：阈值挡不住「相似但错」，需要门控。结论：说不清。
- [x] Task：词法融合、单页打分的模型重排、一次输入多个候选的重排、大模型硬拒答。结果：不行。有的使排名更差，有的对某类问题崩掉，有的误拒偏高；留出验证里排序融合收益很小。大模型重排被用户判定太慢。
- [x] Task：同一个模型作为拒答门控（只判断是否相关，不排序）。结果：评测内行，错误召回明显下降，没有误拒可答问题，尚无线上数据。
- 相关诊断见 [M2](m2-findability.md)。对象或动作不匹配可用于构造留出探针；门控效果仍待按误拒率和错误断言率验证。
- [ ] Task：#30 在留出探针上比较「仅下限」「下限加门控」「再加原文核对」。

## Issue：平台类问题引到官方手册（[#31](https://github.com/yaodiff/memory-lab/issues/31)）

- 假设：平台操作契约引到官方手册更好，团队特有的诊断经验留在记忆。结论：说不清。
- [x] Task：核对记忆与官方手册的重叠。结果：重叠很小；多数平台类记忆记的是手册没覆盖的实测坑，不能整页下线。
- [x] Task：把记忆里手册缺失的内容整理后反哺手册。结果：进行中，需要手册维护者评审。
- [ ] Task：#31 合成问题上比较有无指引的正确率与错误断言率。
