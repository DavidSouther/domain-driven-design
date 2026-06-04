Model an `Order` that owns a non-empty list of `LineItem`s. The `Order` must be
the only public entry point: callers may not construct, mutate, or read
`LineItem`s except through `Order` methods, and no method may hand back a mutable
reference to the internal list. Adding a line item must keep the order's total in
sync. Show the `Order` type and one example call site that adds a line and saves
the change.
