# Scite

Full-text search across 280M+ articles with **Smart Citations** classified as supporting, disputing, or mentioning. Uniquely valuable for "what evidence supports this claim?"

## What it provides

- **Citation-context classification** — Smart Citations: supporting, disputing, mentioning.
- **Full-text search** across the Scite corpus.
- **Institutional-link-resolver integration** for delivery; falls back to Article Galaxy.

## MCP option

`scite.ai/mcp` — hosted MCP endpoint by Research Solutions / Scite. Alternative: `scitedotai/scite-mcp-skill`.

Auth: **Scite subscription**. Obtain a subscription at `scite.ai` and configure the MCP per the repo or the hosted endpoint's instructions.

## HTTP fallback

The Scite API exists but is gated by the same subscription. Most individual-developer usage routes through the hosted MCP. For direct HTTP integration, consult Scite's API documentation behind the user's account.

## Query shapes

- *"Smart Citations for DOI 10.1145/3603287"* → returns lists of supporting, disputing, and mentioning citations with the citation context (the surrounding sentence).
- *"What evidence supports claim X"* — search the corpus; filter to supporting citations.
- *"Has this paper been contradicted"* — citation-context classification; check the `disputing` set.

## Licensing

- Smart Citation classifications are **Scite-proprietary** and require an active subscription.
- The citation contexts (surrounding sentences) are quoted from the citing paper; quote with citation under fair-use research norms.
- Full-text retrieval routes through the user's institutional link resolver or Article Galaxy; the licensing follows that delivery path.

## Failure modes

- **Subscription lapsed** — the *Citation-context classification* capability returns Not-Available. The wiring SKILL's re-verification trigger "Scite subscription lapses" applies.
- **DOI not indexed** — Scite indexes published articles; very recent or non-indexed preprints may be absent.
- **Article Galaxy fallback** — full-text delivery may route through Article Galaxy with its own access posture; treat as a separate delivery surface.
