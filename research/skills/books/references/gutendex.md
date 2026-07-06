# Gutendex / project Gutenberg

Public-domain classics: literature, philosophy, classical, and Enlightenment-era science and mathematics, historical documents through roughly the early twentieth century. Use when the query targets an out-of-copyright text or its full passage.

## What it provides

- **Title+author search** over the Project Gutenberg catalog.
- **Open full text** — plain text, HTML, or EPUB for any cataloged work.
- **Subject and language filtering** — `topic=`, `languages=`.

Example payload (`/books/{id}`):

```
{ "id": 1228, "title": "On the Origin of Species", "authors": [...],
  "formats": { "text/plain; charset=utf-8": "https://www.gutenberg.org/files/1228/1228-0.txt",
               "application/epub+zip": "https://www.gutenberg.org/ebooks/1228.epub.images" } }
```

## MCP option

`bobbyhouse/project-gutenberg` — exposes `search_books`, `get_book_metadata`, `fetch_book_text`, `list_passages`, `get_passage`. **Requires a local Gutenberg mirror.** Gutenberg blocks bots against `gutenberg.org`; the operator points `GUTENBERG_BASE_URL` at the mirror.

`happyfhantum/project-gutenberg-research-scraper` (Apify) is a hosted alternative for bulk search but inherits the same scraping-vs-policy concerns; document as opt-in.

## HTTP fallback

- Base URL: `https://gutendex.com/books`
- Endpoints: `/books?search=...`, `/books?ids=1,2,3`, `/books/{id}`
- Auth: none
- Rate limits: no documented hard limit. Be polite (≤1 req/s).
- Format URLs in `formats` point at `gutenberg.org`. Direct fetch of the format URLs is the path that bot-detection guards; consider mirroring or routing through `gutendex.com` results where possible.

## Query shapes

- *"Opening paragraph of On the Origin of Species"* → `/books?search=origin+of+species+darwin` → fetch the `text/plain` format URL.
- *"Public-domain works by Euclid in English"* → `/books?search=euclid&languages=en`
- *"Philosophy works between 1700 and 1800"* → `/books?topic=philosophy&author_year_start=1700&author_year_end=1800`

## Licensing

Project Gutenberg texts are **public domain in the United States**. Quote freely. **Strip the Gutenberg header and trailer** before quoting; the Gutenberg trademark and license boilerplate are not public domain. Reproduce attributions as a cite-and-link rather than a verbatim quote.

## Failure modes

- **Bot block on gutenberg.org direct fetch** — when fetching format URLs directly without the MCP mirror. Route through `gutendex.com` results and the mirror.
- **Encoding ambiguity** — some older texts have multiple encodings. Prefer `text/plain; charset=utf-8`.
- **Edition mismatch** — Gutenberg's edition may not match the printed edition the user asked about. Disambiguate via Open Library first when the query is edition-sensitive.
