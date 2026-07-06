#!/usr/bin/env bash
# Standalone Vale run: syncs base styles, then lints the repo, or a single
# file (if a path is given as $1, useful for testing one file in isolation)
# with the same e2e exclusion as .github/workflows/vale.yml and
# DEVELOPMENT.md's "Run locally" section.
set -uo pipefail

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$REPO_ROOT" || exit 1

# vale sync

if [ "$#" -gt 0 ]; then
  path="$1"
else
  path="."
fi

# vale --glob='!{**/e2e/**}' --glob='!.ailly/**' "$path"
find "$path" -name '*.md' \
  -not -path './.ailly/*' \
  \( -not -path '*/e2e/*' -o -name 'README.md' \) \
  -print0 | xargs -0 vale