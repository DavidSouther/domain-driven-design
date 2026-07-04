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
