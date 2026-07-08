We convert between domain types by hand and the logic is duplicated at call sites: `new Dollars(cents.value / 100)` here, `new OrderId(draft.id.value)` there — each one reaches into a type's inner primitive and rewraps it.
Define these conversions explicitly and exactly once: a total conversion from `Cents` to `Dollars`, and the canonical place a `DraftOrder` becomes a `PlacedOrder`.
Then show a call site that uses the conversions without reaching into any type's internals.
Total and partial (fallible) conversions must not share a name.
