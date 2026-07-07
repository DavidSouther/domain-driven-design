---
name: internal
description: Search internal sources like Slack, wikis, tickets, and ADRs. Do not use for public internet or code searches.
---

# Internal research

## Overview

Search configured MCP servers to find answers in internal organizational knowledge. Different projects use different integrations; discover what is available before searching. Setup and token rotation belong in [the internal setup reference](../using-research/references/configuring/internal.md); this skill uses the contract that skill defines.

## When to use / When not to use

**Use when:** the answer likely lives in Slack, a wiki, a ticket, an ADR, or another internal system.

**Do NOT use when:**
- Configuring internal sources, installing an MCP, completing OAuth/SSO, or rotating a token → use [the internal setup reference](../using-research/references/configuring/internal.md)
- Searching public documentation or the internet → use `research:public`
- Searching the local codebase → use `research:codebase`

## Query expansion (jeopardy search)

Before running any search, generate 3-5 variant queries by using different phrasings, synonyms, and topic angles. Run all variants across every relevant MCP server.

Example: topic "deployment freeze policy":
1. "deployment freeze"
2. "release freeze policy"
3. "code freeze process"
4. "when can we deploy to production"
5. "deploy blocked announcement"

## Strategy

The contract published by [the internal setup reference](../using-research/references/configuring/internal.md) names capabilities; calling `ListMcpResourcesTool` reads the harness that skill installed.

1. **Discover**: call `ListMcpResourcesTool` to see which MCP servers are available.
2. **Expand queries**: produce 3-5 Jeopardy variants before touching any server.
3. **Search broadly**: run every variant against every relevant server.
4. **Synthesize**: consolidate results, resolve conflicts, note gaps.

## Common mcp server types

| Server | Best for |
|--------|----------|
| Slack | Decisions, discussions, incident context, announcements |
| Confluence / Notion | Specs, ADRs, runbooks, wikis |
| Linear / Jira | Requirements, bug reports, feature history |
| GitHub | Issues, PRs, technical discussions |
| Google Drive | Documents, spreadsheets, presentations |

## Output format

1. Create folder `.ailly/research/YYYY-MM-DD-A-<topic>/`, unless the caller provides a task-scoped research folder such as `.ailly/developer/<session-slug>/research/`
2. Write findings to `internal.md` inside that folder
3. Include a `**Sources**` section listing:
   - Which MCP servers you queried
   - Which documents, threads, or tickets you consulted
   - Links where available

## Common mistakes

- **Searching without discovering**: always call `ListMcpResourcesTool` first; assume nothing about available integrations.
- **Single-query searches**: one phrasing misses results; always expand to 3-5 variants.
- **Using this skill for public content**: internal MCP servers do not index the public internet; use `research:public` instead.
- **Stopping at first result**: run all variants across all servers before synthesizing.
- **Re-teaching the wiring**: a "first, make sure you have installed the Slack MCP and completed OAuth" preface is wiring leakage. The wiring skill owns setup; this skill consumes the contract. If a preface is unavoidable, the contract is incomplete. Widen it in [the internal setup reference](../using-research/references/configuring/internal.md).

## Composes with

- **the internal setup reference**: the wiring partner. Located at `research:using-research` (`references/configuring/internal.md`). Publishes the contract this skill consumes; owns MCP install, OAuth/SSO handshakes, and token rotation.
- **`research:public`**: sibling practice skill for public-web sources.
- **`research:codebase`**: sibling practice skill for the local checkout.
- **`research/references/jeopardy.md`**: query expansion technique.
- **`research/references/citations.md`**: citation format the practice skill writes against.
