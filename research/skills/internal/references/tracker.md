# Linear / Jira (tracker)

The issue tracker. First stop for requirements, bug reports, and the history of why a feature was scoped the way it was.

## What it provides

- **Linear/Jira search** — issue hits with id, state, and assignee, filterable by team and status.
- **Linear/Jira fetch** — the issue body, its comments, and linked documents, given an issue id.

## MCP / connector

Two tracker shapes share this contract row:

- **Linear** — the Anthropic Linear connector exposes `list_issues`, `get_issue`, and `search_documentation`. It completes OAuth via its `authenticate` / `complete_authentication` pair.
- **Jira** — probe the configured Jira MCP for this org; tool names vary by which server is installed, so discover the surface rather than assuming a slug.

If OAuth is not completed, the tracker capabilities are Not-Available.

## Auth

Linear authenticates through the `authenticate` → `complete_authentication` handshake described in [`auth.md`](auth.md); the connector holds the session afterward. Jira authenticates per its configured MCP (OAuth or a token env var, depending on the server). No env var for the OAuth path.

## Contract mapping

- *Linear/Jira search* → `list_issues` (with team/status filter) or `search_documentation` (Linear), or the Jira MCP's issue-search tool. Returns issue hits with id, state, assignee.
- *Linear/Jira fetch* → `get_issue` by id (Linear), or the Jira MCP's issue-read tool. Returns issue body, comments, and linked documents.

## Smoke-test

Search issues by a known team, confirm hits carry id/state/assignee, then fetch one issue by id and confirm the body and comments return. A 401 means re-authenticate (an expiry trigger, see [`auth.md`](auth.md)).
