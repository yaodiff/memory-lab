#!/usr/bin/env python3
"""Privacy scan for a public repository.

Two layers of patterns:
  * generic patterns below: safe to publish, run everywhere (CI included);
  * private patterns: one regex per line in $MEMLAB_PRIVATE_PATTERNS or
    ~/.config/memory-lab/private-patterns.txt. They name the things that must
    not appear (employer, internal systems, people), so the list itself never
    enters the repository. CI does not have it; scripts/merge-pr.sh and the
    pre-push hook do.

Usage:
  scripts/privacy_check.py --all                 scan every tracked file
  scripts/privacy_check.py --range BASE..HEAD    scan lines added in a range
  scripts/privacy_check.py --message FILE        also scan a text file (commit/PR message)
  --require-private                              fail if no private pattern file is found
"""
import argparse
import os
import re
import subprocess
import sys

SELF = "scripts/privacy_check.py"
SKIP = {"LICENSE", SELF}

GENERIC = [
    ("local path", r"(?<![\w.])/(?:home|Users|data\d+|root)/[\w.-]+"),
    ("temp path", r"(?<![\w.])/tmp/[\w.-]+"),
    ("internal host", r"\b[\w-]+(?:\.[\w-]+)*\.(?:internal|corp|intra|intranet|lan)\b"),
    ("private IP", r"\b(?:10\.\d{1,3}|192\.168|172\.(?:1[6-9]|2\d|3[01]))\.\d{1,3}\.\d{1,3}\b"),
    ("token", r"\b(?:ghp_|gho_|github_pat_|sk-ant-|sk-|xox[bp]-|AKIA)[A-Za-z0-9_-]{12,}"),
    ("email", r"\b[\w.+-]+@(?!(?:users\.noreply\.github\.com|example\.(?:com|org))\b)[\w-]+(?:\.[\w-]+)+\b"),
    ("long hex id", r"\b[0-9a-f]{32,}\b"),
]


def load_private():
    path = os.environ.get("MEMLAB_PRIVATE_PATTERNS") or os.path.expanduser(
        "~/.config/memory-lab/private-patterns.txt")
    if not os.path.isfile(path):
        return None, []
    pats = []
    with open(path, encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if line and not line.startswith("#"):
                pats.append(("private pattern", line))
    return path, pats


def git(*args):
    return subprocess.run(["git", *args], check=True, capture_output=True, text=True).stdout


def tracked_lines():
    for name in git("ls-files").splitlines():
        if name in SKIP or not os.path.isfile(name):
            continue
        try:
            with open(name, encoding="utf-8") as f:
                for i, line in enumerate(f, 1):
                    yield f"{name}:{i}", line
        except UnicodeDecodeError:
            continue


def added_lines(rng):
    name, num = None, 0
    for line in git("diff", "--unified=0", "--no-color", rng).splitlines():
        if line.startswith("+++ "):
            name = line[6:] if line.startswith("+++ b/") else None
        elif line.startswith("@@"):
            num = int(re.search(r"\+(\d+)", line).group(1))
        elif line.startswith("+") and name and name not in SKIP:
            yield f"{name}:{num}", line[1:]
            num += 1
    # Commit messages in the range are public too.
    for sha in git("rev-list", rng).split():
        for i, line in enumerate(git("log", "-1", "--format=%B", sha).splitlines(), 1):
            yield f"commit {sha[:12]} message:{i}", line


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--all", action="store_true")
    ap.add_argument("--range")
    ap.add_argument("--message", action="append", default=[])
    ap.add_argument("--require-private", action="store_true")
    a = ap.parse_args()
    if not (a.all or a.range or a.message):
        ap.error("give --all, --range or --message")

    path, private = load_private()
    if a.require_private and not private:
        sys.exit("privacy_check: no private pattern file (set MEMLAB_PRIVATE_PATTERNS or create "
                 "~/.config/memory-lab/private-patterns.txt)")
    rules = [(label, re.compile(p, re.IGNORECASE)) for label, p in GENERIC + private]

    sources = []
    if a.all:
        sources.append(tracked_lines())
    if a.range:
        sources.append(added_lines(a.range))
    for m in a.message:
        with open(m, encoding="utf-8") as f:
            sources.append((f"{m}:{i}", line) for i, line in enumerate(f, 1))

    hits = 0
    for src in sources:
        for where, line in src:
            for label, rx in rules:
                m = rx.search(line)
                if m:
                    hits += 1
                    # Private hits print only the location: the matched text may itself be private.
                    shown = "" if label == "private pattern" else f": {m.group(0)}"
                    print(f"{where}: {label}{shown}")
    scope = f"generic + {len(private)} private patterns" if private else "generic patterns only"
    print(f"privacy_check: {hits} hit(s) ({scope})")
    sys.exit(1 if hits else 0)


if __name__ == "__main__":
    main()
