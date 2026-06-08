# Internal — out of scope

Sources deliberately excluded from the internal contract, with the reason each belongs elsewhere. The wiring SKILL ([`../../configuring-internal/SKILL.md`](../../configuring-internal/SKILL.md)) points here so the boundary between the internal stack and its siblings stays explicit.

## Out-of-scope sources

- **Public internet sources** (external library docs, language specs, community knowledge, anything on the public web) → `research:public`. The internal MCPs do not index the public internet; an authenticated transport adds nothing for an anonymous public page.
- **The local checkout** (symbol definitions, call sites, type structure at the checked-out commit) → `research:codebase`. The code on disk is read through LSP and Bash search, not an authenticated org connector.
- **Git history** (why code changed, who introduced a behavior, when a feature was added or reverted) → `research:archaeology`. History is read from the repository's commit graph, not from an internal document store.

## Why the boundary matters

Each of these has a transport and a re-verification cadence disjoint from the authenticated-MCP stack. Folding them into the internal contract would make the contract dishonest about what authentication buys and would duplicate routing the sibling skills already own.
