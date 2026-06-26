---
name: archaeology
description: Use when a research question asks why code changed over time, who introduced a behavior, when a feature was added or removed, or what motivated a past decision. Applies to questions about deleted code, renamed files, reverted changes, or the historical rationale behind current implementation. Does not apply to questions about current codebase state or dependency structure.
---

# Overview

Archaeology answers "why did this change?" questions by mining git history. It reconstructs intent from commit messages, diffs, and authorship rather than from current code state.

# When to Use

- A behavior exists (or was removed) and the reason is unknown
- A file was renamed, moved, or deleted and you need to trace its lineage
- A bug was introduced at an unknown point in time
- A decision needs historical justification from commits or PR context

**Do NOT use** for questions about current codebase structure (use `codebase`), or about dependency origins (use `dependencies`).

# Core Workflow

1. Decompose the research question into search terms (identifiers, strings, file paths, concepts).
2. Apply Jeopardy! search to expand each term into 3-5 variants before running any command.
3. Run git commands against each variant; collect matching commits.
4. Inspect the most relevant commits with `git show` to read diffs and messages.
5. Synthesize findings into a dated research note.

# Query Expansion

Before executing any git search, generate variants of each search term:

- **Original phrasing** — the term as stated in the question
- **Synonyms** — `remove` → `delete`, `drop`, `strip`; `add` → `introduce`, `create`, `implement`
- **Related concepts** — a feature name plus its associated error codes, flags, or config keys
- **Identifier casing** — `myFunction`, `my_function`, `my-function`, `MyFunction`
- **Path variants** — `src/auth/login.ts`, `auth/login`, `login`

Run each variant independently and union the results.

# Git Command Reference

```bash
# Trace a file through renames
git log --all --oneline --follow -- <path>

# Find commits that added or removed a string (pickaxe)
git log -S "search term" --oneline

# Find commits where the diff matches a regex
git log -G "regex" --oneline

# Search commit messages
git log --grep "pattern" --oneline

# Inspect a commit
git show <hash>

# Line-by-line authorship
git blame <file>

# Visualize branch topology
git log --oneline --graph --all

# Binary search for the introducing commit
git bisect start
git bisect bad HEAD
git bisect good <known-good-ref>
```

# Output Format

Write findings to `.ailly/research/YYYY-MM-DD-A-<topic>/archaeology.md`, unless the caller provides a task-scoped research folder such as `.ailly/developer/<session-slug>/research/`; in that case write `archaeology.md` there.

Structure:

```
# Archaeology: <question>

## Findings
<narrative summary of what the history shows>

## Timeline
- <hash> <date> — <what changed and why>

## Sources
- Commits consulted: <hashes>
- Commands run: <list of git commands with variants>
```

# Common Mistakes

- **Running only one query variant** — always expand before searching; a renamed identifier will not appear under its original name.
- **Reading current code** — archaeology uses only git history; current state is out of scope.
- **Stopping at the first matching commit** — the introducing commit is often preceded by a reverting commit; check surrounding history.
- **Ignoring merge commits** — merge commit messages often name the feature branch and link to external discussion.
