# Aggregate

## Overview

An Aggregate is a cluster of associated domain objects treated as a single unit of change. One object in the cluster (the **Aggregate Root**) is the sole public entry point for all mutations. Every completed operation must transition the cluster from one valid state to another; no intermediate state is ever observable. One aggregate = one transaction. Do not span a transaction across aggregate boundaries.

## When to use

- A business operation touches more than one entity or value object and must appear atomic.
- Partial failure would leave data in a state where types are valid but violates business rules.
- A group of objects shares a consistency invariant that no external caller should be able to split across multiple calls.
- Load the specific object or concept, call one method, persist the result.

**When NOT to use:** independent entities with no shared invariants. Forcing unrelated objects into one aggregate inflates its boundary and makes consistency reasoning harder.

## Core pattern

An `Order` aggregate owns its `LineItem`s. The root validates and enforces the invariant: "a placed order must have at least one item and a positive total." entirely inside one method. Callers never tap internals directly.

```
// Caller: load one aggregate, call one method, persist the result
const order = Order.create("ord-1");
order.place(cartItems);          // throws if any invariant is violated
await orderRepository.save(order);
// Cross-aggregate side effects go via domain events after commit, not direct calls
```

For complete examples, see [`aggregate/typescript.md`](aggregate/typescript.md), [`aggregate/python.md`](aggregate/python.md), and [`aggregate/rust.md`](aggregate/rust.md).

## Quick reference

| Concept | Role |
|---|---|
| **Aggregate Root** | Sole public entry point (`Order`); only it has a repository |
| **Boundary** | Everything that must change together in one transaction (`Order` + `LineItem`s) |
| **Reference other aggregates** | By ID only; never hold an object reference to another aggregate root |
| **Cross-aggregate side effects** | Domain events, handled outside the aggregate after the transaction commits |
| **Invariant** | Rule enforced atomically inside the root (`place` validates before mutating) |

## Common mistakes

**Aggregate too large:** including every related object (customer, address history, payment records) creates a god object. Keep the boundary to what must change *together* in one operation. Small aggregates are almost always better.

**Exposing internal entities:** returning a raw `LineItem[]` reference lets callers mutate internals without going through the root.

**Cross-aggregate mutation:** calling `inventoryAggregate.decrement(...)` from inside `Order.place` spans a consistency boundary and couples two aggregates in one transaction. Use domain events to trigger that update after the order transaction commits.

**Multiple aggregate calls per request:** calling `order.addLine(...)` then `order.confirm(...)` as separate top-level operations re-introduces the partial-failure window. The aggregate pattern exists to eliminate this window. Design one operation per business intent.

## Composes with

- **the domain-objects pattern (`references/patterns/domain-objects.md`)** — the root is an entity; internal cluster members are typically value objects or child entities.
- **the type-states pattern (`references/patterns/type-states.md`)** — model the aggregate's legal lifecycle (for example, `Order<Pending>` → `Order<Placed>`) as distinct types so invalid transitions are compile errors.
- **the repository pattern (`references/patterns/repository.md`)** — load and save the aggregate root through a repository; child entities are never fetched directly.
- **the unit-of-work pattern (`references/patterns/unit-of-work.md`)** — wrap the aggregate operation in a Unit of Work for atomic, durable persistence with guaranteed rollback.
