# Configuring Internal

> Setup reference for the internal authenticated sources.
> Loaded on demand from `research:using-research` (see its "Configuring Sources" section) when bootstrapping or revising the internal stack; not a standalone always-on skill.
> Applies once per environment, never inside a research session.

## Overview

This skill installs the harness that `research:internal` consumes.
An internal research stack is a set of named per-source **capabilities** (search and fetch against Slack, Confluence/Notion, Linear/Jira, GitHub, Google Drive) reached through **authenticated transports**.
These transports are almost always MCP servers behind an OAuth or SSO handshake.
Every internal source authenticates.
Unlike papers, which has a public HTTP cache, this stack provides no anonymous fallback.
The wiring probes each MCP, completes the auth handshake, records the active transport and the token env var, and confirms each source answers a minimal query.

The practice skill's current "always call `ListMcpResourcesTool` first; assume nothing" instruction becomes a consequence of this contract.
Discovery at query time reads the harness this skill installed.
The practice skill `research:internal` cites the contract and dispatches capabilities.
It never re-teaches the configuration.

## Contract

Once you configure the internal sources per this reference, callers of `research:internal` may assume each configured source exposes the two capabilities below.
Availability depends on whether that source's MCP authenticated successfully:

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

Every capability is **conditional**: each is available only when its source's MCP installs and authenticates.
There are no unconditional internal capabilities.
An internal research stack with nothing configured is legal and returns Not-Available for everything.
Practice routes on the Not-Available signal: when a source does not authenticate, practice skips it rather than retrying.

Capability count: **10** (five sources × search + fetch), all conditional.

Conditional capabilities return the typed Not-Available result reused verbatim from the templates:

```
{ result: "not-available", capability: "<name>", reason: "<why>" }
```

The practice skill treats Not-Available as a routing signal, not as an error.

**Auth applies:** every source authenticates before the contract holds.
Store OAuth tokens and API keys in env vars, never committing them.
Complete SSO sessions at configure time.
Their expiry triggers re-verification.
The shared rules live in [`internal/references/auth.md`](../../../internal/references/auth.md); each per-source reference cites that file for the rules it inherits.
This `auth.md` file parallels the books/papers `etiquette.md`.
For an all-authenticated stack, it addresses credentials and handshakes rather than per-host politeness.

## When to use

- Standing up a fresh checkout for the first time and `research:internal` has no sources to call.
- Adding a new internal source, installing a new MCP server, rotating a token, or completing an OAuth/SSO handshake for Slack, Notion, Linear, Google Drive, or another org connector.
- Re-verifying after a re-verification trigger (see below) fires.

**When NOT to use:** inside a research session at a per-query call site.
The per-query partner is `research:internal`; source configuration, MCP install, and auth handshakes happen here, not there.
For non-internal questions use `research:public`, `research:codebase`, or `research:domain`.

## Configure checklist

Walk the checklist top-to-bottom on a fresh environment.
Each item probes the source's MCP first, completes the auth handshake, sets the token env var, and smoke-tests search-then-fetch.
Smoke-test means a minimal authenticated query that confirms the source returns the contract shape.

Default sources (most orgs have these):

- [ ] **Slack**.
      Probe the configured Slack MCP for this org.
      The Anthropic Slack connector exposes search and read tools (`slack_search_*`, `slack_read_*`).
      Complete the workspace OAuth install.
      Token/scope handling per [`internal/references/slack.md`](../../../internal/references/slack.md).
      Smoke-test: search a known term, fetch one matching thread.
      If OAuth is not completed, mark *Slack search* and *Slack fetch* Not-Available.
- [ ] **Confluence / Notion**.
      Probe the configured wiki MCP.
      The Notion connector exposes `notion-search` / `notion-fetch`.
      Complete the workspace OAuth.
      Per [`internal/references/wiki.md`](../../../internal/references/wiki.md).
      Smoke-test: search a known spec page, fetch it.
      If neither wiki MCP authenticates, mark the wiki capabilities Not-Available.
- [ ] **GitHub**.
      Probe the configured GitHub MCP, or fall back to the command-line tool via `gh` with `GH_TOKEN` / `GITHUB_TOKEN`.
      Per [`internal/references/github.md`](../../../internal/references/github.md).
      Smoke-test: issue search in a known repo, fetch one issue.
      If you have no token, mark the GitHub capabilities Not-Available.

Priority sources (common in product orgs):

- [ ] **Linear / Jira**.
      Probe the configured tracker MCP.
      The Linear connector exposes `list_issues` / `get_issue` / `search_documentation` and completes OAuth via its `authenticate` / `complete_authentication` pair.
      Per [`internal/references/tracker.md`](../../../internal/references/tracker.md).
      Smoke-test: issue search by team, fetch one issue.
      If OAuth is not completed, mark the tracker capabilities Not-Available.
- [ ] **Google Drive**.
      Probe the configured Drive MCP.
      The Google Drive connector exposes `search_files` / `read_file_content`.
      Complete the Google OAuth consent.
      Per [`internal/references/google-drive.md`](../../../internal/references/google-drive.md).
      Smoke-test: search a known doc title, read its content.
      If OAuth is not completed, mark the Drive capabilities Not-Available.

Opt-in sources (configure when the user supplies access):

- [ ] **Other authenticated connectors**.
      Probe any additional org MCP the user runs.
      Examples include Gmail, Google Calendar, Salesforce, Datadog, incident.io, Figma, and Microsoft 365.
      For each: probe the configured MCP for that source; complete its OAuth/SSO handshake; set its token env var; add one search + fetch row to the contract; smoke-test.
      If the source has no MCP and no HTTP/command-line tool fallback, mark its capability Not-Available.
      Documented per [`internal/references/other-connectors.md`](../../../internal/references/other-connectors.md).

**MCP install and OAuth.**
The install shape mirrors the papers setup reference (`papers.md`).
Run `/plugin marketplace add <marketplace>` then `/plugin install <connector>`.
Complete the OAuth/SSO handshake when the connector prompts.
The listed connectors expose an `authenticate`-`complete_authentication` pair.
Tokens land in env vars named per source in [`internal/references/auth.md`](../../../internal/references/auth.md); never commit them.

[`internal/references/out-of-scope.md`](../../../internal/references/out-of-scope.md) documents out-of-scope sources and explains why this reference excludes each source.
Public sources belong to `research:public`.
The local checkout belongs to `research:codebase`.
Git history belongs to `research:archaeology`.

## Re-verification triggers

Re-run the wiring when any of the following happens.
Re-running confirms the contract still holds; on a configured system it does not destroy state.

- An MCP connector upgrades and its tool surface or response shape may have shifted.
- **An OAuth token or SSO session expires**: the most frequent internal trigger.
  Slack, Notion, Linear, Google Drive, and Microsoft 365 sessions all expire; renewing them re-runs the wiring.
- An API key or PAT rotates (GitHub `GH_TOKEN`, any service token).
- You add a new internal source that should sit in the contract, or a user joins a new workspace.
- A practice run reports drift: a source returned a shape the practice skill did not expect, or a smoke-test that previously passed now fails (commonly a 401, which means re-authenticate).

## Composes with

- **`research:internal`**: the per-query partner.
  Wiring publishes the contract; practice consumes it.
- **the codebase setup reference (`codebase.md`)** and **the public setup reference (`public.md`)**: sibling wiring for the codebase and public stacks.
  Disjoint at the source level; shared cadence convention.
- **the books setup reference (`books.md`)** and **the papers setup reference (`papers.md`)**: the other two sibling wiring references in the family.
- **`research/references/citations.md`**: internal documents cite as `[Internal]` per the loose IEEE style the practice skill writes against.
- **`research/references/jeopardy.md`**: the 3-5 variant query expansion the practice skill runs against every configured source.
- **`research/references/thread-digest.md`**: the three-pass digest the practice skill routes a fetched conversational thread (Slack, Linear/Jira, GitHub issue/PR comments, Confluence/Notion discussion) through before treating it as scoped.
