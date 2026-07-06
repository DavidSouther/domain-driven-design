# LSP reference: rust (rust-analyzer)

> Priming rules (`cargo check` so the crate graph resolves) live in [`lsp-setup.md`](lsp-setup.md).

## Configuration

rust-analyzer is the standard LSP for Rust. It activates automatically when a `Cargo.toml` is present. Ensure the project has been built at least once (`cargo check` or `cargo build`) so rust-analyzer can resolve the crate graph.

You don't need additional configuration for the LSP tool in Claude Code. Open any `.rs` file and queries are available.

## Most useful queries for research

### Find where code defines a symbol

```
LSP definition
  file: src/lib.rs
  line: <line where symbol appears>
  character: <column of symbol start>
```

Follows `pub use` re-exports, macro-generated items, and `derive` expansions. More reliable than grepping for `fn symbol_name` because it resolves across crate boundaries.

### Understand a type or function signature

```
LSP hover
  file: src/handler.rs
  line: <line of call site>
  character: <column>
```

Returns the full resolved type including generic parameters, lifetime annotations, and the doc comment. Use this to understand what a call site actually receives. Especially useful when rust-analyzer infers the type or a trait bound provides it.

### Find all call sites / usages

```
LSP references
  file: src/lib.rs          # file containing the definition
  line: <definition line>
  character: <definition column>
  includeDeclaration: false
```

Returns every reference in the workspace. For a trait method, this returns all call sites across all implementors. For a struct field, returns all read and write sites.

### Find all trait implementors

Point `references` at the trait definition itself (the `trait Foo` line). rust-analyzer returns every `impl Foo for ...` block in the workspace.

### Errors in a file

> **Note:** `diagnostics` is *not* on the current `LSP` tool surface. That surface exposes `goToDefinition`, `findReferences`, `hover`, `documentSymbol`, `workspaceSymbol`, `goToImplementation`, `prepareCallHierarchy`, `incomingCalls`, and `outgoingCalls`. To check whether a module compiles, run `cargo check` via Bash rather than reaching for an LSP diagnostics call.

```
LSP diagnostics
  file: src/main.rs
```

Returns compile errors and warnings rust-analyzer has inferred without a full `cargo build`. Useful for quickly checking whether a module compiles after reading it.

## Rust-specific patterns

**Macros:** `definition` and `hover` pierce through macro invocations. If a `derive` or `macro_rules!` generates a symbol, hover on the generated item and rust-analyzer expands it.

**Trait bounds and generics:** hover on a generic parameter at a call site to see the inferred concrete type. This is faster than tracing the call chain manually.

**Feature flags:** rust-analyzer resolves based on the active feature set (in most cases `default`). If a symbol seems missing, check whether it is behind a non-default feature and adjust `cargo.features` in your rust-analyzer config.

**Re-exports:** `definition` follows `pub use` chains to the canonical definition file, not the re-export site. Use `references` on the re-export to find all import sites.

**Workspace crates:** queries work across the entire Cargo workspace. You do not need to open the defining crate's file first.
