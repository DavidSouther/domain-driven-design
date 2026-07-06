# Zotero (papers)

The user's reference manager scoped to academic papers, preprints, and conference proceedings.

## What it provides

- **Zotero library lookup** for item types `journalArticle`, `preprint`, `conferencePaper`.
- ID-based lookup by **DOI, PMID, PMCID, arXiv ID**.
- Tag, collection, and full-text-note filtering.

For book items (`book`, `bookSection`), see [`../../books/references/zotero.md`](../../books/references/zotero.md). This file focuses on paper item types and identifier types. Duplication is intentional per design §Reference file layout, as citation linkage differs (DOI, PMID, PMCID rather than ISBN).

## MCP Option

`54yyyu/zotero-mcp` adds semantic search. Choose `kujenga/zotero-mcp` or `cookjohn/zotero-mcp` for ID-based lookup by DOI, ISBN, arXiv, PMID, title, author, year, or tag filters.

Install per the chosen repo's README. Auth: `ZOTERO_API_KEY` and `ZOTERO_LIBRARY_ID`.

## HTTP Fallback

- Base URL: `https://api.zotero.org`
- Endpoints: `/users/{libraryId}/items?q=...&itemType=journalArticle||preprint||conferencePaper`, `/users/{libraryId}/items/{itemKey}`
- Auth: `Zotero-API-Key` header.
- Rate limits: 50 GB/month bandwidth per key; back off on 429.

## Query shapes

- *"Papers with annotations in Zotero"* → `?q=&itemType=journalArticle||preprint&include=notes`
- *"This paper by DOI"* → `?q=10.1145/3603287&itemType=journalArticle`
- *"Preprints in the `formal-methods` collection"* → `/collections/{collectionKey}/items?itemType=preprint`

## Licensing

User-curated library metadata is the user's own. Quotation rights depend on the underlying paper. Notes and tags are freely usable within the user's session.

## Failure modes

- **Invalid API key** — rotate at `zotero.org/settings/keys` and re-run [`../../configuring-papers/SKILL.md`](../../configuring-papers/SKILL.md).
- **Group library mismatch** — use `/groups/{id}` instead of `/users/{id}` for group libraries.
- **Item type omitted** — without an `itemType=` filter, results include books, web pages, and reports; restrict to paper types for predictable behavior.
