# Configuring papers

> Setup reference for the academic-papers sources. Loaded on demand from
> `research:using-research` (see its "Configuring Sources" section) when bootstrapping or
> revising the papers stack; not a standalone always-on skill. Applies once per
> environment, never inside a research session.

## Overview

This skill installs the harness that `research:papers` consumes. An academic-papers research stack is a set of named **capabilities** reached through **transports** (MCP first, HTTP fallback). Capabilities include DOI metadata, DOI to OA-PDF resolution, topic search, citation graphs, preprint search, and biomedical search. The wiring probes each source, installs marketplace plugins where required, completes the SSO handshake for institutional sources, and records the active transport. It confirms that each named capability returns the shape the practice skill expects. Re-running the wiring on a configured system confirms the contract or surfaces drift. It never destroys state.

The harness this skill installs is the **papers capability contract** below. The practice skill `research:papers` cites the contract and dispatches capabilities; it never re-teaches the configuration.

## Contract

Once you configure the papers sources (see this `papers.md` reference), callers of `research:papers` may assume:

| Capability | Inputs | Returns | Conditional |
|---|---|---|---|
| DOI→metadata | DOI | `{ doi, title, authors, year, venue, type }` | no |
| DOI→OA-PDF | DOI | `{ pdf_url, license, oa_status }` or typed Not-Available | no |
| Topic search | query, optional filters | ranked hits across OpenAlex, Semantic Scholar, and DBLP (for CS) | no |
| Citation graph | DOI or paper id | `{ cites: [...], cited_by: [...] }` | no |
| Preprint search | query, optional category | ArXiv hits with category and version metadata | no |
| Biomedical search | query | PubMed citations and PMC full text where open-access | available when configured |
| Wiley journal search | query | semantic-snippet hits with DOI link-out from Scholar Gateway | available when configured |
| Citation-context classification | DOI | Smart Citations (supporting / disputing / mentioning) from Scite | available when configured |
| Zotero library lookup | query, item-type filter | hits from the user's Zotero library | available when configured |

**Conditional capabilities** return a typed Not-Available result when the source is not configured:

```
{ result: "not-available", capability: "<name>", reason: "<why>" }
```

The practice skill treats Not-Available as a routing signal, not as an error.

**Apply these etiquette rules:** use Crossref polite requests with `mailto=` and set the OpenAlex API key in env. Space ArXiv requests three seconds apart on a single connection and use exponential backoff on 429 responses from Semantic Scholar. Add the Unpaywall email parameter and install marketplace plugins where required. The shared rules live in [`papers/references/etiquette.md`](../../../papers/references/etiquette.md). Each per-source reference cites that file for the rules it inherits.

## When to use

- Standing up a fresh checkout for the first time and `research:papers` has no sources to call.
- Adding a new papers source, installing a new MCP server, rotating an API key, completing the Wiley SSO handshake, or installing an Anthropic-curated marketplace plugin.
- Re-verifying after a re-verification trigger (see below) fires.

**When NOT to use:** inside a research session at a per-query call site. The per-query partner is `research:papers`. For non-papers questions use `research:public`, `research:internal`, or `research:domain`.

## Configure checklist

Walk the checklist top-to-bottom on a fresh environment. Each item probes the MCP option first, falls back to HTTP, sets env vars, and smoke-tests the capability the source provides. Smoke-test means a minimal query against the configured transport that exercises the named capability and confirms the contract holds.

Default sources for wide adoption:

- [ ] **Crossref**: HTTP against `api.crossref.org` per [`papers/references/crossref.md`](../../../papers/references/crossref.md). Set `CROSSREF_MAILTO` to a contact email to route requests through polite channels. Smoke-test: DOI to metadata for a known DOI.
- [ ] **Unpaywall**: HTTP against `api.unpaywall.org/v2/{doi}?email=` per [`papers/references/unpaywall.md`](../../../papers/references/unpaywall.md). Set `UNPAYWALL_EMAIL`. Smoke-test: DOI→OA-PDF for a known open-access DOI.
- [ ] **OpenAlex**: probe an OpenAlex MCP (for example, `oksure/openalex-research-mcp`) per [`papers/references/openalex.md`](../../../papers/references/openalex.md); fall back to HTTP against `api.openalex.org`. Set `OPENALEX_API_KEY` (post-February 2026, `$1/day` free credit). Smoke-test: topic search for "domain-driven design."
- [ ] **Semantic Scholar**: probe `FujishigeTemma/semantic-scholar-mcp` per [`papers/references/semantic-scholar.md`](../../../papers/references/semantic-scholar.md); fall back to HTTP against `api.semanticscholar.org`. Set `SEMANTIC_SCHOLAR_API_KEY` (strongly preferred for better limits). With a key, you get 1 RPS; anonymous access allows 5,000 requests per 5 minutes with mandatory exponential backoff on 429 s. Smoke-test: citation graph for a known paper.

Priority sources (personal-default):

- [ ] **ArXiv**: probe `blazickjp/arxiv-mcp-server` per [`papers/references/arxiv.md`](../../../papers/references/arxiv.md); fall back to HTTP against `export.arxiv.org/api/query`. Respect three-second spacing on a single connection. Smoke-test: preprint search in `cs.SE`.
- [ ] **DOI fan-out**: probe `tfscharff/doi-mcp` per [`papers/references/doi.md`](../../../papers/references/doi.md). Fans out DOI resolution across 9+ sources in parallel. Smoke-test: DOI→metadata for a known DOI.

Conditional sources via the Anthropic-curated `life-sciences` marketplace plugin:

- [ ] **PubMed**: run `/plugin marketplace add anthropics/life-sciences` then `/plugin install pubmed@life-sciences` per [`papers/references/pubmed.md`](../../../papers/references/pubmed.md). No account required (covers 36M+ biomedical citations). Smoke-test: biomedical search for a known PMID. If you skip this install, mark the *Biomedical search* capability Not-Available.
- [ ] **Wiley Scholar Gateway**: run `/plugin marketplace add anthropics/life-sciences` (if not already added) then `/plugin install wiley-scholar-gateway@life-sciences` per [`papers/references/wiley-scholar-gateway.md`](../../../papers/references/wiley-scholar-gateway.md). Complete the SSO handshake (Claude Pro plus Wiley institutional or trial SSO). Smoke-test: query a known Wiley journal article. If SSO is not completed, mark the *Wiley journal search* capability Not-Available.

Opt-in sources (configure when the user supplies access):

- [ ] **Scite**: probe the hosted MCP at `scite.ai/mcp` per [`papers/references/scite.md`](../../../papers/references/scite.md); alternative is `scitedotai/scite-mcp-skill`. Requires an active Scite subscription. Smoke-test: citation-context classification for a known DOI.
- [ ] **DBLP**: HTTP against `dblp.org/search/.../api` per [`papers/references/dblp.md`](../../../papers/references/dblp.md). Smoke-test: author search for a known CS author.
- [ ] **Europe PMC**: HTTP against `ebi.ac.uk/europepmc/webservices/rest/search` per [`papers/references/europe-pmc.md`](../../../papers/references/europe-pmc.md). Smoke-test: title search for a known biomedical preprint.
- [ ] **CORE**: HTTP against `core.ac.uk/services/api` per [`papers/references/core.md`](../../../papers/references/core.md). Set `CORE_API_KEY`. Smoke-test: full-text search for a known phrase.
- [ ] **Zotero**: probe `54yyyu/zotero-mcp` (or `cookjohn/zotero-mcp`) per [`papers/references/zotero.md`](../../../papers/references/zotero.md). Set `ZOTERO_API_KEY` and `ZOTERO_LIBRARY_ID`. Smoke-test: item-type filter for `journalArticle`.

You can find **out-of-scope sources** in [`papers/references/out-of-scope.md`](../../../papers/references/out-of-scope.md), which documents why we exclude each. These include Wiley TDM (contractual license), per-publisher institutional MCPs, Google Scholar, and Connected Papers. The institutional MCPs comprise Web of Science, ScienceDirect, Springer, and Scopus, while Connected Papers requires official clients.

## Re-verification triggers

Re-run the wiring when any of the following happens. Re-running confirms the contract still holds; on a configured system it does not destroy state.

- An MCP server upgrades and its tool surface or response shape may have shifted.
- An API key rotates (OpenAlex, Semantic Scholar, CORE, Zotero).
- **The Wiley SSO token expires** and the institutional or trial session needs renewing.
- **A Scite subscription lapses** or renews and the hosted MCP becomes unavailable or available.
- You add a new papers source that should sit in the contract.
- A practice run reports a drift: a capability returned a shape the practice skill did not expect, or a smoke-test that previously passed now fails.
- An Anthropic-curated `life-sciences` plugin updates and may require re-install or re-authentication.

## Composes with

- **`research:papers`**: the per-query partner. Wiring publishes the contract; practice consumes it.
- **the books setup reference (`books.md`)**: sibling wiring for the books stack. The two harnesses are disjoint at the source level but share the cadence convention.
- **`research/references/citations.md`**: IEEE citation format the practice skill writes against.
- **`research/references/jeopardy.md`**: query expansion the practice skill applies before dispatching to a capability.
