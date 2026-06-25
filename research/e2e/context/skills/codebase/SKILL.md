---
name: codebase
description: Use when performing research on the current codebase — finding where a symbol is defined, discovering all call sites of a function, understanding a type's structure, tracing interface implementations, or answering any question about what the code does right now at the checked-out commit.
---

# Codebase Research

## Overview

Answers research questions about the current codebase state using LSP queries first, Bash search as fallback. Never uses git history — that is archaeology's domain. Language-server install and project priming belong in [the codebase setup reference](../using-research/references/configuring/codebase.md); this skill consumes the contract that skill publishes.

## When to Use

- Finding where a symbol is defined or what type it has
- Locating all call sites / references to a function or type
- Understanding interface implementations or trait bounds
- Reading a module's public surface without opening every file

**Do NOT use** for questions about why code changed (use `archaeology`), or about dependency origins (use `dependencies`). To install or prime a language server, or to add a new language to the contract, use [the codebase setup reference](../using-research/references/configuring/codebase.md), not this skill.

## Query Expansion (Jeopardy! Search)

Before any search, generate 3-5 variants of the target term:

- **Original** — exact identifier as stated
- **Case variants** — `myFn`, `my_fn`, `my-fn`, `MyFn`
- **Synonyms** — `create`/`new`/`build`; `error`/`err`/`failure`
- **Related concepts** — interface name, trait name, module path
- **Partial prefixes** — useful for glob and completion searches

Run all variants; union results before drawing conclusions.

## Search Strategy

**Prefer LSP** (see language reference files) for:
- Symbol definitions and hover types — `goToDefinition`, `hover`
- All call sites / usages — `findReferences`
- Interface/trait implementors — `goToImplementation`
- A file's or workspace's symbol tree — `documentSymbol`, `workspaceSymbol`
- Callers / callees of a function — `prepareCallHierarchy` with `incomingCalls`/`outgoingCalls`
- Available members on a value — `hover` (the `LSP` tool exposes no `completions`)
- Errors in a file — run `cargo check` / `tsc` via Bash (the `LSP` tool exposes no `diagnostics`)

**Bash fallback** when LSP is unavailable or for:
- String literals and comments (not symbols)
- File-level discovery (`Glob` for paths, `Grep` for patterns)

**Hard constraint:** Never run `git log`, `git blame`, `git show`, `git diff`, or any other git command. Use only current-state tools. You may use `git rev-parse --short HEAD` to get the current commit sha for preparing `**Sources**`.

## Output Format

Write findings to `docs/research/YYYY-MM-DD-A-<topic>/codebase.md`.

```
# Codebase: <question>

## Findings
<narrative: what the code does, where key logic lives>

## Sources
- [1] `path/to/file.rs` [CommitSha]
- [2] `path/to/other.ts` [CommitSha]
```

## Common Mistakes

- **Single query only** — always expand before searching; renamed identifiers won't appear under old names.
- **Grep instead of LSP** — LSP follows type aliases, generics, and macros; grep matches text only.
- **Using git for context** — blame and log are archaeology tools; avoid them here.
- **Stopping at first match** — a symbol may have multiple definitions (overloads, feature flags); collect all before concluding.
- **Asserting a universal without searching its negation** — claims like "no caller does X" or "every write path does Y" are easy to state and easy to be wrong about. Before reporting a universal, search for its counterexample. See `research/references/falsify.md`.
- **Re-teaching the wiring** — a "first, make sure rust-analyzer is installed" or "activate the venv before searching" preface is wiring leakage. The wiring SKILL owns install and priming; this skill consumes the contract. If a preface is unavoidable, the contract is incomplete — widen it in [the codebase setup reference](../using-research/references/configuring/codebase.md).

## Composes With

- **the codebase setup reference** (`research:using-research`, `references/configuring/codebase.md`) — the wiring partner. Publishes the LSP-operation contract this skill consumes and owns language-server install and project priming.
- **`research/references/jeopardy.md`** — the identifier-variant query expansion this skill runs before searching.
- **`research/references/falsify.md`** — the falsification pass on universal claims (see Common Mistakes).
