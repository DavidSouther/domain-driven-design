# Hathitrust

Research-library digitized holdings. The Bibliographic API provides unrestricted access; the full-text Data API requires institutional OAuth. Use for academic library-catalog questions or confirming that a consortium copy exists.

## What it provides

- **Bibliographic API** (open)—volume info, rights tier, member-holding records.
- **Data API** (OAuth)—page images, per-page OCR, METS metadata; subject to copyright-tier restrictions.

## Mcp option

None first-party. Use HTTP.

## Http fallback

**Bibliographic API**:

- Base URL: `https://catalog.hathitrust.org/api/volumes/`
- Endpoints accept ISBN, LCCN, OCLC, or HathiTrust ID (HTID): `/brief/isbn/{isbn}.json`, `/full/oclc/{oclc}.json`, etc.
- Auth: none.

**Data API**:

- Base URL: `https://babel.hathitrust.org/cgi/htd/`
- Auth: OAuth 1.0a; requires institutional credentials issued by HathiTrust.
- Rate limits: gated per institutional access tier.

## Query shapes

- *"Is this 1934 sociology monograph held by a HathiTrust member library"* → Bibliographic API by ISBN or OCLC.
- *"Rights tier of this digitized text"* → Bibliographic API; check the `rightsCode` field.
- *"Page-level OCR for an in-copyright text"* — Data API; gated by OAuth and the rights tier; non-consumptive only.

## Licensing

- **Public-domain tier** — quotable.
- **In-copyright tier** — Data API access is **non-consumptive only**; results may inform research, but you cannot relay the full text to users as quoted prose.
- **Member-only** items require the user's institutional affiliation.

## Failure modes

- **Item not held** — HathiTrust restricts its catalog to member-library holdings. For broader coverage, fall back to Open Library + Internet Archive.
- **OAuth not configured** — Data API requests fail with 401. Bibliographic API remains usable.
- **Rights tier denies full text** — the practice skill returns a typed Not-Available for the open-full-text capability and continues with the bibliographic result.
