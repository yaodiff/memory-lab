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
| E019 | [复验关系候选融合与任务上下文锚定](E019-graph-recall-revalidation/README.md) | Works（合成题找齐证据） | 2026-11-24 | 无 |
| E020 | [实体整理为什么没改善检索](E020-structure-retrieval-diagnosis/README.md) | Does not work | 2026-11-25 | 无 |
| E021 | [150 题留出集比较 BM25 融合与四路召回](E021-heldout-retrieval-fusion/README.md) | Works | 2026-11-25 | 无 |
| E022 | [仅按问题重排已有出链](E022-existing-link-reranking/README.md) | Works | 2026-11-25 | 无 |
| E023 | [给检索结果加适用范围提示](E023-page-applicability-replay/README.md) | Inconclusive | 2026-11-25 | 无 |
| E024 | [发现缺内容并在增量写入时防回退](E024-content-gap-write-guard/README.md) | Works | 2026-11-25 | 无 |
| E025 | [第二个团队空间的推广体检与四臂检索重放](E025-rollout-checkup-four-arm-replay/README.md) | Inconclusive | 2026-11-25 | 无 |
| E026 | [外部仓同名错页、短句改写与回源核实三短板 50 题](E026-three-gap-regression/README.md) | Works / Inconclusive 分项 | 2026-11-25 | 无 |
| E027 | [新补契约页的真实召回复测与大实体页稀释](E027-live-recall-contract-recheck/README.md) | Does not work as hoped | 2026-11-25 | 无 |
| E028 | [会话到记忆主链路真实模板复测与上传假成功根因](E028-session-memory-v3-retest/README.md) | Works（最小修复原型 4/4；修复待合并） | 2026-11-25 | 无 |
| E029 | [统一版与精简版指令两轮终验未过门槛，暂停提示词微调](E029-skill-prompt-acceptance-fail/README.md) | Does not meet the bar | 2026-11-26 | 无 |
| E030 | [出链相关性重排的生产影子验证](E030-link-rerank-production-shadow/README.md) | Works as a safe shadow rollout | 2026-11-25 | 无 |
| E031 | [治理后线上检索复测](E031-governance-retrieval-recheck/README.md) | Inconclusive | 2026-11-27 | [#99](https://github.com/yaodiff/memory-lab/issues/99) |
| E032 | [关键词融合线上找齐率](E032-keyword-fusion-live/README.md) | Works | 2026-11-27 | [#99](https://github.com/yaodiff/memory-lab/issues/99) |
| E033 | [拦截纯审批会话并清理存量](E033-approval-only-ingestion/README.md) | Works | 2026-11-27 | [#99](https://github.com/yaodiff/memory-lab/issues/99) |
| E034 | [仅事件页冷藏的生产试点](E034-event-only-cooling-live/README.md) | Works | 2026-11-27 | [#99](https://github.com/yaodiff/memory-lab/issues/99) |
| E035 | [清理滞留检索副本](E035-stale-projection-cleanup/README.md) | Works | 2026-11-27 | [#99](https://github.com/yaodiff/memory-lab/issues/99) |
| E036 | [放宽事件页降权和结果上限](E036-event-weight-cap-replay/README.md) | Does not work | 2026-11-27 | [#99](https://github.com/yaodiff/memory-lab/issues/99) |
| E037 | [夜间整理后保留证据和导航](E037-nightly-curation-readback/README.md) | Works | 2026-11-27 | [#99](https://github.com/yaodiff/memory-lab/issues/99) |
| E038 | [定点补内容和常见问法](E038-targeted-content-repair/README.md) | Inconclusive | 2026-11-27 | [#99](https://github.com/yaodiff/memory-lab/issues/99) |
| E039 | [后台限流隔离与检索长尾](E039-retrieval-load-isolation/README.md) | Works | 2026-11-27 | [#99](https://github.com/yaodiff/memory-lab/issues/99) |
| E040 | [跨类取代与证据时间](E040-cross-category-supersession/README.md) | Works | 2026-11-27 | [#99](https://github.com/yaodiff/memory-lab/issues/99) |
| E041 | [检索后的记忆使用规则](E041-memory-use-guidance/README.md) | Inconclusive | 2026-11-27 | [#99](https://github.com/yaodiff/memory-lab/issues/99) |
| E042 | [用关键词批量修正临时绕法](E042-workaround-scope-review/README.md) | Does not work | 2026-11-28 | [#99](https://github.com/yaodiff/memory-lab/issues/99) |
| E043 | [跨范围推广按批过闸](E043-curation-rollout-waves/README.md) | Inconclusive | 2026-11-28 | [#99](https://github.com/yaodiff/memory-lab/issues/99) |
| E044 | [实体归叶与线上排序复测](E044-leaf-coverage-live/README.md) | Inconclusive | 2026-11-28 | [#99](https://github.com/yaodiff/memory-lab/issues/99) |
| E045 | [实体结构进入主榜的四种方法](E045-entity-structure-ranking/README.md) | Does not work | 2026-11-28 | [#99](https://github.com/yaodiff/memory-lab/issues/99) |
| E046 | [自写召回摘要灰度](E046-generated-preview-pilot/README.md) | Inconclusive | 2026-11-28 | [#99](https://github.com/yaodiff/memory-lab/issues/99) |
| E047 | [出链重排开启后回收](E047-outgoing-link-live/README.md) | Inconclusive | 2026-11-28 | [#99](https://github.com/yaodiff/memory-lab/issues/99) |
| E048 | [入库收紧及补引上层会话证据](E048-ingest-gate-evidence/README.md) | Inconclusive | 2026-11-28 | [#99](https://github.com/yaodiff/memory-lab/issues/99) |
| E049 | [实体作索引的两段检索](E049-entity-index-two-stage/README.md) | Does not work | 2026-11-29 | [#99](https://github.com/yaodiff/memory-lab/issues/99) |
| E050 | [冷藏后事件页定向抬权](E050-targeted-event-boost-after-cooling/README.md) | Inconclusive | 2026-11-29 | [#99](https://github.com/yaodiff/memory-lab/issues/99) |
| E051 | [已有页补问法和适用范围](E051-question-and-scope-enrichment/README.md) | Works | 2026-11-29 | [#101](https://github.com/yaodiff/memory-lab/issues/101) |
| E052 | [定点补问法和适用范围线上复测](E052-targeted-content-enrichment-live/README.md) | Works | 2026-11-29 | [#101](https://github.com/yaodiff/memory-lab/issues/101) |
| E053 | [规则池内重排两法](E053-rule-based-in-pool-reranking/README.md) | Does not work | 2026-11-29 | [#101](https://github.com/yaodiff/memory-lab/issues/101) |
| E054 | [实体下钻导航](E054-entity-drilldown-navigation/README.md) | Inconclusive | 2026-11-29 | [#101](https://github.com/yaodiff/memory-lab/issues/101) |
| E055 | [来源去重、时间版本与字面补候选](E055-dedup-time-and-literal-replay/README.md) | Does not work | 2026-11-29 | [#101](https://github.com/yaodiff/memory-lab/issues/101) |
| E056 | [无漏题导向的高频页批量补问法](E056-blind-faq-enrichment/README.md) | Does not work | 2026-11-29 | [#101](https://github.com/yaodiff/memory-lab/issues/101) |
