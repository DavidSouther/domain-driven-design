---
name: dependencies
description: Use when answering questions about a project's declared dependencies, library versions, package constraints, module requirements, or third-party imports. You must not have already loaded the dependency source in context.
---

# Dependencies research

## Overview

Answers research questions about a project's declared dependencies.
Reads main config files and uses LSP for type resolution.
Searches local source when available and fetches external docs when not.

## When to use / when not to use

**Use when:** asked about a dependency's version, API, changelog, compatibility, or purpose.

**Do NOT use when:**
- Source code is already in context (read it directly)
- Asked about transitive/resolved deps.
  Those live in lock files, which this skill ignores
- Asked about internal usage patterns.
  Use the `codebase` skill for that

## Query expansion (jeopardy search)

Before any search, generate 3–5 variant queries covering:
- Different phrasings: "latest version" / "current release" / "newest tag"
- Synonyms: "dependency" / "package" / "module" / "library" / "requirement"
- Package name variants: exact name, scoped name (`@scope/pkg`), import path
- Related concepts: changelog, migration guide, breaking changes, API surface

Run the best 2–3 variants.
Stop when results converge.

## Search strategy

Follow this order and stop as soon as you answer the question:

1. **Read main config**: identify declared dependencies and version constraints
2. **LSP hover**: on relevant import statements to get resolved type signatures
3. **Local source**: if the project vendors the dependency or it lives in a monorepo sibling, use Bash to search it
4. **Web**: use WebSearch + WebFetch for docs, changelogs, or API references when source is not local

## Ecosystem config files reference

| Ecosystem | Read | Never read |
|-----------|------|------------|
| Node.js | `package.json` | `package-lock.json`, `yarn.lock`, `pnpm-lock.yaml` |
| Rust | `Cargo.toml` | `Cargo.lock` |
| Python | `pyproject.toml`, `setup.py`, `requirements.txt` | `requirements.lock`, `pip.lock` |
| Go | `go.mod` | `go.sum` |
| Java/Kotlin | `pom.xml`, `build.gradle`, `build.gradle.kts` | None |

## Output format

Find `.ailly/research/YYYY-MM-DD-A-<topic>/` and write findings to `dependencies.md` inside it.
If the caller provides a task-scoped research folder such as `.ailly/developer/<session-slug>/research/`, write `dependencies.md` there instead.

Include a `**Sources**` section listing every config path and URL consulted.

## Common mistakes

- Reading lock files.
  They list resolved transitive deps, not declared deps; ignore them.
- Searching git history.
  Use the `archaeology` skill for that.
- Searching codebase for usage.
  Use the `codebase` skill for that.
- Running a single query.
  Always expand to 3–5 variants before searching.
