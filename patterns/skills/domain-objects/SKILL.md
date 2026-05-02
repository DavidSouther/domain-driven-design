---
name: domain-objects
description: Use when modeling domain objects and operations and the code conflates identity-bearing things, immutable values, and logic that spans multiple objects. Distinguishes objects that have lifecycle and identity (Entities), objects that are equal by value alone (Value Objects), and pure functions that encode domain logic not owned by a single entity (Domain Service Functions).
---

# Entities, Value Objects, and Domain Service Functions

## Overview

Not all domain objects are the same kind of thing. Treating identity-bearing objects the same as value snapshots, or scattering cross-entity logic into arbitrary places, produces models that are hard to reason about and error-prone to modify. This pattern names and separates three distinct roles so each carries exactly the responsibility that fits its nature.

## When to Use

- A concept has stable identity that persists through state changes (a `User` is still the same user after changing their email).
- Two instances of a concept are interchangeable if all their fields match (`Money(5, "USD")` equals any other `Money(5, "USD")`).
- A domain operation involves more than one entity or value and has no natural "owner" among them (allocating stock across multiple batches).
- Business logic is leaking into service layers, controllers, or utility modules because no single entity felt like the right home.

**When NOT to use:** Procedural scripts, one-off data transformations, or code with no business invariants — the overhead of explicit classification adds noise without benefit.

## Core Pattern

- **Entity** (`Batch`) — carries an `id`; two batches with the same SKU and quantity are still different batches. State changes; identity persists. Equality by `id`.
- **Value Object** (`OrderLine`) — no identity; replace it with another `OrderLine` carrying identical data and the domain doesn't care. "Mutation" returns a new instance.
- **Domain Service Function** (`allocate`) — spans multiple `Batch` entities, is stateless itself, and does not belong to any single entity.

For complete examples, see [`references/typescript.md`](references/typescript.md), [`references/python.md`](references/python.md), and [`references/rust.md`](references/rust.md).

## Quick Reference

| Concept | Identity | Mutable | Equality | Lives where |
|---|---|---|---|---|
| **Entity** | Yes (`id` field) | Yes | By reference / id | Class with state |
| **Value Object** | No | No — return new instance | By field values | Class or plain record |
| **Domain Service Function** | N/A | No — stateless; entities it calls may mutate | N/A | Plain function |

## Common Mistakes

**Giving a Value Object an id:** Adding a database surrogate key to `Money` or `OrderLine` tempts callers to treat it as an entity. If two instances with matching fields are interchangeable, they are a Value Object — omit the id from the domain model.

**Putting cross-entity logic inside one entity:** An `allocate` method on `Batch` that iterates over all batches creates hidden coupling. When logic spans multiple entities, extract it to a domain service function.

**Mutating Value Objects in place:** Modifying a shared `Money` or `Address` instance produces aliasing bugs. Construct a new Value Object with the changed fields (`withQty`, `withCurrency`) and replace the reference. Prefer immutable structs whenever possible.

**Stateful service classes for simple logic:** A Domain Service Function is usually a plain function. Reach for a service class only when the function needs collaborators such as a repository or external gateway (see the Repository and Unit of Work patterns).

**Confusing Domain Services with Application Services:** Domain service functions contain domain rules and speak the ubiquitous language. Application services orchestrate use cases (load, call, save) but hold no business logic — see `patterns:bootstrap-and-service`.

## Composes With

- **`patterns:newtype`** — brand entity IDs and constrained value-object fields (`UserId`, `Cents`) to prevent mixing at the type level.
- **`patterns:builder`** — when constructing an entity with many required fields, a builder prevents partial initialization.
- **`patterns:aggregate`** — the root entity of a cluster becomes the Aggregate Root; its internal value objects are owned by the aggregate boundary.
- **`patterns:repository`** — aggregate roots (entities) are loaded and saved through a repository; the repository interface belongs to the domain layer.
