# Claude Reader (Apple Books)

The user's macOS Apple Books DRM-free imports — typically self-uploaded EPUBs and PDFs (academic theses, technical reports, self-published work). Use for personally-curated material outside Kindle.

## What it provides

- **Apple Books library search** over DRM-free imports.
- **Chapter navigation** — `get_current_chapter`, `goto`.

DRM-protected books in Apple Books are auto-skipped.

## MCP option

`jasonbates/claude-reader` (Apache-style MIT license, not affiliated with Anthropic). Tools: `get_current_chapter`, `search_library`, `goto`. Runs locally on macOS against the Apple Books library directory.

Install: clone the repo and follow the README; configure the MCP entry in Claude Code settings. No env vars; the server reads the Apple Books library at the standard macOS path.

## HTTP fallback

None. Apple Books is local-only; no public API exists.

## Query shapes

- *"That EPUB I imported about software architecture last spring"* → `search_library("software architecture")`.
- *"Open chapter 4 of the thesis I imported"* → `search_library("thesis title")` → `goto(book_id, "chapter-4")`.

## Licensing

User-imported EPUBs and PDFs are **personal-use licensed**. The user is the licensee; quotation rights depend on the original work. Within the user's own session, quoting is fine; do not stage passages from copyrighted personal imports into public artifacts.

## Failure modes

- **macOS only** — on other OSes the *Apple Books library search* capability returns Not-Available.
- **DRM-locked book** — skipped silently. The user's purchased iBooks are typically DRM-locked and will not appear.
- **Index out of date** — Apple Books reindexes asynchronously; recently-added books may not appear until the system finishes.
