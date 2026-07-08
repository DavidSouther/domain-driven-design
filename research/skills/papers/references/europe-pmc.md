# Europe pmc

EMBL-EBI's biomedical and life-sciences index: 33M+ publications including 10.2M full-text and 6.5M open-access.

## What it provides

- **Biomedical and life-sciences search** with full-text coverage broader than PubMed.
- **Per-paper metadata** including authors, abstracts, full-text-link availability.
- **Citation graph** within the Europe PMC corpus.

## Mcp option

None first-party for Europe PMC as a single source.
Aggregators (`xingyulu23/Academix`, `openags/paper-search-mcp`) may include it; check the active server's source list.

## Http fallback

- Base URL: `https://www.ebi.ac.uk/europepmc/webservices/rest/search`
- Endpoints: `/search?query=...&format=json`, `/article/PMC/{pmcid}/fullTextXML`
- Auth: none.
- Output: JSON or XML.

## Query shapes

- *"Biomedical full-text articles on CRISPR delivery, 2024"* → `/search?query=CRISPR+delivery+AND+SRC:PMC+AND+OPEN_ACCESS:Y&format=json`
- *"Full text of an open-access PMC article"* → `/article/PMC/PMC1234567/fullTextXML`
- *"Citation graph for a known PMID"* → `/article/MED/{pmid}/citations`

## Licensing

- **Open-access full text** retrieved through Europe PMC carries the license declared by the depositor (typically CC-BY-*).
- **Abstracts and metadata** are freely usable.
- **Gated full text** is metadata-only; Europe PMC does not deliver the body for non-open-access articles.

## Failure modes

- **Full text gated**: when `inEPMC: false` or `isOpenAccess: false`, the body is not retrievable.
  Return a typed Not-Available and cite the article via DOI.
- **XML parsing**: Europe PMC's full-text XML is JATS; verbose.
  Prefer a JATS parser over hand-rolled regular expressions.
- **Result paginated**: page via `pageSize` and `cursorMark`; large biomedical topics easily exceed default page size.
