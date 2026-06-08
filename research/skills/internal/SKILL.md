---
name: internal
description: Use when research requires searching internal organizational documents, communication channels, wikis, tickets, or any non-public source — Slack threads, Confluence pages, ADRs, Linear issues, Notion docs, Google Drive files, GitHub issues/PRs. Not for public internet or codebase searches.
---

# Internal Research

## Overview

Search configured MCP servers to answer questions from internal organizational knowledge. Different projects have different integrations; discover what is available before searching. Setup, MCP install, OAuth/SSO handshakes, and token rotation belong in [`research:configuring-internal`](../configuring-internal/SKILL.md); this skill consumes the contract that skill publishes.

## When to Use / When NOT to Use

**Use when:** the answer likely lives in Slack, a wiki, a ticket, an ADR, or another internal system.

**Do NOT use when:**
- Configuring internal sources, installing an MCP, completing OAuth/SSO, or rotating a token → use [`research:configuring-internal`](../configuring-internal/SKILL.md)
- Searching public documentation or the internet → use `research:public`
- Searching the local codebase → use `research:codebase`

## Query Expansion (Jeopardy! Search)

Before running any search, generate 3-5 variant queries using different phrasings, synonyms, and topic angles. Run all variants across every relevant MCP server.

Example — topic "deployment freeze policy":
1. "deployment freeze"
2. "release freeze policy"
3. "code freeze process"
4. "when can we deploy to production"
5. "deploy blocked announcement"

## Strategy

Capabilities are named in the contract published by [`research:configuring-internal`](../configuring-internal/SKILL.md); calling `ListMcpResourcesTool` reads the harness that skill installed.

1. **Discover** — call `ListMcpResourcesTool` to see which MCP servers are available.
2. **Expand queries** — produce 3-5 Jeopardy! variants before touching any server.
3. **Search broadly** — run every variant against every relevant server.
4. **Synthesize** — consolidate results, resolve conflicts, note gaps.

## Common MCP Server Types

| Server | Best for |
|--------|----------|
| Slack | Decisions, discussions, incident context, announcements |
| Confluence / Notion | Specs, ADRs, runbooks, wikis |
| Linear / Jira | Requirements, bug reports, feature history |
| GitHub | Issues, PRs, technical discussions |
| Google Drive | Documents, spreadsheets, presentations |

## Output Format

1. Create folder `docs/research/YYYY-MM-DD-A-<topic>/`
2. Write findings to `docs/research/YYYY-MM-DD-A-<topic>/internal.md`
3. Include a `**Sources**` section listing:
   - Which MCP servers were queried
   - Which documents, threads, or tickets were consulted
   - Links where available

## Common Mistakes

- **Searching without discovering** — always call `ListMcpResourcesTool` first; assume nothing about available integrations.
- **Single-query searches** — one phrasing misses results; always expand to 3-5 variants.
- **Using this skill for public content** — internal MCP servers do not index the public internet; use `research:public` instead.
- **Stopping at first result** — run all variants across all servers before synthesizing.
- **Re-teaching the wiring** — a "first, make sure you have installed the Slack MCP and completed OAuth" preface is wiring leakage. The wiring SKILL owns setup; this skill consumes the contract. If a preface is unavoidable, the contract is incomplete — widen it in [`research:configuring-internal`](../configuring-internal/SKILL.md).

## Composes With

- **`research:configuring-internal`** — the wiring partner. Publishes the contract this skill consumes; owns MCP install, OAuth/SSO handshakes, and token rotation.
- **`research:public`** — sibling practice skill for public-web sources.
- **`research:codebase`** — sibling practice skill for the local checkout.
- **`research/references/jeopardy.md`** — query expansion technique.
- **`research/references/citations.md`** — citation format the practice skill writes against.
