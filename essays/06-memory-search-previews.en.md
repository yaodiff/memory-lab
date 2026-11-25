# Why did the agent use less memory when the ranking stayed the same?

English · [中文](06-memory-search-previews.md)

> Field notes. The live observations and offline replay come from small internal samples, reported as coarse proportions. The configuration example is synthetic.

## The result text goes into the agent's context

We replaced excerpts from team memory pages with generated summaries in search results. The summaries gave a quick sense of each page's subject. After the switch, **the share of searches for which the agent used at least one returned page fell by about a quarter**. That's a relative change in a search-level rate. Using several pages still counts once, and the denominator is all searches in the measured scope.

We first checked how searches were counted and found that some test traffic had been included in live metrics. Fixing the classification narrowed the drop in first-result adoption. That metric asks whether the first result from a particular search was used in the same session. The quarter-drop figure measures adoption of any result. A later breakdown still left some of the live gap unexplained, so the size of the summary's contribution remains open. After we restored excerpts, answer quality mostly recovered. First-result adoption showed a smaller recovery, with insufficient statistical evidence.

[The three gates essay](01-three-gates.en.md) asks what happens after the agent finds the right page. There's a decision in between finding and following it. Can the agent tell which result to open, or whether the rule visible in a result applies?

## Freeze the ranking and swap the visible text

For each question, the replay used the same pages in the same order. One arm saw generated summaries and the other saw excerpts. That fixed the candidate set and positions. The rates below are per question, with each arm's replay questions as its denominator.

| Replay measure | Generated summary | Body excerpt |
| --- | --- | --- |
| Questions judged to require the full page to answer | About nine in ten | About half |

This measured whether the visible text carried enough information. The simulated agent couldn't open the full page, so the replay couldn't measure actual open rates, the cost of extra reads, or how much an extra read would recover. It also used one model with one run per condition. The result points to a plausible bottleneck in the text the agent sees. Estimating its live impact requires a live comparison.

With fixed rankings, a first-result hit rate computed only from page IDs and positions is identical by construction. A regression suite that stops there would give both responses the same score, even if only one tells the agent when a rule applies.

## What should a useful preview contain?

Take a synthetic case. An agent is building a configuration updater for a sample project and is about to remove keys it doesn't recognize. Two search results point to the same page.

- Topic summary. “This document explains compatibility requirements and testing for configuration updates.”
- Evidence-bearing preview. “Preserve unknown keys when updating a user's configuration in place. Only an explicit reset may delete them. After changing the write path, run a round-trip test with an unknown key.”

The first helps decide which page to open. The second also supplies the condition, the exception, and the check needed at that decision point. An excerpt that shows only “preserve unknown keys” introduces a risk of its own. The agent may apply the rule during a reset. Both generated summaries and excerpts can lose scope. Link to the source, and tell the agent to open it before acting when the condition or exception doesn't fit in the preview. If sources disagree, check their scope and version before using either.

## How to evaluate a preview change

Start on development questions with three options: body excerpts, topic summaries, and summaries that preserve conditions and sources. Freeze the questions, page revisions, candidate order, and display budget at each position. Fix the model, tools, and scoring rules. Tune on the development set and evaluate on a holdout with separate sources. Run a paired preview-only comparison first, then repeat with the same full-page access and reading budget in both arms. The second pass measures how much an agent can recover and what it costs.

| Layer | What to record |
| --- | --- |
| Find | On questions with a labeled relevant page, did it appear and where? With fixed rankings, use this as an integrity check. |
| Understand | On questions with usable evidence, did the preview carry the rule and conditions needed for the decision? Track incorrect scope, stale guidance, and unsupported claims separately. |
| Read | Across valid replay questions with full-page access enabled, how often did the agent open a page, how many reads did it make, and how long did it take? |
| Act | Across valid replay questions, did the agent take the right next step? Check specific actions where a rule applies and inappropriate use where none applies. |

Set the primary measure and acceptable regression before release. Report paired wins and losses with an uncertainty interval. Inspect cases that require a full read, invite overapplication, or lack supporting evidence. Hide the arm from reviewers and resolve disagreements against the evidence and proposed action. Then use a live comparison that isolates test traffic to measure actual adoption, and audit a sample of actions to validate that signal. Until that comparison is available, the replay can inform the choice of baseline. The live effect remains an open measurement.

[Next-step Replay](../bench/next-step-replay/README.md) evaluates what the agent does at a decision point. The same question applies to a preview change. Once the rule appears in the results, does the agent take the right next step?
