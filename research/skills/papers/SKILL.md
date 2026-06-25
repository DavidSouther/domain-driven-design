---
name: papers
description: Use when a research question targets an academic paper, preprint, or citation — DOI lookup, DOI→OA-PDF retrieval, topic search across OpenAlex / Semantic Scholar / DBLP, citation graphs, ArXiv preprints, PubMed biomedical literature, or Wiley journal content. Applies every time a research question targets academic papers, preprints, or citations.
---

# Papers

## Overview

Per-query research against the configured papers capability contract. Pick the **capability** the question needs (DOI metadata, OA-PDF retrieval, topic search, citation graph, preprint search, biomedical search, citation-context classification), dispatch to it, write the result with IEEE citations. The transport (MCP or HTTP) is the wiring's concern, not this skill's. Setup, key rotation, marketplace-plugin installs, and SSO handshakes belong in [the papers setup reference](../using-research/references/configuring/papers.md); this skill consumes the contract that skill publishes.

## When to use / When NOT to use

**Use** for:

- Academic literature: DOI lookup, OA-PDF retrieval, abstract retrieval, topic search.
- Citation graphs: what cites this paper, what does this paper cite.
- Preprint search and ArXiv-specific queries.
- Biomedical literature via PubMed when access is configured.
- Wiley journal content via Scholar Gateway when access is configured (snippet plus DOI).
- Citation-context classification (supporting / disputing / mentioning) via Scite when subscribed.
- The user's saved papers in Zotero when access is configured.

**When NOT to use:**

- To configure papers sources, install an MCP, complete SSO, install a marketplace plugin, or rotate a key. Those belong in [the papers setup reference](../using-research/references/configuring/papers.md).
- For language reference, library documentation, RFCs, or public web search — use `research:public`.
- For internal documents (Slack, Confluence, Linear, Notion) — use `research:internal`.
- For domain-model questions (entities, bounded contexts, ubiquitous language) — use `research:domain`.
- For citable book content (ISBN, table of contents, public-domain full text) — use `research:books`.

## Query expansion (Jeopardy! search)

Before dispatching to a capability, expand the question into 3-5 variants (see [`research/references/jeopardy.md`](../../references/jeopardy.md) for the general technique). Papers-specific axes:

- **DOI-vs-title** — when a DOI is in hand, prefer DOI-keyed capabilities; when only the title is known, run title-and-author queries against the topic-search capability.
- **Author-name normalization** — first-author-last-name forms, ORCID id when known, common transliteration variants for non-English author names.
- **Venue and year** — preprint year (ArXiv) vs. published year (Crossref); conference name (`PLDI 2024`) vs. journal name.
- **Identifier variants** — DOI, PMID, PMCID, arXiv id; the same paper often has multiple identifiers and the *DOI fan-out* capability resolves disagreement.
- **Topic-and-keyword variants** — narrow (specific technique with technology), broad (the field name), synonyms (`backpropagation` / `gradient descent` / `optimizer`).

Run the variants in the order that the routing table below dictates. Union the result sets before deciding which capability has the highest-quality hit.

## Capability routing

Capabilities are named in the contract published by [the papers setup reference](../using-research/references/configuring/papers.md). The routing table maps question type to the capability that answers it.

| Question intent | Primary capability | Reference |
|---|---|---|
| "Metadata for this DOI" | DOI→metadata | [`references/crossref.md`](references/crossref.md) |
| "DOI is suspect or might be hallucinated" | DOI fan-out | [`references/doi.md`](references/doi.md) |
| "Is there a free PDF for this DOI" | DOI→OA-PDF | [`references/unpaywall.md`](references/unpaywall.md) |
| "Topic search across the broadest open corpus" | Topic search via OpenAlex | [`references/openalex.md`](references/openalex.md) |
| "Topic search biased to CS / ML quality" | Topic search via Semantic Scholar | [`references/semantic-scholar.md`](references/semantic-scholar.md) |
| "Topic search authoritative for CS" | DBLP venue/author/keyword | [`references/dblp.md`](references/dblp.md) |
| "What cites this paper" | Citation graph | [`references/semantic-scholar.md`](references/semantic-scholar.md) |
| "Preprint or pre-publication version" | Preprint search | [`references/arxiv.md`](references/arxiv.md) |
| Biomedical query | Biomedical search via PubMed | [`references/pubmed.md`](references/pubmed.md) |
| Wiley journal article | Wiley journal search | [`references/wiley-scholar-gateway.md`](references/wiley-scholar-gateway.md) |
| "What supports or contradicts this claim" | Citation-context classification | [`references/scite.md`](references/scite.md) |
| Open-access full text when publisher version gated | Full-text via CORE | [`references/core.md`](references/core.md) |
| Biomedical full text broader than PubMed | Europe PMC | [`references/europe-pmc.md`](references/europe-pmc.md) |
| Papers I have saved in Zotero | Zotero library lookup | [`references/zotero.md`](references/zotero.md) |

### Routing heuristic

The routing table is the lookup. The heuristic below is what to apply when the question does not name a source:

- **DOI in hand** → DOI fan-out via `doi-mcp` first, then Crossref + Unpaywall in parallel.
- **Topic search without DOI** → OpenAlex (breadth) + Semantic Scholar (CS/ML quality), and DBLP if the topic is unambiguously CS.
- **Preprint-only / not-yet-published** → ArXiv directly.
- **"What cites this paper"** → Semantic Scholar citation graph. If subscribed, Scite Smart Citations classifies the supporting / disputing / mentioning posture.
- **Biomedical** → `pubmed@life-sciences` when the plugin is installed; Europe PMC for full-text coverage beyond PubMed.
- **Publisher-specific** → Wiley Scholar Gateway when SSO is configured.

For conditional capabilities that the contract marks Not-Available (plugin not installed, SSO not completed, subscription lapsed), accept the typed Not-Available result as a routing signal and continue with the next capability in the heuristic. The free stack (OpenAlex + Semantic Scholar + Crossref + Unpaywall + ArXiv) covers the majority of queries without any conditional source.

## Output format

Write findings to `docs/research/YYYY-MM-DD-A-<topic>/papers.md`. Cite per the loose IEEE style in [`research/references/citations.md`](../../references/citations.md). One consolidated `papers.md` per session topic (per Decision 6: no per-source split, no cache).

```
# Papers: <question>

## Findings
<narrative: synthesized answer with inline citations [N]>

## Sources
[1] Author/Org. "Title." Date. [Online]. Available: <URL>
[2] Author/Org. "Title." Date. [Online]. Available: <URL>
```

Excerpts only; do not stage cached PDFs or full bodies. For passages from licensed sources (Wiley, Scite, Zotero of copyrighted papers), quote within the session for the user's own work and cite-and-link with the DOI; do not stage to public artifacts.

## Common mistakes

- **Skipping query expansion.** A single phrasing often misses the canonical identifier or the venue the user actually meant. Always expand first.
- **Mixing capabilities.** Asking for OA-PDF when the question is about citation graph; asking ArXiv for a published-only paper that never had a preprint. The routing table is the lookup.
- **Quoting from non-quotable sources.** Wiley snippets are display-only; Scite Smart Citations are proprietary; gated journal full text is non-redistributable. Cite-and-link with the DOI.
- **Ignoring typed Not-Available.** A conditional capability returning Not-Available (no PubMed plugin, no Wiley SSO, no Scite subscription) is a routing signal, not a failure. Continue with the next capability in the heuristic.
- **Re-teaching the wiring.** A "first, make sure you have installed the PubMed plugin" preface is wiring leakage. The wiring SKILL owns setup; this skill consumes the contract. If a preface is unavoidable, the contract is incomplete — widen it in [the papers setup reference](../using-research/references/configuring/papers.md).
- **Hallucinated DOIs.** Plausible-looking DOIs that no source recognizes are common in AI-mediated work. Use the *DOI fan-out* capability when a DOI looks suspect; if no source returns a record, return Not-Available rather than fabricating a citation.
- **Treating OpenAlex's metering as a hard block.** OpenAlex's $1/day free credit covers most individual research sessions. Above the credit, degrade to Semantic Scholar + Crossref for the topic search; do not silently skip the query.

## Composes With

- **the papers setup reference** (`research:using-research`, `references/configuring/papers.md`) — the wiring partner. Publishes the contract this skill consumes.
- **`research:books`** — sibling practice skill for citable books.
- **`research/references/jeopardy.md`** — query expansion technique.
- **`research/references/citations.md`** — IEEE citation format.
