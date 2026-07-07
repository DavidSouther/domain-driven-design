---
name: public
description: Research public information using web search and URL fetch. Use for library docs, specs, APIs, and community knowledge. Do not use for codebase or internal documents.
---

# Overview

Public research finds answers on the open internet using `WebSearch` and `WebFetch`. It makes query variants, finds top sources, and adds inline citations to findings.

Etiquette, allowed/blocked-domain policy, and any augmentation provider belong in [the public setup reference](../using-research/references/configuring/public.md); this skill consumes the contract that skill publishes. The cross-reference makes the pairing symmetric.

# When to use / when not to use

**Use** for:
- External library or framework documentation
- Language specifications and RFCs
- Third-party API references
- Community knowledge (Stack Overflow, GitHub issues, official blogs)

**Do NOT use** for:
- Current codebase questions. Use `research:codebase` instead.
- Internal documents or private knowledge bases. Use `research:internal` instead.
- Questions answered entirely from git history. Use `research:archaeology` instead.
- Configuring sources. Setting the contact User-Agent, recording allowed/blocked domains, adjusting rate limits, or wiring an augmentation provider belong in [the public setup reference](../using-research/references/configuring/public.md).

# Query expansion (jeopardy search)

Before issuing any search, generate 3-5 variant queries:

- **Synonyms**: different words for the same concept (`timeout` / `deadline` / `cancellation`)
- **Narrow**: specific term plus technology/version context (`tokio timeout rust 1.78`)
- **Broad**: general concept without specifics (`async cancellation rust`)
- **Alternate phrasing**: question form vs. keyword form. For example: `how to set request timeout` vs. `http client timeout configuration`
- **Related terms**: adjacent concepts that appear in relevant docs (`select!`, `CancellationToken`, `AbortSignal`)

Run all variants. Union the result sets before deciding which URLs to fetch.

# Search strategy

1. Expand the research question into 3-5 query variants.
2. Run `WebSearch` for each variant.
3. Score results: prefer official docs, then GitHub, then reputable tutorials, then Stack Overflow, then blogs.
4. `WebFetch` the top 2-3 URLs per variant (skip near-duplicate URLs).
5. Compare findings across fetched sources. High-confidence facts appear in multiple independent sources.
6. Note conflicts and prefer the higher-quality source.

# Source quality

Source quality determines how much weight to assign each piece of evidence. A single high-quality source confirming a claim is stronger than five low-quality sources. No number of confirming sources proves a universal claim. One well-found counterexample refutes it. See `research/references/falsify.md`.

## Tiers

**Tier 1–Primary sources**
- Original research, published studies, raw datasets
- Official specifications and standards (IETF RFCs, W3C specs, ISO standards)
- Official documentation from the originating author or maintainer
- Primary records, legal texts, canonical source code

**Tier 2–Authoritative secondary sources**
- Peer-reviewed surveys and systematic reviews
- Official engineering blogs and technical reports from the originating organization
- Reference implementations and their accompanying documentation

**Tier 3–Practitioner sources**
- Reputable community documentation (project wikis, curated guides)
- Domain expert talks, published presentations, and editorial columns
- Q&A platforms (Stack Overflow, GitHub issues): useful for locating claims, but verify against primary sources before treating as authoritative

**Tier 4–General community content**
- Blog posts: treat as leads toward primary sources, not as findings
- Forum threads, social media, Reddit: useful for discovering that a question exists, not for answering it

Within a tier, prefer sources that are recent, specific, and cite their own sources.

## User-generated content and background alignment

When a research question involves user-generated content, adjust source weight based on the author's background. User-generated content includes forum posts, comments, project issues, and Q&A.

Content from people with a background similar to the user's carries more weight. A post from a practitioner who works in the same domain, organization type, or technical context is more likely to reflect the user's actual constraints and assumptions.

To apply this adjustment:
- Prefer content whose vocabulary and problem framing match the user's stated background
- Prefer content that addresses systems, scales, or constraints similar to the user's context
- Prefer content from people the user has referenced or whose work the user knows

Background alignment only operates within a tier. A tier-4 blog post from a closely matched practitioner is still tier 4. Use alignment only to choose between sources at the same tier when other factors are equal.

## Corroboration and falsification

High-confidence findings appear in multiple independent sources at the same or adjacent tiers. Verify any claim found only in tier-3 or tier-4 sources against a tier-1 or tier-2 source before including it as a finding.

Corroboration alone is insufficient for load-bearing claims. Confirmation bias causes search to surface confirming results and bury contradictions. When a claim drives a significant downstream decision, run a falsification pass:

1. Restate the claim as a universal ("every X does Y").
2. Negate it into 2-3 concrete hypotheses about where the claim would be false.
3. Search specifically for those negations.
4. If any search returns a counterexample, narrow, qualify, or retract the original claim.

Report which tiers corroborate each finding. Include whether a falsification pass ran, what it found (or where it looked), any conflicts between sources, and which source you preferred.

# Output format

Write findings to `.ailly/research/YYYY-MM-DD-A-<topic>/public.md`. If the caller provides a task-scoped research folder such as `.ailly/developer/<session-slug>/research/`, write `public.md` there instead.

```
# Public: <question>

## Findings
<narrative: synthesized answer with inline citations ([Source](url))>

## Sources
- [Title](url), reason consulted
- [Title](url), reason consulted
```

# Common mistakes

- **Single query only**: one phrasing frequently misses the canonical term used in official docs. Always expand first.
- **Fetching without searching**: guessing URLs skips relevance ranking. Search first, then fetch top results.
- **Stopping at snippets**: search result snippets are frequently too short. Fetch the full page for precise answers.
- **Treating blogs as authoritative**: verify blog claims against official docs before including them as findings.
- **Ignoring version specifics**: API behavior frequently differs across versions. Include the version in at least one query variant.
- **Reporting only confirming hits**: web search ranks confirming results highly and buries contradictions. When a claim is load-bearing, run a falsification pass: search specifically for the negation. See `research/references/falsify.md`.
- **Re-teaching the wiring** – A "first, set your User-Agent, record your blocked domains" preface is wiring leakage. The wiring skill (configured in the public setup reference) owns setup; this skill consumes the contract. If a preface becomes unavoidable, the contract is incomplete. Widen it in [the public setup reference](../using-research/references/configuring/public.md).

# Composes with

- **the public setup reference**: The wiring partner. Located at `research:using-research` and `references/configuring/public.md`. Publishes the contract this skill consumes: built-in web search and fetch capabilities, etiquette and domain policy, and optional augmentation provider.
- **`research:books`** and **`research:papers`**: sibling practice skills for citable books and academic papers.
- **`research/references/jeopardy.md`**: query expansion technique.
- **`research/references/citations.md`**: IEEE citation format.
- **`research/references/falsify.md`**: falsification pass for load-bearing claims.
