# Falsification Reference

A single negative example disproves a claim. This is the asymmetry Karl Popper named in *The Logic of Scientific Discovery*: no number of confirming observations can prove a universal claim, but one well-found counterexample can refute it [1]. Confirmation is suggestive. Refutation is decisive.

Most research instinctively gathers evidence *for* a claim. That instinct is biased. The same query, framed positively, will surface confirming hits and skip past contradictions because the contradictions do not match the search terms. Falsification flips the search: instead of "where is this true?", ask "where would this be false, and is that there?"

## When to Use

Reach for falsification when:

- A user says "are you sure?", "double-check that", or otherwise signals doubt about a stated conclusion.
- A claim is load-bearing for a downstream decision, especially one that is hard to reverse.
- The evidence so far is all confirming and none of it would distinguish the claim from its near-neighbors.
- Stakes are high enough that a missed counterexample would be expensive: production behavior, security boundaries, compliance, public statements.
- The claim is universal in form ("always", "never", "every", "no caller does X"). Universals are cheapest to refute.

Falsification is overkill for casual lookups and for questions where the answer is purely observational. Use it when the cost of being wrong exceeds the cost of one extra round of search.

## Procedure

1. **Restate the claim as a universal.** Convert "the cache invalidates correctly" into "every write path invalidates the cache." Universals expose a clear failure mode: any single write path that does not invalidate refutes the claim.
2. **Negate the claim into 3 to 5 falsifiable hypotheses.** Each hypothesis should describe a concrete situation in which the original claim would be false. Vague negations ("maybe it is wrong somewhere") cannot be searched. Concrete negations ("there is a write path that bypasses the invalidation helper") can.
3. **Dispatch a subagent per hypothesis.** Each subagent searches specifically for evidence of its assigned negation, not for the original claim. Run them in parallel. Combining negations into one search reintroduces the original confirmation bias.
4. **Collect counterexamples, not absences.** A subagent that finds a counterexample returns the specific file, line, document, or quote. A subagent that finds nothing returns the queries it ran and where it looked, so the search is auditable.
5. **Update the claim.** If any subagent returns a real counterexample, the original universal cannot be entirely true. Either narrow the claim ("every write path *in module X* invalidates the cache"), qualify it ("usually, except for the legacy batch path"), or retract it.

## Interpreting Results

Evidence of the negation refutes the original. Absence of evidence for the negation does not confirm the original; it only fails to refute it [1]. Popper's asymmetry runs in exactly one direction.

When all subagents return nothing, the right report is "no counterexamples found after searching A, B, and C", not "the claim is true". The list of places searched is itself the most important output, because it tells the next reader where the search did *not* look.

## Limits

Falsification works best on claims that name observable conditions in observable places. It works poorly when:

- The claim is non-falsifiable in principle ("this code is elegant"). Reframe before searching, or accept that falsification does not apply.
- The search space is unbounded and the negation is rare. A single hidden counterexample buried in a generated file may not surface in any reasonable search budget. State the budget honestly in the report.
- The claim depends on runtime behavior not visible in source. Static search cannot refute a claim about what happens under load; that requires running the system.

## Relation to Jeopardy! Search

Jeopardy! search (`jeopardy.md`) widens the *query* for a given claim by generating variants of the same intent. Falsification widens the *intent* by generating opposite claims. Both expand coverage, in different directions, and they compose: each falsifying hypothesis is itself a good candidate for Jeopardy! query expansion.

## Citations

- [1] Popper, K. "The Logic of Scientific Discovery." 1959. [Online]. Available: https://en.wikipedia.org/wiki/The_Logic_of_Scientific_Discovery
- [2] ddd_skill. "research/references/falsify.md" #UNCOMMITTED
