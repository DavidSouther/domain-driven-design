# Entities, values, and services

## Overview

Not all domain objects play the same role.
When you treat identity-bearing objects as value snapshots, your models become hard to understand and fragile.
When you scatter cross-entity logic everywhere, you face similar problems.
This pattern names three distinct roles, each with the responsibility that fits it.

## When to use

- A concept has stable identity that persists through state changes.
  For example, a `User` is still the same user after changing their email.
- Two instances of a concept are interchangeable if all their fields match (`Money(5, "USD")` equals any other `Money(5, "USD")`).
- A domain operation involves more than one entity or value and has no natural "owner" among them (allocating stock across multiple batches).
- Business logic is leaking into service layers, controllers, or utility modules because no single entity felt like the right home.

**When NOT to use:** procedural scripts, one-off data transformations, or code with no business invariants.
The overhead of explicit classification adds noise without benefit.

## Core pattern

- **Entity** (`Batch`): carries an `id`.
  Two batches with the same SKU and quantity are still different batches.
  State changes; identity persists.
  Equality by `id`.
- **Value Object** (`OrderLine`): no identity.
  Replace it with another `OrderLine` carrying identical data and the domain doesn't care.
  "Mutation" returns a new instance.
- **Domain Service Function** (`allocate`): spans multiple `Batch` entities, is stateless, and does not belong to any single entity.

For complete examples, see [`domain-objects/typescript.md`](domain-objects/typescript.md), [`domain-objects/python.md`](domain-objects/python.md), and [`domain-objects/rust.md`](domain-objects/rust.md).

## Quick reference

| Concept | Identity | Mutable | Equality | Lives where |
|---|---|---|---|---|
| **Entity** | Yes (`id` field) | Yes | By reference / id | Class with state |
| **Value Object** | No | No, return new instance | By field values | Class or plain record |
| **Domain Service Function** | N/A | No, stateless; entities it calls may mutate | N/A | Plain function |

## Common mistakes

**Giving a Value Object an id:** adding a database surrogate key to `Money` or `OrderLine` tempts callers to treat it as an entity.
If two instances with matching fields are interchangeable, they are a Value Object.
Omit the id from the domain model.

**Putting cross-entity logic inside one entity:** an `allocate` method on `Batch` that iterates over all batches creates hidden coupling.
When logic spans multiple entities, extract it to a domain service function.

**Mutating Value Objects in place:** modifying a shared `Money` or `Address` instance produces aliasing bugs.
Construct a new Value Object with the changed fields (`withQty`, `withCurrency`) and replace the reference.
Prefer immutable structs whenever possible.

**Stateful service classes for simple logic:** a Domain Service Function is, in most cases, a plain function.
Reach for a service class only when the function needs collaborators such as a repository or external gateway (see the Repository and Unit of Work patterns).

**Confusing Domain Services with Application Services:** domain service functions contain domain rules and speak the ubiquitous language.
Application services orchestrate use cases (load, call, save) but hold no business logic.
See the bootstrap-and-service pattern (`references/patterns/bootstrap-and-service.md`).

## Composes with

- **the newtype pattern (`references/patterns/newtype.md`)**.
  Brands entity IDs and constrained value object fields (`UserId`, `Cents`) to prevent mixing at the type level.
- **the builder pattern (`references/patterns/builder.md`)**.
  When constructing an entity with many required fields, a builder prevents partial initialization.
- **the aggregate pattern (`references/patterns/aggregate.md`)**.
  The root entity of a cluster becomes the Aggregate Root; the aggregate boundary owns its internal value objects.
- **the repository pattern (`references/patterns/repository.md`)**.
  A repository loads and saves aggregate roots (entities); the repository interface belongs to the domain layer.
