A raw `unknown` value arrives off an HTTP request body that *should* describe an order — `{ "id": "...", "customerEmail": "...", "totalCents": ... }`.
Write a `parseOrder(raw: unknown): Order` that returns a fully-typed domain `Order` or fails with a specific, actionable error per failure mode (missing field, bad email, non-positive total).
Downstream code that takes an `Order` must not re-check any field the parser already proved.
Show the `Order` type, `parseOrder`, and one downstream function that consumes an `Order`.
