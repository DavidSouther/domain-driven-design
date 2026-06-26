---
name: public
description: Use when a research question requires publicly available information — external library documentation, language specifications, API references, community knowledge, or any topic not contained in the local codebase or internal documents. Applies when the answer lives on the public internet and must be fetched via web search or URL retrieval. Does not apply to codebase structure questions (use `research:codebase`) or internal document questions (use `research:internal`).
---

# Overview

Public research answers questions using `WebSearch` and `WebFetch` against the open internet. It expands each query into multiple variants before searching, fetches high-value sources, and synthesizes findings with inline citations.

Etiquette, allowed/blocked-domain policy, and any augmentation provider belong in [the public setup reference](../using-research/references/configuring/public.md); this skill consumes the contract that skill publishes. The cross-reference makes the pairing symmetric.

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
- Configuring sources: setting the contact User-Agent, recording allowed/blocked domains, adjusting rate limits, or wiring an augmentation provider — those belong in [the public setup reference](../using-research/references/configuring/public.md)

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

Source quality determines how much weight to assign each piece of evidence. A single high-quality source confirming a claim is stronger than five low-quality sources. No number of confirming sources proves a universal claim — but one well-found counterexample refutes it. See `research/references/falsify.md`.

## Tiers

**Tier 1 — Primary sources**
- Original research, published studies, raw datasets
- Official specifications and standards (IETF RFCs, W3C specs, ISO standards)
- Official documentation from the originating author or maintainer
- Primary records, legal texts, canonical source code

**Tier 2 — Authoritative secondary sources**
- Peer-reviewed surveys and systematic reviews
- Official engineering blogs and technical reports from the originating organization
- Reference implementations and their accompanying documentation

**Tier 3 — Practitioner sources**
- Reputable community documentation (project wikis, curated guides)
- Domain expert talks, published presentations, and editorial columns
- Q&A platforms (Stack Overflow, GitHub issues): useful for locating claims, but verify against primary sources before treating as authoritative

**Tier 4 — General community content**
- Blog posts: treat as leads toward primary sources, not as findings
- Forum threads, social media, Reddit: useful for discovering that a question exists, not for answering it

Within a tier, prefer sources that are recent, specific, and cite their own sources.

## User-Generated Content and Background Alignment

When a research question involves user-generated content (forum posts, comments, project issues, Q&A), adjust source weight based on the apparent background of the author relative to the user.

Content from people with a background similar to the user's carries more weight than content from unknown or unrelated backgrounds. A post from a practitioner who works in the same domain, organization type, or technical context as the user is more likely to reflect constraints and assumptions the user actually faces.

To apply this adjustment:
- Prefer content whose vocabulary and problem framing match the user's stated background
- Prefer content that addresses systems, scales, or constraints similar to the user's context
- Prefer content from people the user has referenced or whose work the user knows

Background alignment only operates within a tier. A tier-4 blog post from a closely matched practitioner is still tier 4. Use alignment only to choose between sources at the same tier when other factors are equal.

## Corroboration and Falsification

High-confidence findings appear in multiple independent sources at the same or adjacent tiers. A claim found only in tier-3 or tier-4 sources should be verified against a tier-1 or tier-2 source before inclusion as a finding.

Corroboration alone is insufficient for load-bearing claims. Confirmation bias causes search to surface confirming results and bury contradictions. When a claim drives a significant downstream decision, run a falsification pass:

1. Restate the claim as a universal ("every X does Y").
2. Negate it into 2-3 concrete hypotheses about where the claim would be false.
3. Search specifically for those negations.
4. If any search returns a counterexample, narrow, qualify, or retract the original claim.

Report which tiers each finding is supported by, whether a falsification pass was run and what it found (or where it looked), and any conflicts between sources and which was preferred.

# Output Format

Write findings to `.ailly/research/YYYY-MM-DD-A-<topic>/public.md`, unless the caller provides a task-scoped research folder such as `.ailly/developer/<session-slug>/research/`; in that case write `public.md` there.

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
- **Reporting only confirming hits** — web search ranks confirming results highly and buries contradictions. When a claim is load-bearing, run a falsification pass: search specifically for the negation. See `research/references/falsify.md`.
- **Re-teaching the wiring** — a "first, set your User-Agent / record your blocked domains" preface is wiring leakage. The wiring SKILL owns setup; this skill consumes the contract. If a preface is unavoidable, the contract is incomplete — widen it in [the public setup reference](../using-research/references/configuring/public.md).

# Composes With

- **the public setup reference** (`research:using-research`, `references/configuring/public.md`) — the wiring partner. Publishes the contract this skill consumes (built-in web search/fetch, etiquette and domain policy, optional augmentation provider).
- **`research:books`** and **`research:papers`** — sibling practice skills for citable books and academic papers.
- **`research/references/jeopardy.md`** — query expansion technique.
- **`research/references/citations.md`** — IEEE citation format.
- **`research/references/falsify.md`** — falsification pass for load-bearing claims.
