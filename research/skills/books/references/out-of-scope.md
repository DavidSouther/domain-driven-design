# Books — out of scope

Documented-but-excluded books sources with reasons. When a user asks for one of these, the practice skill cites this file and routes to the closest in-scope alternative.

## WorldCat

- **Reason:** WorldCat Search API v1 has been retired. v2 and the Discovery API at `developer.api.oclc.org` require a **WSKey** tied to an OCLC cataloging subscription, which is institutional and not available to individual developers.
- **Closest alternative:** Open Library for bibliographic anchor; HathiTrust for member-library holding confirmation.

## Goodreads

- **Reason:** Goodreads retired its public API in **December 2020**. Current Goodreads MCPs (`getgather-hub/goodreads`, `faisal-burhanudin/goodreads`) work by **scraping the logged-in user's pages** with `GOODREADS_EMAIL` and `GOODREADS_PASSWORD` in env. This is against Goodreads ToS, and credentials-in-env is a security smell that this stack will not endorse.
- **Closest alternative:** Hardcover for reviews and reading-community signal.

## Amazon Kindle (no public MCP)

- **Reason:** Amazon does not expose a public API for Kindle library content. The Kindle Cloud Reader is browser-only and is not licensed for programmatic access. The user-supplied-MCP path remains in scope and is documented separately in [`kindle.md`](kindle.md); this entry covers the absence of a public option.
- **Closest alternative:** Calibre + Kindle plugin (DRM strip per the user's jurisdiction) or `MyClippings.txt` parse.

## IEEE Xplore

- **Reason:** IEEE Xplore's developer API returns metadata across the full corpus, but full-text access is gated to **separate sales contracts**. The IEEE Member Digital Library is browser-only with no programmatic path. Out of scope for an individual-developer skill.
- **Closest alternative:** for technical books, O'Reilly Learning; for technical papers, route via [`../../papers/SKILL.md`](../../papers/SKILL.md).

## ACM Digital Library

- **Reason:** the ACM Skills Bundle proxies to O'Reilly Learning via a browser SSO at `go.oreilly.com/acm`. No documented programmatic path on the ACM side.
- **Closest alternative:** O'Reilly Learning MCP when the user has enterprise access; otherwise browser-only.

## LinkedIn Learning

- **Reason:** API is restricted to **LinkedIn Partner Program members and organizations with site licenses**; OAuth two-legged, no individual-developer tier.
- **Closest alternative:** O'Reilly Learning for technical career-skill content.

## Guidepoint

- **Reason:** **Wrong topic.** Guidepoint MCP exposes expert-interview transcripts, not books. Routed elsewhere if expert-interview surfaces are added to the research stack; not in scope for `research:books`.

## ISBNdb

- **Reason:** Paid-only; plans start at **\$14.99/month**. Useful as a fallback if Open Library + Google Books miss a title, but not a default.
- **Closest alternative:** Open Library + Google Books for ISBN lookup.

## Per-publisher institutional MCPs

- **Reason:** Servers like `LinXueyuanStdio/academic-mcp`, `Dianel555/paper-search-mcp-nodejs`, and `qwe4559999/scopus-mcp` require the user's own institutional publisher API key (`WOS_API_KEY`, `ELSEVIER_API_KEY`, `SPRINGER_API_KEY`). These keys are themselves gated by institutional subscription. Document as **opt-in for institutional users only**; not surfaced as defaults.
- **Closest alternative:** for papers, the default OpenAlex + Semantic Scholar + Crossref + Unpaywall stack.

## Wiley TDM (full-text)

- **Reason:** Wiley's Text and Data Mining API at `api.wiley.com` delivers full-text PDFs under a **contractual TDM license** that is incompatible with the individual-developer posture of this stack. Wiley Scholar Gateway (snippet plus DOI link-out) is in scope under [`../../papers/references/wiley-scholar-gateway.md`](../../papers/references/wiley-scholar-gateway.md); the TDM full-text API is excluded.
