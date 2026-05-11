# Amazon Kindle

The user's personal e-book collection across genres and depth. Use for "what did I read about X" or "find a passage from a book I already own".

## What it provides

- **Kindle library search** (expected shape): `search-by-title(query) → { hits: [...] }`.
- **Fetch-passage** (expected shape): `fetch-passage(book_id, locator) → { text, source }`.

No public MCP exists for Kindle today; the wiring defines the **expected capability shape** so the user can supply a server that conforms.

## MCP options (probe order)

**Primary: user-supplied MCP** conforming to the expected shape above. The user runs whatever local server they prefer (a homegrown adapter against `MyClippings.txt` and the Kindle library metadata, or a third-party tool); the wiring records the tool names and confirms the contract.

**Fallback: `trieloff/calibre-mcp` + Kindle plugin** — Calibre with the Kindle import plugin can DRM-strip and ingest the Kindle library; once imported, the user's books are searchable through the Calibre MCP. See [`calibre.md`](calibre.md) for the Calibre side. DRM stripping is a user choice with legal implications and is the user's responsibility.

**Fallback: `MyClippings.txt` parse** — every Kindle device exports highlights and notes to `MyClippings.txt`; a thin parser yields a searchable index of the user's own annotations (not the full text).

**Not-Available** when none of the above is configured. The practice skill returns a typed Not-Available for the Kindle library search capability and degrades to Open Library, Google Books, or O'Reilly.

## HTTP fallback

None. Amazon does not expose a public API for Kindle library content. The Kindle Cloud Reader is browser-only and is not licensed for programmatic access.

## Stub server

**Not shipped in this repo** (Decision 1 in the plan). The expected capability shape is documented here so a user-supplied server can conform without re-discovering the API surface.

## Query shapes

- *"The chapter in my Kindle library where Eric Evans defines Bounded Context"* → `search-by-title("Domain-Driven Design")` → `fetch-passage(book_id, "Bounded Context")`.
- *"Books I have on Kafka"* → `search-by-title("Kafka")` filtered to the user's library.
- *"All my highlights tagged systems"* — only via the `MyClippings.txt` path; full library search is restricted to titles.

## Licensing

Books in the user's Kindle library are **personal-use licensed**. Quote within the user's own session for their own work; do not redistribute. DRM stripping (Calibre + Kindle plugin) is jurisdictionally varied; document and defer to the user.

## Failure modes

- **No server configured** — return Not-Available; route to alternatives.
- **DRM-locked title** — Calibre + Kindle plugin cannot import; the title is invisible to the search capability.
- **MyClippings.txt only path** — full-text search is restricted to highlights and notes; the *search-by-title* capability returns hits only for books the user has highlighted.
