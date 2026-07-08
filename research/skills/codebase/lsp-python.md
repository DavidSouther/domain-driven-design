# LSP reference: python (pylsp / pyright)

> Priming rules (venv activation, pyright config) live in [`lsp-setup.md`](lsp-setup.md).

## Configuration

Two common Python LSPs:

- **pylsp** (python-lsp-server): installed via `pip install python-lsp-server`.
  Wraps multiple analysis backends (pyflakes, rope, jedi).
- **pyright**: installed via `npm install -g pyright` or `pip install pyright`.
  Stronger type inference; preferred for typed codebases.

Claude Code uses whichever LSP the project has configured.
For research purposes both expose the same operations (`hover`, `definition`, `references`).

> **Note:** `completions` and `diagnostics` are *not* on the current `LSP` tool surface.
> The tool exposes `goToDefinition`, `findReferences`, `hover`, `documentSymbol`, `workspaceSymbol`, `goToImplementation`, `prepareCallHierarchy`, `incomingCalls`, and `outgoingCalls`.
> Where they appear below they describe a server-specific path not reachable through the `LSP` tool; use Bash search or a typed-symbol `hover` instead.

For pyright to resolve types fully, a `pyrightconfig.json` or `pyproject.toml` with `[tool.pyright]` should be present.
Set `venvPath` or `pythonPath` to point to the active virtual environment.

## Most useful queries for research

### Locate a symbol definition

```
LSP definition
  file: src/service.py
  line: <line where symbol appears>
  character: <column>
```

Follows imports, `__init__.py` re-exports, and `from x import y as z` aliases.
More reliable than grepping for `def symbol` because it handles re-exports and conditional imports.

### Understand inferred type

```
LSP hover
  file: src/service.py
  line: <line of variable or call>
  character: <column>
```

Pyright returns the inferred type even for unannotated variables.
Use this to understand what a duck-typed parameter actually receives at a given call site, or to confirm the return type of a chained method call.

### Find all call sites / usages

```
LSP references
  file: src/service.py      # file containing the definition
  line: <def line>
  character: <column of name>
  includeDeclaration: false
```

Returns every call site across the project.
For a method defined on a class, returns calls via instances, subclasses, and `super()`.

### Understand protocol / duck-typed interface

When a function accepts a duck-typed argument, use `completions` at the point where the function body uses the argument.
The completion list shows what attributes the function assumes on the object, revealing the implicit protocol.

### Errors and type mismatches

```
LSP diagnostics
  file: src/models.py
```

Pyright reports type errors, missing attributes, and unreachable code.
Useful for quickly finding where type assumptions break without running the full test suite.

## Python-specific patterns

**Untyped code:** when there are no annotations, pyright infers types from assignments and return values.
Hover returns `Unknown` when inference fails.
This signals a place where Bash grep may be more useful than LSP.

**Dynamic attributes (`__getattr__`, dataclasses, pydantic):** pyright understands `dataclasses.dataclass` and `pydantic.BaseModel` field generation.
Hover on a field access to confirm the inferred type.

**`__init__.py` re-exports:** `definition` follows the import chain to the original definition file.
If you need to know what a package's public surface is, open the `__init__.py` and use `completions` at the module level.

**Multiple implementations of a base class:** use `references` on the base class method definition to find all overriding methods across subclasses.
This is faster than grepping for `def method_name` which returns unrelated functions with the same name.

**Virtual environment:** if LSP returns no results, confirm you activated the virtual environment and it matches your pyright configuration.
Mismatched environments cause import resolution failures.
