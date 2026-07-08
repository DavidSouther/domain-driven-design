# Wiley scholar gateway

Search across 3 million articles in 1,300 Wiley journals.
Returns **snippets with DOI links**, not full PDFs.

## What it provides

- **Wiley journal search**: semantic-snippet hits.
- **DOI link-out** to the article on `onlinelibrary.wiley.com`.
- Coverage explicitly **excludes figures, charts, and multimedia**.

## MCP option (primary)

**`wiley-scholar-gateway@life-sciences`**: Anthropic-curated marketplace plugin.
Install:

```
/plugin marketplace add anthropics/life-sciences
/plugin install wiley-scholar-gateway@life-sciences
```

Auth: oauth 2.0 via Wiley CONNECT SSO.
Complete the SSO handshake after install.

Access requires:

- **Claude Pro account**.
- **Wiley institutional subscription** **or** a **limited free-trial registration** for active researchers, valid through June 30, 2026.

The wiring checklist marks the *Wiley journal search* capability available only after install **and** SSO handshake completes.

## HTTP fallback

- The Scholar Gateway MCP wire endpoint is `https://connector.scholargateway.ai/mcp`.
  Direct HTTP integration is not the supported individual-developer path; use the MCP via the marketplace plugin.

## Query shapes

- *"Semantic search across Wiley journals for `transformer attention`"* is the primary capability.
- *"DOI link-out for the most relevant Wiley article on a topic"*: read the `doi` field of the snippet result.
- Snippets are short; for the full body, **link the user to the DOI** and let them open the article in their authenticated session.

## Licensing

Snippets are **for display within the user's session**.
Full text remains gated by the user's Wiley subscription.
Cite-and-link with the DOI; do not stage Wiley passages into public artifacts.

## Failure modes

- **SSO not configured**: the *Wiley journal search* capability returns Not-Available.
  The re-verification trigger "Wiley SSO token expired" applies.
- **Trial expired**: For free-trial users past June 30, 2026, access lapses unless the user configures an institutional subscription.
- **Excluded media**: Figures and charts are not returned by Scholar Gateway; the practice skill cannot retrieve them.
  Link to the DOI for the user's authenticated session.

## Out-of-scope (related)

**Wiley TDM API** at `api.wiley.com` delivers full-text PDFs under a contractual TDM license.
Distinct from Scholar Gateway and **out of scope** for this stack.
See [`out-of-scope.md`](out-of-scope.md).
