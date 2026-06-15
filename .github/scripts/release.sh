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

# --- Change detection ---------------------------------------------------------

last_tag=$(git -C "${REPO}" describe --tags --match 'release/*' --abbrev=0 2>/dev/null \
  || git -C "${REPO}" rev-list --max-parents=0 HEAD)

changed=()
for plugin in "${PLUGINS[@]}"; do
  if [[ -n "$(git -C "${REPO}" log "${last_tag}..HEAD" -- "${plugin}/" 2>/dev/null)" ]]; then
    changed+=("${plugin}")
  fi
done

if [[ ${#changed[@]} -eq 0 ]]; then
  echo "No changes since last release, skipping."
  exit 0
fi

# --- Version computation ------------------------------------------------------

ym="${RELEASE_DATE:-$(date +%Y.%m)}"
micro=$(git -C "${REPO}" tag -l "release/${ym}.*" | wc -l | tr -d ' ')
VERSION="${ym}.${micro}"

# --- Plugin version bump ------------------------------------------------------

for plugin in "${changed[@]}"; do
  json="${REPO}/${plugin}/.claude-plugin/plugin.json"
  python3 - "${json}" "${VERSION}" <<'PY'
import json, sys
path, ver = sys.argv[1], sys.argv[2]
with open(path) as f: d = json.load(f)
d["version"] = ver
with open(path, "w") as f: json.dump(d, f, indent=2); f.write("\n")
PY
done

# --- Changelog generation -----------------------------------------------------

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
CLIFF_CONFIG="${SCRIPT_DIR}/../../cliff.toml"

git cliff \
  --config "${CLIFF_CONFIG}" \
  --repository "${REPO}" \
  --tag "release/${VERSION}" \
  --output "${REPO}/CHANGELOG.md"

# --- Signed commit + signed umbrella tag -------------------------------------

git -C "${REPO}" add .
git -C "${REPO}" commit -m "chore: release ${VERSION}"

git -C "${REPO}" tag -a "release/${VERSION}" -m "Release ${VERSION}"

for plugin in "${changed[@]}"; do
  git -C "${REPO}" tag -a "${plugin}/${VERSION}" -m "Release ${plugin} ${VERSION}"
done
