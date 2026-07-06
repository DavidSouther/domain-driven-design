# O'Reilly learning

Technical content from O'Reilly Media and partner publishers (Manning, Pragmatic Programmers, Packt, No Starch, Wiley tech imprints). Plus video courses and live events. First stop for any hands-on technical question routing through this skill.

## What it provides

- **O'Reilly library search** — AI-powered search across roughly 60,000 books, video courses, and live events.
- **Chapter and section retrieval** — planned for 2026; not all official-MCP versions expose it at launch.

## MCP options (probe order)

**Primary: official O'Reilly Learning MCP** (launched November 19, 2025).

- Transport: standard MCP wire protocol; gated to **enterprise** O'Reilly customers at launch; wider rollout to individual subscribers promised for 2026 with no published date.
- Auth: O'Reilly enterprise SSO token.
- Supported clients per O'Reilly: Claude Code, Cursor, VS Code.

**Fallback: `odewahn/orm-discovery-mcp`** (community).

- Wraps the O'Reilly Platform Search API at `oreilly.com/online-learning/integration-docs/search.html`.
- Requires a personal O'Reilly Learning subscription; auth details are not publicly documented.
- Small project (≈4 stars at May 2026); the official MCP will likely deprecate it when it opens to individuals.

**Not-Available** when neither is reachable. The wiring skill returns a typed Not-Available result for the *O'Reilly library search* capability; the practice skill degrades to Google Books and Open Library for the same query.

## HTTP fallback

None practical for individual developers. O'Reilly's separate SCIM API token is for user provisioning only, not content retrieval. ACM's "O'Reilly Online Learning" benefit ($75/year add-on) proxies to the same platform but exposes only the browser UI; no documented programmatic path from the ACM side.

## Query shapes

- *"Books on Linux system administration"* → primary capability: O'Reilly library search.
- *"Chapters on Kafka stream processing"* → primary capability: O'Reilly library search; section retrieval if the active server exposes it.
- *"Hands-on Rust async runtimes course"* → primary capability: O'Reilly library search (includes courses).
- *"PostgreSQL performance tuning"* → primary capability: O'Reilly library search.
- *"AWS networking for SREs"* → primary capability: O'Reilly library search.

## Licensing

O'Reilly content is **subscription-licensed**. Cite-and-link with the platform URL and the user's session; do not redistribute passages. You may quote snippets returned by the MCP within the user's own session for their own work; do not stage them into public artifacts.

## Failure modes

- **SSO token expired** (enterprise MCP)—re-authenticate. This is a re-verification trigger in [`../../configuring-books/SKILL.md`](../../configuring-books/SKILL.md).
- **Search API quota exceeded** (community MCP)—back off; the Platform Search API is not documented in detail and quotas can shift without notice.
- **Capability mismatch** — section-level retrieval is on the 2026 roadmap; if the deployed MCP does not expose it, the *section retrieval* capability returns Not-Available.
- **Individual access opens in 2026** — when the official MCP opens to individual subscribers, promote it from the enterprise-only probe to the primary transport for personal use. This is a named re-verification trigger.
