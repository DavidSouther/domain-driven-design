---
name: codebase
description: Use when performing research on the current codebase. Find where code defines a symbol, discover all call sites of a function, understand a type's structure, trace interface implementations, or answer any question about what the code does right now at the checked-out commit.
---

# Codebase research

## Overview

Answers research questions about the current codebase state by using LSP queries first, Bash search as fallback.
Never uses git history.
That is archaeology's domain.
Language-server install and project priming belong in [the codebase setup reference](../using-research/references/configuring/codebase.md); this skill consumes the contract that skill publishes.

## When to use

- Finding where code defines a symbol or what type it has
- Locating all call sites / references to a function or type
- Understanding interface implementations or trait bounds
- Reading a module's public surface without opening every file

**Do NOT use** for questions about why code changed or for dependency origins.
Use `archaeology` for the former and `dependencies` for the latter.
To install or prime a language server, or to add a new language to the contract, use [the codebase setup reference](../using-research/references/configuring/codebase.md), not this skill.

## Query expansion (Jeopardy search)

Before any search, generate 3-5 variants of the target term:

- **Original:** exact identifier as stated
- **Naming variants:** `myFn`, `my_fn`, `my-fn`, `MyFn`
- **Synonyms:** `create`/`new`/`build`; `error`/`err`/`failure`
- **Related concepts:** interface name, trait name, module path
- **Partial prefixes:** useful for glob and completion searches

Run all variants; union results before drawing conclusions.

## Search strategy

**Prefer LSP** (see language reference files) for:
- Symbol definitions and hover types: `goToDefinition`, `hover`
- All call sites / usages: `findReferences`
- Interface/trait implementors: `goToImplementation`
- A file's or workspace's symbol tree: `documentSymbol`, `workspaceSymbol`
- Callers / callees of a function: `prepareCallHierarchy` with `incomingCalls`/`outgoingCalls`
- Available members on a value: `hover` (the `LSP` tool exposes no `completions`)
- Errors in a file.
  Run `cargo check` / `tsc` via Bash (the `LSP` tool exposes no `diagnostics`)

**Bash fallback** when LSP is unavailable or for:
- String literals and comments (not symbols)
- File-level discovery (`Glob` for paths, `Grep` for patterns)

**Hard constraint:** never run `git log`, `git blame`, `git show`, `git diff`, or any other git command.
Use only current-state tools.
You may use `git rev-parse --short HEAD` to get the current commit sha for preparing `**Sources**`.

## Output format

Write findings to `.ailly/research/YYYY-MM-DD-A-<topic>/codebase.md`.
When the caller provides a task-scoped research folder such as `.ailly/developer/<session-slug>/research/`, write `codebase.md` there instead.

```
# Codebase: <question>

## Findings
<narrative: what the code does, where key logic lives>

## Sources
- [1] `path/to/file.rs` [CommitSha]
- [2] `path/to/other.ts` [CommitSha]
```

## Common mistakes

- **Single query only:** always expand before searching; renamed identifiers won't appear under old names.
- **Grep instead of LSP:** LSP follows type aliases, generics, and macros; grep matches text only.
- **Using git for context:** blame and log are archaeology tools; avoid them here.
- **Stopping at first match:** a symbol may have multiple definitions (overloads, feature flags); collect all before concluding.
- **Asserting a universal without searching its negation:** claims like "no caller does X" or "every write path does Y" are easy to state and easy to be wrong about.
  Before reporting a universal, search for its counterexample.
  See `research/references/falsify.md`.
- **Re-teaching the wiring.**
  A "first, make sure you install rust-analyzer" or "activate the venv before searching" preface is wiring leakage.
  The codebase setup reference owns install and priming.
  This skill consumes the contract.
  If a preface is unavoidable, the contract is incomplete.
  Widen it in [the codebase setup reference](../using-research/references/configuring/codebase.md).

## Composes with

- **the codebase setup reference:** the wiring partner.
  See `research:using-research` and `references/configuring/codebase.md`.
  Publishes the LSP-operation contract this skill consumes and owns language-server install and project priming.
- **`research/references/jeopardy.md`:** the identifier-variant query expansion this skill runs before searching.
- **`research/references/falsify.md`:** the falsification pass on universal claims (see Common Mistakes).
