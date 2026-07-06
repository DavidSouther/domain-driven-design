# Core

200M+ open-access full-text aggregation. Strong for full-text retrieval when the publisher gates the version and Unpaywall reports a repository copy held in CORE.

## What it provides

- **Full-text search** across the open-access aggregation.
- **Per-paper metadata** with full-text URL and license.
- **Repository-level metadata** — which institutional or subject repository deposited the article.

## MCP option

None first-party. The Alexandria aggregator's keyed set includes CORE for cross-corpus aggregation, but the per-source HTTP path is more controllable.

## HTTP fallback

- Base URL: `https://api.core.ac.uk/v3`
- Endpoints: `/search/outputs?q=...`, `/outputs/{id}`, `/search/works?q=...`
- Auth: **API key required (free)**. Sent as `Authorization: Bearer <CORE_API_KEY>`. Obtain at `core.ac.uk/services/api`.
- Rate limits: **1 req/10 s for batch, 5 req/10 s for single queries**; higher tiers for member institutions.

## Query shapes

- *"Open-access full text for a known DOI"* → `/search/outputs?q=doi:10.1145/3603287`
- *"Full-text search for a phrase across the OA aggregation"* → `/search/outputs?q="domain-driven design"`
- *"Repository-level metadata for an institution's deposits"* → `/search/works?q=publisher:"University of X"`

## Licensing

Per-article. CORE reports the license string for each record; aggregates only legitimately open-access content. Quote per the article's license, cite with the canonical DOI.

## Failure modes

- **Missing API key** — 401. Set `CORE_API_KEY`.
- **Rate-limit (429)** — particularly low at 1 req/10 s for batch. Use the higher single-query rate when feasible.
- **License mismatch** — occasional records report ambiguous licenses; cross-check with Unpaywall before quoting.
