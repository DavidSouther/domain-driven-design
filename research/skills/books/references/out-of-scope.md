# Books out of scope

Excluded book sources. Find why and suggested alternatives below.

## Worldcat

- **Reason:** OCLC retired WorldCat Search API v1. v2 and the Discovery API at `developer.api.oclc.org` require a **WSKey** tied to an OCLC cataloging subscription, which is institutional and not available to individual developers.
- **Closest alternative:** Open Library for bibliographic anchor; HathiTrust for member-library holding confirmation.

## Goodreads

- **Reason:** Goodreads retired its public API in **December 2020**. Current Goodreads MCPs scrape logged-in user pages through tools like `getgather-hub/goodreads` and `faisal-burhanudin/goodreads`. They require `GOODREADS_EMAIL` and `GOODREADS_PASSWORD` in environment variables. This violates Goodreads ToS. Storing credentials in environment variables is a security smell this stack does not endorse.
- **Closest alternative:** Hardcover for reviews and reading-community signal.

## Amazon Kindle (no public mcp)

- **Reason:** Amazon does not expose a public API for Kindle library content. The browser-based Kindle reader does not permit programmatic access. The [`kindle.md`](kindle.md) file documents the user-supplied-MCP path separately; this entry covers the absence of a public option.
- **Closest alternative:** Calibre + Kindle plugin (DRM strip per the user's jurisdiction) or `MyClippings.txt` parse.

## IEEE xplore

- **Reason:** IEEE Xplore's developer API returns metadata across the full corpus, but full-text access requires **separate sales contracts**. The IEEE Member Digital Library is browser-only with no programmatic path. Out of scope for an individual-developer skill.
- **Closest alternative:** for technical books, O'Reilly Learning; for technical papers, route via [`../../papers/SKILL.md`](../../papers/SKILL.md).

## ACM digital library

- **Reason:** the ACM Skills Bundle proxies to O'Reilly Learning via a browser SSO at `go.oreilly.com/acm`. No documented programmatic path on the ACM side.
- **Closest alternative:** O'Reilly Learning MCP when the user has enterprise access; otherwise browser-only.

## LinkedIn learning

- **Reason:** LinkedIn restricts API access to **Partner Program members and organizations with site licenses**; OAuth is two-legged, with no individual-developer tier.
- **Closest alternative:** O'Reilly Learning for technical career-skill content.

## Guidepoint

- **Reason:** **Wrong topic.** The Guidepoint MCP exposes expert-interview transcripts, not books. When the research stack adds expert-interview surfaces, this skill routes Guidepoint elsewhere; it is not in scope for `research:books`.

## ISBNdb

- **Reason:** Paid-only; plans start at **\$14.99/month**. Useful as a fallback if Open Library + Google Books miss a title, but not a default.
- **Closest alternative:** Open Library + Google Books for ISBN lookup.

## Per publisher institutional MCPs

- **Reason:** Servers like `LinXueyuanStdio/academic-mcp`, `Dianel555/paper-search-mcp-nodejs`, and `qwe4559999/scopus-mcp` require the user to supply institutional publisher API keys (`WOS_API_KEY`, `ELSEVIER_API_KEY`, `SPRINGER_API_KEY`). Institutional subscriptions control access to these keys. This skill documents these as **opt-in for institutional users only**; they are not surfaced as defaults.
- **Closest alternative:** for papers, the default OpenAlex + Semantic Scholar + Crossref + Unpaywall stack.

## Wiley TDM (full text)

- **Reason:** Wiley's Text and Data Mining API at `api.wiley.com` delivers full-text PDFs under a **contractual TDM license** that is incompatible with the individual-developer posture of this stack. Wiley Scholar Gateway (snippet plus DOI link-out) fits within the scope defined in [`../../papers/references/wiley-scholar-gateway.md`](../../papers/references/wiley-scholar-gateway.md); this skill excludes the TDM full-text API.
