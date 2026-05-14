# Jeopardy! Search

Jeopardy! search is a query-expansion technique. Before searching for an answer, generate the *questions* the desired answer would answer. Search those questions instead of the original query. The technique is named for the game show, in which contestants are given answers and must phrase the response as a question [1].

## Why It Helps

A single phrasing of a query carries a single set of biases: it favors documents that use the same words. Search engines and embedding stores reward lexical overlap and confirming hits, so one phrasing returns the documents that share its vocabulary and quietly buries the ones that say the same thing with different words.

Expanding the query into several variants, before any search runs, surfaces sources that the original phrasing would have missed. The cost is a few extra search calls. The benefit is coverage.

## Procedure

For each research question:

1. **Restate the question in 3-5 variants.** Cover synonyms, narrower phrasings with technology or version context, broader phrasings without specifics, question form versus keyword form, and adjacent terms that appear in relevant documents.
2. **Run every variant.** Combining variants into one search reintroduces the original bias.
3. **Union the result sets.** Deduplicate by URL or document ID before deciding which sources to fetch.
4. **Score and fetch.** Prefer canonical sources over aggregators; see [research.md](research.md) for the source-quality ladder.

For a worked example of these variant types applied to a single query, see the "Query Expansion" section of [research.md](research.md).

## Background: Index-Side Variant

The technique also has an index-side application, used by retrieval systems backed by embedding stores. Two strategies exist:

- **HyDE-style enrichment** generates synthetic documents that resemble the source document, intending to expand the document's footprint in the source embedding space. The synthetic documents are likely to confabulate, inflating false-positive matches.
- **Jeopardy! enrichment** instead generates the *queries* that the source document would answer, and stores those queries in a parallel embedding space. Search-time similarity runs against the query space, which transparently returns the original document.

The Jeopardy! variant trades document-side confabulation for query-side coverage, and amortizes the LLM cost at ingestion rather than at request time.

A further refinement seeds the query-generation prompt with examples from prior personas and their accepted results: *"The Executive Persona used query ABC and chose document XYZ. Generate ten queries the Executive Persona would ask that document VBN would answer."* The persona conditioning narrows the synthetic queries toward language the real audience uses.

## Limits

Chunking is a precondition for any of the above. A document is split into chunks of roughly 512 tokens with 64-token overlap, ideally respecting structural boundaries (headings, prose versus code blocks). Document length is the O(n) for every operation downstream [citation needed]. None of the techniques compensate for poor chunking.

Query expansion does not fix poor source quality. If the canonical source uses no words in common with any plausible query, no number of variants will find it; that is an indexing problem, not a search problem.

## Relation to Falsification

Jeopardy! search widens coverage of a *single* claim by varying the phrasing. Falsification widens coverage by varying the *intent*, generating opposite claims that would disprove the original; see [falsify.md](falsify.md). Each falsifying hypothesis is itself a good candidate for Jeopardy! query expansion. The two techniques compose.

## Citations

- [1] Wikipedia. "Jeopardy!" 2026-05-01. [Online]. Available: https://en.wikipedia.org/wiki/Jeopardy!
- [2] ddd_skill. "chat/ailly/references/jeopardy.md" #UNCOMMITTED
