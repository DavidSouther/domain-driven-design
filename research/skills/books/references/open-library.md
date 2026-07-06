# Open library

Bibliographic anchor for any printed book. First stop for ISBN resolution, edition disambiguation, and author normalization.

## What it provides

- **ISBN→edition lookup** — returns `{ isbn13, authors, publisher, year, work_id }`.
- **Title+author search** — ranked editions with work-ID linkage.
- **Author lookup** — works, biographical metadata, alternate names.
- **Covers** — cover image URLs at S/M/L sizes (CC-BY-SA).

Example payload (edition `/books/{olid}.json`):

```
{ "isbn_13": ["9780321125217"], "authors": [{ "key": "/authors/OL392753A" }],
  "publishers": ["Addison-Wesley"], "publish_date": "2003", "works": [{ "key": "/works/OL15852072W" }] }
```

## MCP option

`8enSmith/mcp-open-library` — TypeScript, stdio, unauthenticated. Tools: `get_book_by_title`, `get_authors_by_name`, `get_author_info`, `get_book_cover`, `get_book_by_id`. Install: `npx -y @8enSmith/mcp-open-library`. Env: none required, but the server respects `OPENLIBRARY_USER_AGENT` if set.

## HTTP fallback

- Base URL: `https://openlibrary.org`
- Endpoints: `/search.json?q=...`, `/isbn/{isbn}.json` (redirects to edition), `/works/{olid}.json`, `/authors/{olid}.json`
- Auth: none
- Headers: send `User-Agent` containing an app name and a contact email. See [`etiquette.md`](etiquette.md).
- Rate limits: 1 req/s anonymous; 3 req/s when the User-Agent carries a contact email.

## Query shapes

- *"Canonical ISBN-13 for Domain-Driven Design hardcover, Addison-Wesley, 2003"* → `/search.json?q=title:"Domain-Driven Design"+author:"Eric Evans"&fields=isbn,publisher,publish_date,key`
- *"All editions of On the Origin of Species"* → `/works/OL2627321W.json` then `/works/OL2627321W/editions.json`
- *"Who wrote The Soul of a New Machine"* → `/search.json?q=title:"The Soul of a New Machine"&fields=author_name`

## Licensing

Bibliographic data is **CC0**; freely quotable and redistributable. Cover images are CC-BY-SA; attribute Open Library when reproducing. Open Library does not serve full book text; for that, follow the work-ID to Internet Archive or Gutendex.

## Failure modes

- **HTTP 429** — exceeded rate limit. Back off; ensure the User-Agent carries the contact email to qualify for the higher anonymous tier.
- **Missing edition** — older or obscure books may have a work record but no edition. Cross-check Google Books for ISBN-13.
- **Stale data** — Open Library is community-edited. Treat publisher/year for self-published or print-on-demand titles with skepticism.
