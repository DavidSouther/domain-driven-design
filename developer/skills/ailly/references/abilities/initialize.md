# Initialize

> Coordinator reference loaded by `developer:ailly` when setting up a new project
> or language environment. There is no standalone `developer:initialize` skill; the
> coordinator and the tool-failure reference route here for local environment fixes.

## Overview

Prepares a project folder for development using language-agnostic orchestration with language-specific details in reference files. Validates existing layout before scaffolding.

**Announce at start:** "Using the developer:ailly initialize reference to set up the project."

## Behavior

1. Identify the target language/toolchain (Rust, Python, TypeScript, or Mise monorepo).
2. Read the appropriate reference file (see table below).
3. Validate the project folder against the reference file's required layout.
4. Apply fixes described in the reference file where validation fails.
5. Configure the four development hooks.
6. Verify the project builds/starts cleanly.

## Language Reference Files

| Language/Toolchain | Reference file |
|---|---|
| Rust | `developer/skills/ailly/references/abilities/initialize/rust.md` |
| Python | `developer/skills/ailly/references/abilities/initialize/python.md` |
| TypeScript | `developer/skills/ailly/references/abilities/initialize/typescript.md` |
| Mise monorepo | `developer/skills/ailly/references/abilities/initialize/mise.md` |

If the target language is not in this table, ask the user which toolchain to use as the basis and adapt the closest reference file.

## Four Development Hooks

Every initialized project must have these hooks configured in the agent's settings:

| Hook | When | Command |
|---|---|---|
| **Format** | After editing any file | Run formatter on the edited file |
| **Check** | Before running tests | Run static analysis (type check, lint) |
| **Test** | After every change | Run full test suite |
| **Lint** | After every task completes | Run linter on changed files |

The exact commands for each hook come from the language reference file.

## Validation

Validation must confirm:
- Required config files exist with correct content
- Directory layout matches the reference file
- Tooling is installed (e.g., `cargo`, `uv`, `node`, `mise`)
- The project builds/runs cleanly with zero errors and zero warnings

If validation fails, apply the fixes from the reference file before proceeding. Do not declare initialization complete until a clean build succeeds.

## Verification Command

After setup, run the verification command from the reference file and confirm:
- Exit code 0
- No warnings
- Output matches expected format

Report any failures to the user with the exact command and output.
