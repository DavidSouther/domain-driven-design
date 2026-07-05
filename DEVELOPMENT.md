# Development

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


## Project Management

Issues tracked in Github under DavidSouther/domain-driven-design.

## Evals

Feature and unit tests for Ailly should be in the form of evals. Feature tests are authored in the root e2e/ folder; unit tests are authored in individual plugin e2e/ folders.

## Releasing

Review RELEASING.md when changing or troubleshooting the release process.

## Prose Linting (Vale)

This repository lints prose with [Vale](https://vale.sh/), configured in `.vale.ini` at the repo root, with custom rules under `styles/DDD/`.

### Install

- macOS: `brew install vale`
- Or download a binary from <https://vale.sh/>

### Run locally

1. Sync the base styles once (and again after any `.vale.ini` change): `vale sync`
2. Lint a file: `vale README.md`
3. Lint the whole repo: `vale --glob='!{**/skills/**}' .` — skill/agent definition files under any `skills/` directory carry YAML frontmatter that isn't prose (and can crash Vale's frontmatter parser), so they're excluded

### Severity levels

- `error` — must fix before merge (broken grammar, consistency violations)
- `warning` — should fix (style infractions, filler)
- `suggestion` — consider (nominalization, sentence length)

Wrap a passage in `<!-- vale off -->` / `<!-- vale on -->` to suspend checks locally when a sentence needs an exception.

### CI

Every push and pull request runs `.github/workflows/vale.yml` automatically. Warnings and suggestions are reported but don't fail the build; only `error`-level findings do (`fail_on_error: false`).
