# Amazon kindle

The user's e-book library.
Search for books on a topic or passages from them.

## What it provides

- **Kindle library search** (expected shape): `search-by-title(query) → { hits: [...] }`.
- **Fetch-passage** (expected shape): `fetch-passage(book_id, locator) → { text, source }`.

No public Kindle MCP exists yet.
This document shows what a Kindle server should provide so you can build or use one that matches.

## MCP options (probe order)

**Primary: user-supplied MCP** matching the expected shape.
You run any local server you choose.
For example, you might build an adapter for `MyClippings.txt` and Kindle metadata, or use a third-party tool.
This wiring records the tool names and confirms the contract.

**Fallback: `trieloff/calibre-mcp` + Kindle plugin.**
Calibre with the Kindle plugin can remove DRM and import your library.
Once imported, books are searchable through the Calibre MCP.
See [`calibre.md`](calibre.md) for details.
DRM removal is your choice and your responsibility; check your local laws.

**Fallback: `MyClippings.txt` parse.**
Every Kindle device exports highlights and notes to `MyClippings.txt`; a thin parser yields a searchable index of the user's own annotations (not the full text).

**Not-Available** when you configure none of the above.
The practice skill returns Not-Available for Kindle search and switches to Open Library, Google Books, or O'Reilly.

## HTTP fallback

None.
Amazon has no public API for Kindle library content.
The web Kindle reader works only in browsers and doesn't allow automated access.

## Stub server

**Not shipped in this repo** (Decision 1 in the plan).
This document shows what shape a Kindle server should have so you can build one without guesswork.

## Query shapes

- *"The section in a Kindle library where Eric Evans defines bounded context"* → `search-by-title("Domain-Driven Design")` → `fetch-passage(book_id, "bounded context")`.
- *"Books about Kafka"* → `search-by-title("Kafka")` filtered to the user's library.
- *"All highlights tagged systems"* (only via the `MyClippings.txt` path); full library search returns only titles.

## Licensing

Books in your Kindle library are for personal use only.
Quote them in your own work; do not share them.
DRM removal (Calibre + Kindle plugin) is legal in some places and not others; check your local laws before proceeding.

## Failure modes

- **No server configured.**
  Return Not-Available; route to alternatives.
- **DRM-locked title.**
  Calibre + Kindle plugin cannot import; the title is invisible to the search capability.
- **MyClippings.txt only path.**
  Full-text search works only on your highlights and notes; *search-by-title* only returns books you have highlighted.
