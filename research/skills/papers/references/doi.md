# DOI fan-out

Parallel DOI resolution across 9+ sources. Use when a DOI must resolve to authoritative metadata and the source is unknown, or when one source's outage should not stall the lookup.

## What it provides

- **DOI→metadata** fan-out across CrossRef, OpenAlex, PubMed, zbMATH, ERIC, HAL, INSPIRE-HEP, Semantic Scholar, and DBLP in parallel.
- Result reconciliation — chooses the most complete record across the fan-out, exposes the per-source results when they disagree.
- Hallucinated-DOI guard — if no source returns a record, the practice skill returns a typed Not-Available rather than a fabricated citation.

## MCP option

`tfscharff/doi-mcp` is the canonical fan-out server. Install per the repo README; no auth required at the server level (the underlying sources have their own etiquette; the server applies polite-pool conventions).

## HTTP fallback

None as a single endpoint — DOI fan-out is the capability the MCP server implements on top of the per-source HTTP APIs documented in [`crossref.md`](crossref.md), [`openalex.md`](openalex.md), [`semantic-scholar.md`](semantic-scholar.md), [`pubmed.md`](pubmed.md), [`dblp.md`](dblp.md), [`europe-pmc.md`](europe-pmc.md). If the MCP is absent, the practice skill issues the fan-out itself in parallel against those endpoints.

## Query shapes

- *"Resolve DOI 10.1145/3603287 to authoritative metadata"* — the canonical fan-out query.
- *"Does this DOI exist at all"* — if no source returns a record, the DOI is suspect; return Not-Available.
- *"Where is this paper indexed"* — the per-source results expose which indexes carry the record.

## Licensing

The MCP returns metadata only; the upstream sources govern redistribution. Crossref metadata is CC0; OpenAlex is CC0; Semantic Scholar metadata is freely usable; PubMed records are public domain; zbMATH, ERIC, HAL, INSPIRE-HEP, DBLP are per-source CC0 or equivalent for metadata.

## Failure modes

- **One source slow** — the fan-out returns when a quorum of sources have responded; slow sources are dropped from the result.
- **All sources report no record** — the DOI is suspect or newly minted; return Not-Available.
- **Disagreement on year or title** — surface both records; do not silently choose. The practice skill cites the source with the most complete record and notes the disagreement.
