# Mise monorepo reference

Toolchain: mise + per-language sub-projects

## Overview

A mise monorepo hosts multiple language sub-projects under one root.
Mise provides a unified task interface (`mise format`, `mise test`, etc.) that delegates to each sub-project's own tooling.

## Required layout

```
<monorepo>/
  mise.toml           # root tasks and tool versions
  .mise.toml          # optional local overrides (gitignored)
  <service-a>/        # Rust, Python, TypeScript sub-project
    mise.toml         # service-level task overrides (optional)
    <lang-specific layout (see language reference)
  <service-b>/
    ...
  docs/
```

## Required root `mise.toml`

```toml
[tools]
# Declare language versions used across the monorepo
node = "22"
python = "3.12"
rust = "stable"

[tasks.format]
description = "Format all sub-projects"
run = """
for dir in */; do
  if [ -f "$dir/mise.toml" ] || [ -f "$dir/Cargo.toml" ] || [ -f "$dir/pyproject.toml" ] || [ -f "$dir/package.json" ]; then
    (cd "$dir" && mise run format 2>/dev/null || true)
  fi
done
"""

[tasks.check]
description = "Static analysis for all sub-projects"
run = """
set -e
for dir in */; do
  if [ -f "$dir/Cargo.toml" ]; then
    (cd "$dir" && cargo clippy -- -D warnings)
  elif [ -f "$dir/pyproject.toml" ]; then
    (cd "$dir" && uv run pyright && uv run ruff check src tests)
  elif [ -f "$dir/package.json" ]; then
    (cd "$dir" && npm run check)
  fi
done
"""

[tasks.test]
description = "Run tests for all sub-projects"
run = """
set -e
for dir in */; do
  if [ -f "$dir/Cargo.toml" ]; then
    (cd "$dir" && cargo test)
  elif [ -f "$dir/pyproject.toml" ]; then
    (cd "$dir" && uv run pytest)
  elif [ -f "$dir/package.json" ]; then
    (cd "$dir" && npm test)
  fi
done
"""

[tasks.lint]
description = "Lint all sub-projects"
run = """
set -e
for dir in */; do
  if [ -f "$dir/Cargo.toml" ]; then
    (cd "$dir" && cargo clippy -- -D warnings)
  elif [ -f "$dir/pyproject.toml" ]; then
    (cd "$dir" && uv run ruff check --fix src tests)
  elif [ -f "$dir/package.json" ]; then
    (cd "$dir" && npx biome lint --write src tests)
  fi
done
"""

[tasks.run]
description = "Start the primary service"
run = "echo 'Override in service mise.toml'"

[tasks.serve]
description = "Start all services for local development"
run = "echo 'Override with service-specific commands'"
```

## Validation checklist

- [ ] Verify you have installed `mise` (run `mise --version`)
- [ ] Root `mise.toml` exists with `format`, `check`, `test`, `lint` tasks
- [ ] Run `mise trust` (or set `MISE_TRUSTED_CONFIG_PATHS`)
- [ ] Each sub-project has its own language reference validated
- [ ] `mise run check` exits 0
- [ ] `mise run test` exits 0

## Scaffolding (if validation fails)

```bash
# Install mise (if missing)
curl https://mise.run | sh

# Scaffold root
cat > mise.toml << 'EOF'
[tools]
node = "22"
python = "3.12"
rust = "stable"
EOF

# Add tasks from template above
mise trust
mise install

# Verify
mise run check
mise run test
```

## Development hooks

| Hook | Command |
|---|---|
| Format | `mise run format` |
| Check | `mise run check` |
| Test | `mise run test` |
| Lint | `mise run lint` |

## Per-service tasks

Each sub-project can override tasks in its own `mise.toml`:

```toml
# service-a/mise.toml
[tasks.format]
run = "cargo fmt"

[tasks.check]
run = "cargo clippy -- -D warnings"

[tasks.test]
run = "cargo test"
```

## Service-specific `run` and `serve`

Configure `run` for primary service startup and `serve` for full local dev (all services + dependencies):

```toml
# service-a/mise.toml
[tasks.run]
run = "cargo run --bin service-a"

[tasks.serve]
run = "docker compose up -d db && cargo run --bin service-a"
```

## Verification command

```bash
mise run check && mise run test
```

Expected: all sub-projects pass static analysis and tests, exit 0.
