# Alexandria (aggregator)

Broad keyless aggregation across 46 public-domain digital libraries (Project Gutenberg, Oxford ORA, Cambridge Apollo, Wikisource, Library of Congress, HathiTrust public-domain tier, Smithsonian, NASA ADS, CourtListener). Use for cross-corpus queries when the user does not know which library holds a text or wants the broadest sweep.

## What it provides

- **Aggregated public-domain search** across 61 sources total: 46 keyless, 15 free-key.
- Source-level routing — Alexandria exposes which underlying source returned each hit.

Alexandria is positioned as a **supplement** to the per-source capabilities, not a replacement. For targeted source-specific queries (ISBN lookup, edition resolution, public-domain full-text retrieval), the per-source capabilities remain primary.

## MCP option

`suavecito585/alexandria-mcp`. Install per the repo README. Free keys for 15 of the 61 sources (CORE, Semantic Scholar, NASA ADS, Smithsonian, Springer Nature, Google Books, CourtListener); the other 46 run keyless.

**Does not include** O'Reilly, Wiley journals, or Oxford/Cambridge commercial presses. The per-source skills in this stack cover those separately.

## HTTP fallback

None. Alexandria is the aggregator; the per-source HTTP endpoints are reachable directly through their own reference files.

## Query shapes

- *"Digitized 18th-century treatises on celestial mechanics across institutional repositories"* — cross-corpus query.
- *"Where might I find a digitized copy of this 1810 botanical monograph"* — when the source is unknown.
- *"Sweep all public-domain digital libraries for any mention of <topic>"* — broad cross-corpus.

For ISBN lookup, edition disambiguation, or technical-book search, route to the targeted per-source capability instead; Alexandria's aggregated results are noisier than a focused per-source query.

## Licensing

Per-source. Alexandria does not re-license; the originating source's terms apply. Most of the 46 keyless sources are public domain or CC; the 15 keyed sources vary (CORE is OA, Springer Nature is metadata-only without subscription, etc.).

## Failure modes

- **Source-level outage** — one underlying source failing degrades aggregated coverage. Alexandria reports which sources returned hits.
- **Duplicate hits across sources** — the same public-domain work may appear from multiple libraries. Dedupe by canonical identifier (ISBN, OL work id, Gutenberg id).
- **Quality variance** — aggregated search hides source-specific etiquette and licensing; for high-stakes queries, route to the per-source capability after Alexandria narrows the candidate.
