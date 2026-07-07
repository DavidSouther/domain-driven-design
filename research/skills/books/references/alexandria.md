# Alexandria (aggregator)

Search across 46 public-domain digital libraries. These include Project Gutenberg, Wikisource, the Library of Congress, and HathiTrust. Use it when you're not sure which library has your text.

## What it provides

- **Public-domain search across 61 sources**: 46 keyless, 15 free-key.
- Source-level routing. You can see which source returned each result.

Alexandria adds to the per-source tools, not replace them. For focused searches—like ISBN lookup or finding specific editions—use the per-source tools instead.

## MCP option

`suavecito585/alexandria-mcp`. Install per the repo README. Free keys for 15 of the 61 sources. These include CORE, Semantic Scholar, NASA ADS, Smithsonian, Springer Nature, Google Books, and CourtListener. The other 46 run keyless.

**Does not include** O'Reilly, Wiley journals, or Oxford/Cambridge commercial presses. The per-source skills in this stack cover those separately.

## HTTP fallback

None. Alexandria is the aggregator; the per-source HTTP endpoints are reachable directly through their own reference files.

## Query shapes

- *"Digitized eighteenth-century treatises on celestial mechanics across institutional repositories"*: cross-corpus query.
- *"Where might one find a digitized copy of this 1810 botanical monograph"*: when the source is unknown.
- *"Sweep all public-domain digital libraries for any mention of <topic>"*: broad cross-corpus.

For ISBN lookups, finding specific editions, or technical book searches, use the per-source tools instead. Alexandria's results mix more sources and may be noisier.

## Licensing

Per-source. Alexandria does not re-license; the source's terms apply. Most of the 46 keyless sources are public domain or CC. The 15 keyed sources vary: CORE is open access, Springer is metadata only without a subscription, and so on.

## Failure modes

- **Source-level outage**: if one source goes down, coverage drops. Alexandria tells you which sources returned results.
- **Duplicate hits across sources**: the same public-domain work may show up from multiple sources. Remove duplicates by matching ISBN, OL work id, or Gutenberg id.
- **Quality variance**: combining many sources can hide differences in how they work and their rules. For important searches, use the per-source tools after Alexandria narrows the options.
