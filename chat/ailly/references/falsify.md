# Falsification Reference

A single negative example disproves a claim. This is the asymmetry Karl Popper named in *The Logic of Scientific Discovery*: no number of confirming observations can prove a universal claim, but one well-found counterexample can refute it ([Popper, via Wikipedia](https://en.wikipedia.org/wiki/The_Logic_of_Scientific_Discovery)). Confirmation is suggestive. Refutation is decisive.

Most research instinctively gathers evidence *for* a claim. That instinct is biased. The same query, framed positively, surfaces confirming hits and skips past contradictions because the contradictions do not match the search terms. Falsification flips the search: instead of "where is this true?", ask "where would this be false, and is that there?"

## When to Use

Reach for falsification when:

- A user says "are you sure?", "double-check that", or otherwise signals doubt about a stated conclusion.
- A claim is load-bearing for a decision, especially one that is hard to reverse.
- The evidence so far is all confirming and none of it would distinguish the claim from its near-neighbors.
- Stakes are high enough that a missed counterexample would be expensive: a purchase, a public statement, a medical or legal or financial conclusion.
- The claim is universal in form ("always", "never", "every", "the only"). Universals are cheapest to refute.

Falsification is overkill for casual lookups and for questions where the answer is purely observational. Use it when the cost of being wrong exceeds the cost of one extra round of search.

## Procedure

1. **Restate the claim as a universal.** Convert "this charger works with my phone" into "this charger supports every phone in my model line." Universals expose a clear failure mode: any single unsupported model refutes the claim.
2. **Negate the claim into 2 to 4 falsifiable hypotheses.** Each describes a concrete situation in which the original would be false. Vague negations ("maybe it is wrong somewhere") cannot be searched. Concrete ones ("there is a model in the line that needs a different wattage") can.
3. **Search each negation.** Run a separate search for each hypothesis, expanded with [jeopardy.md](jeopardy.md). Search *for the negation*, not for the original claim. On a phone, run them one after another in the session. When subagents are available, run one per hypothesis in parallel; the technique is identical, only the concurrency changes.
4. **Collect counterexamples, not absences.** A search that finds a counterexample returns the specific page, quote, or connector item. A search that finds nothing returns where it looked, so the result is auditable.
5. **Update the claim.** If any search returns a real counterexample, the original universal cannot be entirely true. Narrow it ("supports every model *except the 2019*"), qualify it ("usually, but check the wattage on older units"), or retract it.

## Interpreting Results

Evidence of the negation refutes the original. Absence of evidence for the negation does not confirm the original; it only fails to refute it. Popper's asymmetry runs in one direction.

When the searches return nothing, the honest report is "I looked for the negation in A, B, and C and found none", not "the claim is true". Naming where you looked tells the reader where you did *not* look.

## Limits

Falsification works best on claims that name observable conditions in findable places. It works poorly when:

- The claim is non-falsifiable in principle ("this design is elegant"). Reframe, or accept that falsification does not apply.
- The negation is rare and the search space is vast. A single buried counterexample may not surface in a reasonable search budget. State the budget honestly.
- The claim depends on behavior not visible in any source. Search cannot refute a claim about what happens only at runtime, or only in private data you cannot reach.

## Relation to Jeopardy! Search

[jeopardy.md](jeopardy.md) widens the *query* for a given claim by generating variants of the same intent. Falsification widens the *intent* by generating opposite claims. Both expand coverage, in different directions, and they compose: each falsifying hypothesis is itself a good candidate for query expansion.
