# Other authenticated connectors

The pattern for adding any additional authenticated org MCP beyond the five named contract sources. Configure when the user supplies access. Each follows the same shape, so a new connector adds one search + fetch row to the contract without a new template.

## Which connectors

Any authenticated org source the user runs, for example: Gmail, Google Calendar, Salesforce, Datadog, incident.io, Figma, Microsoft 365. Each is an opt-in source — none is assumed present.

## The add-a-connector pattern

For each additional connector, follow the five steps below. This is the same shape the five named sources follow; it is written out once here so the opt-in row stays a pattern rather than a list.

1. **Probe** — probe the configured MCP for that source. Do not assume a package slug; discover the tool surface with `ListMcpResourcesTool`. Where the source has no MCP, look for an HTTP/CLI fallback; where neither exists, mark its capability Not-Available.
2. **Auth** — complete the connector's OAuth/SSO handshake. The Anthropic connectors expose the `authenticate` → `complete_authentication` pair described in [`auth.md`](auth.md).
3. **Env var** — set the connector's token or API-key env var if it authenticates from one (name it `<SOURCE>_API_KEY` or the provider's documented variable); OAuth-session connectors need none. Never commit it; see [`auth.md`](auth.md).
4. **Contract row** — add one search + fetch row to the published contract, naming the source and the two capabilities it exposes, marked conditional ("available when configured").
5. **Smoke-test** — run a minimal authenticated search, confirm the contract shape, then fetch one matching item. A 401 means re-authenticate (an expiry trigger, see [`auth.md`](auth.md)).

## Notes

- A connector that exposes only search, or only fetch, gets only that half of the row; mark the missing half Not-Available.
- Sources whose MCP tool names are not known are referenced as "probe the configured MCP for <source>" rather than a fabricated slug, matching the rest of the internal stack.
