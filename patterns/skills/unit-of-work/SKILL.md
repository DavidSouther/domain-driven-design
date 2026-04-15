---
name: unit-of-work
description: Use when an application handler must load an aggregate, run a domain operation, and persist all changes atomically — tracking every mutation during the business transaction and flushing them together on commit or discarding them entirely on rollback. Applies wherever partial writes are unacceptable and rollback must be guaranteed.
---

# Unit of Work

## Overview

The Unit of Work pattern pairs an Aggregate with a Repository inside a single transactional boundary: all mutations are *deferred* until `commit()`, and a failed operation can be *entirely undone* via `rollback()`. This keeps durability concerns (row locks, optimistic-concurrency tokens, session lifecycle) out of application-layer code and makes handlers testable without a real database.

## When to Use

- A handler makes changes that must all succeed or all fail — partial writes are unacceptable.
- Rollback behavior (validation error, concurrent conflict, infrastructure failure) must be explicit and guaranteed.
- The aggregate operation and its persistence should be tested together without a real database.
- Durability details must be kept out of application-layer and domain code.

**When NOT to use:** read-only queries, fire-and-forget writes with no rollback requirement, or simple CRUD with no domain logic.

## Core Pattern

The abstract UoW interface exposes a repository and `commit()`/`rollback()` methods. The context manager (Python `with`, TypeScript `await using`, Rust `Drop`) guarantees rollback on any unhandled exception. A `FakeUnitOfWork` is provided for tests — no database required.

```
def allocate(cmd, uow: AbstractUnitOfWork) -> str:
    with uow:                          # 1. open transaction (auto-rollback on exception)
        product = uow.products.get(cmd.sku)   # 2. load aggregate
        batch_id = product.allocate(...)      # 3. run domain operation
        uow.commit()                          # 4. flush all deferred writes
    return batch_id                           # 5. respond (outside UoW scope)
```

For complete examples in TypeScript, Python, and Rust, see `references/unit-of-work.md`.

## Quick Reference

1. **Open** — enter the `with` block; UoW creates the session and repository.
2. **Load** — fetch the aggregate through the repository (no write yet).
3. **Operate** — call the aggregate's domain method; mutations are tracked in memory.
4. **Commit or rollback** — `commit()` flushes all deferred writes atomically; `__exit__` calls `rollback()` automatically on any exception.
5. **Respond** — return results or surface domain errors *outside* the `with` block.

## Common Mistakes

**Forgetting the rollback path.** Calling `commit()` outside a `with` block (or `try/finally`) leaves the session dirty on failure. Always use context-manager interface, Drop semantics, or similar.

**Using the repository outside a context management block.** Accessing `uow.products` after exiting the context is undefined — the session is closed. All aggregate work must happen inside the `with` block. The `uow` may be dropped in some languages.

**UoW spanning multiple aggregate roots.** A UoW should map 1:1 to one aggregate operation. Chaining multiple aggregate updates inflates the consistency boundary and makes failure recovery ambiguous.

**Leaking the session into the domain.** The ORM session must stay inside the UoW implementation. Aggregates and repositories must never import or reference it directly.

**Ignoring domain events.** After `commit()`, call `collect_events()` and publish any events the aggregate raised. Skipping this silently drops side-effects.

## Composes With

- **`patterns:aggregate`** — the UoW wraps exactly one aggregate operation; atomicity here enforces the aggregate's consistency guarantee at the storage level.
- **`patterns:repository`** — the UoW owns and creates the repository instance; the repository is never constructed or used outside a UoW in transactional handlers.
- **`patterns:bootstrap-and-service`** — application services create and use the UoW; the Composition Root injects the concrete UoW factory so tests can substitute `FakeUnitOfWork`.
