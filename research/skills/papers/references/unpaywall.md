# Unpaywall

DOI→open-access PDF resolver. The canonical "is there a legal free PDF for this paper" service.

## What it provides

- **DOI→OA-PDF**: best legal open-access location for a DOI, with license and OA-status metadata.

Example payload (`/v2/{doi}?email=...`):

```
{ "doi": "10.1145/3603287", "is_oa": true, "oa_status": "hybrid",
  "best_oa_location": { "url": "...", "url_for_pdf": "...", "license": "cc-by-4.0",
                         "host_type": "repository", "version": "publishedVersion" },
  "oa_locations": [...] }
```

## MCP option

None first-party. The aggregators `xingyulu23/Academix`, `benedict2310/Scientific-Papers-MCP`, and `tfscharff/doi-mcp` include Unpaywall in their fan-out.

## HTTP fallback

- Base URL: `https://api.unpaywall.org/v2/{doi}?email=you@example.org`
- Auth: **email parameter required**. No key. See [`etiquette.md`](etiquette.md).
- Output: JSON.
- Rate limits: not strictly published; the email parameter functions as a per-caller identifier for fair use.

## Query shapes

- *"Open-access PDF for DOI 10.1145/3603287"* → `/v2/10.1145/3603287?email=...`
- *"Is this paper open-access at all"* → check `is_oa`.
- *"Best OA repository copy when the publisher gates the version"* → check `oa_locations` and prefer `host_type: "repository"` when `best_oa_location` points at a gated publisher.

## Licensing

Per-location. Unpaywall reports the license string for each OA location; `cc-by-4.0`, `cc-by-nc-4.0`, etc. The repository or publisher hosts the PDF at the OA location; quote per its license, cite with the DOI.

## Failure modes

- **No email parameter**: request rejected. Set `UNPAYWALL_EMAIL`.
- **`is_oa: false`**: no legal free copy known. The practice skill returns a typed Not-Available for the *DOI→OA-PDF* capability.
- **Stale OA location**: repositories occasionally take a copy down. Re-resolve through Crossref or Semantic Scholar for an alternative location.
