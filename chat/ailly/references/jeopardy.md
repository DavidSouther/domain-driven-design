# Jeopardy! Search

Jeopardy! search is a query-expansion technique. Before searching for an answer, generate the *questions* the desired answer would answer, and search those instead of the original phrasing. The technique is named for the game show, in which contestants are given answers and must phrase the response as a question ([Wikipedia](https://en.wikipedia.org/wiki/Jeopardy!)).

## Why It Helps

A single phrasing of a query carries a single set of biases: it favors documents that use the same words. Search engines reward lexical overlap, so one phrasing returns the documents that share its vocabulary and quietly buries the ones that say the same thing with different words.

Expanding the query into several variants, before any search runs, surfaces sources the original phrasing would miss. The cost is a few extra search calls. The benefit is coverage. On a phone those extra calls are cheap and invisible to the reader; the better answer is not.

## Procedure

For each question:

1. **Restate it in 3-5 variants.** Cover synonyms, narrower phrasings with technology or version context, broader phrasings without specifics, question form versus keyword form, and adjacent terms that appear in the relevant documents.
2. **Run every variant.** Combining them into one search reintroduces the original bias.
3. **Union the results.** Deduplicate by URL before deciding which sources to fetch.
4. **Score and fetch.** Prefer canonical sources over aggregators; see the source-quality ladder in [research.md](research.md).

## Worked Example

Question: "how do I cancel an in-flight HTTP request in the browser".

- Synonym: "abort fetch request javascript"
- Narrow: "AbortController fetch signal example"
- Broad: "cancel async operation browser"
- Question form: "how to stop a fetch that is already running"
- Related terms: "AbortSignal timeout reason"

Five searches, one union, the canonical MDN page surfaces even though the original phrasing used none of its vocabulary.

## Relation to Falsification

Jeopardy! search widens coverage of a *single* claim by varying the phrasing. Falsification widens coverage by varying the *intent*, generating opposite claims that would disprove the original; see [falsify.md](falsify.md). Each falsifying hypothesis is itself a good candidate for Jeopardy! expansion. The two compose.
