# Confluence / notion (wiki)

The org knowledge base.
First stop for specs, ADRs, runbooks, and any long-form document that outlives a Slack thread.

## What it provides

- **Confluence/Notion search**: page hits with their space (Confluence) or workspace (Notion) and a URL.
- **Confluence/Notion fetch**: the page body, and comments where the connector exposes them, given a page id or URL.

## MCP / Connector

Two wiki shapes share this contract row:

- **Notion**: the Anthropic Notion connector exposes `notion-search` and `notion-fetch` (plus `notion-get-comments` when you want comments).
- **Confluence**: probe the configured Confluence MCP for this org; tool names vary by which server you install, so discover the surface rather than assuming a slug.

If neither wiki MCP authenticates, the wiki capabilities are Not-Available.

## Auth

Workspace OAuth for both.
The connector holds the session after the OAuth completes; see [`auth.md`](auth.md).
No env var for the OAuth path.

## Contract mapping

- *Confluence/Notion search* → `notion-search` (Notion) or the Confluence MCP's search tool with the query.
  Returns page hits with space/workspace and URL.
- *Confluence/Notion fetch* → `notion-fetch` (Notion) by page id or URL, or the Confluence MCP's page-read tool.
  Returns the page body and comments where exposed.

## Smoke-test

Search for a known spec or ADR title, confirm the hit carries its space/workspace and URL, then fetch that page by id and confirm the body returns.
A 401 means re-authenticate (an expiry trigger, see [`auth.md`](auth.md)).
