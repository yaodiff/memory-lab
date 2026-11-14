# Memory Lab: correction-driven team memory for coding agents

English · [中文](README.zh.md)

> Status: early draft. Nothing here is benchmarked yet.

**One line**: we evaluate team memory for coding agents by asking *"does the agent still get corrected?"*, not *"can it recall a fact?"*.

Memory Lab is three things in one repo:

1. **Essays**: field notes from running team memory for coding agents in practice, including the negative results.
2. **Bench**: *Next-step Replay*. Cut a real (here: synthetic, open-source-repo) agent session just before a human correction, replay it with and without memory, and let two independent judges score whether the plan still violates the team convention.
3. **Reproductions** of well-known memory papers (Mem0, A-MEM, Generative Agents, Agent Workflow Memory…) on public datasets, each compared against the ideas above.

A small reference implementation (`memlite/`) exists only to make the experiments runnable. It is not a product.

## The three gates

A team convention only helps if it passes three gates:

| Gate | Question | Typical failure |
|---|---|---|
| **Written right** | Was the correction captured as a reusable rule with its scope intact? | Captured as progress or a one-off; scope ("first phase only") dropped; mid-task side remarks never captured |
| **Found** | Does the agent search *at the decision point*, with a query that matches the rule? | Agent searches for the task at hand, while the rule is about "how we do this kind of step" |
| **Used** | Having read it, does the agent follow it? | Read in full, then partially followed |

Details: [essay 01](essays/01-three-gates.en.md).

## Essays

Each essay is written in Chinese first, with an English version covering the same content.

| # | English | 中文 |
|---|---|---|
| 01 | [Three gates for team memory: written right, found, used](essays/01-three-gates.en.md) | [团队记忆的三道关：写对、搜得到、用得上](essays/01-three-gates.md) |
| 02 | [Reading Anthropic's "components of agent memory" against field data from team memory](essays/02-reading-the-components.en.md) | [用团队记忆的一线数据读 Anthropic 的「记忆组件」](essays/02-reading-the-components.md) |

## Layout

```
essays/            field notes: NN-slug.md (zh) + NN-slug.en.md (en)
bench/
  next-step-replay/  session cutting, case building, replay runner
  datasets/          loaders for public data + synthetic session generator
  judges/            judge prompts, agreement stats
memlite/           minimal reference memory: typed pages, sentence-level provenance,
                   write decisions, consolidation with hard constraints, retrieval that explains empty results
reproductions/     one folder per paper: README (what / numbers / gaps vs paper) + run.sh
docs/              related work, CoALA mapping
```

## Roadmap

- [x] Essay 01: the three gates (draft)
- [x] Essay 02: reading Anthropic's components of agent memory against our field data (draft)
- [ ] Essay 03: same-session leakage inflates memory evals
- [ ] Essay 04: step-conditioned retrieval
- [ ] Bench: "look back and verify memory" arms on Next-step Replay (planned in essay 02)
- [ ] Repro: Mem0 vs full context on LoCoMo
- [ ] Repro: A-MEM link evolution ablation on LoCoMo
- [ ] Bench: Next-step Replay demo on one open-source repo (5–10 synthetic corrections)

## Data policy

Only public datasets and synthetic sessions on public open-source repositories. No proprietary code, sessions, or documents. Examples in the essays are rewritten or synthetic; internal measurements are given only as ratios or in coarse terms, with no raw data, and are labelled as small samples from our own setting.

## Contributing

Every change goes issue → PR → checks → squash merge; `main` is protected. See [CONTRIBUTING.md](CONTRIBUTING.md).

## License

Apache-2.0
