# OpenAlex

OurResearch's open scholarly graph. Broadest coverage at ~240M works, with citation graph, institutions, authors, concepts, and sources.

## What it provides

- **Topic search** across the broadest open index.
- **DOI / PMID / OpenAlex-ID lookup**.
- **Citation graph** — `referenced_works`, `cited_by_count`, `cited_by_api_url`.
- **Institutions, authors, concepts, sources** as first-class entities.

Example payload (`/works/{doi}`):

```
{ "id": "https://openalex.org/W...", "doi": "...", "title": "...", "authorships": [...],
  "host_venue": { "display_name": "...", "issn_l": "..." }, "concepts": [...], "cited_by_count": 1234,
  "referenced_works": [...], "open_access": { "is_oa": true, "oa_status": "gold" } }
```

## MCP options

`oksure/openalex-research-mcp`, `drAbreu/alex-mcp`, `hbiaou/openalex-mcp`. The aggregators (`xingyulu23/Academix`, `openags/paper-search-mcp`) include OpenAlex in their fan-out.

## HTTP fallback

- Base URL: `https://api.openalex.org`
- Endpoints: `/works`, `/works/{id-or-doi}`, `/authors`, `/concepts`, `/institutions`, `/sources`
- Auth: **API key required as of 13 February 2026** (free, 30-second signup). Pass via `api_key` query parameter or `Authorization: Bearer ...` header. Set `OPENALEX_API_KEY`.
- Pricing: $1/day free credit; per-call thereafter ($0 singletons, $0.0001/list, $0.001/search, $0.01/semantic-search or content download).
- The historic `mailto=` polite-pool convention still works for politeness signaling but no longer governs access.

## Query shapes

- *"Papers about domain-driven design, sorted by citation count"* → `/works?search=domain-driven+design&sort=cited_by_count:desc&api_key=...`
- *"This paper's references"* → `/works/{id}?select=referenced_works&api_key=...`
- *"All works by an author"* → `/authors/{author-id}/works?api_key=...`
- *"Open-access works only"* → `/works?search=...&filter=is_oa:true&api_key=...`

## Licensing

OpenAlex metadata is **CC0**. Full text is linked through OpenAlex but hosted at the original repository; quote per the original license. Concept and institution data are freely usable.

## Failure modes

- **401 / missing key** — set `OPENALEX_API_KEY`.
- **Daily credit exhausted** — the practice skill returns a typed Not-Available for the *Topic search* capability via OpenAlex; degrade to Semantic Scholar or Crossref.
- **Result paginated** — OpenAlex uses cursor-based pagination beyond 10k results; pass `cursor=*` to start.
