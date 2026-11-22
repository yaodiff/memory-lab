# 实验索引

用 [实验模板](_template/README.md) 记录试跑并在表里登记。结论对应实验要回答的问题，可以填写「行」「不行」或「说不清」。

| 编号 | 标题 | 结论（行 / 不行 / 说不清） | 日期 | 交接 |
| --- | --- | --- | --- | --- |
| E001 | [Next-step Replay bounded CLI smoke](E001-next-step-replay-smoke/README.md) | 说不清 | 2026-11-15 | 无 |
| E002 | [Next-step Replay complete shipped-case pilot](E002-next-step-replay-full/README.md) | 说不清 | 2026-11-15 | 无 |
| E003 | [LLM 相关性判别：硬剔除 vs 两段式重排，组内归一化陷阱](E003-llm-rerank-vs-hard-drop/README.md) | Does not work | 2026-11-21 | 无 |
| E004 | [meta 优化的记忆读写提示，换到没见过的世界还赢通用版吗（合成）](E004-meta-optimized-memory-prompts/README.md) | 不行 | 2026-11-20 | 无 |
| E005 | [页类型硬过滤 vs「类型偏好 + 低分回退」，及工具名优先于错误码](E005-type-preference-fallback/README.md) | Inconclusive（初始离线） | 2026-11-20 | 无 |
| E006 | [孤立实体判定：小模型只看页首不对代码，以及代码引用当候选过滤器](E006-orphan-entity-check/README.md) | Does not work | 2026-11-20 | 无 |
| E007 | [与平台官方手册重复的记忆：取代 + 精简，并从整理侧拦住新增重复](E007-manual-overlap-dedup/README.md) | Inconclusive | 2026-11-20 | 无 |
| E008 | [去掉文档召回腿：延迟大幅下降、正确页未丢，但错页改善有限](E008-drop-doc-leg/README.md) | Inconclusive | 2026-11-20 | 无 |
| E009 | [召回时沿实体关系扩一层：多页题一题没多找齐，扩不到主要因为结果里没有可扩的实体](E009-typed-relation-expansion/README.md) | Does not work | 2026-11-20 | 无 |
| E010 | [Supersession and abstention on LongMemEval](E010-longmemeval-supersession/README.md) | Inconclusive | 2026-11-20 | 无 |
| E011 | [Next-step replay with historical and current memory](E011-next-step-memory-replay/README.md) | Inconclusive | 2026-11-20 | 无 |
| E012 | [Local memory retrieval on LongMemEval](E012-local-memory-components/README.md) | Inconclusive | 2026-11-20 | 无 |
| E013 | [Hot-tier candidate cooling — retrieval non-regression gate](E013-hot-tier-candidate-cooling/README.md) | Works | 2026-11-22 | 无 |
| E014 | [Memory usage instructions and held-out regression](E014-memory-instruction-regression/README.md) | Inconclusive | 2026-11-22 | 无 |
| E015 | [Two-stage reranking across three evaluation sets](E015-two-stage-rerank-replay/README.md) | Does not work | 2026-11-21 | 无 |
| E016 | [Evidence-backed entity attachment changes](E016-entity-attachment-review/README.md) | Inconclusive | 2026-11-22 | 无 |
| E017 | [Programmatic screening for duplicate entities](E017-duplicate-screening/README.md) | Does not work | 2026-11-22 | 无 |
| E018 | [Adding rule pages and repeating the behavior evaluation](E018-rule-page-admission/README.md) | Inconclusive | 2026-11-22 | 无 |
