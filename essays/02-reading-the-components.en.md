# Reading Anthropic's "components of agent memory" against field data from team memory

English · [中文](02-reading-the-components.md)

> Draft v1. Numbers attributed to "us" come from running a team memory system internally. We report them only as ratios or in coarse terms, with no raw data or examples. Samples are small, and the setting is team conventions for coding agents; don't read them as general claims. Anthropic's numbers are quoted from their post.

## In one paragraph

On 2026-11-06 Anthropic published [The components of agent memory](https://www.anthropic.com/research/components-of-agent-memory). It breaks agent memory into a few parts: notes written during a session, an injected top layer, representations such as wikis, and offline consolidation ("dreaming"). We lined it up against the three gates from [essay 01](01-three-gates.en.md) (written right / found / used):

- **Written right and found**: their findings point the same way as ours, though they land on different things.
- **Used**: they give it one sentence. In our data it is the gate that leaks the most.
- **Consolidation**: we have hit almost every failure mode they describe, plus a few more.

## What kind of comparison this is

- **Different settings.** Their experiments are database Q&A on CL-Bench, playing Pokémon, and answering questions or drafting legal briefs over document collections: one agent, with a ground truth to check against. Ours are coding agents on multi-person teams, where the supervision signal is a human correction and there is no answer key.
- **Neither sample is large.** Some of their experiments use 25 or 24 questions. Ours are smaller: a few dozen items, two passes per arm.
- So what follows is "where the directions agree" and "where they don't". It is not a reproduction, and it is not a verdict on who is right.

## Gate 1: written right ↔ "memory is a prediction"

**What they say**

- Writing down a rule is a prediction that the pattern will matter again.
- The Pokémon comparison: an older model saved everything, hundreds of files that kept going stale as the game changed, until it spent more time combing through memory than playing. A newer model saved only what the screen couldn't tell it (strategy, plans, tested rules), wrote far fewer files, and got much further.
- **Tell the model what memory is for, not how to use it.** On CL-Bench, just telling strong models that a memory folder existed was enough. Adding a fixed rule such as "record only failures" cost them much of the gain memory had given them. For an older model, on the other hand, prompting it to read memory before answering and to test its theories nearly doubled its score.

**Where we agree**

- Essay 01's rule "don't store facts you can read straight from the code" is the same idea as "don't store what's on the screen": a stored copy goes stale and then contradicts the real state.
- **Rewording prescriptive instructions is not the lever.** On Next-step Replay (cut a real session right before a correction and replay it) we compared several versions of the memory-usage Skill: key points at the top of each page, compressed results, an added index. On 49 real items with two passes per arm, the best variant beat the baseline on one item, lost on one, and tied on the rest. The baseline gave identical results on both of its passes.

**Where we don't, and what to keep in mind**

- Their instructions are about *how to write* memory. Ours were mostly about *how to use* it: when to search, how to phrase the query, how results are shown. Both point to "prescriptive instructions aren't the lever", but they target different things, so neither counts as evidence for the other.
- They saw fixed rules *hurt*. We saw *no difference*. Our reading is not that the model already judges well on its own. The bottleneck is just somewhere else (see gate 2).
- Teams add a problem their setup doesn't have: the session that writes a memory is not the one that uses it, and often belongs to a different person. "Predicting future use" here also means predicting *who* will need it, and *at which step*. That makes **scope** ("first phase only", "unreleased versions") worth more than the conclusion itself. Essay 01's checker that deleted scope as a detail, leaving the rule broader than intended, is this failure.
- A sizable share of those 49 items were misaligned: the correction and the last user message before it were about different things. After cleaning, only about half passed both checks. So "no difference" means "no measurable difference on this set", and no more.

## Gate 2: found ↔ "keep the injected layer small" and "wiki + search"

**What they say**

- Memory is layered. The top layer is injected at the start of every session; lower layers are read or searched when needed. The top has to stay small: it costs tokens, a wrong note gets carried into every session, and loading a note doesn't guarantee the model acts on it. Claude Code's auto memory loads only the first 200 lines or 25 KB of `MEMORY.md`, used as an index of what Claude knows and where to find it.
- On a company document corpus of about 350,000 files, wiki + search rose from 54% to 61% as the wiki grew. Search alone scored 53%; the wiki alone peaked at 48%. Wiki + search also saved about 20,000 tokens per question. The wiki helped a lot on items that needed facts from several documents (87% vs 73%), and showed no clear gain where one document was enough.

**Where we agree**

- By default we inject **nothing**. A usage Skill plus a set of search tools, and the agent decides when to search. In their terms, our top layer is close to empty and everything rides on retrieval.
- **When the query is right, ranking is good enough.** Using the summary of a correction as the query puts the right page in the top 3 most of the time.
- **Misses come from query mismatch.** At the decision point the agent searches for the task in hand ("commit this branch and push it"), while the convention is about how to do a kind of step ("which checks to run before committing"). Among those 49 items, one group was found by every arm on every pass and another group was missed by every arm on every pass. Whether the agent's natural query at that moment matched the page decided the outcome, not the Skill wording. Rewriting the query server-side rescued nothing, because the meaning wasn't in the query to begin with.

**How this connects to their layering**

- One reading of why wiki + search beats search alone: the wiki is a map, so the agent doesn't need to know what to search for first. *(Inferred.)* That is exactly where we hurt. Our failures aren't ranking; the agent doesn't know there is a convention for this step.
- But their tasks are Q&A and brief writing, where the task itself is the query. A team convention for a coding agent has to come to mind when **nobody is asking**. Their experiments don't cover that.
- Top-layer injection is expensive for teams: the conventions an active team builds up don't fit in 200 lines, and stuffing them in runs into "longer instructions, lower adherence". We'd rather try a third route, **step-conditioned retrieval**: when searching, the agent also writes one line, "the step I'm about to take", and we run a second search on that step and merge the results. Offline pre-checks recover part of the "how does the team do this kind of step" conventions, though not domain decisions. More in essay 04.

## Gate 3: used ↔ "loading a note doesn't guarantee Claude acts on it"

**What they say**

One sentence, in the section on the injected layer: loading a note doesn't guarantee Claude acts on it, and the Claude Code docs warn that longer instruction files reduce adherence. Elsewhere they note that an older model often didn't read its memory folder at all, but that is about reading, so it still belongs to gate 2.

**What we see**

- Across a few dozen real corrections we split each case by where it got stuck: didn't search; searched but missed the right page; read the page in full but didn't fully follow it; followed it. **The biggest bucket is "read in full, didn't fully follow", close to four in ten**, larger than either "didn't search" or "didn't find".
- With the right page placed directly in front of the agent, no search needed, **about one plan in five still violated the convention**.
- "Didn't fully follow" mostly looks like one of two things (rewritten, synthetic examples, not real cases):
  - **A missed detail.** The convention says "when you change a public interface, update the callers and the docs and commit them together." The agent updates the interface and the callers and leaves the docs alone.
  - **Extra design.** The convention says "config changes in this repo go through the existing loader; don't add a new read path." The agent reads it, then writes a small wrapper "for clarity".

Part of why this gets one sentence in their post, we suspect, is that most of their tasks have an answer key: if the note is right, following it scores, so "read it but followed half" rarely shows up on its own. Team conventions often carry several points, and an agent can easily get the main one right and drop another. *(Inferred.)*

**Why this gate is the hardest to measure**

1. **No natural signal.** Searches are logged and page reads are logged. Following shows up only in later behaviour, and often only partly. Asking the agent to report "I used this" tells you it read the page, not that it followed it.
2. **Judging has to go point by point.** A convention has several points, so "followed" means checking each one. A single right/wrong label swallows partial compliance. Judges are noisy too: rejudge the same batch with another model and some labels flip. So use at least two independent judges, report agreement, and read every disagreement.
3. **It is tangled with the other two gates.** The final violation rate alone can't tell "not found" from "not followed".
4. **Leakage contaminates it easily.** If the page was learned from the session under test, the memory arm has effectively seen the answer (essay 03 covers this).

**How Next-step Replay measures it**

- Cut the session at the last user message before the correction and drop everything after it. The public version uses synthetic sessions on open-source repositories.
- One arm is `oracle_page`: the right page goes straight in front of the agent. It short-circuits "found", so whatever violations remain are pure "used" failures.
- Judges score each plan per convention point as `full` / `partial` / `violates`. Two independent judges; report agreement across the three labels.
- Funnel: searched → right page found → read in full → followed. The gap between `memory_search` and `oracle_page` is the loss at "found"; the gap between `oracle_page` and a perfect score is the loss at "used".
- Report separately by page origin (another session / the same session / written after the correction).

Case format and arm definitions: [bench/next-step-replay](../bench/next-step-replay/README.md).

## Overnight consolidation ↔ dreaming

**What they say**

- **Check notes against the raw transcript.** In Pokémon, a note put a landmark building on the wrong side of a mountain; trusting it, the agent decided the cave was done and kept dropping back onto the route it came from. Once dreaming checked the note against the session transcript and fixed it, the agent went back into the cave and reached the next city. The run with the uncorrected note never got past the mountain.
- **Wikis can bloat.** On one task the wiki grew larger than the source documents, like the map in Borges's "On Exactitude in Science" that was as large as the empire: it abstracted nothing.
- **Several agents writing one page lose facts.** Agents writing into a shared table of contract terms overwrote one another, and only 41 of 57 graded facts (72%) survived. With one agent and one page per contract, quoting terms word for word, all 57 survived.
- **Tune consolidation instructions to the goal.** The original instructions never said contract terms were what mattered most. That only surfaced after Claude reflected on its failures, revised the instructions, and rebuilt the wiki.
- A second dreaming pass can repair links that point to pages that don't exist.
- Open question: checking everything is expensive, so focus on information likely to change, and tune the cadence by how often memories are accessed.

**Where we agree**

Our overnight consolidation does four things: merge near-duplicate pages, rewrite, split long pages, and add cross-links.

- **Merging unrelated conventions, crudely.** We found near-duplicate clusters offline and merged them. When two judges reviewed every merge, **nearly half had a substantive problem**: conventions about different objects or scopes were fused into one, and exceptions and conditions got weakened. We rolled all of those back, and merges in the conventions directory are now held by default. The mechanism differs from "several agents writing one table" (ours weren't concurrent writes), but the outcome is the same kind: things that should stay separate get squashed into one, and what gets lost is the most valuable detail. For them it was the exact contract terms; for us, scope and exceptions. Their fix was one page per object with verbatim quotes. Ours is a hard constraint: a merge must not drop any citation.
- **Links that look right, and about six in ten that hold up.** Overnight we attached "convention → concrete practice" links (pointing to experience pages). At launch the spot checks passed almost everything. Under a strict re-review of all of them (judges read full pages and must check for conflicts), both judges accepted about six in ten. The rest were merely on-topic or contradicted the convention. They had passed at first because the judges saw only excerpts and waved through anything on-topic. Their post has no direct counterpart, but it is the same warning as "a wiki as large as its sources": a richer-looking representation is not a more useful one.
- **A threshold rule retired conventions that should have stayed.** One step retired conventions automatically when they fell below a quality threshold. On review, **most of the retired conventions should have been restored**; the rest mostly duplicated what the repository's own instruction file already said. Retirement is an invisible failure: a convention disappearing raises no error, and you only find out the next time someone corrects the agent.
- **Rewriting the same page several times a night.** Unchanged neighbouring pages in a batch were rewritten anyway, and about three in ten pages were changed two or three times in one night. Fixed: write back only pages that actually changed.
- **Checking against the raw record.** Every sentence on our pages carries a citation back to the source message, so checking against the original is possible in principle. Today we only check that the citations are still there, not that the content still matches the source. Their example shows the second check is worth it, and that is the experiment below.

Their "tune instructions to the goal" translates for us like this: our consolidation instructions are generic (dedupe, rewrite, split) and never say that scope and exceptions are the most important part of a convention. By their experience, that sentence belongs in the instructions. *(Inferred.)*

## Next: add "look back at the record and check the memory" to Next-step Replay

A plan only. Nothing has been run.

**Question**: before the agent makes its decision, does checking the memory page against the raw record it cites reduce partial compliance (gate 3) and over-broad rules with lost scope (gate 1)?

**Arms**

1. `memory_search`: the status quo; the agent decides whether to search.
2. `oracle_page`: the right page is put in front of the agent.
3. `oracle_page + verify`: the page comes with the source excerpts it cites, and the agent must check page against source and list the points before planning.
4. `dream_verify`: first run an offline "check against the raw record" consolidation pass, index the checked pages, then run `memory_search`.

**Data**: synthetic sessions and corrections on open-source repositories, starting with 5–10 cases. Each case gets deliberately flawed pages: scope removed, contradicting the source, out of date.

**Metrics**: per-point `full` / `partial` / `violates`; agreement between the two judges; the share at each funnel step; extra tokens spent on checking; the share of correct pages the check makes worse (false-edit rate).

**Reading the results**: if 3 beats 2, part of the loss at "used" comes from not turning the page into a checklist. If 4 beats 1, checking against the source during consolidation is worth the compute. If nothing differs, we'll report that too.

**Out of scope**: running this on internal data and publishing those numbers; comparing models.

## Summary

| Gate | Anthropic's post | Our field observations | Do they line up? |
|---|---|---|---|
| Written right | Memory is a prediction; say what it's for, don't prescribe how; fixed rules can hurt | Rewording the Skill: within one item on 49; scope matters more than the conclusion | Same direction, different target |
| Found | Keep the injected layer small; wiki + search 61% vs search alone 53% | The agent searches for its task; conventions are about steps; ranking isn't the bottleneck | Complementary: they offer a map, we lack "knowing this step has a rule" |
| Used | One sentence: loading doesn't guarantee acting | The leakiest gate: close to four in ten read in full but didn't fully follow; about one in five still violates with the page in front of it | Not developed in the post; the part we most want to add |
| Consolidation | Check against the source; wikis bloat; many writers lose facts; tune instructions to the goal | Nearly half of crude merges were bad; about six in ten links held up under strict review; most threshold retirements should have been restored | Failure modes line up closely |

Next: "Your memory eval may be inflated: same-session leakage".
