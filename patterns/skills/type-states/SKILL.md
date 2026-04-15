---
name: type-states
description: Use when a domain object has distinct lifecycle phases (e.g., open/closed, draft/published, at-war/at-peace) and only a subset of operations are valid in each phase. Prevents representing invalid combinations of state and data by encoding each phase as a separate type, making illegal states unrepresentable at compile time.
---

# Discriminated Unions, Type States, and Protocols

## Overview

Make illegal states unrepresentable by encoding each variant of a domain object as a distinct type. Instead of one flat type with optional fields and runtime checks, define one type per valid state — the compiler then rejects any code that tries to use data or call methods that do not exist in the current state.

## When to Use

- A domain object passes through lifecycle phases where different fields are valid in each phase (e.g., `Draft`, `Published`, `Archived`).
- A state machine has transitions that should be enforced at compile time, not runtime.
- Invalid combinations of fields exist but are only caught today by runtime guards or null checks.
- An object owns resources that must only be released or acted on once (e.g., a network connection, a file handle).

**When NOT to use:** Purely dynamic data where the set of variants is open-ended and unknown at compile time — use a runtime discriminant and validation there instead.

## Core Pattern

Three sub-patterns, each making a different class of illegal state unrepresentable:

**Discriminated union** — each valid state combination is its own type. The compiler rejects any value whose fields belong to different states (e.g., `{ status: "peace", ruler: "dictator" }` is not assignable to `Rome`).

**Type state** — the state parameter `S` is carried only at compile time (a _phantom type_); no runtime value is stored for it. Transition functions consume the old state and return a new one, so the caller cannot reuse a stale handle.

**Protocols / interfaces** — define narrow interfaces per capability so callers only access what their context permits. A function that accepts `Readable` cannot accidentally call `write`.

For complete examples in TypeScript, Python, and Rust, see `references/type-states.md`.

## Quick Reference

| Pattern | Use Case | Benefit |
|---|---|---|
| Discriminated union | Multiple valid states, each with different fields | Compiler rejects impossible field combinations |
| Type state | Object moves through ordered lifecycle phases | Invalid transitions are compile errors, not runtime panics |
| Protocol / interface | Limit which operations a caller can perform | Scoped capability; no accidental misuse across contexts |

## Common Mistakes

**Using enums + runtime checks instead of types:** A single `status: Status` field plus `if (status === "war")` guards means the compiler cannot verify consistency. The Roman bug passes every type check; only tests (or production) catch it.

**Shared mutable state across states:** Storing all possible fields in one object and leaving some `undefined` recreates the flat-type problem. Each state type should carry only the fields relevant to that state.

**Reusing a handle after transition:** If a transition function takes the connection by reference instead of by value, the caller keeps a reference to the pre-transition object and can still call methods on the wrong state. Transition functions must consume (take ownership of) the old handle — in TypeScript, reassign and never alias: `conn = open(conn)`.

## Composes With

- **`patterns:aggregate`** — type states model the legal lifecycle of an aggregate (e.g., `Order<Pending>` → `Order<Placed>`); invalid transitions become compile errors rather than runtime panics.
- **`patterns:newtype`** — phantom types use the same compile-time brand technique; the state parameter `S` in `Connection<S>` is erased at runtime, just like a newtype brand.
