# TypeScript LSP (tsserver)

> Priming rules live in [`lsp-setup.md`](lsp-setup.md): run `npm install` to populate `node_modules`, then `tsc --build` for project references.
>
> **Note:** `completions` and `diagnostics` are *not* on the current `LSP` tool surface. The LSP tool exposes `goToDefinition`, `findReferences`, `hover`, `documentSymbol`, `workspaceSymbol`, `goToImplementation`, `prepareCallHierarchy`, `incomingCalls`, and `outgoingCalls`. Where they appear below they describe a server-specific path not reachable through the `LSP` tool. To enumerate members, use `hover` on the value. To check type-correctness, run `tsc` via Bash.

## Configuration

TypeScript bundles tsserver. It activates automatically when a `tsconfig.json` is present. You need no separate installation beyond `npm install` (or equivalent) to populate `node_modules`.

For accurate cross-package resolution in monorepos, configure `paths` or `references` in `tsconfig.json` correctly. Project references (`composite: true`) enable tsserver to resolve types across sub-packages.

## Most useful queries for research

### Find symbol definitions

```
LSP definition
  file: src/api/handler.ts
  line: <line where symbol appears>
  character: <column>
```

Follows `export * from`, barrel files, type aliases, and declaration merging. Works across `node_modules` into `.d.ts` declaration files when source maps are unavailable.

### Understand a type at a specific site

```
LSP hover
  file: src/api/handler.ts
  line: <line of expression>
  character: <column>
```

Returns the fully resolved type after generic substitution and type narrowing. Hover after an `if` or `switch` discriminant to see the narrowed type inside the branch. This is faster than manually tracing `typeof` / `instanceof` chains.

### Find all references / call sites

```
LSP references
  file: src/domain/user.ts    # file containing the definition
  line: <definition line>
  character: <column of name>
  includeDeclaration: false
```

Returns every usage across the project including `.tsx` files. For an interface method, returns implementations in addition to call sites when `includeDeclaration: true`.

### Find all implementations of an interface

Point `references` at the interface or abstract method definition. tsserver returns every `implements` clause and every class that satisfies the structural type (if used structurally).

Alternatively, hover on the interface name and read the "X implementations" inlay if available.

### Understand available members on a value

```
LSP completions
  file: src/service.ts
  line: <line after a `.` access>
  character: <column after the dot>
```

Returns all valid members including inherited ones and those from merged declarations. Use this to understand what a third-party type exposes without reading its `.d.ts` file manually.

### Errors in a file

```
LSP diagnostics
  file: src/service.ts
```

Returns TypeScript compiler errors: type mismatches, missing properties, and unused variables (if configured). This is useful for quickly checking whether a module is type-correct without running `tsc`.

## TypeScript-specific patterns

**Generic resolution:** hover on a call to a generic function to see the concrete type arguments TypeScript inferred. This saves you from manually tracing which overload TypeScript selected.

**Type narrowing:** hover inside an `if`, `switch`, or optional-chain branch to see the narrowed type. The type after `if (x !== null)` differs from outside. LSP shows the correct narrowed form.

**Barrel files (`index.ts`):** `definition` follows barrel re-exports to the canonical source. If a symbol appears exported from an `index.ts`, use `definition` to jump to the original implementation file.

**Declaration merging:** interfaces and namespaces merge across files. `references` on an interface name finds all merge sites as well as all `implements` sites.

**`.d.ts` only dependencies:** when a package ships only declarations (no source), `definition` lands in the `.d.ts` file. Hover there to read the type; use `completions` to enumerate members. Use LSP instead of grepping the `node_modules` source.

**Monorepo project references:** if tsserver fails to resolve cross-package imports, run `tsc --build` in the root to regenerate declaration files for referenced sub-packages.
