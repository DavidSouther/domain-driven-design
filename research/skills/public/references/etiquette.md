# public: etiquette

Shared rules for the public-web stack.
The wiring in [`../../configuring-public/SKILL.md`](../../configuring-public/SKILL.md) cites this file at configure time.
The per-provider reference file at [`augmented-search.md`](augmented-search.md) cites it for the shared rules it inherits.

The core transport includes `WebSearch` and `WebFetch` and needs no install.
These rules are **policy** layered over that transport: who the project identifies as, how fast it may hit a host, and which hosts it may reach at all.

## Contact user-agent

- Every fetch carries a `User-Agent` containing the app name and a **contact email**, so a host operator who notices the traffic can reach a human.
- Hold the string in `RESEARCH_USER_AGENT` (or the environment's equivalent).
  Never hard-code an email into committed source.
  Keep it in env so it travels with the operator, not the repo.
- A descriptive user-agent distinguishes a polite agent from anonymous scrapers.
  Some hosts raise anonymous rate limits when a contact header is present.

## Rate limits and backoff

- Respect **per-host request spacing**.
  Record the default spacing in this file; tighten it for any host that documents a stricter cap.
- **Back off on HTTP 429** (and on 503).
  A 429 is the host signaling rate-limit pressure rather than failing hard; honor `Retry-After` when present, otherwise use exponential backoff before retrying the same host.
- Serialize fan-out into any host that signals pressure; do not parallelize requests to a host that has already returned a 429.

## Allowed-domain list

- The allowed-domain list **scopes search and fetch** when set.
  An **empty allowed list means unrestricted**: the default for general public research.
- When the project sets an allowed list, fetches outside it are out of policy; route the query elsewhere or report that the answer is not reachable under policy.

## Blocked-domain list

- The system honors the blocked-domain list unconditionally.
  **Blocked hosts reject all fetches** before the request travels, even when the allowed list is empty.
- Use the blocked list for hosts the project must not tap.
  Include paywalled mirrors that violate terms, hosts operators request you to avoid, and known-malicious domains.
- A fetch that should block but succeeds signals drift and triggers re-verification in [`../../configuring-public/SKILL.md`](../../configuring-public/SKILL.md).

## Key handling

- Any provider key (for the optional augmented-search provider) travels in an environment variable; never in committed source.
- Rotation of a provider key triggers a re-run of [`../../configuring-public/SKILL.md`](../../configuring-public/SKILL.md) to refresh the wiring and the smoke-tests.

## Cross-topic note

The books and papers stacks maintain their own etiquette files at [`../../books/references/etiquette.md`](../../books/references/etiquette.md) and [`../../papers/references/etiquette.md`](../../papers/references/etiquette.md).
All three share the **key-handling** and **backoff-on-429** posture.

The public file is the thinnest because the public stack bundles its core transport without authentication.
It has no per-host auth surface and no per-source rights tiers.
Its distinct concerns are the **contact user-agent** and the **allowed/blocked-domain policy**.
These provide project-level governance over an open transport, rather than per-source credentials.
