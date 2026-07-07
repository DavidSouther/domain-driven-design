# Amazon kindle

The user's e-book collection. Use for "what you read about X" or "find a passage from a book you own."

## What it provides

- **Kindle library search** (expected shape): `search-by-title(query) → { hits: [...] }`.
- **Fetch-passage** (expected shape): `fetch-passage(book_id, locator) → { text, source }`.

No public MCP exists for Kindle today; the wiring defines the **expected capability shape** so the user can supply a server that conforms.

## MCP options (probe order)

**Primary: user-supplied MCP** conforming to the expected shape in the preceding section. The user runs whatever local server they prefer. For example, they might use a homegrown adapter against `MyClippings.txt` and the Kindle library metadata, or a third-party tool. The wiring records the tool names and confirms the contract.

**Fallback: `trieloff/calibre-mcp` + Kindle plugin.** Calibre with the Kindle import plugin can DRM-strip and import the Kindle library; once imported, the user's books are searchable through the Calibre MCP. See [`calibre.md`](calibre.md) for the Calibre side. DRM stripping is a user choice with legal implications and is the user's responsibility.

**Fallback: `MyClippings.txt` parse.** Every Kindle device exports highlights and notes to `MyClippings.txt`; a thin parser yields a searchable index of the user's own annotations (not the full text).

**Not-Available** when the user configures none of the preceding options. The practice skill returns a typed Not-Available for the Kindle library search capability and degrades to Open Library, Google Books, or O'Reilly.

## HTTP fallback

None. Amazon does not expose a public API for Kindle library content. The web-based Kindle reader is browser-only and is not licensed for programmatic access.

## Stub server

**Not shipped in this repo** (Decision 1 in the plan). This document describes the expected capability shape so a user-supplied server can conform without re-discovering the API surface.

## Query shapes

- *"The section in a Kindle library where Eric Evans defines bounded context"* → `search-by-title("Domain-Driven Design")` → `fetch-passage(book_id, "bounded context")`.
- *"Books about Kafka"* → `search-by-title("Kafka")` filtered to the user's library.
- *"All highlights tagged systems"* (only via the `MyClippings.txt` path); full library search returns only titles.

## Licensing

Books in the user's Kindle library are **personal-use licensed**. Quote within the user's own session for their own work; do not redistribute. DRM stripping (Calibre + Kindle plugin) is jurisdictionally varied; document and defer to the user.

## Failure modes

- **No server configured.** Return Not-Available; route to alternatives.
- **DRM-locked title.** Calibre + Kindle plugin cannot import; the title is invisible to the search capability.
- **MyClippings.txt only path.** Full-text search works only with highlights and notes; the *search-by-title* capability returns hits only for books the user has highlighted.
