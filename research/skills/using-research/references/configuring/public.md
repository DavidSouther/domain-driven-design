# Configuring Public

> Setup reference for the public-web sources. Loaded on demand from
> `research:using-research` (see its "Configuring Sources" section) when bootstrapping or
> revising the public stack; not a standalone always-on skill. Applies once per
> environment, never inside a research session.

## Overview

This skill installs the harness that `research:public` consumes. The core transport — `WebSearch` and `WebFetch` — is **built in**: it needs no install, no key, and no handshake. The harness here is **policy, not plumbing**: a contact User-Agent, per-host rate limits, an allowed/blocked-domain list, and an optional **augmented-search** provider for higher-recall or domain-scoped search. The wiring records that policy, confirms the built-in tools, and smoke-tests them plus any augmentation. Re-running confirms the policy and the optional provider; it never destroys state.

The harness this skill installs is the **public capability contract** below. The practice skill `research:public` cites the contract and dispatches capabilities; it never re-teaches the configuration.

## Contract

After the public sources have been configured (this `public.md` reference), callers of `research:public` may assume:

| Capability | Inputs | Returns | Conditional |
|---|---|---|---|
| Web search | query | ranked result list (title, URL, snippet) | no |
| Web fetch | URL | page content, subject to the allowed/blocked-domain policy | no |
| Augmented search | query, optional provider/domain scope | provider-ranked hits (e.g., a search-API MCP or a domain-scoped index) | available when configured |

Capability count: **3** — two unconditional (built-in `WebSearch` / `WebFetch`), one conditional (augmented search).

The conditional capability returns a typed Not-Available result when no provider is configured:

```
{ result: "not-available", capability: "augmented-search", reason: "<no augmentation provider configured; falls back to built-in WebSearch>" }
```

The practice skill treats Not-Available as a routing signal, not as an error: with no augmentation configured it uses built-in `WebSearch`, which is always available.

**Etiquette is applied:** requests carry a `User-Agent` containing a contact email, per-host rate limits are respected, the blocked-domain list is honored (fetches to blocked hosts are refused), and the allowed-domain list (when set) scopes search. The shared rules live in [`public/references/etiquette.md`](../../../public/references/etiquette.md); the per-provider reference cites that file for the rules it inherits.

## When to Use

- Standing up a fresh checkout for the first time and confirming `research:public` has its transport and policy in place.
- Changing the contact User-Agent, adjusting per-host rate limits, or adding a domain to the allowed or blocked list.
- Adding or rotating a search-augmentation provider.
- Re-verifying after a re-verification trigger (see below) fires.

**When NOT to use:** inside a research session at a per-query call site. Per-query web search and fetch belong in `research:public`. For non-public questions use `research:books`, `research:papers`, `research:internal`, or `research:domain`.

## Configure Checklist

Walk top-to-bottom on a fresh environment. The default items are **policy, not installs**; the opt-in item is the only thing that probes an MCP. Smoke-test means a minimal query that confirms the contract holds.

Default (policy — no install):

- [ ] **Built-in WebSearch / WebFetch** — confirm both tools are available in the environment (they are built in; no install). Set `RESEARCH_USER_AGENT` (or the environment's equivalent) to a string containing a contact email per [`public/references/etiquette.md`](../../../public/references/etiquette.md). Smoke-test: a web search for a known term, then a fetch of one result.
- [ ] **Domain policy** — record the allowed-domain list (empty means unrestricted) and the blocked-domain list in [`public/references/etiquette.md`](../../../public/references/etiquette.md). Smoke-test: a fetch to a blocked host is refused; a fetch to an allowed host succeeds.
- [ ] **Rate limits** — record per-host request spacing and backoff-on-429 per the etiquette file. Smoke-test: confirm backoff behavior on a host that signals 429, or document the limit if none is hit.

Priority (none). The public stack has no priority-tier installs — the default tier is complete on its own. This item is called out for parity with the sibling skills.

Opt-in (configure when the user supplies access):

- [ ] **Search-augmentation provider** — probe the configured search-augmentation MCP for this project (a hosted search-API connector, or a domain-scoped index the user runs); else fall back to built-in `WebSearch`. Set the provider's API key env var if it has one. Per [`public/references/augmented-search.md`](../../../public/references/augmented-search.md). Smoke-test: an augmented search for a known term returns provider-ranked hits. If no provider is configured, mark *augmented search* Not-Available.

**No marketplace plugins required** for the default stack; the augmentation provider, if any, installs in the `/plugin marketplace add … / /plugin install …` shape for parity with the sibling skills.

**The public stack is genuinely thin.** Two of its three capabilities ship with the environment and need no configuration at all. This `public.md` reference exists for three reasons only: (1) to apply etiquette so the project is a polite web citizen, (2) to record allowed/blocked domains as project policy, and (3) to wire an optional augmentation provider. There is no transport to install for the core path. This is the structural opposite of the internal setup reference (`internal.md`), where nothing works until an MCP authenticates.

## Re-Verification Triggers

Re-run the wiring when any of the following happens. Re-running confirms the contract still holds; on a configured system it does not destroy state.

- The contact `User-Agent` or contact email changes.
- The allowed/blocked-domain policy changes (a domain is added to either list).
- Per-host rate limits change, or a host begins signaling 429 where it did not before.
- An augmentation provider is added, its key rotates, or its MCP upgrades and may have shifted its response shape.
- A practice run reports drift: a fetch that should be blocked succeeded, or an augmented search returned a shape the practice skill did not expect.

## Composes With

- **`research:public`** — the per-query partner. Wiring publishes the contract and the etiquette/domain policy; practice consumes them.
- **the internal setup reference (`internal.md`)** and **the codebase setup reference (`codebase.md`)** — sibling wiring for the other two stacks. Disjoint at the source level; shared cadence convention.
- **the books setup reference (`books.md`)** and **the papers setup reference (`papers.md`)** — the established sibling wiring references in the family.
- **`research/references/citations.md`** — the IEEE `[Online]` citation form the practice skill writes against.
- **`research/references/jeopardy.md`** — the 3-5 variant query expansion the practice skill runs before searching.
- **`research/references/falsify.md`** — the falsification pass the practice skill runs on load-bearing claims (its Source Quality section already cites this).
