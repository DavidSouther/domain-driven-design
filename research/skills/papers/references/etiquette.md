# Papers: Etiquette

Per-host rules for the papers stack.
The wiring process (see [`../../configuring-papers/SKILL.md`](../../configuring-papers/SKILL.md)) cites this file at configure time; the per-source reference files cite it for the shared rules.

## Crossref

- Enter the **polite tier** by adding `mailto=you@example.org` as a query parameter or `User-Agent` header.
  Set `CROSSREF_MAILTO` in env.
- Watch `x-rate-limit-limit` / `x-rate-limit-interval` headers; back off on 429 s.
- Rate limits revised downward December 1, 2025.

## Openalex

- **API key required as of February 13, 2026.**
  Free, 30-second signup.
  Set `OPENALEX_API_KEY`.
- Daily budget: **$1/day free credit**.
  Per-call thereafter: $0 for singletons, $0.0001 for lists, $0.001 for search, $0.01 for semantic-search or content download.
- The historic `mailto=` parameter still works for politeness but no longer governs access.

## Semantic scholar

- API key strongly preferred.
  Request via the developer portal; pass as `x-api-key` header.
  Set `SEMANTIC_SCHOLAR_API_KEY`.
- **With key**: 1 RPS dedicated.
- **Anonymous**: global shared quota capped at 5,000 requests per 5 minutes.
- **Mandatory exponential backoff on 429 s.**

## Arxiv

- **One request per three seconds, single connection.**
  Serialize fan-out into this source.
- Use OAI-PMH at `https://oaipmh.arxiv.org/oai` for bulk metadata harvesting.
  Reserve the query API for live use.
- Output is Atom/XML; budget the parse cost accordingly.

## Unpaywall

- email parameter required: `?email=you@example.org`.
  Set `UNPAYWALL_EMAIL`.
- No key, no documented hard rate limit; the email serves as a per-caller fair-use identifier.

## Core

- API key required (free).
  Set `CORE_API_KEY`; pass as `Authorization: Bearer ...`.
- Rate limits: **1 req/10 s for batch, 5 req/10 s for single queries**.
  Higher tiers for member institutions.

## Pubmed

- API key optional but recommended.
  Raises rate from 3 RPS to 10 RPS.
  Pass `&api_key=...`.
- Use `tool=` and `email=` parameters for politeness identification.

## Wiley scholar gateway

- OAuth 2.0 via Wiley CONNECT SSO.
  Claude Pro plus Wiley institutional or trial SSO.
  Trial valid through June 30, 2026.
- Treat SSO-token expiration as a re-verification trigger in [`../../configuring-papers/SKILL.md`](../../configuring-papers/SKILL.md).

## Scite

- Active Scite subscription required.
  Treat subscription lapse as a re-verification trigger.
- Smart Citation classifications are Scite-proprietary; cite-and-link rather than redistribute.

## Zotero

- API key in `ZOTERO_API_KEY`; library ID in `ZOTERO_LIBRARY_ID`.
- Group libraries use `/groups/{id}` instead of `/users/{id}`.
- 50 GB/month bandwidth per key; back off on 429.

## DBLP / Europe PMC

- No auth required.
  Be polite (≤2 req/s for DBLP).
  Default to a similar posture for Europe PMC unless the user is institutional.

## Key handling

- All API keys travel in environment variables; never in committed source.
- Rotation of any key triggers a re-run of [`../../configuring-papers/SKILL.md`](../../configuring-papers/SKILL.md) to refresh the wiring and the smoke-tests.
- Tokens with explicit expiration carry re-verification triggers in the wiring process.
  These include Wiley SSO, Scite subscription, and OpenAlex daily budget.

## Cross-topic note

The books stack maintains its own [`../../books/references/etiquette.md`](../../books/references/etiquette.md).
The two files share the **key-handling** posture but differ on every per-host rule.

Papers rules center on three aspects: **`mailto=` parameters for politeness**, **exponential backoff**, and **per-source request spacing** with ArXiv's three-second cap as the strictest limit.
Books rules center on **User-Agent contact emails**, **edition disambiguation**, and **full-text rights tiers** with HathiTrust OAuth as the strictest auth surface.
