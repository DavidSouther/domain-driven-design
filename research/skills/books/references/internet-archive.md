# Internet archive

Digitized scans of twentieth-century books, journals, technical manuals, government publications, and magazines, plus controlled-digital-lending borrows. Strong for older technical references, out-of-print monographs, and pre-internet documentation. OCR-backed full-text search.

## What it provides

- **Title+keyword search** over digitized holdings.
- **Per-item metadata** including `rights` (public domain, CC, "Available to the Library").
- **Open full text** for items whose rights permit redistribution.
- **Page-level search** via the beta full-text endpoint, returning page and bounding-box coordinates inside scanned books.

Example payload (`/metadata/{identifier}`):

```
{ "metadata": { "title": "IBM System/360 Operating System Concepts", "year": "1972",
                "creator": "International Business Machines Corporation", "rights": "Public Domain" },
  "files": [{ "name": "ibm-360-concepts_djvu.txt", "format": "DjVuTXT" }] }
```

## MCP option

None first-party. Use HTTP.

## HTTP fallback

- Base URL: `https://archive.org`
- Endpoints:
  - `/metadata/{identifier}`—full per-item metadata and file listing.
  - `/advancedsearch.php?q=...&output=json` — catalog search.
  - Beta full-text: `https://api.archivelab.org/books/{identifier}/search?q=...` — returns matching pages and bounding boxes.
- Auth: none for read access. S3-style auth keys exist for upload but are not needed for research.
- Rate limits: no published hard cap; back off on 429/503. Be polite (≤2 req/s).

## Query shapes

- *"1970&nbsp;s IBM System/360 manuals"* → `/advancedsearch.php?q=System/360+manual&fl[]=identifier,title,year&output=json`
- *"Full text of a public-domain nineteenth-century chemistry textbook"* → search → fetch the `_djvu.txt` file from the item's file listing.
- *"Page number where Knuth defines a knuth-bendix completion in a digitized 1970&nbsp;s monograph"* → beta full-text search.

## Licensing

Per-item; check the `rights` field. **Public Domain** and **CC-***: safe to quote. **Available to the Library** items require the user's own borrow under the controlled-digital-lending program; the user can read but cannot relay. Items without an explicit rights statement are uncertain; default to cite-and-link.

## Failure modes

- **Slow OCR**: scanned-text files (`_djvu.txt`) can be very large and OCR quality varies.
- **Missing full-text file**: some items are page-image-only. Use the beta full-text endpoint to search inside them.
- **CDL borrow required**: when `access-restricted-item: true`, access gates the body; the practice skill returns a typed Not-Available for the full-text-retrieval capability.
