# Releasing

## CalVer scheme

Releases follow `YYYY.MM.MICRO`:

- `YYYY.MM` is the calendar year and month of the release run.
- `MICRO` is zero-indexed: the first release in a month is `.0`, the second is `.1`, etc.

Examples: `2026.06.0`, `2026.06.1`, `2026.07.0`.

## Automated release

A nightly workflow (`.github/workflows/nightly-release.yml`) runs at 02:00 UTC every day.

- If no plugin has new commits since the last `release/*` tag the workflow exits 0 with "No changes since last release, skipping."
- Otherwise it bumps Claude and Codex plugin manifest versions together, generates `CHANGELOG.md`, creates a signed release commit with those files, pushes `main`, creates a signed umbrella tag from that committed state, and publishes a GitHub Release.
- The changelog update must land on `main` before the `release/*` tag is created, so the tag always points at a commit that already contains the release notes.
- Trigger on demand via **Actions → Nightly Release → Run workflow**.
- Logs are in the Actions tab; investigate and re-trigger if a push step fails.

## Final release

The nightly workflow was removed in `775bfc2`. The last release of this repository, `2026.09.3`, covers `developer` and `general` only and is cut by hand. This is a human-approved step: the release commit, tag, push, and GitHub Release are not part of any automated change.

`2026.09.3` is reserved for this repository. The successor (`davidsouther/ailly`) computes only current-month versions, and its September versions closed at `2026.09.2`, so the successor never produces this value.

1. Set the manifest versions: `python3 .github/scripts/release.py --version 2026.09.3`. The script rewrites the `developer` and `general` Claude and Codex manifests and `.claude-plugin/marketplace.json`, and prints the version. It does not commit, tag, push, or write `CHANGELOG.md`.
2. Generate `CHANGELOG.md` with git-cliff.
3. Create the signed release commit with the manifests and `CHANGELOG.md`.
4. Create the signed tag `release/2026.09.3` on that commit.
5. Push `main` and the tag.
6. Publish a GitHub Release whose note states that Ailly moved to `davidsouther/ailly` and points at `general/scripts/migrate-to-ailly.py`.

## Optional developer SSH signing

Register your public key on GitHub under **Settings → SSH and GPG keys → New SSH key → Signing Key**.

To sign your own commits locally with an approved signing key:

```bash
git config --global gpg.format ssh
git config --global user.signingkey ~/.ssh/id_ed25519.pub
git config --global commit.gpgsign true
git config --global tag.gpgsign true
```

Swap `--global` for `--local` to scope signing to this repository only (the
setting is then shared across its worktrees but does not affect other repos).

This config is not stored in the repository, so it does not travel with a clone.
On every new machine or fresh checkout, confirm it is set before committing:

```bash
git config --get commit.gpgsign   # expect: true
```

If it prints nothing, commits will be unsigned and show as unverified on GitHub.
Re-run the block above to fix.

## CI key provisioning (one-time, admin only)

```bash
ssh-keygen -t ed25519 -f ci_signing_key -N "" -C "releases@ailly"
echo "davidsouther@gmail.com namespaces=\"git\" $(cat ci_signing_key.pub)" >> signing/allowed_signers
gh secret set SSH_SIGNING_KEY < ci_signing_key
rm ci_signing_key ci_signing_key.pub
```

Then register the public key on GitHub under **Profile Settings → SSH and GPG keys → New SSH key → Signing Key** (copy it from `signing/allowed_signers`), and commit and push `signing/allowed_signers`. (note: profile settings, not project settings.)

## SLSA statement

This repository targets **SLSA Source Level 1** with signed-tag provenance: every release commit and umbrella tag is SSH-signed by the CI bot key, and the tag can be verified locally with `git verify-tag <tag>`.
