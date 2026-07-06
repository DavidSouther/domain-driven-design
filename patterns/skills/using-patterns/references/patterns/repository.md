# Repository

## Overview

The Repository pattern inserts an interface between domain objects and storage. The domain layer defines this interface, while the infrastructure layer implements it. Domain objects contain business logic; the Repository handles all I/O. Storage implementations can change without touching domain code.

Repositories differ from DAOs. A DAO maps to a single table and exposes raw CRUD. A Repository maps to an **aggregate root** and exposes collection-like semantics (`add`, `get`, `list`). Only aggregate roots get repositories. Child entities are only reached through their root.

## When to use

- You load domain objects from or save them to a database, file, or external API
- Repository instances enable isolated unit tests that do not hit a real data store
- You need multiple storage backends (for example, production SQL vs. test in-memory)
- The codebase mixes ORM queries with business rules that you should separate

**When NOT to use:** one-off scripts, simple CRUD tools with no domain logic, or prototypes where the storage technology is already the entire point.

## Core pattern

The domain layer defines the interface: `AbstractProductRepository` / `ProductRepository` trait. Domain code receives the repository through dependency injection and calls only the abstract interface, never ORM sessions, file handles, or HTTP clients. Concrete implementations live in the infrastructure layer.

```
# domain/repositories.py — interface only; no ORM imports
class AbstractProductRepository(ABC):
    @abstractmethod
    def get(self, sku: str) -> Optional[Product]: ...
    @abstractmethod
    def add(self, product: Product) -> None: ...

# infrastructure/repositories.py — implements the interface
class InMemoryProductRepository(AbstractProductRepository): ...
class SqlProductRepository(AbstractProductRepository): ...

# domain/services.py — depends only on the interface
def allocate(order_line, repo: AbstractProductRepository) -> str: ...
```

For complete examples, see [`repository/typescript.md`](repository/typescript.md), [`repository/python.md`](repository/python.md), and [`repository/rust.md`](repository/rust.md).

## Quick reference

| Implementation | Purpose |
|---|---|
| `InMemoryRepository` | Unit tests, fast, no I/O |
| `SqlAlchemyRepository` | Production relational database |
| `MongoRepository` | Document store |
| `HttpApiRepository` | Downstream service as data source |
| `CsvRepository` | Reporting or data export |

## Common mistakes

- **Interface in the wrong layer.** Placing the abstract repository in the infrastructure package inverts the dependency the wrong way. Define it in the domain package; infrastructure imports from domain, never the reverse.
- **Repository for every entity.** Only aggregate roots get repositories. Accessing a child entity directly (bypassing its root) breaks aggregate consistency boundaries.
- **Leaking ORM models into domain logic.** If `Product` extends `Base` (SQLAlchemy) or `Model` (Django), you couple the domain layer to the ORM. Map ORM rows to plain domain objects inside the repository.
- **Active Record antipattern.** When domain objects call `save()` or `delete()` on themselves they become their own repositories. Move persistence entirely outside the domain object.
- **Too many query methods.** Repositories with `find_by_sku_and_warehouse_and_status(...)` leak query concerns into the domain interface. Keep the interface narrow; push complex filtering to a Specification object or a separate read-model query service.

## Composes with

- **the aggregate pattern (`references/patterns/aggregate.md`)** — one repository per aggregate root; child entities are always reached through the root, never fetched directly.
- **the unit-of-work pattern (`references/patterns/unit-of-work.md`)** — the Unit of Work owns the repository instance and coordinates when it flushes writes; always access the repository through a UoW in transactional handlers.
- **the bootstrap-and-service pattern (`references/patterns/bootstrap-and-service.md`)** — the Composition Root is the only place that constructs concrete repository implementations and injects them into services or UoW factories.
