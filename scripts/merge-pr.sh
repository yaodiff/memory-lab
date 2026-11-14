#!/bin/bash
# Merge a PR after the private-pattern scan passes (CONTRIBUTING.md, "Merging"):
#   scripts/merge-pr.sh <PR number>
# CI only has the generic patterns. This scans the PR's commits and its squash message with your private
# patterns too, then squash-merges exactly the head it scanned, with the message it scanned.
set -euo pipefail
pr="${1:?usage: scripts/merge-pr.sh <PR number>}"
case "$pr" in *[!0-9]*) echo "merge-pr: not a PR number: $pr" >&2; exit 2 ;; esac
cd "$(git rev-parse --show-toplevel)"
repo="$(gh repo view --json nameWithOwner -q .nameWithOwner)"
tmp="$(mktemp -d)"; trap 'rm -rf "$tmp"' EXIT

gh pr view "$pr" --json headRefOid,baseRefName,title,body,state > "$tmp/pr.json"
python3 - "$tmp" "$pr" <<'PY'
import json, sys
tmp, pr = sys.argv[1:]
v = json.load(open(f"{tmp}/pr.json", encoding="utf-8"))
if v["state"] != "OPEN":
    sys.exit(f"merge-pr: #{pr} is {v['state']}")
open(f"{tmp}/fields", "w").write(f"{v['headRefOid']}\n{v['baseRefName']}\n")
open(f"{tmp}/subject", "w", encoding="utf-8").write(f"{v['title']} (#{pr})")
open(f"{tmp}/body", "w", encoding="utf-8").write(v["body"])
open(f"{tmp}/message", "w", encoding="utf-8").write(f"{v['title']} (#{pr})\n\n{v['body']}\n")
PY
{ read -r head; read -r base; } < "$tmp/fields"

PR_BODY="$(cat "$tmp/body")" REPO="$repo" python3 scripts/pr_links_issue.py

git fetch -q origin "refs/heads/$base"; base_sha="$(git rev-parse FETCH_HEAD)"
git fetch -q origin "pull/$pr/head"
[ "$(git rev-parse FETCH_HEAD)" = "$head" ] || { echo "merge-pr: the PR moved while fetching; run again" >&2; exit 1; }
python3 scripts/privacy_check.py --require-private --range "$base_sha..$head" --message "$tmp/message" \
  || { echo "merge-pr: #$pr not merged: fix the hits above first" >&2; exit 1; }

# Required checks are enforced by the ruleset; GitHub refuses the merge while they are pending or red.
# The repository setting "delete branch on merge" removes the branch.
(cd / && gh pr merge "$pr" --repo "$repo" --squash --match-head-commit "$head" \
  --subject "$(cat "$tmp/subject")" --body-file "$tmp/body")
echo "merge-pr: #$pr merged"
