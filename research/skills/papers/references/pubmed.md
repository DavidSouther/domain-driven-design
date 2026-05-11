# PubMed

Biomedical literature: 36M+ citations, abstracts, and PMC full text where open-access. The primary biomedical-search capability for `research:papers`.

## What it provides

- **Biomedical search** by keyword, MeSH term, author, or year.
- **Citation lookup** via PMID, PMCID, or DOI.
- **PMC full text** for open-access articles.
- **ID conversion** across PMID, PMCID, and DOI.

## MCP option (primary)

**`pubmed@life-sciences`** — Anthropic-curated marketplace plugin. Install:

```
/plugin marketplace add anthropics/life-sciences
/plugin install pubmed@life-sciences
```

No account required. Free. The wiring SKILL's checklist marks the *Biomedical search* capability available only after install completes.

## HTTP fallback

- Base URL: `https://eutils.ncbi.nlm.nih.gov`
- Endpoints: `/entrez/eutils/esearch.fcgi`, `/entrez/eutils/efetch.fcgi`, `/entrez/eutils/esummary.fcgi`, `/entrez/eutils/elink.fcgi`
- Auth: API key optional but recommended (raises rate from 3 RPS to 10 RPS). Pass `&api_key=...`.
- Rate limits: 3 RPS anonymous; 10 RPS with key. Use a `tool=` and `email=` parameter for polite-pool identification.

## Query shapes

- *"PubMed citations for `CRISPR` published 2024-2025"* → `?db=pubmed&term=CRISPR+AND+2024:2025[dp]` then `efetch` per PMID.
- *"PMC full text for an open-access biomedical article"* → resolve PMID → PMCID → `efetch` on PMC.
- *"Convert DOI to PMID"* → `/entrez/eutils/esearch.fcgi?db=pubmed&term=10.1038/...[doi]`

## Licensing

- PubMed records (metadata) are **public domain**.
- PMC full text is per-article: many are CC-BY or CC-BY-NC; some are publisher-released to PMC under a non-redistribution license. Check the per-article license string.

## Failure modes

- **Plugin not installed** — the *Biomedical search* capability returns Not-Available. The HTTP fallback remains usable if the user prefers raw E-utilities.
- **Rate-limit (429)** — at 3 RPS anonymous, easy to exceed under fan-out. Add the API key or back off.
- **PMID without PMCID** — many articles are abstract-only in PubMed; PMC full text is unavailable. The practice skill returns the abstract and a typed Not-Available for the full-text capability.
