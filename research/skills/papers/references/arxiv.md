# ArXiv

The canonical preprint archive: physics, mathematics, computer science, quantitative biology, statistics, finance. Strong for any pre-publication or open-licensed version of a research paper.

## What it provides

- **Preprint search** by keyword, title, author, category, or ArXiv ID.
- **Per-paper metadata** including authors, title, abstract, categories, version history.
- **Full PDF** and source TeX for every preprint.

Example payload (Atom):

```
<entry>
  <id>http://arxiv.org/abs/2401.01234v2</id>
  <title>...</title>
  <author>...</author>
  <category term="cs.SE"/>
  <link href=".../pdf/2401.01234v2" rel="related" type="application/pdf"/>
</entry>
```

## MCP options

- `blazickjp/arxiv-mcp-server` — search, download to local markdown, analysis prompts. Most-referenced.
- `shoumikdc/arXiv-mcp` — latest-paper polling.
- `win4r/arxiv-search-MCP-Server` and `Tejas242/arxiv-mcp` with Docker image `mcp/arxiv-mcp-server`.

All wrap the public ArXiv API; no auth required.

## HTTP fallback

- Base URL: `http://export.arxiv.org/api/query`
- Auth: none.
- Output: Atom/XML.
- Pagination: `start`/`max_results` with a hard cap of 2,000 items per slice, 30,000 max results overall.
- **Etiquette: one request per three seconds, single connection** (see [`etiquette.md`](etiquette.md)).
- OAI-PMH at `https://oaipmh.arxiv.org/oai` is preferred for bulk metadata harvesting.

## Query shapes

- *"Latest ArXiv preprints on type-driven design in `cs.SE`"* → `?search_query=cat:cs.SE+AND+all:type-driven&sortBy=submittedDate`
- *"All versions of `2401.01234`"* → `?id_list=2401.01234`
- *"Survey papers on transformer architectures"* → `?search_query=ti:survey+AND+all:transformer&sortBy=relevance`

## Licensing

Most ArXiv preprints carry a non-exclusive ArXiv license; many additionally carry CC licenses chosen by the author (`metadata` includes the license URL). Quote with citation; the canonical citation form is `arXiv:2401.01234 [cs.SE]`.

## Failure modes

- **HTTP 503 / rate-limit** — exceeded the three-second spacing. Back off; serialize requests to a single connection.
- **Atom XML parse** — Atom is verbose; prefer the MCP for structured output if the request volume is high.
- **Version mismatch** — `?id_list=2401.01234` returns the latest version; pin with `2401.01234v2` for reproducibility.
