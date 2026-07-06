# Visibility

## Overview

A domain object's invariants are only as strong as the surface it exposes. If a field is public, every caller is now a co-author of the rules that govern it. Visibility controls collapse that surface to a small, named, intentional API: private internals, read-only views, explicit mutation methods, and construction through a builder or factory. The object becomes the sole keeper of its rules.

## When to use

- A struct or class exposes fields that participate in invariants (totals, status, balances, lifecycle flags).
- A getter returns the underlying `List`, `Map`, or `Set` that backs internal state, allowing the caller to mutate it.
- State changes happen via field assignment from outside the object (`order.status = "cancelled"`).
- Construction takes a long parameter list of optional fields, allowing partially initialized instances.

**When NOT to use:** plain transport DTOs at a serialization boundary that carry no invariants. For those, prefer the parse-dont-validate pattern (`references/patterns/parse-dont-validate.md`) to convert the DTO into a domain object as soon as it crosses inward. Exposing fields is the point at that boundary.

## Core pattern

Four rules, applied together:

1. **Private internals.** Every field is private. Domain objects forbid public fields. Inheritance does not relax this; subclasses use the public mutation API like everyone else.
2. **Reference-only getters.** Reads return immutable views. You can return scalars and value objects directly because nothing can mutate them. Return collections as read-only wrappers, frozen copies, or iterators. Return internal entities by reference only when the caller cannot use that reference to bypass an invariant.
3. **Explicit mutation methods.** Every state change is a named domain operation: `order.cancel()`, `batch.allocate(line)`, `account.deposit(amount)`. The method checks invariants inside. Forbid setters when they would let a caller establish an illegal state.
4. **Builder-oriented creation.** The constructor is private. Construction goes through a builder, factory function, or `from`/`parse` method that enforces required fields and cross-field validation before producing the object. There is no path to a partially initialized instance.

**Before** — every rule of the Order is enforceable only by convention.
```
order.status = "cancelled";        // no check that the order is cancellable
order.lines.push(line);            // bypasses total recomputation
order.total = 0;                   // contradicts order.lines
```

**After** — the Order owns its rules.
```
order.cancel();                    // throws if not in a cancellable state
order.addLine(line);               // recomputes total atomically
order.lines();                     // returns a read-only view
order.total();                     // derived; cannot be set
```

For complete examples, see [`visibility/typescript.md`](visibility/typescript.md), [`visibility/python.md`](visibility/python.md), and [`visibility/rust.md`](visibility/rust.md).

## Quick reference

| Concern | Apply |
|---|---|
| Field exposed publicly | Make it private; expose a getter only if needed |
| Getter returns mutable collection | Return a read-only wrapper, frozen copy, or iterator |
| State change via assignment | Replace with a named method that checks invariants |
| Long-parameter constructor | Make constructor private; expose a `builder` or `from` factory |
| Computed value cached as a field | Expose a getter; do not let callers set it |

## Common mistakes

- **Public getter, private setter.** The getter returns the live `List`; callers call `.add` on it and bypass every rule. Wrap or copy on the way out.
- **`get` plus `set` instead of a domain method.** A pair of accessors lets a caller read the status, branch, and assign a new one, losing the invariants that would have lived inside `cancel()` or `ship()`. Name the operation; remove the setter.
- **Constructor that accepts every field.** Even with private fields, a public constructor that takes the full state lets callers fabricate any combination, including illegal ones. Make the constructor private and route through a builder or factory.
- **Returning a defensive copy that callers think is live.** If the domain expects subsequent reads to reflect the caller's changes, a copy is misleading. Either commit to immutability or expose a mutation method that records the change on the object itself.
- **Trusting friend access in the same module.** "It's only used internally" is a runtime claim, not a compile-time one. Future code added to the same module reaches in. Encode the rule in visibility, not in habit.

## Composes with

- **the builder pattern (`references/patterns/builder.md`)** — the natural partner for rule four. The builder is the only public path to construction; the product's constructor stays private.
- **the domain-objects pattern (`references/patterns/domain-objects.md`)** — entities and value objects are the things that need this discipline. Value objects take it further by being immutable end-to-end, so reads are inherently safe.
- **the aggregate pattern (`references/patterns/aggregate.md`)** — the aggregate root is the only object with a public mutation surface for the cluster. Internal entities are reachable only through methods on the root, which is the strongest app of these rules.
- **the parse-dont-validate pattern (`references/patterns/parse-dont-validate.md`)** — at a boundary, parse the input into a constructed domain object whose internals are already private. Do not pass the raw record inward.
