#!/usr/bin/env bash
# Feature test: .github/scripts/release.sh produces correct version bumps,
# changelog update, and a signed umbrella tag for changed plugins only.
# Exercises the early-exit path (no changes) and the release path (two plugins changed).
#
# Run from the repo root:
#   bash e2e/release/test.sh
#
# Prerequisites: git, git-cliff on PATH.
# Does NOT require gh (--skip-gh is passed) or network access.

set -euo pipefail

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
RELEASE_SH="${REPO_ROOT}/.github/scripts/release.sh"

fail() { echo "FAIL: $*" >&2; exit 1; }
ok()   { echo "OK:   $*"; }

[[ -f "${RELEASE_SH}" ]] || fail "release script not found at ${RELEASE_SH}"

# --- Setup: temp repo ---------------------------------------------------------

TMPDIR_ROOT="$(mktemp -d)"
trap 'rm -rf "${TMPDIR_ROOT}"' EXIT

REPO="${TMPDIR_ROOT}/repo"
git init -q "${REPO}"

git -C "${REPO}" config user.email "releases@ailly"
git -C "${REPO}" config user.name "Ailly Release Bot"

# Generate a throwaway Ed25519 key simulating the CI signing key in Secrets.
KEY="${TMPDIR_ROOT}/signing_key"
ssh-keygen -t ed25519 -f "${KEY}" -N "" -C "releases@ailly" -q

# Configure signing the same way photostructure/git-ssh-signing-action does.
git -C "${REPO}" config gpg.format ssh
git -C "${REPO}" config user.signingkey "${KEY}.pub"
git -C "${REPO}" config commit.gpgsign true
git -C "${REPO}" config tag.gpgsign true

# Wire up allowed_signers so git verify-tag works locally.
ALLOWED_SIGNERS="${REPO}/signing/allowed_signers"
mkdir -p "${REPO}/signing"
echo "releases@ailly namespaces=\"git\" $(cat "${KEY}.pub")" > "${ALLOWED_SIGNERS}"
git -C "${REPO}" config gpg.ssh.allowedSignersFile "${ALLOWED_SIGNERS}"

# --- Scaffold minimal plugin structure ----------------------------------------

PLUGINS=(developer general patterns domain research characters)

for plugin in "${PLUGINS[@]}"; do
  mkdir -p "${REPO}/${plugin}/.claude-plugin"
  cat > "${REPO}/${plugin}/.claude-plugin/plugin.json" <<JSON
{
  "name": "${plugin}",
  "version": "2026.05.0"
}
JSON
done

# Initial baseline commit + signed tag simulating a prior release.
git -C "${REPO}" add .
git -C "${REPO}" commit -q -m "chore: initial scaffold"
git -C "${REPO}" tag -s "release/2026.05.0" -m "Release 2026.05.0"

# --- Part 1: early-exit path (no changes since last tag) ----------------------

RELEASE_DATE="2026.06" \
  bash "${RELEASE_SH}" \
    --repo "${REPO}" \
    --skip-push \
    --skip-gh \
  | grep -q "No changes" \
  || fail "release.sh should exit early when no plugin has changed"
ok "early-exit path: no changes detected, script skipped release"

# --- Commits that change only developer and general ---------------------------
# Write to non-JSON files so plugin.json stays valid for the version-bump step.

echo "# skill update" > "${REPO}/developer/SKILL.md"
git -C "${REPO}" add .
git -C "${REPO}" commit -q -m "feat(developer): add bugfix skill shape"

echo "# skill update" > "${REPO}/general/SKILL.md"
git -C "${REPO}" add .
git -C "${REPO}" commit -q -m "fix(general): correct dispatching agent prompt"

# --- Part 2: release path -----------------------------------------------------

RELEASE_DATE="2026.06" \
  bash "${RELEASE_SH}" \
    --repo "${REPO}" \
    --skip-push \
    --skip-gh

# --- Assertions ---------------------------------------------------------------

# 1. developer and general got a new version.
dev_version="$(python3 -c "import json,sys; d=json.load(open(sys.argv[1])); print(d['version'])" \
  "${REPO}/developer/.claude-plugin/plugin.json")"
[[ "${dev_version}" == "2026.06.0" ]] \
  || fail "developer version expected 2026.06.0, got ${dev_version}"
ok "developer plugin.json version is ${dev_version}"

gen_version="$(python3 -c "import json,sys; d=json.load(open(sys.argv[1])); print(d['version'])" \
  "${REPO}/general/.claude-plugin/plugin.json")"
[[ "${gen_version}" == "2026.06.0" ]] \
  || fail "general version expected 2026.06.0, got ${gen_version}"
ok "general plugin.json version is ${gen_version}"

# 2. patterns (unchanged) kept its prior version.
pat_version="$(python3 -c "import json,sys; d=json.load(open(sys.argv[1])); print(d['version'])" \
  "${REPO}/patterns/.claude-plugin/plugin.json")"
[[ "${pat_version}" == "2026.05.0" ]] \
  || fail "patterns version should be unchanged 2026.05.0, got ${pat_version}"
ok "patterns plugin.json version unchanged at ${pat_version}"

# 3. CHANGELOG.md exists and contains the new tag.
[[ -f "${REPO}/CHANGELOG.md" ]] \
  || fail "CHANGELOG.md was not created"
grep -q "release/2026.06.0" "${REPO}/CHANGELOG.md" \
  || fail "CHANGELOG.md does not mention release/2026.06.0"
ok "CHANGELOG.md contains release/2026.06.0 entry"

# 4. Signed umbrella tag exists.
git -C "${REPO}" tag -l "release/2026.06.0" | grep -q "release/2026.06.0" \
  || fail "umbrella tag release/2026.06.0 not found"
ok "umbrella tag release/2026.06.0 exists"

# 5. Tag signature is valid.
git -C "${REPO}" verify-tag "release/2026.06.0" 2>/dev/null \
  || fail "git verify-tag release/2026.06.0 failed"
ok "tag release/2026.06.0 signature is valid"

# 6. Version-bump commit is signed.
release_commit="$(git -C "${REPO}" rev-list -1 "release/2026.06.0")"
git -C "${REPO}" verify-commit "${release_commit}" 2>/dev/null \
  || fail "version-bump commit ${release_commit:0:8} is not signed"
ok "version-bump commit ${release_commit:0:8} signature is valid"

echo ""
echo "All assertions passed."
