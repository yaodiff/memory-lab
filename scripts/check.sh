#!/bin/bash
# Every check a PR must pass; CI runs exactly this. Locally it also uses your private patterns, if present.
set -euo pipefail
cd "$(git rev-parse --show-toplevel)"
python3 scripts/check_docs.py
python3 scripts/pr_links_issue.py --self-test
python3 scripts/privacy_check.py --all
