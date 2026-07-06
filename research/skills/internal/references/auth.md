# Internal auth

Shared credential and handshake rules for the internal stack. The wiring skill (see [`../../configuring-internal/SKILL.md`](../../configuring-internal/SKILL.md)) cites this file at configure time. Per-source reference files cite it for the shared rules they inherit. This is the internal-stack analog of `etiquette.md` in books/papers. For an all-authenticated stack, the shared file focuses on credentials and handshakes rather than per-host politeness.

## OAuth/SSO handshake pattern

Every internal source authenticates before the contract holds; there is no anonymous fallback. The Anthropic-style connectors expose a two-call handshake:

- `authenticate` — opens the provider's OAuth/SSO flow and returns a URL (or device code) the user completes in a browser.
- `complete_authentication` — exchanges the completed flow for a session the MCP holds. After it returns, the connector's search and fetch tools answer.

The handshake runs once per environment at configure time. A connector that has not completed it answers Not-Available, not an error. Sources reached over a command-line tool (GitHub via `gh`) or a server-side API key skip the browser flow and authenticate from the env var below.

## Token / API-key env vars

All credentials travel in environment variables; never in committed source. Connectors that hold their own OAuth session after `complete_authentication` need no env var. The session lives in the MCP. The env vars below are for sources that authenticate from a token the user supplies.

| Source | Env var | Auth shape |
|---|---|---|
| GitHub | `GH_TOKEN` / `GITHUB_TOKEN` | PAT or `gh auth` session |
| Slack | held by the connector's OAuth session | workspace OAuth |
| Confluence/Notion | held by the connector's OAuth session | workspace OAuth |
| Linear/Jira | held by the connector's OAuth session | `authenticate` → `complete_authentication` |
| Google Drive | held by the connector's OAuth session | Google OAuth consent |
| Other connectors | per-provider key when one exists (else OAuth session) | see [`other-connectors.md`](other-connectors.md) |

When a connector does expose a server-side key (a self-hosted MCP, a provider PAT), name it `<SOURCE>_API_KEY` or the provider's documented variable and set it before probing.

## Never-commit posture

- No token, PAT, OAuth refresh token, or API key is ever written to a tracked file. They live in the environment or in the MCP's own session store.
- Rotate a leaked token at the provider and re-run the wiring to refresh the session and the smoke-tests.
- Smoke-test queries use known-public-internal terms; do not stage fetched internal content into committed artifacts.

## Expiry is a re-verification trigger

OAuth tokens and SSO sessions expire. A capability that authenticated last week can return a 401 today. Treat any of the following as a trigger to re-run [`../../configuring-internal/SKILL.md`](../../configuring-internal/SKILL.md):

- OAuth tokens and SSO sessions expire, including in Slack, Notion, Linear, Google Drive, and Microsoft 365.
- A PAT or API key rotates (`GH_TOKEN`, any service token).
- A smoke-test that previously passed now returns 401. Re-authenticate the source.

A practice run that hits 401 should surface drift to the wiring rather than retry blindly.
