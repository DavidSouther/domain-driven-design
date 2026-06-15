# AGENTS.md

Guidance for AI agents working in this repository.

## Commit conventions

All commits must follow [Conventional Commits](https://www.conventionalcommits.org/).
Use a plugin name as the scope:

```
type(scope): description
```

| Type | When to use |
|------|-------------|
| `feat` | New skill, new capability, new reference file |
| `fix` | Correcting broken behavior in an existing skill |
| `docs` | Documentation-only changes (README, RELEASING, comments) |
| `refactor` | Internal restructuring with no behavior change |
| `test` | Adding or updating evals / e2e tests |
| `chore` | Tooling, CI, version bumps, generated files |
| `feat!` | Breaking change to a skill's interface or routing |

Scope is the plugin name: `developer`, `general`, `patterns`, `domain`, `research`, `characters`.

Examples:

```
feat(developer): add bugfix skill shape
fix(general): correct dispatching agent prompt
docs(patterns): clarify newtype vs domain-objects
chore: release 2026.06.0
```

See `RELEASING.md` for the full changelog mapping and CalVer release process.
