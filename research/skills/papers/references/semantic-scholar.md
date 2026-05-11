# Semantic Scholar

Allen Institute for AI's academic graph. Strong for citation-graph queries, ML/AI coverage, and DOI/arXiv/PMID lookup with consistent shape across identifiers.

## What it provides

- **Topic search** with quality ranking biased to CS, ML, and AI.
- **DOI / arXiv / PMID lookup** in a single shape.
- **Citation graph** — `/paper/{id}/citations` and `/paper/{id}/references`.
- **Author endpoints** and **recommendations**.

Example payload (`/graph/v1/paper/{id}`):

```
{ "paperId": "...", "title": "...", "authors": [...], "venue": "...",
  "citationCount": 1234, "abstract": "..." }
```

## MCP option

`FujishigeTemma/semantic-scholar-mcp` — wraps the Graph API. `afrise/academic-search-mcp-server` combines Semantic Scholar with Crossref.

## HTTP fallback

- Base URL: `https://api.semanticscholar.org/graph/v1`
- Endpoints: `/paper/search?query=...`, `/paper/{id}`, `/paper/{id}/citations`, `/paper/{id}/references`, `/author/{id}`
- Auth: API key strongly preferred. Request via the Semantic Scholar developer portal. Pass as header `x-api-key: ...`. Set `SEMANTIC_SCHOLAR_API_KEY`.
- Rate limits:
  - **With key**: 1 RPS dedicated.
  - **Anonymous**: global shared pool of 5,000 requests per 5 minutes; **mandatory exponential backoff on 429s**. See [`etiquette.md`](etiquette.md).

## Query shapes

- *"What cites this paper"* → `/paper/{id}/citations?fields=title,authors,year,venue`
- *"Top 10 ML papers about transformers, sorted by citationCount"* → `/paper/search?query=transformer&limit=10` with client-side sort.
- *"Get this paper by DOI"* → `/paper/DOI:10.1145/3603287`
- *"Get this paper by arXiv id"* → `/paper/arXiv:2401.01234`

## Licensing

Metadata, abstracts, and citation-graph edges are freely usable. Full PDFs are linked through Semantic Scholar but hosted at their original repositories; quote per the original license.

## Failure modes

- **429 without backoff** — anonymous pool exhausted. Apply exponential backoff or set the API key.
- **Identifier prefix missing** — endpoints disambiguate via prefix (`DOI:`, `arXiv:`, `PMID:`). Forgetting the prefix matches no record.
- **Citation graph truncation** — `/citations` is paginated; iterate via `offset`. Highly-cited papers (10k+ citations) require many requests.
