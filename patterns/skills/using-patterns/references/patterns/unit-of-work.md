# Unit of work

## Overview

The Unit of Work pattern bundles an Aggregate and Repository inside one transactional boundary. All mutations defer until `commit()`. A failed operation reverts entirely via `rollback()`. This approach keeps durability concerns out of app-layer code and leaves row locks, optimistic-concurrency tokens, and session lifecycle details to the pattern. Handlers become testable without a real database.

## When to use

- A handler makes changes that must all succeed or all fail. Partial writes are unacceptable.
- Rollback behavior must be explicit and guaranteed. Validation errors, concurrent conflicts, and infrastructure failures all trigger it predictably.
- Tests must verify aggregate operations and persistence together without a real database.
- Keep durability details out of app-layer and domain code.

**When NOT to use:** read-only queries, fire-and-forget writes with no rollback requirement, or simple CRUD with no domain logic.

## Core pattern

The abstract UoW interface exposes a repository and `commit()`/`rollback()` methods. The context manager (Python `with`, TypeScript `await using`, Rust `Drop`) guarantees rollback on any unhandled exception. Tests use a `FakeUnitOfWork` that requires no database.

```
def allocate(cmd, uow: AbstractUnitOfWork) -> str:
    with uow:                          # 1. open transaction (auto-rollback on exception)
        product = uow.products.get(cmd.sku)   # 2. load aggregate
        batch_id = product.allocate(...)      # 3. run domain operation
        uow.commit()                          # 4. flush all deferred writes
    return batch_id                           # 5. respond (outside UoW scope)
```

For complete examples, see [`unit-of-work/typescript.md`](unit-of-work/typescript.md), [`unit-of-work/python.md`](unit-of-work/python.md), and [`unit-of-work/rust.md`](unit-of-work/rust.md).

## Quick reference

1. **Open**: enter the `with` block; UoW creates the session and repository.
2. **Load**: fetch the aggregate through the repository (no write yet).
3. **Operate**: call the aggregate's domain method. The UoW tracks mutations in memory.
4. **Commit or rollback**: `commit()` flushes all deferred writes atomically; `__exit__` calls `rollback()` automatically on any exception.
5. **Respond**: return results or surface domain errors *outside* the `with` block.

## Common mistakes

**Forgetting the rollback path.** Calling `commit()` outside a `with` block (or `try/finally`) leaves the session dirty on failure. Always use context-manager interface, Drop semantics, or similar.

**Using the repository outside a context management block.** Accessing `uow.products` after exiting the context causes undefined behavior. The session closes. All aggregate work must happen inside the `with` block. Some languages drop the `uow` automatically.

**UoW spanning multiple aggregate roots.** A UoW should map 1:1 to one aggregate operation. Chaining multiple aggregate updates inflates the consistency boundary and makes failure recovery ambiguous.

**Leaking the session into the domain.** The ORM session must stay inside the UoW implementation. Aggregates and repositories must never import or reference it directly.

**Ignoring domain events.** After `commit()`, call `collect_events()` and publish any events the aggregate raised. Skipping this silently drops side-effects.

## Composes with

- **the aggregate pattern (`references/patterns/aggregate.md`)**: the UoW wraps exactly one aggregate operation; atomicity here enforces the aggregate's consistency guarantee at the storage level.
- **the repository pattern (`references/patterns/repository.md`)**: the UoW owns and creates the repository instance; the repository is never constructed or used outside a UoW in transactional handlers.
- **the bootstrap-and-service pattern (`references/patterns/bootstrap-and-service.md`)**: app services create and use the UoW. The Composition Root injects the concrete UoW factory so tests can substitute `FakeUnitOfWork`.
