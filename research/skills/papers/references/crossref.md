# Crossref

The canonical DOI-metadata service. First stop for DOI→metadata, references-from-DOI, journal and publisher lookups.

## What it provides

- **DOI→metadata** — title, authors, year, venue, type, license, container ISSN/ISBN.
- **References-from-DOI** — the cited works of a paper, when the publisher deposits them.
- **Journal and publisher search**.

Example payload (`/works/{doi}`):

```
{ "message": { "DOI": "10.1145/3603287", "title": ["..."], "author": [...], "container-title": ["CACM"],
               "issued": { "date-parts": [[2024, 7]] }, "reference": [{ "DOI": "..." }], "license": [{ "URL": "..." }] } }
```

## MCP option

None canonical first-party. Use HTTP; the multi-source aggregators (`xingyulu23/Academix`, `openags/paper-search-mcp`, `benedict2310/Scientific-Papers-MCP`) include Crossref alongside other sources.

## HTTP fallback

- Base URL: `https://api.crossref.org`
- Endpoints: `/works/{doi}`, `/works?query=...&rows=...`, `/journals/{issn}`, `/members/{id}`
- Auth: none.
- **Polite pool: pass `mailto=you@example.org`** as a query parameter or `User-Agent` header. See [`etiquette.md`](etiquette.md).
- Rate limits: returned in `x-rate-limit-limit`/`x-rate-limit-interval` headers; 429 on overage. Revised downward on 1 December 2025.

## Query shapes

- *"Metadata for DOI 10.1145/3603287"* → `/works/10.1145/3603287`
- *"What does Eric Evans cite in the original DDD paper"* — Crossref reference list (when the publisher deposits references) → check the `reference` field.
- *"All papers in this journal"* → `/journals/{issn}/works?query=...`

## Licensing

Crossref metadata is **CC0**. Freely usable. The underlying full-text content lives at the publisher's domain and is licensed per the publisher (the `license` field carries the URL of the applicable license).

## Failure modes

- **Polite-pool not entered** — without `mailto=`, requests share an anonymous pool with stricter limits.
- **Missing references** — many publishers do not deposit reference lists; the `reference` field is absent or partial. Cross-check Semantic Scholar's citation graph.
- **DOI not found** — Crossref hosts ~150M DOIs but not every publisher participates. Fall back to DataCite for dataset DOIs, MEDLINE for older biomedical, or OpenAlex's broader index.
