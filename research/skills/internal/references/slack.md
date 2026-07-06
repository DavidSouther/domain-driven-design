# Slack

Org communication channel. First stop for decisions, incident context, announcements, and the discussion that never made it into a doc.

## What it provides

- **Slack search** — message and thread hits with permalink, filterable by channel, user, and date.
- **Slack fetch** — the full contents of a thread or a canvas, given a channel + ts or a permalink.

## MCP/connector

The Anthropic Slack connector. Search tools are `slack_search_*`, including `slack_search_public`, `slack_search_public_and_private`, `slack_search_channels`, and `slack_search_users`. Read tools are `slack_read_*`, including `slack_read_thread`, `slack_read_channel`, `slack_read_canvas`, `slack_read_user_profile`, and `slack_read_file`. If this connector is not the one installed, probe the configured Slack MCP for this org.

## Auth

Workspace OAuth install. The connector holds the session after the install completes; see [`auth.md`](auth.md). No env var is set for the OAuth path. The session lives in the connector. If OAuth is not completed, *Slack search* and *Slack fetch* return Not-Available.

## Contract mapping

- *Slack search* → `slack_search_public` / `slack_search_public_and_private` with the query and optional channel/user/date filters. Returns message and thread hits with permalink.
- *Slack fetch* → `slack_read_thread` (channel + ts) or `slack_read_canvas`; a permalink resolves to the channel + ts. Returns thread or canvas contents.

## Smoke-test

Search a known term (a recent project name or channel topic), confirm hits carry permalinks, then fetch one matching thread by its channel + ts. A 401 means re-authenticate (an expiry trigger, see [`auth.md`](auth.md)).
