# Reading Meta's Self-Improving Memory: the model rewrites its own memory prompts, then learns them

English · [中文](04-self-improving-memory.md)

> Draft v1. The paper's numbers are quoted from the source. Observations attributed to "us" come from running a team memory system internally; we give them only in coarse terms, from small samples, in a setting of team conventions for coding agents. The companion experiment is [E004](../experiments/E004-meta-optimized-memory-prompts/README.md), on synthetic data only.

## In one paragraph

Meta FAIR's [Self-Improving Memory: Meta-Optimization and Harness Distillation for Continual Learning Agents](https://facebookresearch.github.io/RAM/blogs/self_improving_memory/) (Tong Chen, Jason Weston and others; [source files](https://github.com/facebookresearch/RAM/tree/main/projects/self_improving_memory)) was first committed to its repository on 2026-11-10; we read the 2026-11-17 revision. As of 2026-11-20 we found only the blog post, no arXiv paper, so the post is our source.

It does two things. First, the model **rewrites its own memory prompts** (LOAD and OFFLOAD) per task and keeps the best-scoring versions. Second, it runs with those prompts, **swaps them back to the generic ones** in the recorded runs, and is fine-tuned on the result, so that it manages memory that way under generic prompts too. Numbers: generic prompts 36.1, optimized 56.0 (best hand-written 44.6); after distillation, 43.1 under generic prompts versus 37.6 for the control.

Our take: the first step's evidence is solid but has a "selected and reported on the same tasks" flavour; the second step's gain is real, but it recovers only about a third of the first step's gain. For team memory, the most useful part is not the automatic prompt search but what it found: **read guardrails before facts, mark each fact's status, write failures as IF→THEN rules, and keep an index instead of one ever-growing file**.

## The problem

An agent works through many related subtasks. Each subtask starts with an empty context; only a memory directory (Markdown files, read and written with file tools) carries over. **What to write, how to organize it, and when to read it back** are decided today by hand-written prompts, and no single prompt wins on every task.

The post's pilot (Figure 2) compares a generic prompt with four hand-written memory strategies (summary, retrieval, skill library, hypothesis tracking) on three Continual Learning Bench tasks (Database question answering, Codebase bug fixing, Spectrum analysis). Each task has a different winner. That matches the benchmark paper's own finding that dedicated memory systems do not fix cross-instance reuse ([Asawa et al., 2026](https://arxiv.org/abs/2606.05661)).

So the authors argue that the model should discover its memory strategy itself, and then have it trained into its weights.

## Method

### The generic harness

- The memory directory starts empty and persists across the task stream.
- After each subtask an OFFLOAD prompt asks the model to update memory; then the context is cleared.
- Before the next subtask a LOAD prompt lets the model read memory (at once, say a README, or later on).
- The generic LOAD and OFFLOAD are deliberately short. From Figure 1: LOAD "Read your memory directory." OFFLOAD "Update it. What to keep is your decision."

### Step 1: harness optimization (Discover)

A meta agent reads the task agent's trajectories and scores and rewrites LOAD and OFFLOAD; an outer loop evaluates and keeps candidates:

1. Seed pool: four hand-written harnesses (summary, retrieval, skill library, hypothesis tracking).
2. Each candidate runs the full task stream N times (e.g. 5), recording trajectories, subtask scores and final memory directories.
3. Rank by mean score and take the top P (e.g. 4) as parents.
4. For each parent, the meta agent summarizes each subtask, then each run, then consolidates across runs into revised LOAD and OFFLOAD. The revision joins the pool.

Repeat for some iterations and keep the best survivor. The post says selection uses the mean score on a holdout the meta agent cannot see.

**What the search found** (Figure 1, Database task):

> LOAD: Read GUARDRAILS.md, then SCHEMA.md. Before answering, check price unit and timestamp type; target ≤5 queries.
> OFFLOAD: Record each group's price unit and timestamp format (CONFIRMED/UNTESTED); log failures as IF→THEN rules.

The Codebase revisions (Figure 7) tell the story best:

| Version | Gist of LOAD / OFFLOAD | Score |
| --- | --- | --- |
| Generic | Read memory; decide yourself what to keep | 33.5 |
| Hand-written "summary" | Read the one running summary; fold each lesson into it | 34.3 |
| Meta report | Every run kept one linearly growing file; agents still searched for the repository again, corrupted files with sed, and were blocked by already-failing tests | — |
| Iteration 1, better | Reuse the recorded repository path, reproduce the bug first, run all tests before submitting; keep a quick reference, pitfall rules and a fix log, and **add a rule after each failure** | 52.2 |
| Iteration 1, weaker | Record the repository root and test command; cap memory at 4,000 characters and **keep details of only the last two fixes** | 36.6 |
| Meta report | One append-only file with no index from symptoms to fixes, so agents re-explored solved problems | — |
| Iteration 2, best | Read a short quickstart and the symptom-to-fix index, **restate the matching fixes and rules, then follow them**; keep a capped quickstart, one file per fix, merge duplicates after failures | 55.7 |

### Step 2: harness distillation (Demonstrate → Distill)

1. Run the base model with each task's best harness on the train subtasks, logging every call: prompt, response, reasoning, tool calls and tool results.
2. In the logs, **replace the optimized LOAD and OFFLOAD with the generic ones**, keeping the responses. The argument for why this works: the optimized harness prescribes one memory design, while the generic harness leaves the design to the model, so the behaviour is still consistent with the generic prompt.
3. Pool the tasks, compute the loss only on assistant tokens (reasoning and tool calls included), normalize per task by supervised-token count so each task weighs the same. LoRA rank 64 on the attention projections.

The meta agent and the task agent are the same model (Kimi-K2.6), so the model learns memory skills it discovered itself.

## Evidence and numbers

All from the post's Figures 1, 4, 5 and 6 and its text. Model: Kimi-K2.6. Three Continual Learning Bench tasks; the train split is the early part of each task stream and the test split the later part, cut at the phase transition the benchmark builds in.

**Harness optimization** (Figure 4, test scores; 95% CIs in the original figure)

| | No memory | Compaction | Generic | Best hand-written | Optimized |
| --- | ---: | ---: | ---: | ---: | ---: |
| Database | 7.5 | 39.8 | 32.3 | 47.9 | 53.8 |
| Codebase | 31.8 | 36.9 | 33.5 | 43.7 | 64.3 |
| Spectrum | 21.9 | 34.6 | 42.5 | 42.1 | 49.9 |
| Average | 20.4 | 37.1 | 36.1 | 44.6 | 56.0 |

**Harness distillation** (Figure 5, all evaluated under generic prompts, ten matched evaluation seeds)

| | No SFT | SFT on generic trajectories | SFT on optimized trajectories (prompts swapped back) |
| --- | ---: | ---: | ---: |
| Database | 32.3 | 31.6 | 37.7 |
| Codebase | 33.5 | 37.5 | 45.1 |
| Spectrum | 42.5 | 43.6 | 46.5 |
| Average | 36.1 | 37.6 | 43.1 |

**The search itself** (Figure 6): 37 of 44 revisions generated by the meta agent did not beat the best score from earlier iterations. Database and Spectrum reached 53.8 and 49.9 in the first generation and never improved; only Codebase kept climbing, to 64.3 in the fourth. On Spectrum, generic and optimized score almost the same on the first subtask (21.7 and 21.9); the gap opens as experience accumulates (test means 42.5 and 49.9).

## Limits

1. **"Best" is picked among evaluated candidates.** The authors say so: both the hand-written seeds and the optimized harnesses are selected by task score, so these are the best observed scores among candidates. They select on a holdout, but report no number for a frozen harness on a task stream that took no part in selection. How much of 56.0 vs 44.6 is selection optimism cannot be read off.
2. **Three tasks, one model.** Meta agent and task agent are both Kimi-K2.6; no other models or task families.
3. **Distillation recovers only part.** Optimized prompts gain 19.9 over generic; the distilled model gains 7.0 over no fine-tuning, which the authors call descriptive because the base model was evaluated separately. The matched comparison is 43.1 vs 37.6 (+5.5). On Database, training on generic trajectories scores below no fine-tuning (31.6 vs 32.3).
4. **Where the distillation gain comes from is open.** The authors "hypothesize that the gain partly reflects improved memory organization and retrieval, alongside task-solving behavior, but isolating this mechanism requires direct behavioral analysis." Whether the tuned model got better at using memory or just at these three tasks is not yet separated.
5. **The search is expensive and mostly misses.** Each candidate runs the whole stream five times; 37 of 44 revisions were wasted. No token or cost figures.
6. **Swapping prompts assumes the behaviour still fits the generic prompt.** That is an argument, not a test: nobody checks whether the swapped trajectories are something the model would produce under the generic prompt.

## How far to trust it

- **Trust "no hand-written memory strategy wins everywhere."** The pilot, the benchmark paper and [Yang et al., 2026](https://arxiv.org/abs/2604.11610) agree, and in team memory we also see different workspaces and task types favour different ways of writing.
- **Trust "rewriting prompts per task gains a lot", with a discount.** The direction is credible (the Codebase story makes sense, and the misses are reported), but the size waits for a select-then-test-on-fresh-streams number. Our small experiment [E004](../experiments/E004-meta-optimized-memory-prompts/README.md) tries exactly that.
- **Stay neutral on "distilling into weights."** The +5.5 has a matched control and is real, but we do not train models, so this half matters to us only indirectly: it shows good memory behaviour can be moved out of the prompt. For us, the place to move it is the default flow of the Skill and the extraction prompts.
- **What is most worth taking is the writing patterns the search found.** They overlap heavily with mistakes we have made; see the next section.

## Against what we do

Our setting: coding agents in a multi-person team. Memory is a wiki (rules, decisions, experiences, entities, events) that a background pipeline extracts from sessions; agents learn when to search and how to use hits from a Skill. The biggest difference from the paper: **its LOAD/OFFLOAD prompts govern both writing and reading, while for us writing belongs to the background extraction prompts and reading to the Skill, tuned separately.** Four points of comparison:

### 1. Read order: guardrails first, facts second, restate before acting

| What the search found | What we do now | What to borrow |
| --- | --- | --- |
| Database: read GUARDRAILS.md before SCHEMA.md; check price unit and timestamp type before answering | At the start, search once with the request verbatim, then once for rules only; search again at decision points mid-task | We have "guardrails" (the rules-only search), but read them after the task search. Worth trying: read the prohibitions for this kind of step first |
| Codebase best: read the quickstart and the symptom-to-fix index, **restate the matching fixes and rules, then follow them** | Before delivery, check the diff against the rules read, one by one | Our check comes after acting. In [essay 01](01-three-gates.en.md) the leakiest gate is "used": read in full, then only partly followed. Moving "restate the matching rules" before acting is cheap and testable |

### 2. Extraction prompts: an index, one problem per page, merge after failures

| What the search found | What we do now | What to borrow |
| --- | --- | --- |
| One file per fix; a capped quickstart; merge duplicates after failures | One problem per page; the background consolidation merges the same experience | Already aligned |
| A symptom-to-fix index | Rules have a category index; experience pages have no index by error symptom | Add an index from "error text / symptom" to experience pages; it matches the moment an agent searches with an error mid-task |
| The weaker revision capped memory and kept only the last two fixes: 36.6 | Our consolidation has also lost facts when merging | Confirms it: cutting history to control length hurts more than not controlling length |

### 3. The scope of failure lessons

The paper's OFFLOAD says "add a rule after each failure", written as IF→THEN. Our extraction prompt also asks experience pages to spell out branches as IF/THEN. But a failure we have hit is **one failure turned into a permanent rule with its scope widened, misleading later tasks** ([#19](https://github.com/yaodiff/memory-lab/issues/19) tests this). The useful thing about IF→THEN is that it forces a condition to be written: the IF half is the scope. What to borrow is to write the IF as **the observed condition** (which system, which error, which prior state), not an inferred general one; with a single source, the IF keeps "observed once, when X".

### 4. CONFIRMED / UNTESTED status marks

The paper's Database OFFLOAD marks each fact CONFIRMED or UNTESTED. Our decision pages carry a status (decided / rejected / retired), but **single facts inside experience and entity pages carry no "was this verified" mark**: a command paraphrased from a chat looks the same as one that was run. The Skill has a patch rule, "run an entry with a command or path before adopting it", but the agent cannot tell from the page which ones need running.

There is a conflict to handle with care. Our extraction prompt **deliberately keeps** one-off verification results and progress out of experience pages ("deployed and verified", "passed N tests"), because spot checks showed such status goes stale fast and readers take it as current. The paper's CONFIRMED marks **the basis of the fact itself** (this group's price unit was confirmed by feedback), not task progress. So what to borrow is a mark for the kind of basis: the command was run / checked against code / someone said so in a chat, not "verified on some day". The Skill then asks for a check only on the last kind; an entry that was corrected falls back to "said so".

### 5. Automatic prompt rewriting itself

In the paper, 37 of 44 rewrites did not win, and Database and Spectrum stopped improving after the first generation. That matches our experience rewriting the Skill: in a small internal sample, even the best version separated from the baseline on only a few items. **Rewriting is cheap; evaluation and selection are the cost.** To use a meta agent on our Skill or extraction prompts, we would first need a frozen evaluation set isolated from the rewriter, and a report on items that took no part in selection.

## Our small experiment: E004

What we wanted is the number the paper does not give: **does a memory prompt selected and frozen on one world still beat the generic prompt on fresh worlds that took no part in selection?** The setup is a synthetic unit-inference task (is a group's price in cents or dollars, its quantity in units or dozens; only feedback tells), with a small model as both task agent and meta agent and the decision line fixed before running. Details and every reading are in [E004](../experiments/E004-meta-optimized-memory-prompts/README.md).

| Arm | Mean accuracy over 3 fresh worlds |
| --- | ---: |
| No memory | 0.17 |
| Generic | 0.57 |
| Hand-written "summary" | 0.57 |
| The paper's Database prompt, transplanted | 0.43 |
| Selected by search (= the generic prompt, run again) | 0.36 |

- **None of the 4 meta rewrites beat the best seed**, so the search selected the generic prompt itself. Same direction as the paper's 37 misses out of 44.
- **The same prompt run twice differs by 0.21**, and by 0.29 in one world. At this scale the noise is larger than any gain the paper reports. By the pre-registered line the verdict is "does not work", but the more accurate reading is that this scale cannot measure the effect of meta-optimization.
- **The paper's searched prompt does not transfer**; it got every post-flip question wrong.
- One failure directly relevant to team memory: one run wrote "all prices are in cents" as a global rule after the first question, then got 12 of the next 13 wrong. Memory recorded every contradicting feedback, but the rule never changed. That is point 3 above, "one observation turned into a permanent rule", and it appeared at random under the same prompt. Prompt wording alone is not enough; the IF condition and the basis status are better made part of the memory format.

## Summary

| Finding | Strength of evidence | For team memory |
| --- | --- | --- |
| No hand-written memory strategy wins everywhere | Strong, several sources agree | Agree |
| Rewriting prompts per task gains 11 to 20 points | Direction credible; size includes selection bias; our small test cannot measure it | Take the patterns it found; hold off on automatic search until a frozen eval set exists |
| Distillation moves part of the gain into weights | +5.5 with a matched control | We do not train models; the equivalent is making these the defaults in the Skill and extraction prompts |
| Patterns found: guardrails first, restate then act, basis status, IF→THEN, symptom index | Case studies | Four testable changes: restate rules before acting, read rules first, write the observed IF condition, mark the kind of basis |
