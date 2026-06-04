Our `Order` exposes public fields, so callers do `order.status = "cancelled"` and
`order.lines.push(line)` and bypass every rule, and a getter hands back the live
list so they can mutate it. I want the object to be the sole keeper of its
invariants — private internals, read-only views, named mutation methods. Which
`patterns:*` skill applies?
