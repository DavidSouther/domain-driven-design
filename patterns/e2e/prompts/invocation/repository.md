Define an `OrderRepository` interface in the domain layer with `get(orderId: OrderId): Promise<Order | undefined>` and `add(order: Order): Promise<void>`.
Provide two concrete implementations: `InMemoryOrderRepository` for tests and `SqlOrderRepository` for production.
A domain service `placeOrder(cmd: PlaceOrder, repo: OrderRepository): Promise<OrderId>` must depend only on the abstract interface — no SQL types, query builders, ORM sessions, or connection objects may leak across the domain boundary.
Show the interface, both implementations, and the `placeOrder` signature.
