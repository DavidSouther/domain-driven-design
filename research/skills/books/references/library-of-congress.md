# Library of congress

A searchable collection of rare books, manuscripts, government documents, and historical newspapers.
Use it for primary sources and Americana.

## What it provides

- **Catalog search** across digitized holdings.
- **Item metadata**: title, creator, year, format, digitization status.
- **Format-aware retrieval**: many items expose direct links to scanned PDFs, JPEGs, or transcripts.

The catalog scope is the **digitized subset** of LoC's holdings, not the full card catalog.
Non-digitized items appear in the LoC online catalog at `catalog.loc.gov` but not in the JSON API.

## Mcp option

None first-party.
Use HTTP.

## Http fallback

- Base URL: `https://www.loc.gov`
- Endpoint pattern: `/{endpoint}/?fo=json&q=...`
- Example endpoints: `/books/?fo=json`, `/manuscripts/?fo=json`, `/photos/?fo=json`, `/chronicling-america/?fo=json`.
- Auth: none.
  No documented hard rate limit; be polite (≤2 req/s).

## Query shapes

- *"Digitized copy of the Federalist Papers from LoC"* → `/books/?fo=json&q=Federalist+Papers`
- *"Manuscripts of Frederick Douglass"* → `/manuscripts/?fo=json&q=Frederick+Douglass`
- *"Chicago newspaper coverage of the 1893 World's Fair"* → `/chronicling-america/?fo=json&q=World+Columbian+Exposition&dates=1893`

## Licensing

- United States Government works are typically in the **public domain**.
  Most LoC-created records and digitizations are public-domain or `usgov` rights.
- Donated and acquired collections retain their original copyright; the per-item `rights` field carries the exact statement.
- Chronicling America newspapers are public domain in the United States.

## Failure modes

- **Item not digitized**: appears in `catalog.loc.gov` but not in the JSON API.
  The practice skill returns the catalog reference and a typed Not-Available for the full-text-retrieval capability.
- **Sparse metadata for older items**: some digitizations lack structured metadata.
  Fall back to the item's HTML page for the human-readable description.
- **Format diversity**: items may offer PDF, JPEG, MP3, or only a transcript depending on type.
  The `original_format` field in the JSON response routes the practice skill to the right artifact.
