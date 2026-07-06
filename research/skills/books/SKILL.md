---
name: books
description: Use when a research question targets a citable book, including ISBN-keyed editions, public-domain full text, technical reference content (O'Reilly), the user's own library (Kindle, Apple Books, Calibre, Zotero), or aggregated public-domain digital libraries. Applies every time a research question targets books.
---

# Books

## Overview

Per-query research against the configured books capability contract. Pick the **capability** the question needs: ISBN lookup, table-of-contents, library search, or full-text retrieval. Dispatch to it, write the result with IEEE citations. The transport (MCP or HTTP) is the wiring's concern, not this skill's. Setup, key rotation, and re-verification belong in [the books setup reference](../using-research/references/configuring/books.md); this skill consumes the contract that skill publishes.

## When to use / When not to use

**Use** for:

- Citable book content: edition resolution, full-text retrieval, table-of-contents fetch, table-of-contents+section selection.
- The user's own library (Kindle, Apple Books, Calibre, Zotero, Ebook-MCP) when you configure it.
- Technical book and course content via O'Reilly Learning when access is configured.
- Reading-community signal (reviews, comparable titles) via Hardcover.

**When not to use:**

- To configure books sources, install an MCP, rotate a key, or add a new source. Those belong in [the books setup reference](../using-research/references/configuring/books.md).
- For language reference, library documentation, RFCs, or public web search. Use `research:public`.
- For internal documents (Slack, Confluence, Linear, Notion). Use `research:internal`.
- For domain-model questions (entities, bounded contexts, ubiquitous language). Use `research:domain`.
- For academic papers, preprints, DOIs, citation graphs. Use `research:papers`.

## Query expansion (Jeopardy search)

Before dispatching to a capability, expand the question into 3-5 variants; see [`research/references/jeopardy.md`](../../references/jeopardy.md) for the general technique. Books-specific axes:

- **ISBN variants** — ISBN-10 and ISBN-13; edition-specific vs work-level (Open Library `/works/{olid}` vs `/books/{olid}`).
- **Title-and-author variants** — full title, subtitle, abbreviated title, common short forms (`DDD` for *Domain-Driven Design*); first-author-only vs. all-authors.
- **Edition-disambiguation variants** — original-edition year and publisher, anniversary or annotated editions, paperback vs. hardcover, translated editions.
- **Topic-and-keyword variants** — when the user does not know the title; pair the domain keyword with the publisher's known imprint (for example, O'Reilly for Linux administration).
- **Author-name normalization** — anglicized vs. native script, initials vs. full first name, common pen-name aliases.

Run the variants in the order that the routing table below dictates. Union the result sets before deciding which capability has the highest-quality hit.

## Capability routing

[The books setup reference](../using-research/references/configuring/books.md) names the capabilities in its published contract. The routing table maps question type to the capability that answers it.

| Question intent | Primary capability | Reference |
|---|---|---|
| "What is the canonical ISBN-13 for X" | ISBN→edition lookup | [`references/open-library.md`](references/open-library.md) |
| "All editions of X" | Title+author search | [`references/open-library.md`](references/open-library.md) |
| "Quote a passage from a public-domain text" | Open full text | [`references/gutendex.md`](references/gutendex.md) |
| "Older or out-of-print scanned book" | Open full text via Internet Archive | [`references/internet-archive.md`](references/internet-archive.md) |
| "Table of contents for a recent commercial book" | Table-of-contents fetch | [`references/google-books.md`](references/google-books.md) |
| Technical / hands-on / career-skill query | O'Reilly library search | [`references/oreilly.md`](references/oreilly.md) |
| "Find a passage from a book in a user's library" | Kindle library search | [`references/kindle.md`](references/kindle.md) |
| "Find an EPUB imported into Apple Books" | Apple Books library search | [`references/claude-reader.md`](references/claude-reader.md) |
| "Search a Calibre library" | Calibre full-text search | [`references/calibre.md`](references/calibre.md) |
| "Find books saved or annotated in Zotero" | Zotero library lookup | [`references/zotero.md`](references/zotero.md) |
| Cross-corpus public-domain sweep | Aggregated public-domain search | [`references/alexandria.md`](references/alexandria.md) |
| "Local EPUB / PDF directory semantic search" | Ebook-MCP / bookreader-mcp | [`references/ebook-mcp.md`](references/ebook-mcp.md) |
| "What do other readers say about this book" | Hardcover reviews | [`references/hardcover.md`](references/hardcover.md) |
| Academic library holding confirmation | HathiTrust bibliographic API | [`references/hathitrust.md`](references/hathitrust.md) |
| Primary-source historical document | Library of Congress | [`references/library-of-congress.md`](references/library-of-congress.md) |

### Routing heuristic

The routing table is the lookup. The heuristic below is what to apply when the question does not name a source:

- **Technical or career-skill query** → O'Reilly first, then Google Books for TOC, then Open Library for edition disambiguation.
- **Classic or out-of-copyright text** → Gutendex or Internet Archive for the full text, with Open Library as the bibliographic anchor.
- **Recent commercial nonfiction** → Google Books for TOC, Open Library for edition data, Hardcover for reader signal.
- **Primary-source historical document** → Library of Congress or Internet Archive.
- **User's own corpus** → ordered by what you configure: Kindle, Apple Books (Claude Reader), Calibre, Zotero, Ebook-MCP.
- **Source unknown / broadest sweep** → Alexandria for aggregated cross-corpus discovery, then narrow to the targeted per-source capability for the strongest hits.

For conditional capabilities marked Not-Available by the contract (no MCP configured, key missing, SSO expired), accept this as a routing signal. Continue with the next capability in the heuristic. Do not pretend the source is unreachable as an error; the practice skill degrades gracefully to the public-free stack.

## Output format

Write findings to `.ailly/research/YYYY-MM-DD-A-<topic>/books.md`. If the caller provides a task-scoped research folder such as `.ailly/developer/<session-slug>/research/`, write `books.md` there instead. Cite per the loose IEEE style in [`research/references/citations.md`](../../references/citations.md). One consolidated `books.md` per session topic (per Decision 6: no per-source split, no cache).

```
# Books: <question>

## Findings
<narrative: synthesized answer with inline citations [N]>

## Sources
[1] Author/Org. "Title." Date. [Online]. Available: <URL>
[2] Author/Org. "Title." Date. [Online]. Available: <URL>
```

Excerpts only; do not stage cached PDFs or full bodies. For passages from copyrighted or licensed sources—O'Reilly, Kindle, Apple Books, Calibre, and HathiTrust gated content—quote within the session for the user's own work and cite-and-link. Do not stage to public artifacts.

## Common mistakes

- **Skipping query expansion.** A single phrasing frequently misses the canonical ISBN or the edition the user actually owns. Always expand first.
- **Mixing capabilities.** Calling Gutendex for an in-copyright recent technical book; calling Google Books for a nineteenth-century classic. Each capability has a content focus; the routing table is the lookup.
- **Quoting from non-quotable sources.** HathiTrust gated full text is non-consumptive; Hardcover reviews are user-generated under platform terms; O'Reilly content is subscription-licensed; Kindle and Apple Books content is personal-use licensed. Cite-and-link instead.
- **Ignoring typed Not-Available.** A conditional capability returning Not-Available is a routing signal, not a failure. Continue with the next capability in the heuristic.
- **Re-teaching the wiring.** A "first, make sure you have configured O'Reilly access" preface is wiring leakage. The wiring skill owns setup; this skill consumes the contract. If a preface is unavoidable, the contract is incomplete. Widen it in [the books setup reference](../using-research/references/configuring/books.md).
- **Routing the user's own corpus to public sources first.** When the user asks about a passage from a book they own, the priority order is their library (Kindle, Apple Books, Calibre, Zotero, Ebook-MCP) **before** Open Library or Internet Archive.
- **Treating Alexandria as a replacement for per-source capabilities.** Alexandria is a supplement for cross-corpus sweeps; for targeted ISBN lookup, edition disambiguation, or public-domain full-text retrieval, the per-source capability gives richer query shapes and licensing metadata.

## Composes with

- **the books setup reference**—The wiring partner that publishes the contract this skill consumes. Located at `research:using-research` and `references/configuring/books.md`.
- **`research:papers`** — sibling practice skill for academic papers.
- **`research/references/jeopardy.md`** — query expansion technique.
- **`research/references/citations.md`** — IEEE citation format.
