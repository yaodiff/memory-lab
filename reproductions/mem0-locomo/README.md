# Repro 1: Mem0 vs full context on LoCoMo

- Paper: *Mem0: Building Production-Ready AI Agents with Scalable Long-Term Memory*, arXiv 2504.19413
- Code: https://github.com/mem0ai/mem0
- Data: LoCoMo, arXiv 2402.17753, https://github.com/snap-research/locomo (check the license before redistributing anything)

## What we reproduce
- Accuracy (LLM-judge), tokens per query and p50/p95 latency for:
  1. full context
  2. Mem0 (vector)
  3. Mem0g (graph), if it is cheap enough
- Start with 1–2 conversations, then all 10.

## What we add
- **Write-decision audit**: sample 50 ADD/UPDATE/DELETE/NOOP decisions and label them by hand. How often does an UPDATE drop the scope of the original fact?
- Two judges and their agreement rate, instead of one judge.

## Known caveats
- We rerun every baseline ourselves and do not copy numbers from the paper.

## Status
- [ ] `run.sh` skeleton
- [ ] 1-conversation smoke run
- [ ] full run and a results table
