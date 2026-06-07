---
name: research
description: Web-search procedure for Ailly. Expand each query, search, fetch the best sources, and answer in the chat with inline citations. Covers the connector enhancement (the user's own authorized accounts) and the saved-report enhancement (a file written when a filesystem is present).
---

# Overview

Research answers a question with `WebSearch` and `WebFetch` against the open web. Expand each query into variants before searching, fetch the high-value sources, read them, and synthesize an answer with inline citations. On a phone the answer is the chat message itself; do not reach for files or subagents unless they are present and the work calls for them.

## When to Use

- Anything current: news, prices, releases, schedules, "what is the latest".
- External documentation: a library, framework, API, language spec, or standard.
- Anything contested or load-bearing, where a citation matters.
- Community knowledge: official blogs, GitHub issues, forums, reviews.
- A product, library, or service the user is choosing between. See [shopping.md](shopping.md).

## Query Expansion (Jeopardy! Search)

Before issuing any search, generate 3-5 variant queries. One phrasing carries one set of biases and returns the documents that share its vocabulary, quietly burying the ones that say the same thing in different words.

- **Synonyms** — different words for the same concept (`timeout` / `deadline` / `cancellation`).
- **Narrow** — the specific term plus technology or version context (`tokio timeout rust 1.78`).
- **Broad** — the general concept without specifics (`async cancellation rust`).
- **Alternate phrasing** — question form versus keyword form.
- **Related terms** — adjacent concepts that appear in the relevant documents.

Run the variants. Union the result sets before deciding which URLs to fetch. The full rationale is in [jeopardy.md](jeopardy.md).

## Search Strategy

1. Expand the question into 3-5 query variants.
2. Run `WebSearch` for each variant.
3. Score results by source quality (below). Prefer official sources.
4. `WebFetch` the top 2-3 URLs (skip near-duplicates). Read them. Do not answer from search snippets alone; a snippet is a lead, not a source.
5. Compare findings across sources. A fact that appears in several independent sources is high-confidence; a fact in one source is reported as such.
6. Note conflicts and prefer the higher-quality source.

## Source Quality

1. Official documentation (docs.rs, python.org, developer.mozilla.org, the vendor's own site).
2. The project's own source or README (GitHub, GitLab).
3. Reputable engineering blogs and standards bodies.
4. Stack Overflow and forums — useful, but verify against a primary source.
5. Random blogs and content farms — leads to a primary source, not authorities themselves.

## Answering in the Chat

This is the default. The reader is on a phone.

- **Answer first.** Open with the finding, not the method.
- **Cite inline, as links.** Put the source name in the link text, right after the claim it supports. No footnote numbers, no trailing bibliography. See [citations.md](citations.md).
- **Be brief.** A few sentences. If the topic is large, give the headline and offer to go deeper rather than dumping the whole thing.
- **Signal confidence.** When sources agree, state the fact plainly. When they conflict or only one source carries it, say so.

A worked shape:

```text
The current LTS is Node 22, released October 2024 ([Node release schedule](url)).
It is supported until April 2027. Node 20 drops to maintenance now, so a new
project should start on 22. I can compare 22 against 20 feature-by-feature if useful.
```

## Enhancement: Authorized Connectors

When the question is about the user's own world (their inbox, calendar, files, team messages, tickets) and a connector is authorized, search it the same way: expand the query, read the actual item, cite it. Cite a connector source by name and by a stable handle, "*the Linear ticket NOM-412*", "*the calendar invite for Thursday*", so the user knows exactly which item. If no connector is authorized, say what you would need and stop; do not guess at private data.

## Enhancement: Saved Report

When a filesystem is present and the user wants something to keep, write the long form to `docs/research/YYYY-MM-DD-A-<topic>/public.md`. There the heavier citation format earns its place:

```text
# Public: <question>

## Findings
<synthesized answer with inline citations>

## Sources
- [Title](url) — reason consulted
- [Title](url) — reason consulted
```

This is never the default. On a phone there is no file; the chat message is the deliverable.

## Enhancement: Parallel Falsification

A falsification pass (see [falsify.md](falsify.md)) runs faster when subagents are available: one subagent per negation, in parallel. Without subagents, run the negations in sequence in the session. The technique is the same either way; only the concurrency changes.

## Common Mistakes

- **Single query only** — one phrasing misses the canonical term; always expand first.
- **Fetching without searching** — guessing URLs skips relevance ranking; search, then fetch.
- **Stopping at snippets** — fetch the full page for a precise answer.
- **Treating blogs as authoritative** — verify against the primary source.
- **Ignoring version specifics** — behavior differs across versions; put the version in at least one variant.
- **Burying the answer** — on a phone, methodology up front loses the reader. Answer first.
- **Reporting only confirming hits** — search ranks confirmations high and buries contradictions. When a claim is load-bearing, search for the negation. See [falsify.md](falsify.md).
