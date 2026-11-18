# Three gates for team memory: written right, found, used

English · [中文](01-three-gates.md)

> These observations come from a small internal sample of team conventions for coding agents.

## In one line

When you build team memory for a coding agent, the question that matters most is not "can it remember?" but "**does the same person still have to correct it for the same thing?**" Asked that way, a team convention has to pass three gates: **written right, found, used**. Each gate fails differently, and each needs a different fix.

## Why not an existing benchmark

Benchmarks such as LongMemEval and LoCoMo bury a fact in a long conversation and ask about it later. They measure **fact recall**: what the user said they liked last week, which day something happened.

The valuable part of team memory is a different kind of thing:

- **Conventions**: "run check X before committing in this repo"; "trace calls with tool Y, don't grep the logs yourself".
- **Decisions**: "use approach A for the first phase, switch in phase two".
- **Lessons**: "this error is actually an expired credential, not a network problem".

Nobody asks about these directly. They matter only when the agent is **about to take a particular step**, and nobody reminds the agent that now is the moment to recall them. So the unit of evaluation has to change: not "a question" but "**a correction**".

## Corrections are free supervision

When a user corrects an agent ("no, you need to … first", "that's not how we do it"), the correction tells you three things:

1. There is a team convention here (or a personal preference; keep the two apart).
2. The agent didn't follow it.
3. The moment just before the correction is the decision point where the convention should have applied.

Reconcile every correction worth remembering against memory, and sort it into one of three outcomes:

| Outcome | Meaning | Which gate is leaking |
|---|---|---|
| The page already existed, and the agent was still corrected | Memory had it; the agent didn't use it | Found / used |
| Never learned, or learned only in part | The correction happened; memory has nothing, or an incomplete version | Written right |
| Learned afterwards | Written into memory after the correction | Expected; check next time whether it took effect |

This table can be produced automatically every night, far more cheaply than any manual labelling. **A different model can reclassify some corrections originally marked "never learned".** Use at least two independent judges, report their agreement, and review every disagreement.

## Gate 1: written right

The common ways a write goes wrong:

- **Progress recorded as a decision.** "Changed A first today" becomes "the team decided on A".
- **A one-off request recorded as a rule.** The user says "skip the tests this time" and it becomes a team convention.
- **Scope dropped.** "First phase", "unreleased versions" get deleted as irrelevant detail, and the conclusion becomes broader than it was. We tried an automatic checker to "clean up" decision pages; in blind review the old versions won more often than they lost, because the checker had deleted the scope.
- **Side remarks in a long task never captured.** The extractor organizes pages by task topic, so off-topic environment and collaboration conventions get dropped (for example "don't start a database locally, use the shared test environment" or "links you give the user must open directly").

One counter-intuitive gain: **don't store facts you can read straight from the code.** A stored copy only goes stale and then contradicts the code. On any conflict, the code and merged changes win.

## Gate 2: found

This is where we spent the most time, and where we were most surprised.

The short version: **ranking is mostly fine; the problem is what the agent asks for.**

- Using a correction summary as the query usually puts the relevant page near the top. When the query is right, ranking is good enough.
- But the queries the agent actually sends describe **the task in hand** (say, "commit this branch's changes and push them"), while the convention describes **how to do this kind of step** ("which checks to run before committing"). The two aren't talking about the same thing.
- Rewriting the query on the server (extract the action phrase, rephrase as "how does the team do this step") rescued none of them, because that meaning simply isn't in the agent's query.
- Rewording the Skill, compressing results, adding an index: on a replay of "the moment just before the correction", almost nothing changed item by item. Items that were found stayed found whatever we changed; items that were missed stayed missed.

The direction we want to try is **step-conditioned retrieval**: when searching, the agent also writes "the step I'm about to take", we run a second search on that step and merge it with the original results. Offline pre-checks recover part of the "how does the team do this" conventions, but not domain decisions. That is the subject of essay 04.

## Gate 3: used

Reading the whole page and following only part of it was the most common failure in this small sample. The page spells out the requirement, yet the agent adds a design of its own or skips a detail.

So instrument it in layers, at least these: **did it search → did it find the right page → did it read it in full → did it follow it.** A single "adoption rate" won't tell you what to fix.

## The biggest pitfall: same-session leakage

For the evaluation, take the step just before a correction in a real session, have the agent produce a plan with memory and without it, then judge whether the plan violates the convention. Across this small sample, violations were less frequent when memory was available.

Checking the origin of each page showed that many pages **had been learned from the same session** and some were updated after the correction. The memory arm had effectively seen the answer in advance. Looking only at cases where the page came from another session and had no updates after the correction, **we saw almost no gain**.

This deserves its own essay ([essay 03](03-same-session-leakage.en.md)). The conclusion is simple: **when evaluating team memory, split out same-session cases by page origin**, or the gain will be badly overstated.

## Another class of incident: pipelines that break silently

Many "not found" problems have nothing to do with the retrieval algorithm:

- The storage layer quietly changed the write path while reads and deletes stayed the same, so recall lost pages and cleanup deleted the wrong ones.
- Message ingestion stopped for several days and nobody noticed.
- An environment variable wasn't expanded, and a batch of memories went into an empty space.
- An expired credential returned an empty result, which was read as "there's really nothing".

So **an empty retrieval result must carry a reason** (truly nothing / blocked / broken), and every write should be read back for a consistency check.

## Summary

| Gate | Check this first | Don't start with this |
|---|---|---|
| Written right | Was the scope kept? Were mid-task corrections captured? | Adding a checker to "clean up" pages |
| Found | Did the agent search at the decision point? Is the query the task or the step? | Tuning ranking, rewording |
| Used | Of the pages read in full, how many were followed? | Watching a single adoption rate |
| Evaluation | Split out same-session cases; use two judges | Drawing conclusions from the overall comparison |

Next: ["Reading Anthropic's 'components of agent memory' against field data from team memory"](02-reading-the-components.en.md). After that: ["Your memory eval may be inflated: same-session leakage"](03-same-session-leakage.en.md).
