# Contributing

Every change, essays and typo fixes included, goes **issue → branch → PR → checks → squash merge**. `main` is protected: direct pushes, force pushes and deletion are rejected.

## Flow

1. **Find or open an issue.** `gh issue list --state all --search "<keywords>"`. No match: open one with a template (Essay, Correction, Experiment) or a blank issue saying what and why.
2. **Claim it** with a comment, so two people (or Agents) don't do the same thing:
   ```text
   Claim: <what you're doing>
   Plan: <how>
   ETA: <how long>
   Agent: yes (<machine> / <branch>)      # only when an Agent does the work
   ```
3. **Branch** from `main`, named with the issue number: `essay/5-leakage`, `fix/7-broken-link`, `chore/1-merge-workflow`. Update it by merging `origin/main`; don't force-push a branch with an open PR.
4. **Open one PR per issue.** English title (it becomes the commit on `main`), the template filled in, and `Fixes #N` (closes the issue) or `Refs #N` (links only) in the description.
5. **Checks must be green.** CI runs on every push and every edit of the description:
   - `checks`: `scripts/check.sh` (links resolve, zh/en pairs and language switches, generic privacy scan);
   - `pr-links-issue`: the description links an issue of this repository.
6. **Merge** with `scripts/merge-pr.sh <PR>`. Squash merge is the only method allowed; the branch is deleted on merge.

## Merging

CI only knows generic patterns (local paths, internal-looking hosts, private IPs, tokens, emails). The names that must never appear here (employer, internal systems, people) are themselves private, so they live outside the repository, one regex per line, in `~/.config/memory-lab/private-patterns.txt` (or `$MEMLAB_PRIVATE_PATTERNS`).

`scripts/merge-pr.sh` reads the PR once, checks the issue link, scans the PR's added lines, its commit messages and the squash message with both pattern sets, then squash-merges exactly the head it scanned. It refuses to run without the private file.

Optional: `git config core.hooksPath scripts/hooks` scans the whole tree with your private patterns on every push.

## Writing rules

- **Bilingual pairs change together**: `essays/NN-slug.md` (Chinese, written first) with `essays/NN-slug.en.md` (idiomatic English, not word for word); `README.md` with `README.zh.md`.
- **Internal findings only as ratios or coarse terms** ("about six in ten", "roughly fifty items"), labelled as small samples from our setting. No raw data, examples, internal names, people or links. Examples are rewritten or synthetic.
- **Negative results are reported as they are.**
- **Claims about other work link or quote the source.**
- Issues, PRs and commit messages are in English; essays are in both languages.
