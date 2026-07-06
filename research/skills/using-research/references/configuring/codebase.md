# Configuring codebase

> Setup reference for the codebase language servers. Loaded on demand from
> `research:using-research` (see its "Configuring Sources" section) when bootstrapping or
> revising the LSP stack; not a standalone always-on skill. Applies once per environment,
> never inside a research session.

## Overview

This skill installs the harness that `research:codebase` consumes. A codebase research stack is a set of named **LSP operations** made available by a **language server for each language present** in the checkout. These operations include definition, references, hover, document symbols, workspace symbols, implementations, and call hierarchy.

The transport is the built-in `LSP` tool. The wiring ensures each language has its server installed and resolving so that `LSP` operations return real results instead of "no server configured."

The wiring detects each language by checking for `Cargo.toml`, `pyproject.toml`/`venv`, or `tsconfig.json`. It confirms the server is present, primes it (with `cargo check`, venv activation, or `npm install`), and smoke-tests one operation per language. Re-running the wiring on a configured system confirms the contract or surfaces drift. It never destroys state.

The harness this skill installs is the **codebase capability contract** below. The practice skill `research:codebase` cites the contract and dispatches LSP operations, falling back to Bash search where a language is Not-Available. It never re-teaches the configuration.

## Contract

Once you configure the codebase language servers using this reference, callers of `research:codebase` may assume the following LSP operations are available **for each language whose server resolved**. Operation names match the built-in `LSP` tool surface:

| Capability | Inputs | Returns | Conditional |
|---|---|---|---|
| Definition (`goToDefinition`) | filePath, line, character | defining locations, following re-exports/aliases | available per language |
| References (`findReferences`) | filePath, line, character | all usage locations across the workspace | available per language |
| Hover (`hover`) | filePath, line, character | resolved type and doc for the symbol | available per language |
| Document symbols (`documentSymbol`) | filePath | the file's symbol tree (functions, types, members) | available per language |
| Workspace symbols (`workspaceSymbol`) | query | matching symbols across the workspace | available per language |
| Implementations (`goToImplementation`) | filePath, line, character | implementors of an interface/trait/abstract method | available per language |
| Call hierarchy | filePath, line, character | callers and callees of functions | available per language |

Capability count: **7** LSP operations, each available per language that resolved. Call hierarchy counts as one capability with three calls. The capability axis is **language**, not source. An operation is available for Python when pyright or pylsp resolved, for Rust when rust-analyzer resolved, and for TypeScript when typescript-language-server resolved.

A language with no installed server returns the typed Not-Available result for all seven operations; the practice skill falls back to Bash `Grep`/`Glob` for that language:

```
{ result: "not-available", capability: "<operation>", reason: "<no language server for <lang>; falls back to Bash search>" }
```

The practice skill treats Not-Available as a routing signal, not as an error.

**Note on operation surface.** The built-in `LSP` tool exposes `goToDefinition`, `findReferences`, `hover`, `documentSymbol`, `workspaceSymbol`, `goToImplementation`, `prepareCallHierarchy`, `incomingCalls`, and `outgoingCalls`. It does **not** expose `completions` or `diagnostics`. The preceding contract lists only operations the tool actually exposes. The per-language `lsp-*.md` references footnote `completions` and `diagnostics` as not on the current `LSP` tool surface.

**Toolchain is primed:** for each language the server resolves, the project is ready. The Rust crate graph has been built via `cargo check`. The Python venv has been activated and matches the pyright config. TypeScript has `node_modules` populated and project references built.

The shared rules live in [`../codebase/lsp-setup.md`](../../../codebase/lsp-setup.md), which contains the priming and configuration rules shared across this stack. Each per-language `lsp-*.md` file cites this for the priming step it inherits.

## When to use

- Standing up a fresh checkout for the first time and `research:codebase` has no language server resolving its LSP operations.
- Adding a new language to the checkout, installing or upgrading a language server, or re-priming after a toolchain bump.
- Re-verifying after a re-verification trigger (see below) fires.

**When NOT to use:** inside a research session at a per-query call site. The per-query partner is `research:codebase` — dispatching `goToDefinition`/`findReferences`/etc. against the contract this skill publishes is its job, not this one's. For non-codebase questions use `research:public`, `research:internal`, or `research:domain`.

## Configure checklist

Walk the checklist top-to-bottom on a fresh environment. Each item detects whether the language is present, confirms or installs its server, primes the project so the server resolves, and smoke-tests one operation. Smoke-test means a minimal LSP operation that confirms the server returns the contract shape.

Default languages (detect from the checkout; configure each that is present):

- [ ] **Rust** — present when `Cargo.toml` exists. rust-analyzer is the standard server and activates automatically. Prime with `cargo check` so the crate graph resolves, per the priming rules in [`../codebase/lsp-setup.md`](../../../codebase/lsp-setup.md) and [`../codebase/lsp-rust.md`](../../../codebase/lsp-rust.md). Smoke-test: `goToDefinition` on a known `pub fn`. If `cargo check` fails, mark the Rust capabilities Not-Available and fall back to Bash.
- [ ] **Python** — present when `pyproject.toml`, `setup.py`, or `*.py` exists. Install pyright (`pip install pyright` or `npm install -g pyright`); pylsp is the alternative. Activate the venv and point the pyright config at it, per [`../codebase/lsp-setup.md`](../../../codebase/lsp-setup.md). Per [`../codebase/lsp-python.md`](../../../codebase/lsp-python.md). Smoke-test: `hover` on a typed symbol returns a concrete type (not `Unknown`). If the venv is wrong or absent, mark the Python capabilities Not-Available.
- [ ] **TypeScript / JavaScript** — present when `tsconfig.json` or `package.json` exists. typescript-language-server (tsserver) ships with TypeScript; run `npm install` (or equivalent) to populate `node_modules`, and `tsc --build` for monorepo project references, per [`../codebase/lsp-setup.md`](../../../codebase/lsp-setup.md). Per [`../codebase/lsp-typescript.md`](../../../codebase/lsp-typescript.md). Smoke-test: `findReferences` on an exported symbol crosses files. If resolution fails, mark the TS capabilities Not-Available.

Priority languages (configure when present and the user works in them):

- [ ] **Go, Java, C#, C++** and other compiled languages. Detect from the project's manifest (`go.mod`, `pom.xml`, `build.gradle`, `.csproj`, or `CMakeLists.txt`). For each language, confirm the standard server is installed (gopls for Go, jdtls for Java, OmniSharp for C#, clangd for C++). Prime the build so the server resolves, add the language to the contract, and smoke-test one operation. Document per a new `../codebase/lsp-<lang>.md` file created when first configured.

Opt-in languages (configure on demand):

- [ ] **Any other language with an LSP** — same shape: detect, install the server, prime, smoke-test, add to the contract. If no server exists for the language, mark its capabilities Not-Available; the practice skill uses Bash search for that language.

**No marketplace plugins and no env vars** are required for the default stack. Language servers are toolchain installs, not credentialed MCPs. This item is called out for parity with the sibling skills. The codebase stack has no auth to configure, which is the structural opposite of the internal setup reference (`internal.md`).

## Re-verification triggers

Re-run the wiring when any of the following happens. Re-running confirms the contract still holds; on a configured system it does not destroy state.

- **A toolchain bump** — Rust edition or `rustc` version, Python version, or Node major version. The server may resolve differently or you may need to reinstall it.
- A language server upgrade that changes its operation surface or response shape.
- **The crate graph or `node_modules` goes stale** — you added a dependency, moved a workspace member, or have not re-run `cargo check` or `npm install` since the last pull. A previously resolving `goToDefinition` now returns nothing.
- You add a new language to the checkout that should sit in the contract.
- A practice run reports drift: an operation returned nothing where it previously resolved, often due to an unactivated venv or an unbuilt project.

## Composes with

- **`research:codebase`** — the per-query partner. Wiring confirms the servers resolve; practice dispatches LSP operations and falls back to Bash where a language is Not-Available.
- **the internal setup reference (`internal.md`)** and **the public setup reference (`public.md`)** — sibling wiring for the other two stacks. Disjoint at the source level; shared cadence convention.
- **the books setup reference (`books.md`)** and **the papers setup reference (`papers.md`)** — the established sibling wiring references in the family.
- **`research/references/falsify.md`** — the "search the negation before asserting a universal" rule the practice skill's Common Mistakes already point at; the wiring skill names it so the pair shares the reference. See [`../../references/falsify.md`](../../../../references/falsify.md).
- **`research/references/jeopardy.md`** — the identifier-variant query expansion (capitalization variants, synonyms) the practice skill runs before searching. See [`../../references/jeopardy.md`](../../../../references/jeopardy.md).

Note: codebase composes with `falsify.md` and `jeopardy.md`, not `citations.md`. Its Sources section uses the `path [CommitSha]` file-reference form, not inline IEEE numbering. This matches the practice skill's existing output block.
