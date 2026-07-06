# Calibre

The user's local Calibre catalog with curated metadata and DRM-stripped full-text search. Strong for a power-user e-book library.

## What it provides

- **Calibre full-text search** via Calibre's built-in full-text engine.
- **Library metadata** — title, author, publisher, series, tags, custom columns.
- **Passage retrieval** from indexed books.

## MCP option

`trieloff/calibre-mcp` — searches a local Calibre catalog and returns matching passages. Install per the repo README. Configuration: a path to the Calibre library directory (typically `~/Calibre Library`). No external auth required.

## HTTP fallback

If the user runs Calibre's content server (`calibre-server`), it exposes a local HTTP API at the configured port. Treat it as opt-in; most users do not have it running.

- Endpoint shape: `http://localhost:8080/ajax/search/?query=...`
- Auth: configured in `calibre-server`; default is none.

## Query shapes

- *"Search the Calibre library for any book mentioning Conway's law"* — Calibre full-text search.
- *"All books in the `architecture` Calibre tag"* — metadata query on `tags:architecture`.
- *"Find the passage where Brooks discusses team scaling and productivity"* — full-text search with a phrase query.

## Licensing

Books in the user's Calibre library are **personal-use licensed**. The user is the licensee; quotation rights depend on the original work. Calibre can DRM-strip with the appropriate plugin (Kindle, Adobe ADE); DRM stripping is the user's choice and responsibility.

## Failure modes

- **Library path wrong** — the MCP cannot find the catalog. Re-configure with the absolute path.
- **Full-text index out of date** — Calibre rebuilds the index in the background; recently added books may be invisible until the index catches up. The Calibre UI has a "Reindex now" action.
- **DRM-locked book** — full-text search does not match the body; only metadata is searchable.
