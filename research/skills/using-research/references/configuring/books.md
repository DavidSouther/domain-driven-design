# Configuring books

> Setup reference for the books research sources. Loaded on demand from
> `research:using-research` (see its "Configuring Sources" section) when bootstrapping or
> revising the books stack; not a standalone always-on skill. Applies once per
> environment, never inside a research session.

## Overview

This skill installs the harness that `research:books` consumes. A books research stack is a set of named **capabilities** reached through **transports**. Capabilities include ISBN lookup, full-text retrieval, and library search. Transports are MCP first, with HTTP as a fallback.

The wiring probes each source and installs marketplace plugins where required. It records the active transport and confirms that each named capability returns the shape the practice skill expects. Re-running the wiring on a configured system confirms the contract or surfaces drift; it never destroys state.

The harness this skill installs is the **books capability contract** below. The practice skill `research:books` cites the contract and dispatches capabilities; it never re-teaches the configuration.

## Contract

Once you configure the books sources (see this `books.md` reference), callers of `research:books` may assume:

| Capability | Inputs | Returns | Conditional |
|---|---|---|---|
| ISBN→edition lookup | ISBN-13 | `{ isbn13, authors, publisher, year, work_id }` | no |
| Title+author search | title, author | ranked editions with work-ID linkage | no |
| Open full text | work_id or title (public-domain) | plain text or page references | no |
| Table-of-contents fetch | volume id or title | document listing, or typed Not-Available | no |
| Calibre full-text search | query | hits from the user's local Calibre library | available when configured |
| Kindle library search | query | hits from the user's Kindle collection, or typed Not-Available | available when configured |
| O'Reilly library search | query | hits from O'Reilly Learning | available when configured |
| Apple Books library search | query | hits from the user's macOS Apple Books DRM-free imports | available when configured |
| Zotero library lookup | query, tag filter | hits from the user's Zotero library | available when configured |
| Aggregated public-domain search | query | hits across Alexandria's keyless sources | available when configured |

**Conditional capabilities** return a typed Not-Available result when the source is not configured:

```
{ result: "not-available", capability: "<name>", reason: "<why>" }
```

The practice skill treats Not-Available as a routing signal, not as an error.

**Apply the following etiquette rules:** include a contact email in the user-agent, hold the Google Books key in env, and respect per-host rate limits. Install marketplace plugins where required.

The shared rules live in [`books/references/etiquette.md`](../../../books/references/etiquette.md). Each per-source reference cites that file for the rules it inherits.

## When to use

- Standing up a fresh checkout for the first time and `research:books` has no sources to call.
- Adding a new books source, installing a new MCP server, rotating an API key, or completing the O'Reilly enterprise SSO handshake.
- Re-verifying after a re-verification trigger (see below) fires.

**When NOT to use:** inside a research session at a per-query call site. The per-query partner is `research:books`. For non-books questions use `research:public`, `research:internal`, or `research:domain`.

## Configure checklist

Walk the checklist top-to-bottom on a fresh environment. Each item probes the MCP option first, falls back to HTTP, sets env vars, and smoke-tests the capability the source provides. Smoke-test means a minimal query against the configured transport that exercises the named capability and confirms the contract holds.

Default sources for wide adoption:

- [ ] **Open Library**: probe `8enSmith/mcp-open-library`; if absent, configure HTTP fallback against `openlibrary.org` per [`books/references/open-library.md`](../../../books/references/open-library.md). Set `OPENLIBRARY_USER_AGENT` to a string containing a contact email. Smoke-test: ISBN→edition lookup for `9780321125217`.
- [ ] **Gutendex / Project Gutenberg**: probe `bobbyhouse/project-gutenberg` (needs a local Gutenberg mirror); otherwise HTTP against `gutendex.com/books` per [`books/references/gutendex.md`](../../../books/references/gutendex.md). Smoke-test: title search for *On the Origin of Species*, fetch one passage.
- [ ] **Internet Archive**: HTTP only against `archive.org/metadata` and `archive.org/advancedsearch.php` per [`books/references/internet-archive.md`](../../../books/references/internet-archive.md). Smoke-test: title search for one out-of-print technical manual.
- [ ] **Google Books**: HTTP against `googleapis.com/books/v1/volumes` per [`books/references/google-books.md`](../../../books/references/google-books.md). Set `GOOGLE_BOOKS_API_KEY`. Smoke-test: table-of-contents fetch for a recent commercial nonfiction title.

Priority sources (personal-default; conditional on access):

- [ ] **O'Reilly Learning**: probe order per [`books/references/oreilly.md`](../../../books/references/oreilly.md): official O'Reilly Learning MCP (enterprise SSO) first; if absent, `odewahn/orm-discovery-mcp` against the Platform Search API (personal subscription). If neither is reachable, mark the *O'Reilly library search* capability Not-Available. Smoke-test: search for "Kafka stream processing."
- [ ] **Amazon Kindle**: no public MCP today; configure the user-supplied MCP path or the `calibre-mcp` + Kindle plugin fallback per [`books/references/kindle.md`](../../../books/references/kindle.md). Expected capability shape: `search-by-title`, `fetch-passage`. If neither is reachable, mark the *Kindle library search* capability Not-Available. Smoke-test: search the user's Kindle library for a known title.

Opt-in sources: user's own corpus and aggregators. Configure these when the user supplies access:

- [ ] **Apple Books via Claude Reader**: probe `jasonbates/claude-reader` per [`books/references/claude-reader.md`](../../../books/references/claude-reader.md). Local; DRM-free EPUB/PDF only. Smoke-test: search a known import.
- [ ] **Calibre**: probe `trieloff/calibre-mcp` against the configured Calibre library path per [`books/references/calibre.md`](../../../books/references/calibre.md). Smoke-test: full-text search for a known phrase.
- [ ] **Zotero**: probe `54yyyu/zotero-mcp` (or `cookjohn/zotero-mcp`) per [`books/references/zotero.md`](../../../books/references/zotero.md). Set `ZOTERO_API_KEY` and `ZOTERO_LIBRARY_ID`. Smoke-test: tag filter for a known tag.
- [ ] **Alexandria (aggregator)**: probe `suavecito585/alexandria-mcp` per [`books/references/alexandria.md`](../../../books/references/alexandria.md). Smoke-test: cross-corpus query against the 46 keyless sources.
- [ ] **Ebook-MCP / bookreader-mcp**: probe `onebirdrocks/ebook-mcp` or `jtmcn/bookreader-mcp` per [`books/references/ebook-mcp.md`](../../../books/references/ebook-mcp.md). Configure the EPUB/PDF directory path. Smoke-test: semantic search for a known phrase.
- [ ] **Hardcover**: HTTP against `api.hardcover.app/v1/graphql` per [`books/references/hardcover.md`](../../../books/references/hardcover.md). Set `HARDCOVER_API_KEY`. Smoke-test: review search for a known title.
- [ ] **HathiTrust**: HTTP against `catalog.hathitrust.org/api/volumes/...` per [`books/references/hathitrust.md`](../../../books/references/hathitrust.md). The Bibliographic API is publicly available; the full-text Data API requires OAuth, configure when institutional access is available.
- [ ] **Library of Congress**: HTTP against `loc.gov/{endpoint}/?fo=json` per [`books/references/library-of-congress.md`](../../../books/references/library-of-congress.md). Smoke-test: digitized primary-source query.

**Marketplace plugins.** Books currently uses no Anthropic-curated marketplace plugins, but this skill includes the configure step for parity with the papers setup reference (`papers.md`). The shape is the same when you add one later: `/plugin marketplace add anthropics/<marketplace>` then `/plugin install <plugin>@<marketplace>`, complete SSO if prompted.

**Out-of-scope sources** appear in [`books/references/out-of-scope.md`](../../../books/references/out-of-scope.md) with the reasons for excluding each.

## Re-verification triggers

Re-run the wiring when any of the following happens. Re-running confirms the contract still holds; on a configured system it does not destroy state.

- An MCP server upgrades and its tool surface or response shape may have shifted.
- An API key rotates or an OAuth token expires. Examples include Google Books, Hardcover, HathiTrust, Zotero, and O'Reilly SSO.
- You add a new books source that should sit in the contract.
- A practice run reports a drift: a capability returned a shape the practice skill did not expect, or a smoke-test that previously passed now fails.
- **O'Reilly individual access opens.** Target is 2026 with no published date as of writing. When the official O'Reilly Learning MCP becomes available to individual subscribers, promote it from the enterprise-only probe to the primary transport for personal use and update [`books/references/oreilly.md`](../../../books/references/oreilly.md) accordingly.

## Composes with

- **`research:books`**: the per-query partner. Wiring publishes the contract; practice consumes it.
- **the papers setup reference (`papers.md`)**: sibling wiring for the papers stack. The two harnesses are disjoint at the source level but share the cadence convention.
- **`research/references/citations.md`**: IEEE citation format the practice skill writes against.
- **`research/references/jeopardy.md`**: query expansion the practice skill applies before dispatching to a capability.
