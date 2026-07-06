# Zotero (books)

The user's reference manager. Strong for books the user has cited, annotated, or tagged for a research project.

## What it provides

- **Zotero library lookup** for items the user has saved.
- ID-based lookup by ISBN.
- Tag, collection, and full-text-note filtering.

For papers items (`journalArticle`, `preprint`, `conferencePaper`), see [`../../papers/references/zotero.md`](../../papers/references/zotero.md). This copy focuses on book items (`book`, `bookSection`).

## Mcp option

`54yyyu/zotero-mcp` adds semantic search. `cookjohn/zotero-mcp` provides ID-based lookup by DOI, ISBN, arXiv, PMID, title, author, year, and tag filters. `kujenga/zotero-mcp` is a third option.

Install per the chosen repo's README. Auth: `ZOTERO_API_KEY` (generated at `zotero.org/settings/keys`) and `ZOTERO_LIBRARY_ID`, the numeric ID found at the same page.

## Http fallback

- Base URL: `https://api.zotero.org`
- Endpoints: `/users/{libraryId}/items?q=...&itemType=book||bookSection`, `/users/{libraryId}/items/{itemKey}`
- Auth: `Zotero-API-Key` header.
- Rate limits: published as 50 GB/month bandwidth; back off on 429.

## Query shapes

- *"Books tagged `domain-modeling` in Zotero"* → `?tag=domain-modeling&itemType=book`
- *"Find a saved copy of Domain-Driven Design by ISBN"* → `?q=9780321125217&itemType=book`
- *"Annotated copies of Refactoring"* → `?q=Refactoring&itemType=book` then check the item's notes.

## Licensing

Personal library metadata is the user's own. Quotation rights depend on the original work the user has cataloged. The Zotero notes and tags are the user's, freely usable in the user's own session.

## Failure modes

- **Invalid API key** — rotate at `zotero.org/settings/keys` and re-run [`../../configuring-books/SKILL.md`](../../configuring-books/SKILL.md).
- **Library ID mismatch** — for group libraries, swap `/users/{id}` for `/groups/{id}`.
- **Missing item type filter** — without `itemType=book||bookSection`, results may include papers and web pages.
