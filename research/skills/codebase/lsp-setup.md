# Codebase — LSP setup

Per-language priming rules for the codebase stack. The wiring SKILL ([`../configuring-codebase/SKILL.md`](../configuring-codebase/SKILL.md)) cites this file at configure time; the per-language reference files (`lsp-rust.md`, `lsp-python.md`, `lsp-typescript.md`) cite it for the priming step each inherits.

Priming is the codebase analog of the books/papers `etiquette.md`: a shared-rules file. The concern is not host politeness or credential handling — language servers are toolchain installs with no auth — but **project resolution**. A server that is installed but unprimed answers `goToDefinition` with nothing. The rules below make each language server resolve the project before the contract holds.

## Rust (rust-analyzer)

- rust-analyzer activates automatically when `Cargo.toml` is present; no separate install.
- **Prime with `cargo check`** so the crate graph resolves. Until the graph is built at least once, cross-crate `goToDefinition`/`findReferences` return nothing.
- Workspace crates resolve once the workspace root has been checked; you do not need to check each member crate separately.
- Feature flags affect what resolves. rust-analyzer uses the active feature set (usually `default`); a symbol behind a non-default feature appears Not-Available until that feature is enabled in the rust-analyzer config.

## Python (pyright / pylsp)

- Install pyright (`pip install pyright` or `npm install -g pyright`); pylsp (`pip install python-lsp-server`) is the alternative.
- **Activate the venv and match the pyright config to it.** A `pyrightconfig.json` or a `[tool.pyright]` block in `pyproject.toml` must point `venvPath`/`pythonPath` at the active virtual environment. A mismatched or absent venv causes import-resolution failures and `hover` returns `Unknown`.
- After the venv is correct, `hover` on a typed symbol returns a concrete type. If it returns `Unknown`, the priming is incomplete (wrong venv) or the code is genuinely untyped.

## TypeScript / JavaScript (typescript-language-server)

- tsserver ships with TypeScript; no separate install beyond the project's dependencies.
- **Run `npm install` (or equivalent) to populate `node_modules`.** Until dependencies are installed, imports into third-party packages and `.d.ts` declarations do not resolve.
- For monorepos, **run `tsc --build`** so project references (`composite: true`) regenerate the declaration files tsserver needs to resolve cross-package imports. Until then, cross-package `goToDefinition` lands nowhere.

## Other languages

Each compiled language follows the same shape: install the standard server, then prime the build so the server resolves the project before smoke-testing. Document the per-language priming step in that language's `lsp-<lang>.md` and cite this file for the shared rationale.

- **Go (gopls):** `go build ./...` so the module graph resolves.
- **Java (jdtls):** import/build the project (`mvn compile` / `gradle build`) so the classpath resolves.
- **C# (OmniSharp):** restore and build (`dotnet build`) so project references resolve.
- **C++ (clangd):** generate `compile_commands.json` (CMake `-DCMAKE_EXPORT_COMPILE_COMMANDS=ON`) so clangd has the compilation database.

## Re-priming trigger

Priming is not one-and-done. Re-run the priming step for a language when its build inputs change — a dependency added to `Cargo.toml`/`package.json`, a pulled branch, a moved workspace member. A previously resolving operation that now returns nothing is the signal that the project needs re-priming, and is a re-verification trigger in [`../configuring-codebase/SKILL.md`](../configuring-codebase/SKILL.md).
