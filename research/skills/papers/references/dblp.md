# Dblp

Authoritative CS publication index.
Reliable for author disambiguation and exact-match publication searches.

## What it provides

- **CS publication search** by keyword, author, venue.
- **Author disambiguation:** DBLP's strong invariant.
  The per-author token gives exact-match publication lists.
- **Venue listings:** conference proceedings, journal volumes.

## Mcp option

None first-party.
The multi-source aggregators (`xingyulu23/Academix`, `tfscharff/doi-mcp` fan-out) include DBLP among their sources.

## Http fallback

- Base URL: `https://dblp.org/search`
- Endpoints: `/publ/api?q=...&format=json`, `/author/api?q=...&format=json`, `/venue/api?q=...&format=json`
- Auth: none.
- Output: XML or JSON (pass `format=json`).
- Data is **CC0**.

## Query shapes

- *"All publications by `Eric Evans` in software-engineering venues".*
  Use author search to resolve to the canonical DBLP author key, then get the publication list.
- *"Programming Language Design and Implementation 2024 papers".*
  Venue search for `PLDI/2024`.
- *"Software engineering papers on bounded contexts"* → `/publ/api?q=bounded+contexts&format=json`

## Licensing

Dblp data is **CC0** for metadata.
The underlying full text lives at the publisher's domain under the publisher's license.
Cite with the Dblp key or the canonical publisher DOI.

## Failure modes

- **Author ambiguity:** common names resolve to multiple author records.
  DBLP exposes a disambiguation page; prefer the canonical `pid` over the human name.
- **Coverage gap outside CS.**
  DBLP is CS-only.
  For broader topic search, route to OpenAlex or Semantic Scholar.
- **Rate-limit (429).**
  No specific limit published; back off on 429.
