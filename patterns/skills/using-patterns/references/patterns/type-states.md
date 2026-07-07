# State types, variants, and protocols

## Overview

Represent each valid state as a separate type. Instead of one object with optional fields and runtime checks, use one type per state. The compiler rejects code that tries to use data or methods unavailable in the current state.

## When to use

- A domain object passes through lifecycle phases where different fields are valid in each phase (for example, `Draft`, `Published`, `Archived`).
- A state machine has transitions; the compiler enforces them at compile time, not runtime.
- Invalid combinations of fields exist but are only caught today by runtime guards or null checks.
- An object owns resources that you must release or act on only once (for example, a network connection or file).

**When not to use:** purely dynamic data where the set of variants remains open-ended at compile time. Use a runtime discriminant and validation instead.

## Core pattern

Three sub-patterns, each making a different class of illegal state unrepresentable:

**Discriminated union:** each valid state combination is its own type. The compiler rejects any value whose fields belong to different states. For example, `{ status: "peace", ruler: "dictator" }` is not assignable to `Rome`.

**Type state:** the state parameter `S` exists only at compile time (a _phantom type_); the runtime stores no value for it. Transition functions consume the old state and return a new one, so the caller cannot reuse a stale reference.

**Protocols / interfaces:** define narrow interfaces per capability so callers only access what their context permits. A function that accepts `Readable` cannot accidentally call `write`.

For complete examples, see [`type-states/typescript.md`](type-states/typescript.md), [`type-states/python.md`](type-states/python.md), and [`type-states/rust.md`](type-states/rust.md).

## Quick reference

| Pattern | Use scenario | Benefit |
|---|---|---|
| Discriminated union | Multiple valid states, each with different fields | Compiler rejects impossible field combinations |
| Type state | Object moves through ordered lifecycle phases | Invalid transitions are compile errors, not runtime panics |
| Protocol / interface | Limit which operations a caller can perform | Scoped capability; no accidental misuse across contexts |

## Common mistakes

**Using enums + runtime checks instead of types:** a single `status: Status` field plus `if (status === "war")` guards means the compiler cannot verify consistency. The Roman bug passes every type check; only tests (or production) catch it.

**Shared mutable state across states:** storing all possible fields in one object and leaving some `undefined` recreates the flat-type problem. Each state type should carry only the fields relevant to that state.

**Reusing a resource after transition:** if a transition function takes the connection by reference instead of by value, the caller keeps a reference to the pre-transition object. The caller can then still call methods on the wrong state. Transition functions must consume (take ownership of) the old resource instead. In TypeScript, reassign, and never alias: `conn = open(conn)`.

## Composes with

- **the aggregate pattern (`references/patterns/aggregate.md`):** type states model the legal lifecycle of an aggregate (for example, `Order<Pending>` → `Order<Placed>`); invalid transitions become compile errors rather than runtime panics.
- **the newtype pattern (`references/patterns/newtype.md`):** phantom types use the same compile-time brand technique; the runtime erases the state parameter `S` in `Connection<S>`, just like a newtype brand.
