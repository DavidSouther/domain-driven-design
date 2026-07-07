# Google books

Broadest commercial-publisher coverage, including tables of contents, publisher metadata, and preview snippets for recent commercial nonfiction and modern textbooks. Strong for "what does the TOC look like" and modern-edition disambiguation.

## What it provides

- **ISBN, title, author search** with publisher and date metadata.
- **Table-of-contents**: exposed in `volumeInfo.tableOfContents` when the publisher provides it.
- **Preview snippets**: short excerpts where the publisher has authorized preview.

Example payload (`/volumes?q=isbn:9780321125217`):

```
{ "items": [{ "volumeInfo": { "title": "Domain-Driven Design", "subtitle": "Tackling Complexity in the Heart of Software",
              "authors": ["Eric Evans"], "publisher": "Addison-Wesley", "publishedDate": "2003-08-30",
              "industryIdentifiers": [{ "type": "ISBN_13", "identifier": "9780321125217" }],
              "tableOfContents": "Part I: Putting the Domain Model to Work..." } }] }
```

## MCP option

None first-party. A Medium walkthrough demonstrates a hand-rolled Express proxy but it is not packaged for redistribution; do not depend on it.

## HTTP fallback

- Base URL: `https://www.googleapis.com/books/v1/volumes`
- Auth: API key. Obtain from Google Cloud Platform Console; set `GOOGLE_BOOKS_API_KEY` and pass as `?key=...`.
- Rate limits: 1,000 req/day with a key; 1 req/s per user ceiling. Anonymous calls work but are aggressively throttled.
- `maxResults` caps at 40.

## Query shapes

- *"Chapters in the twentieth-anniversary edition of The Pragmatic Programmer"* → `?q=isbn:9780135957059&key=...` → read `volumeInfo.tableOfContents`.
- *"Recent commercial books about systems thinking"* → `?q=intitle:systems+thinking&orderBy=newest&key=...`
- *"Publisher of the first-edition Spanish translation of Cathedral and Bazaar"* → `?q=intitle:"Catedral+y+Bazar"&key=...`

## Licensing

Google licenses snippets and preview text for display, not redistribution. Quote at most very short fragments and **cite-and-link** rather than transcribe entire previews. Bibliographic metadata is freely usable. Cover thumbnails are linkable but should not be hot-linked at scale; Google Books TOS asks for the Books-API attribution when reproducing.

## Failure modes

- **403 / `dailyLimitExceeded`**: key has hit the 1,000/day quota. Rotate to a different project or back off until reset.
- **Missing tableOfContents**: publisher did not provide one. The practice skill returns a typed Not-Available for the table-of-contents-fetch capability.
- **Sparse metadata for older books**: Google Books favors recent commercial publishing. For older or out-of-print titles, prefer Open Library or HathiTrust.
