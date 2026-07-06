# Books: Etiquette

Per-host rules for the books stack. The wiring skill ([`../../configuring-books/SKILL.md`](../../configuring-books/SKILL.md)) cites this file at configure time; the per-source reference files cite it for the shared rules.

## Open library

- Send a `User-Agent` header containing the app name and a **contact email**. With this header the anonymous rate limit rises from 1 req/s to 3 req/s.
- Back off on HTTP 429; the server signals rate-limit pressure rather than failing hard.
- Bibliographic data is CC0; cover images are CC-BY-SA. Attribute Open Library when reproducing covers.

## Google books

- Hold the API key in `GOOGLE_BOOKS_API_KEY`; pass as `?key=...`. Never commit the key to source.
- Daily quota: 1,000 requests with a key; 1 req/s per user ceiling.
- Snippet text is for display only. Cite-and-link; do not transcribe entire previews.

## Internet archive

- No published hard rate cap. Be polite (≤2 req/s); back off on 429/503.
- Read-only access requires no auth; S3 keys exist for upload only.
- Check the `rights` field per item before quoting full text.

## Gutendex / Project Gutenberg

- Do not fetch `gutenberg.org` format URLs directly at scale; the host blocks bots. Use a local mirror via `bobbyhouse/project-gutenberg` MCP, or route through `gutendex.com` for metadata and fetch format URLs sparingly with a polite User-Agent.
- Strip the Gutenberg header and trailer before quoting; the boilerplate carries the trademark and license, neither of which is public domain.

## Hathitrust

- You can access the Bibliographic API freely without auth or rate-limit headers.
- **Data API requires OAuth 1.0a** with institutional credentials. Tokens carry an expiration; treat expiration as a re-verification trigger in the wiring skill.
- Non-consumptive access for in-copyright items. Do not relay full text from those tiers to the user as quoted prose.

## Library of congress

- Pass `?fo=json` on every catalog endpoint. Be polite (≤2 req/s).
- Most LoC-created records are public domain; check the per-item `rights` field for donated collections.

## Hardcover

- API key in `HARDCOVER_API_KEY`; sent as `Authorization: Bearer ...`.
- Reviews are user-generated under platform terms; cite-and-link rather than verbatim quote.

## Zotero

- API key in `ZOTERO_API_KEY`; library ID in `ZOTERO_LIBRARY_ID`.
- Group libraries use `/groups/{id}` instead of `/users/{id}`.
- Published bandwidth budget is 50 GB/month per key; back off on 429.

## O'Reilly Learning

- Auth is enterprise SSO (official MCP) or a personal Platform Search session (community MCP). Both expire; treat expiration as a re-verification trigger.
- Cite-and-link with the platform URL; do not redistribute passages outside the user's own session.

## Calibre / Claude Reader / ebook-mcp / Kindle

- Local-only sources. No network etiquette applies, but the user's licensing applies, personal-use licensed; do not stage passages from copyrighted personal imports into public artifacts.
- DRM stripping (Calibre + Kindle plugin) is jurisdictionally varied; the user is the licensee and the responsibility holder.

## Key handling

- All API keys travel in environment variables; never in committed source.
- Rotation of any key triggers a re-run of [`../../configuring-books/SKILL.md`](../../configuring-books/SKILL.md) to refresh the wiring and the smoke-tests.
- Tokens with explicit expiration (HathiTrust OAuth, O'Reilly enterprise SSO) carry re-verification triggers in the wiring skill.

## Cross-topic note

The papers stack maintains its own [`../../papers/references/etiquette.md`](../../papers/references/etiquette.md). The two files share the **key-handling** posture but differ on every per-host rule. Books rules center on User-Agent contact emails, edition disambiguation, and full-text rights tiers. Papers rules center on rate-limited `mailto=` parameters, exponential backoff, and per-source request spacing.
