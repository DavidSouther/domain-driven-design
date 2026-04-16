---
name: public
description: Use when a research question requires publicly available information — external library documentation, language specifications, API references, community knowledge, or any topic not contained in the local codebase or internal documents. Applies when the answer lives on the public internet and must be fetched via web search or URL retrieval. Does not apply to codebase structure questions (use `research:codebase`) or internal document questions (use `research:internal`).
---

# Overview

Public research answers questions using `WebSearch` and `WebFetch` against the open internet. It expands each query into multiple variants before searching, fetches high-value sources, and synthesizes findings with inline citations.

# When to Use / When NOT to Use

**Use** for:
- External library or framework documentation
- Language specifications and RFCs
- Third-party API references
- Community knowledge (Stack Overflow, GitHub issues, official blogs)

**Do NOT use** for:
- Current codebase questions — use `research:codebase`
- Internal documents or private knowledge bases — use `research:internal`
- Questions answered entirely from git history — use `research:archaeology`

# Query Expansion (Jeopardy! Search)

Before issuing any search, generate 3-5 variant queries:

- **Synonyms** — different words for the same concept (`timeout` / `deadline` / `cancellation`)
- **Narrow** — specific term plus technology/version context (`tokio timeout rust 1.78`)
- **Broad** — general concept without specifics (`async cancellation rust`)
- **Alternate phrasing** — question form vs. keyword form (`how to set request timeout` vs. `http client timeout configuration`)
- **Related terms** — adjacent concepts that appear in relevant docs (`select!`, `CancellationToken`, `AbortSignal`)

Run all variants. Union the result sets before deciding which URLs to fetch.

# Search Strategy

1. Expand the research question into 3-5 query variants.
2. Run `WebSearch` for each variant.
3. Score results: prefer official docs, then GitHub, then reputable tutorials, then Stack Overflow, then blogs.
4. `WebFetch` the top 2-3 URLs per variant (skip near-duplicate URLs).
5. Compare findings across fetched sources. High-confidence facts appear in multiple independent sources.
6. Note conflicts and prefer the higher-quality source.

# Source Quality

1. Official documentation (docs.rs, python.org, typescriptlang.org, developer.mozilla.org, etc.)
2. GitHub source or README for the library itself
3. Reputable tutorials (MDN, official engineering blogs)
4. Stack Overflow (useful but verify against primary sources)
5. Random blogs (treat as leads to primary sources, not as authoritative)

# Output Format

Write findings to `docs/research/YYYY-MM-DD-<topic>/public.md`.

```
# Public: <question>

## Findings
<narrative: synthesized answer with inline citations ([Source](url))>

## Sources
- [Title](url) — reason consulted
- [Title](url) — reason consulted
```

# Common Mistakes

- **Single query only** — one phrasing often misses the canonical term used in official docs; always expand first.
- **Fetching without searching** — guessing URLs skips relevance ranking; search first, then fetch top results.
- **Stopping at snippets** — search result snippets are often too short; fetch the full page for precise answers.
- **Treating blogs as authoritative** — verify blog claims against official docs before including them as findings.
- **Ignoring version specifics** — API behavior often differs across versions; include the version in at least one query variant.
