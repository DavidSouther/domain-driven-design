Our code is full of `new Dollars(cents.value / 100)` and `new OrderId(draft.id.value)` — reaching into one domain type's inner primitive and rewrapping it as another, with the same conversion logic duplicated at many call sites and a few `as` casts thrown in.
I want each conversion defined explicitly and once.
Which pattern applies, and where is its guidance (which `references/patterns/<name>.md`)?
