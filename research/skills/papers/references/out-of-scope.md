# Papers — out of scope

Documented-but-excluded papers sources with reasons. When a user asks for one of these, the practice skill cites this file and routes to the closest in-scope alternative.

## Wiley TDM API

- **Reason:** Wiley's Text and Data Mining API at `api.wiley.com` delivers **full-text PDFs of subscribed content under a contractual TDM license**. The license posture is incompatible with the individual-developer surface of this stack.
- **Closest alternative:** **Wiley Scholar Gateway** for semantic-snippet hits with DOI link-out — see [`wiley-scholar-gateway.md`](wiley-scholar-gateway.md). Snippet plus link, not full PDF.

## Google Scholar

- **Reason:** **No public API** and the `robots.txt` explicitly **forbids automated access**. Community servers like `JackKuo666/Google-Scholar-MCP-Server` and Apify-hosted scrapers exist but live in a legally gray zone that this stack will not endorse.
- **Closest alternative:** OpenAlex for breadth, Semantic Scholar for CS/ML, ArXiv for preprints. The default stack matches or beats Google Scholar's coverage for most queries this skill targets.

## IEEE Xplore

- **Reason:** IEEE Xplore's developer API returns metadata across the full corpus, but **full-text access is gated behind separate sales contracts**. Out of scope for an individual-developer skill.
- **Closest alternative:** ArXiv for CS preprints; OpenAlex for citations to IEEE papers; DOI resolution via Crossref or `doi-mcp` for the metadata.

## ACM Digital Library

- **Reason:** Paywalled; full-text requires institutional subscription. No public API for full text.
- **Closest alternative:** ArXiv for CS preprints (most ACM papers are available as ArXiv preprints); DBLP for venue-level publication lists; OpenAlex for citation data.

## Connected Papers

- **Reason:** No MCP wrapper. Publishes only **official JS and Python clients**, both **gated by API key requested via email**.
- **Closest alternative:** OpenAlex citation graph and Semantic Scholar citation graph give the same neighborhood signal without the off-stack client.

## Per-publisher institutional MCPs

- **Reason:** Servers like `LinXueyuanStdio/academic-mcp`, `Dianel555/paper-search-mcp-nodejs`, and `qwe4559999/scopus-mcp` advertise Web of Science, ScienceDirect, Springer Nature, Scopus, and Wiley. Each requires the user's own institutional publisher API key (`WOS_API_KEY`, `ELSEVIER_API_KEY`, `SPRINGER_API_KEY`). The keys are themselves gated by institutional subscription. **Opt-in for institutional users only**; not surfaced as defaults.
- **Closest alternative:** the default OpenAlex + Semantic Scholar + Crossref + Unpaywall + ArXiv stack covers most queries without per-publisher keys.

## Goodreads (if a paper-adjacent query lands here by accident)

- **Reason:** Goodreads is a books surface and its API retired in December 2020. See [`../../books/references/out-of-scope.md`](../../books/references/out-of-scope.md) for the full reasoning.

## ISBNdb (paper-adjacent only)

- **Reason:** Books-only and paid. Not relevant to papers.

## LinkedIn Learning

- **Reason:** Books and course content surface, restricted to LinkedIn Partner Program members. Out of scope for both topics.

## Notes on what is **not** out of scope

- **PubMed** is **in scope** via the Anthropic-curated `pubmed@life-sciences` marketplace plugin. See [`pubmed.md`](pubmed.md).
- **Wiley Scholar Gateway** is **in scope** via `wiley-scholar-gateway@life-sciences`. See [`wiley-scholar-gateway.md`](wiley-scholar-gateway.md).
- **Scite** is **opt-in in scope** via the hosted MCP at `scite.ai/mcp` when the user has a subscription. See [`scite.md`](scite.md).
