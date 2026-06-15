#!/usr/bin/env bash
# release.sh — detect changed plugins, bump CalVer versions, generate changelog,
# sign and tag the release, optionally push and create a GitHub Release.
#
# Usage:
#   bash .github/scripts/release.sh [--repo <path>] [--skip-push] [--skip-gh]
#
# Environment:
#   RELEASE_DATE=YYYY.MM   override the date component; default: $(date +%Y.%m)
#
# Exit codes:
#   0  success OR no changes detected (early-exit path)
#   1  unexpected error or unknown flag

set -euo pipefail

REPO="${PWD}"
SKIP_PUSH=false
SKIP_GH=false

while [[ $# -gt 0 ]]; do
  case "$1" in
    --repo)      REPO="$2"; shift 2 ;;
    --skip-push) SKIP_PUSH=true; shift ;;
    --skip-gh)   SKIP_GH=true; shift ;;
    *) echo "Unknown argument: $1" >&2; exit 1 ;;
  esac
done

PLUGINS=(developer general patterns domain research characters)
