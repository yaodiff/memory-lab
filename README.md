# Memory Lab: correction-driven team memory for coding agents

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

Details: [essays/01-three-gates.md](essays/01-three-gates.md).

## Layout

```
essays/            field notes (zh first, en later)
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

- [ ] Essay 1: the three gates
- [ ] Essay 2: same-session leakage inflates memory evals
- [ ] Essay 3: step-conditioned retrieval
- [ ] Repro: Mem0 vs full context on LoCoMo
- [ ] Repro: A-MEM link evolution ablation on LoCoMo
- [ ] Bench: Next-step Replay demo on one open-source repo (5–10 synthetic corrections)

## Data policy

Only public datasets and synthetic sessions on public open-source repositories. No proprietary code, sessions, or documents. Examples in the essays are rewritten or synthetic; internal measurements are described qualitatively only.

## License

Apache-2.0
