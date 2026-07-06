# Ebook-mcp / bookreader-mcp

The user's local EPUB or PDF directory. `bookreader-mcp` adds ChromaDB semantic vector search across the directory. Use for a corpus the user has assembled outside Calibre or Apple Books.

## What it provides

- **EPUB and PDF reading** — `get_metadata`, `get_toc`, `get_chapter_markdown` (ebook-mcp).
- **Semantic search** over an EPUB directory (bookreader-mcp).

## Mcp options

`onebirdrocks/ebook-mcp` (Apache-2.0). Tools: `get_metadata`, `get_toc`, `get_chapter_markdown`. Query-driven, not vector-indexed. Configuration: the path to the EPUB/PDF directory.

`jtmcn/bookreader-mcp`. ChromaDB-backed semantic search over an EPUB directory. Useful when the corpus is large enough that keyword search returns too many hits.

Both are local-only; no auth.

## Http fallback

None. These are local file-system tools.

## Query shapes

- *"Semantic search across an EPUB folder for any mention of Aggregate consistency"* → `bookreader-mcp` semantic query.
- *"Open the table of contents for a PDF"* → `ebook-mcp` `get_toc`.
- *"Quote section 3 from a technical EPUB"* → `ebook-mcp` `get_chapter_markdown`.

## Licensing

Per the original work. The user owns the files; quotation rights depend on the underlying license. For DRM-free public-domain EPUBs (Project Gutenberg dumps, Standard Ebooks), quote freely. For commercial purchases, quote within the user's own session and do not redistribute.

## Failure modes

- **Path not configured** — the MCP cannot find the directory. Configure with an absolute path.
- **Mixed-language EPUBs** — Chroma's semantic embeddings degrade across language boundaries; route to ebook-mcp's exact-match TOC when the EPUB mixes languages.
- **Index out of date** — bookreader-mcp's ChromaDB index does not refresh automatically; trigger a re-index when the directory changes.
