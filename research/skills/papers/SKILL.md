---
name: papers
description: "Use for research on academic papers, preprints, and citations. Find papers by DOI or topic. Track citations. Access biomedical papers and Wiley journals."
---

# Papers

## Overview

Conduct per-query research against your configured papers capability contract. Identify which capability answers the question. Capabilities include DOI metadata, OA-PDF retrieval, topic search, citation graph, preprint search, biomedical search, and citation-context classification. Dispatch to it and write results with IEEE citations. The transport layer (MCP or HTTP) is the wiring's responsibility. For setup, key rotation, marketplace-plugin installs, and SSO configuration, see [the papers setup reference](../using-research/references/configuring/papers.md).

## When to use / when not to use

**Use** for:

- Academic literature: DOI lookup, OA-PDF retrieval, abstract retrieval, topic search.
- Citation graphs: what cites this paper, what does this paper cite.
- Preprint search and ArXiv-specific queries.
- Biomedical literature via PubMed when you configure access.
- Wiley journal content via Scholar Gateway when you configure access (snippet plus DOI).
- Citation-context classification (supporting / disputing / mentioning) via Scite when subscribed.
- Your saved papers in Zotero when you configure access.

**When NOT to use:**

- To configure papers sources, install an MCP, complete SSO, install a marketplace plugin, or rotate a key. Those belong in [the papers setup reference](../using-research/references/configuring/papers.md).
- For language reference, library documentation, RFCs, or public web search: use `research:public`.
- For internal documents (Slack, Confluence, Linear, Notion): use `research:internal`.
- For domain-model questions (entities, bounded contexts, ubiquitous language): use `research:domain`.
- For citable book content (ISBN, table of contents, public-domain full text): use `research:books`.

## Query expansion (jeopardy search)

Before dispatching to a capability, expand the question into 3-5 variants. See [`research/references/jeopardy.md`](../../references/jeopardy.md) for the general technique. Papers-specific axes:

- **DOI-vs-title**: When you have a DOI, prefer DOI-keyed capabilities. When you know only the title, run title-and-author queries against the topic-search capability.
- **Author-name normalization**: First-author-last-name forms, ORCID id when known, common transliteration variants for non-English author names.
- **Venue and year**: Preprint year (ArXiv) vs. published year (Crossref); conference name (`PLDI 2024`) vs. journal name.
- **Identifier variants**: DOI, PMID, PMCID, arXiv id. The same paper frequently has multiple identifiers, and the *DOI fan-out* capability resolves disagreement.
- **Topic-and-keyword variants**: Narrow (specific technique with technology), broad (the field name), synonyms (`backpropagation` / `gradient descent` / `optimizer`).

Run the variants in the order that the routing table below dictates. Union the result sets before deciding which capability has the highest-quality hit.

## Capability routing

[The papers setup reference](../using-research/references/configuring/papers.md) names the capabilities in its published contract. The routing table maps question type to the capability that answers it.

| Question intent | Primary capability | Reference |
|---|---|---|
| "Metadata for this DOI" | DOI→metadata | [`references/crossref.md`](references/crossref.md) |
| "You suspect this DOI is incorrect or hallucinated" | DOI fan-out | [`references/doi.md`](references/doi.md) |
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
| Papers you have saved in Zotero | Zotero library lookup | [`references/zotero.md`](references/zotero.md) |

### Routing heuristic

The routing table is the lookup. The heuristic below is what to apply when the question does not name a source:

- **DOI in hand** → DOI fan-out via `doi-mcp` first, then Crossref + Unpaywall in parallel.
- **Topic search without DOI** → OpenAlex (breadth) + Semantic Scholar (CS/ML quality), and DBLP if the topic is unambiguously CS.
- **Preprint-only / not-yet-published** → ArXiv directly.
- **"What cites this paper"** → Semantic Scholar citation graph. If subscribed, Scite Smart Citations classifies the supporting / disputing / mentioning posture.
- **Biomedical** → `pubmed@life-sciences` when you install the plugin; Europe PMC for full-text coverage beyond PubMed.
- **Publisher-specific** → Wiley Scholar Gateway when you configure SSO.

For conditional capabilities that the contract marks Not-Available, accept the typed result as a routing signal and continue with the next capability in the heuristic. Not-Available indicates you haven't installed the plugin, completed SSO, or maintained your subscription. The free stack includes OpenAlex, Semantic Scholar, Crossref, Unpaywall, and ArXiv. This covers the majority of queries without any conditional source.

## Output format

Write findings to `.ailly/research/YYYY-MM-DD-A-<topic>/papers.md`. If the caller provides a task-scoped research folder such as `.ailly/developer/<session-slug>/research/`, write `papers.md` there instead. Cite per the loose IEEE style in [`research/references/citations.md`](../../references/citations.md). One consolidated `papers.md` per session topic (per Decision 6: no per-source split, no cache).

```
# Papers: <question>

## Findings
<narrative: synthesized answer with inline citations [N]>

## Sources
[1] Author/Org. "Title." Date. [Online]. Available: <URL>
[2] Author/Org. "Title." Date. [Online]. Available: <URL>
```

Excerpts only. Do not stage cached PDFs or full bodies. For passages from licensed sources (Wiley, Scite, Zotero with copyrighted papers), quote within the session for the user's own work. Cite and link with the DOI instead of staging to public artifacts.

## Common mistakes

- **Skipping query expansion.** A single phrasing frequently misses the canonical identifier or the venue the user actually meant. Always expand first.
- **Mixing capabilities.** Asking for OA-PDF when the question is about citation graph; asking ArXiv for a published-only paper that never had a preprint. The routing table is the lookup.
- **Quoting from non-quotable sources.** Wiley snippets are display-only; Scite Smart Citations are proprietary; gated journal full text is non-redistributable. Cite-and-link with the DOI.
- **Ignoring typed Not-Available.** A conditional capability returning Not-Available is a routing signal, not a failure. This can result from: no PubMed plugin, no Wiley SSO, or no Scite subscription. Continue with the next capability in the heuristic.
- **Re-teaching the wiring.** A "first, make sure you have installed the PubMed plugin" preface is wiring leakage. The wiring skill owns setup; this skill consumes the contract. If a preface is unavoidable, the contract is incomplete. Widen it in [the papers setup reference](../using-research/references/configuring/papers.md).
- **Hallucinated DOIs.** Plausible-looking DOIs that no source recognizes are common in AI-mediated work. Use the *DOI fan-out* capability when a DOI looks suspect; if no source returns a record, return Not-Available rather than fabricating a citation.
- **Treating OpenAlex's metering as a hard block.** OpenAlex's $1/day free credit covers most individual research sessions. Above the credit, degrade to Semantic Scholar + Crossref for the topic search; do not silently skip the query.

## Composes with

- **the papers setup reference**: See `research:using-research` and `references/configuring/papers.md`. This is the wiring partner that publishes the contract this skill consumes.
- **`research:books`**: Sibling practice skill for citable books.
- **`research/references/jeopardy.md`**: Query expansion technique.
- **`research/references/citations.md`**: IEEE citation format.
