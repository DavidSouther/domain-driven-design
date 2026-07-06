# Search augmentation

The one optional provider for the public stack. Built-in `WebSearch` is always available and answers the majority of public-research queries. You configure an augmentation provider only when you want **higher-recall or domain-scoped** search. This provider can be a hosted search-API connector or an index you run over a specific corpus.

Inherits the shared rules in [`etiquette.md`](etiquette.md): contact User-Agent, per-host rate limits and backoff-on-429, allowed/blocked-domain policy, and provider-key handling in env.

## What it provides

- **Augmented search** — a provider-ranked result list (title, URL, snippet), keyed off the same query the built-in search takes, optionally scoped to a provider or domain. Returns hits ranked by the provider's index rather than the built-in ranker.

This is the single conditional capability in the public contract. The two unconditional capabilities (`WebSearch`, `WebFetch`) are built in and described in the contract directly. They have no provider reference because there is nothing to configure.

## Probe order

**Primary: the configured search-augmentation MCP.** Probe the MCP this project runs for augmented search. This can be a hosted search-API connector or a domain-scoped index you maintain.

- Transport: standard MCP wire protocol.
- Auth: a provider API key when the provider requires one; set its env var (see below). Some local indexes need no key.

**Fallback: built-in `WebSearch`.** When no augmentation MCP is reachable, fall back to the always-available built-in search. The wiring returns a typed Not-Available result for the *augmented search* capability and the practice skill degrades to `WebSearch` for the same query. No error, no gap in coverage.

**Not-Available** when you don't configure a provider:

```
{ result: "not-available", capability: "augmented-search", reason: "no augmentation provider configured; falls back to built-in WebSearch" }
```

## Key handling

- Hold any provider API key in its own environment variable; never in committed source. Name it after the provider so the wiring smoke-test can find it.
- Rotation of the provider key is a re-verification trigger in [`../../configuring-public/SKILL.md`](../../configuring-public/SKILL.md).

## Install shape

When the provider ships as a marketplace plugin, install it in the same shape the sibling skills use, for parity:

```
/plugin marketplace add <marketplace>
/plugin install <connector>@<marketplace>
```

Set the provider's API key env var if it has one, then smoke-test.

## Smoke-test

- Run an augmented search for a known term. Confirm the provider returns provider-ranked hits in the contract shape (title, URL, snippet).
- If the probe finds no provider, mark *augmented search* Not-Available and confirm the built-in `WebSearch` fallback answers the same term.

## Failure modes

- **No provider configured** — expected on most checkouts; mark Not-Available and use built-in `WebSearch`. This is the default state, not a failure.
- **Provider key missing or rotated** — the MCP is present but unauthenticated. Set or refresh the env var; this is a re-verification trigger.
- **Provider MCP upgraded** — the tool surface or response shape may have shifted; re-run the smoke-test to confirm the contract still holds.
- **Provider response shape drift** — an augmented search returned a shape the practice skill did not expect; widen the contract in [`../../configuring-public/SKILL.md`](../../configuring-public/SKILL.md) rather than patching the practice body.
