# Releasing

## Commit conventions

This repository uses [Conventional Commits](https://www.conventionalcommits.org/).
Use a plugin name as the scope so each plugin's history stays readable:

| Type | Changelog section | Example |
|------|-------------------|---------|
| `feat` | Features | `feat(developer): add bugfix skill shape` |
| `fix` | Bug Fixes | `fix(general): correct dispatching agent prompt` |
| `docs` | Documentation | `docs(patterns): clarify newtype vs domain-objects` |
| `feat!` or `BREAKING CHANGE` body | Breaking Changes | `feat(research)!: rename configuring-public` |
| `chore`, `refactor`, `test`, `perf`, `style` | (skipped) | internal bookkeeping |

## CalVer scheme

Releases follow `YYYY.MM.MICRO`:

- `YYYY.MM` is the calendar year and month of the release run.
- `MICRO` is zero-indexed: the first release in a month is `.0`, the second is `.1`, etc.

Examples: `2026.06.0`, `2026.06.1`, `2026.07.0`.

## Automated release

A nightly workflow (`.github/workflows/nightly-release.yml`) runs at 02:00 UTC every day.

- If no plugin has new commits since the last `release/*` tag the workflow exits 0 with "No changes since last release, skipping."
- Otherwise it bumps versions, generates `CHANGELOG.md`, creates a signed commit and umbrella tag, and publishes a GitHub Release.
- Trigger on demand via **Actions → Nightly Release → Run workflow**.
- Logs are in the Actions tab; investigate and re-trigger if a push step fails.

## Optional developer SSH signing

Register your public key on GitHub under **Settings → SSH and GPG keys → New SSH key → Signing Key**.

To sign your own commits locally with an approved signing key:

```bash
git config --global gpg.format ssh
git config --global user.signingkey ~/.ssh/id_ed25519.pub
git config --global commit.gpgsign true
git config --global tag.gpgsign true
```

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
