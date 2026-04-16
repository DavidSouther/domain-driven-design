---
name: dependencies
description: Use when answering questions about a project's declared dependencies, library versions, package constraints, module requirements, or third-party imports — and the dependency source is not already loaded in context.
---

# Dependencies Research

## Overview

Answers research questions about a project's declared dependencies by reading main config files, using LSP for type resolution, searching local source when available, and fetching external docs when not.

## When to Use / When NOT to Use

**Use when:** asked about a dependency's version, API, changelog, compatibility, or purpose.

**Do NOT use when:**
- Source code is already in context (read it directly)
- Asked about transitive/resolved deps — those live in lock files, which this skill ignores
- Asked about internal usage patterns — that is the `codebase` skill

## Query Expansion (Jeopardy! Search)

Before any search, generate 3–5 variant queries covering:
- Different phrasings: "latest version" / "current release" / "newest tag"
- Synonyms: "dependency" / "package" / "module" / "library" / "requirement"
- Package name variants: exact name, scoped name (`@scope/pkg`), import path
- Related concepts: changelog, migration guide, breaking changes, API surface

Run the best 2–3 variants. Stop when results converge.

## Search Strategy

Follow this order — stop as soon as the question is answered:

1. **Read main config** — identify declared dependencies and version constraints
2. **LSP hover** — on relevant import statements to get resolved type signatures
3. **Local source** — if the dependency is vendored or a monorepo sibling, use Bash to search it
4. **Web** — use WebSearch + WebFetch for docs, changelogs, or API references when source is not local

## Ecosystem Config Files Reference

| Ecosystem | Read | Never read |
|-----------|------|------------|
| Node.js | `package.json` | `package-lock.json`, `yarn.lock`, `pnpm-lock.yaml` |
| Rust | `Cargo.toml` | `Cargo.lock` |
| Python | `pyproject.toml`, `setup.py`, `requirements.txt` | `requirements.lock`, `pip.lock` |
| Go | `go.mod` | `go.sum` |
| Java/Kotlin | `pom.xml`, `build.gradle`, `build.gradle.kts` | — |

## Output Format

Find `docs/research/YYYY-MM-DD-<topic>/` and write findings to `dependencies.md` inside it.

Include a `**Sources**` section listing every config file path and URL consulted.

## Common Mistakes

- Reading lock files — they list resolved transitive deps, not declared deps; ignore them
- Searching git history — use the `archaeology` skill for that
- Searching codebase for usage — use the `codebase` skill for that
- Running a single query — always expand to 3–5 variants before searching
