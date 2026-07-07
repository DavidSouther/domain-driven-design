#!/usr/bin/env bash
set -uo pipefail

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$REPO_ROOT" || exit 1

if [ "$#" -gt 0 ]; then
  path="$1"
else
  path="."
fi

rumdl check "$path"
