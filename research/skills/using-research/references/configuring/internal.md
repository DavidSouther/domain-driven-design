---
name: configuring-internal
description: Use when bootstrapping or revising the internal authenticated sources for this project — installing an MCP server per source, completing the OAuth/SSO handshake, setting token and API-key env vars, recording which sources are reachable, and smoke-testing each source's search and fetch against the published contract. Applies once per environment when bootstrapping or revising the internal sources, never inside a research session.
---

# Configuring Internal

## Overview

This skill installs the harness that `research:internal` consumes. An internal research stack is a set of named per-source **capabilities** (search and fetch against Slack, Confluence/Notion, Linear/Jira, GitHub, Google Drive) reached through **authenticated transports** — almost always an MCP server behind an OAuth or SSO handshake. Every internal source is authenticated; there is no anonymous fallback the way papers has a polite HTTP pool. The wiring probes each MCP, completes the auth handshake, records the active transport and the token env var, and confirms each source answers a minimal query. Re-running the wiring on a configured system confirms the contract or surfaces drift — most often an expired token; it never destroys state.

The practice skill's current "always call `ListMcpResourcesTool` first; assume nothing" instruction becomes a consequence of this contract: discovery at query time reads the harness this skill installed. The practice skill `research:internal` cites the contract and dispatches capabilities; it never re-teaches the configuration.

## Contract

After `research:configuring-internal` has run, callers of `research:internal` may assume each configured source exposes the two capabilities below, keyed by whether that source's MCP authenticated successfully:

| Capability | Inputs | Returns | Conditional |
|---|---|---|---|
| Slack search | query, optional channel/user/date filters | message and thread hits with permalink | available when configured |
| Slack fetch | channel + ts, or permalink | thread or canvas contents | available when configured |
| Confluence/Notion search | query | page hits with space/workspace and URL | available when configured |
| Confluence/Notion fetch | page id or URL | page body (and comments where exposed) | available when configured |
| Linear/Jira search | query, optional team/status filter | issue hits with id, state, assignee | available when configured |
| Linear/Jira fetch | issue id | issue body, comments, linked documents | available when configured |
| GitHub issue/PR search | query, optional repo/label filter | issue and PR hits with number and URL | available when configured |
| GitHub issue/PR fetch | repo + number | body, comments, diff threads where exposed | available when configured |
| Google Drive search | query, optional type filter | file hits with id, type, owner | available when configured |
| Google Drive fetch | file id | file content or extracted text | available when configured |

Every capability is **conditional**: each is available only when its source's MCP is installed and authenticated. There are no unconditional internal capabilities — an internal research stack with nothing configured is legal and returns Not-Available for everything. Practice routes on the Not-Available signal: a source that did not authenticate is skipped, not retried.

Capability count: **10** (five sources × search + fetch), all conditional.

Conditional capabilities return the typed Not-Available result reused verbatim from the templates:

```
{ result: "not-available", capability: "<name>", reason: "<why>" }
```

The practice skill treats Not-Available as a routing signal, not as an error.

**Auth is applied:** every source authenticates before the contract holds. OAuth tokens and API keys are held in env vars, never committed. SSO sessions are completed at configure time and their expiry is a re-verification trigger. The shared rules live in [`internal/references/auth.md`](../internal/references/auth.md); each per-source reference cites that file for the rules it inherits. (`auth.md` is the internal-stack analog of the books/papers `etiquette.md` — for an all-authenticated stack the shared file is about credentials and handshakes rather than per-host politeness.)

## When to Use

- Standing up a fresh checkout for the first time and `research:internal` has no sources to call.
- Adding a new internal source, installing a new MCP server, rotating a token, or completing an OAuth/SSO handshake for Slack, Notion, Linear, Google Drive, or another org connector.
- Re-verifying after a re-verification trigger (see below) fires.

**When NOT to use:** inside a research session at a per-query call site. The per-query partner is `research:internal`; source configuration, MCP install, and auth handshakes happen here, not there. For non-internal questions use `research:public`, `research:codebase`, or `research:domain`.

## Configure Checklist

Walk the checklist top-to-bottom on a fresh environment. Each item probes the source's MCP first, completes the auth handshake, sets the token env var, and smoke-tests search-then-fetch. Smoke-test means a minimal authenticated query that confirms the source returns the contract shape.

Default sources (most orgs have these):

- [ ] **Slack** — probe the configured Slack MCP for this org; the Anthropic Slack connector exposes search and read tools (`slack_search_*`, `slack_read_*`). Complete the workspace OAuth install. Token/scope handling per [`internal/references/slack.md`](../internal/references/slack.md). Smoke-test: search a known term, fetch one matching thread. If OAuth is not completed, mark *Slack search* and *Slack fetch* Not-Available.
- [ ] **Confluence / Notion** — probe the configured wiki MCP; the Notion connector exposes `notion-search` / `notion-fetch`. Complete the workspace OAuth. Per [`internal/references/wiki.md`](../internal/references/wiki.md). Smoke-test: search a known spec page, fetch it. If neither wiki MCP authenticates, mark the wiki capabilities Not-Available.
- [ ] **GitHub** — probe the configured GitHub MCP; else CLI fallback via `gh` with `GH_TOKEN` / `GITHUB_TOKEN` set. Per [`internal/references/github.md`](../internal/references/github.md). Smoke-test: issue search in a known repo, fetch one issue. If no token is set, mark the GitHub capabilities Not-Available.

Priority sources (common in product orgs):

- [ ] **Linear / Jira** — probe the configured tracker MCP; the Linear connector exposes `list_issues` / `get_issue` / `search_documentation`, and completes OAuth via its `authenticate` / `complete_authentication` pair. Per [`internal/references/tracker.md`](../internal/references/tracker.md). Smoke-test: issue search by team, fetch one issue. If OAuth is not completed, mark the tracker capabilities Not-Available.
- [ ] **Google Drive** — probe the configured Drive MCP; the Google Drive connector exposes `search_files` / `read_file_content`. Complete the Google OAuth consent. Per [`internal/references/google-drive.md`](../internal/references/google-drive.md). Smoke-test: search a known doc title, read its content. If OAuth is not completed, mark the Drive capabilities Not-Available.

Opt-in sources (configure when the user supplies access):

- [ ] **Other authenticated connectors** — any additional org MCP the user runs (Gmail, Google Calendar, Salesforce, Datadog, incident.io, Figma, Microsoft 365, and so on). For each: probe the configured MCP for that source; complete its OAuth/SSO handshake; set its token env var; add one search + fetch row to the contract; smoke-test. If the source has no MCP and no HTTP/CLI fallback, mark its capability Not-Available. Documented per [`internal/references/other-connectors.md`](../internal/references/other-connectors.md).

**MCP install and OAuth.** The install shape mirrors `configuring-papers`: `/plugin marketplace add <marketplace>` then `/plugin install <connector>`, then complete the OAuth/SSO handshake when the connector prompts (the connectors above expose an `authenticate` → `complete_authentication` pair). Tokens land in env vars named per source in [`internal/references/auth.md`](../internal/references/auth.md); never commit them.

**Out-of-scope sources** are documented in [`internal/references/out-of-scope.md`](../internal/references/out-of-scope.md) with the reason each is excluded (public sources belong to `research:public`; the local checkout belongs to `research:codebase`; git history belongs to `research:archaeology`).

## Re-Verification Triggers

Re-run the wiring when any of the following happens. Re-running confirms the contract still holds; on a configured system it does not destroy state.

- An MCP connector upgrades and its tool surface or response shape may have shifted.
- **An OAuth token or SSO session expires** — the most frequent internal trigger. Slack, Notion, Linear, Google Drive, and Microsoft 365 sessions all expire; renewing them re-runs the wiring.
- An API key or PAT rotates (GitHub `GH_TOKEN`, any service token).
- A new internal source is added that should sit in the contract, or a user joins a new workspace.
- A practice run reports drift: a source returned a shape the practice skill did not expect, or a smoke-test that previously passed now fails (commonly a 401, which means re-authenticate).

## Composes With

- **`research:internal`** — the per-query partner. Wiring publishes the contract; practice consumes it.
- **`research:configuring-codebase`** and **`research:configuring-public`** — sibling wiring for the codebase and public stacks. Disjoint at the source level; shared cadence convention.
- **`research:configuring-books`** and **`research:configuring-papers`** — the other two sibling wiring skills in the family.
- **`research/references/citations.md`** — internal documents cite as `[Internal]` per the loose IEEE style the practice skill writes against.
- **`research/references/jeopardy.md`** — the 3-5 variant query expansion the practice skill runs against every configured source.
