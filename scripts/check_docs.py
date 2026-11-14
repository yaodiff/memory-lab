#!/usr/bin/env python3
"""Docs checks: relative links resolve, and every bilingual document has its pair.

Pairs: README.md <-> README.zh.md, essays/NN-slug.md (zh) <-> essays/NN-slug.en.md (en).
Each side of a pair must link to the other near the top (the language switch).
"""
import os
import re
import subprocess
import sys

LINK = re.compile(r"\]\(([^)\s]+)\)")
errors = []

files = subprocess.run(["git", "ls-files", "*.md"], check=True, capture_output=True,
                       text=True).stdout.split()

for name in files:
    text = open(name, encoding="utf-8").read()
    text = re.sub(r"```.*?```", "", text, flags=re.S)  # links inside code fences are examples
    for target in LINK.findall(text):
        if re.match(r"[a-z]+:", target) or target.startswith("#"):
            continue
        path = os.path.normpath(os.path.join(os.path.dirname(name), target.split("#")[0]))
        if not os.path.exists(path):
            errors.append(f"{name}: broken link {target}")

pairs = [("README.zh.md", "README.md")]
for name in files:
    m = re.fullmatch(r"essays/(\d\d-[\w-]+)(\.en)?\.md", name)
    if m:
        base = f"essays/{m.group(1)}"
        pairs.append((base + ".md", base + ".en.md"))

for zh, en in sorted(set(pairs)):
    for a, b in ((zh, en), (en, zh)):
        if not os.path.exists(a):
            errors.append(f"{b}: missing its pair {a}")
            continue
        head = "".join(open(a, encoding="utf-8").readlines()[:5])
        if f"]({os.path.basename(b)})" not in head:
            errors.append(f"{a}: no language switch link to {os.path.basename(b)} in the first 5 lines")

for e in errors:
    print(e)
print(f"check_docs: {len(errors)} problem(s) in {len(files)} markdown files")
sys.exit(1 if errors else 0)
