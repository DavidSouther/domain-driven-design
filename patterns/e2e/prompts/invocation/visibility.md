Our `Order` exposes its internals publicly: callers do `order.status = "cancelled"`,
`order.lines.push(line)`, and `order.total = 0` directly, so the invariants are not
enforced. Lock it down: make the internal fields private, expose reads as
immutable/read-only views (never the live collection), turn every state change into
a named method that checks invariants (not field assignment or a setter), and route
construction so there is no path to a half-built `Order`. Show the `Order` and a
call site that cancels an order and adds a line.
