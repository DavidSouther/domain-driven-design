# Internal: out of scope

Sources deliberately excluded from the internal contract, with the reason each belongs elsewhere. The wiring configuration ([`../../configuring-internal/SKILL.md`](../../configuring-internal/SKILL.md)) points here so the boundary between the internal stack and its siblings stays explicit.

## Out-of-scope sources

- **Public internet sources** include external library docs, language specs, community knowledge, and anything on the public web. Route these to `research:public`. The internal MCPs do not index the public internet; an authenticated transport adds nothing for an anonymous public page.
- **The local checkout** includes symbol definitions, call sites, and type structure at the checked-out commit. Route this to `research:codebase`. The code on disk is read through LSP and Bash search, not an authenticated org connector.
- **Git history** covers why code changed, who introduced a behavior, or when developers added or reverted features. Route this to `research:archaeology`. History is read from the repository's commit graph, not from an internal document store.

## Why the boundary matters

Each of these has a transport and a re-verification cadence disjoint from the authenticated-MCP stack. Folding them into the internal contract would make the contract dishonest about what authentication buys and would duplicate routing the sibling skills already own.
