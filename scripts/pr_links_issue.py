#!/usr/bin/env python3
"""Fail unless a PR description links an issue of this repository.

Reads the description from $PR_BODY and the repository from $REPO (owner/name).
Accepts `Fixes #N`, `Closes #N`, `Resolves #N`, `Refs #N` (any case, optional colon,
optional owner/name prefix) or a link to an issue of this repository. Code spans,
fenced blocks and HTML comments (the PR template's hints) do not count.
"""
import os
import re
import sys


def linked(body, repo):
    text = re.sub(r"```.*?(```|$)", " ", body, flags=re.S)
    text = re.sub(r"<!--.*?-->", " ", text, flags=re.S)
    text = re.sub(r"`[^`\n]*`", " ", text)
    me = re.escape(repo)
    kw = re.compile(rf"\b(?:fix(?:e[sd])?|close[sd]?|resolve[sd]?|refs?)(?::\s*|\s+)(?:{me})?#(\d+)\b", re.I)
    url = re.compile(rf"https?://(?:www\.)?github\.com/{me}/issues/(\d+)\b", re.I)
    return sorted({int(n) for n in kw.findall(text) + url.findall(text)})


if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "--self-test":
        r = "yaodiff/memory-lab"
        assert linked("Fixes #3", r) == [3]
        assert linked("refs: #12 and closes yaodiff/memory-lab#4", r) == [4, 12]
        assert linked("see https://github.com/yaodiff/memory-lab/issues/7", r) == [7]
        assert linked("<!-- Fixes #1 -->\n`Fixes #2`\n```\nFixes #5\n```", r) == []
        assert linked("Fixes other/repo#9", r) == []
        print("pr_links_issue: self-test ok")
        sys.exit(0)
    issues = linked(os.environ.get("PR_BODY", ""), os.environ["REPO"])
    if not issues:
        print("PR description links no issue. Add a line such as `Fixes #N` or `Refs #N` "
              "(outside code and comments); see CONTRIBUTING.md.")
        sys.exit(1)
    print("links " + ", ".join(f"#{n}" for n in issues))
