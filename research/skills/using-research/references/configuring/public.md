# Configuring public

> Setup reference for the public-web sources.
> Loaded on demand from `research:using-research` (see its "Configuring Sources" section) when bootstrapping or revising the public stack; not a standalone always-on skill.
> Applies once per environment, never inside a research session.

## Overview

This skill installs the harness that `research:public` consumes.
The core transport (`WebSearch` and `WebFetch`) comes built in: it needs no install, no key, and no handshake.

The harness here is **policy, not plumbing**.
It includes a contact User-Agent, per-host rate limits, an allowed/blocked-domain list, and an optional **augmented-search** provider for higher-recall or domain-scoped search.
The wiring records that policy and confirms the built-in tools.
It smoke-tests them plus any augmentation.
Re-running confirms the policy and the optional provider; it never destroys state.

The harness this skill installs is the **public capability contract** below.
The practice skill `research:public` cites the contract and dispatches capabilities; it never re-teaches the configuration.

## Contract

After you configure the public sources (this `public.md` reference), callers of `research:public` may assume:

| Capability | Inputs | Returns | Conditional |
|---|---|---|---|
| Web search | query | ranked result list (title, URL, snippet) | no |
| Web fetch | URL | page content, subject to the allowed/blocked-domain policy | no |
| Augmented search | query, optional provider/domain scope | provider-ranked hits. This may be a search-API MCP or a domain-scoped index. | available when configured |

Three capabilities are available: two unconditional (built-in `WebSearch` / `WebFetch`) and one conditional for augmented search.

The conditional capability returns a typed Not-Available result when you don't configure a provider:

```
{ result: "not-available", capability: "augmented-search", reason: "<no augmentation provider configured; falls back to built-in WebSearch>" }
```

The practice skill treats Not-Available as a routing signal, not as an error: with no augmentation configured it uses built-in `WebSearch`, which is always available.

**Apply etiquette as follows:** requests carry a `User-Agent` containing a contact email.
Systems respect per-host rate limits.
The implementation honors the blocked-domain list by refusing fetches to blocked hosts.
When set, the allowed-domain list scopes search.
The shared rules live in [`public/references/etiquette.md`](../../../public/references/etiquette.md); the per-provider reference cites that file for the rules it inherits.

## When to use

- Standing up a fresh checkout for the first time and confirming `research:public` has its transport and policy in place.
- Changing the contact User-Agent, adjusting per-host rate limits, or adding a domain to the allowed or blocked list.
- Adding or rotating a search-augmentation provider.
- Re-verifying after a re-verification trigger (see below) fires.

**When NOT to use:** inside a research session at a per-query call site.
Per-query web search and fetch belong in `research:public`.
For non-public questions use `research:books`, `research:papers`, `research:internal`, or `research:domain`.

## Configure checklist

Walk top-to-bottom on a fresh environment.
The default items are **policy, not installs**; the opt-in item is the only entry that probes an MCP.
Smoke-test means a minimal query that confirms the contract holds.

Default (policy, no install):

- [ ] **Built-in WebSearch / WebFetch**: confirm both tools are available in the environment (they come built-in, no install).
      Set `RESEARCH_USER_AGENT` (or the environment's equivalent) to a string containing a contact email per [`public/references/etiquette.md`](../../../public/references/etiquette.md).
      Smoke-test: a web search for a known term, then a fetch of one result.
- [ ] **Domain policy**: record the allowed-domain list (empty means unrestricted) and the blocked-domain list in [`public/references/etiquette.md`](../../../public/references/etiquette.md).
      Smoke-test: fetching from a blocked host fails, and fetching from an allowed host succeeds.
- [ ] **Rate limits**: record per-host request spacing and backoff-on-429 per the etiquette file.
      Smoke-test: confirm backoff behavior on a host that signals 429, or document the limit if you do not encounter it.

Priority (none).
The public stack has no priority-tier installs.
The default tier is complete on its own.
We list this item for parity with the sibling skills.

Opt-in (configure when the user supplies access):

- [ ] **Search-augmentation provider**: probe the configured search-augmentation MCP for this project, which may be a hosted search-API connector or a domain-scoped index the user runs.
      Otherwise fall back to built-in `WebSearch`.
      Set the provider's API key env var if it has one.
      Per [`public/references/augmented-search.md`](../../../public/references/augmented-search.md).
      Smoke-test: an augmented search for a known term returns provider-ranked hits.
      If you don't configure a provider, mark *augmented search* Not-Available.

**Marketplace plugins are not required** for the default stack.
The augmentation provider, if present, installs via the `/plugin marketplace add … / /plugin install …` commands for parity with the sibling skills.

**The public stack is genuinely thin.**
Two of its three capabilities ship with the environment and need no configuration.
This `public.md` reference exists to serve three purposes.
First, you apply etiquette so the project is a polite web citizen.
Second, you record allowed/blocked domains as project policy.
Third, you wire an optional augmentation provider.
There is no transport to install for the core path.
This is the structural opposite of the internal setup reference (`internal.md`), where nothing works until an MCP authenticates.

## Re-verification triggers

Re-run the wiring when any of the following happens.
Re-running confirms the contract still holds; on a configured system it does not destroy state.

- You change the contact `User-Agent` or contact email.
- You change the allowed/blocked-domain policy by adding a domain to either list.
- Per-host rate limits change, or a host begins signaling 429 where it did not before.
- You add an augmentation provider, its key rotates, or its MCP upgrades and may have shifted its response shape.
- A practice run reports drift: the system allowed a fetch to a blocked host, or an augmented search returned an unexpected shape.

## Composes with

- **`research:public`**: the per-query partner.
  Wiring publishes the contract and the etiquette/domain policy; practice consumes them.
- **the internal setup reference (`internal.md`)** and **the codebase setup reference (`codebase.md`)**: sibling wiring for the other two stacks.
  Disjoint at the source level; shared cadence convention.
- **the books setup reference (`books.md`)** and **the papers setup reference (`papers.md`)**: the established sibling wiring references in the family.
- **`research/references/citations.md`**: the IEEE `[Online]` citation form the practice skill writes against.
- **`research/references/jeopardy.md`**: the 3-5 variant query expansion the practice skill runs before searching.
- **`research/references/falsify.md`**: the falsification pass the practice skill runs on load-bearing claims (its Source Quality section already cites this).
- **`research/references/thread-digest.md`**: the three-pass digest the practice skill routes a fetched conversational thread (a forum, Reddit/HN, or mailing-list thread) through before treating it as scoped.
