# Unit of Work — Code Reference

Code examples for the `patterns:unit-of-work` skill. Referenced by `patterns/skills/unit-of-work/SKILL.md`.

---

## Python

```python
from abc import ABC, abstractmethod

class AbstractUnitOfWork(ABC):
    products: AbstractProductRepository

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        if exc_type:
            self.rollback()   # automatic rollback on any unhandled exception
        return False          # never suppress exceptions

    @abstractmethod
    def commit(self): ...

    @abstractmethod
    def rollback(self): ...

    def collect_events(self):
        """Drain domain events from all tracked aggregates after commit."""
        for product in self.products.seen:
            yield from product.events


# SQLAlchemy implementation
class SqlUnitOfWork(AbstractUnitOfWork):
    def __init__(self, session_factory):
        self._session_factory = session_factory

    def __enter__(self):
        self._session = self._session_factory()
        self.products = SqlProductRepository(self._session)
        return super().__enter__()

    def commit(self):
        self._session.commit()

    def rollback(self):
        self._session.rollback()


# In-memory fake — enables fast unit tests with no database
class FakeUnitOfWork(AbstractUnitOfWork):
    def __init__(self):
        self.products = FakeProductRepository()
        self.committed = False

    def commit(self):
        self.committed = True

    def rollback(self):
        pass


# Application handler
def allocate(cmd: AllocateCommand, uow: AbstractUnitOfWork) -> str:
    with uow:                                              # 1. open transaction
        product = uow.products.get(cmd.sku)               # 2. load aggregate
        if product is None:
            raise UnknownSku(cmd.sku)
        batch_id = product.allocate(                      # 3. run domain operation
            OrderLine(cmd.order_id, cmd.sku, cmd.qty)
        )
        uow.commit()                                      # 4. flush all deferred writes
    return batch_id                                       # 5. respond (outside UoW)
```

---

## TypeScript

TypeScript uses `Symbol.asyncDispose` (ES2023 `await using`) for automatic rollback on scope exit.

```typescript
interface UnitOfWork extends AsyncDisposable {
  readonly products: ProductRepository;
  commit(): Promise<void>;
  rollback(): Promise<void>;
  collectEvents(): DomainEvent[];
}

// In-memory fake — fast unit tests without a database
class InMemoryUnitOfWork implements UnitOfWork {
  readonly products = new InMemoryProductRepository();
  committed = false;

  async commit(): Promise<void> {
    this.committed = true;
  }

  async rollback(): Promise<void> {}

  collectEvents(): DomainEvent[] {
    return this.products.seen.flatMap(p => p.events);
  }

  async [Symbol.asyncDispose](): Promise<void> {
    if (!this.committed) await this.rollback(); // automatic rollback on scope exit
  }
}

// Application handler
async function allocate(cmd: AllocateCommand, uow: UnitOfWork): Promise<string> {
  await using _ = uow;                                // 1. open; auto-rollback on exit
  const product = await uow.products.get(cmd.sku);   // 2. load aggregate
  if (!product) throw new UnknownSkuError(cmd.sku);
  const batchId = product.allocate(                  // 3. run domain operation
    new OrderLine(cmd.orderId, cmd.sku, cmd.qty)
  );
  await uow.commit();                                // 4. flush all deferred writes
  return batchId;                                    // 5. respond (outside UoW scope)
}
```

---

## Rust

Rust uses the `Drop` trait for guaranteed rollback when the UoW goes out of scope without an explicit commit.

```rust
use async_trait::async_trait;

#[async_trait]
pub trait UnitOfWork: Send {
    fn products(&self) -> &dyn ProductRepository;
    async fn commit(&mut self) -> anyhow::Result<()>;
    async fn rollback(&mut self) -> anyhow::Result<()>;
}

// In-memory fake — fast unit tests without a database
pub struct InMemoryUnitOfWork {
    products_repo: InMemoryProductRepository,
    pub committed: bool,
}

impl InMemoryUnitOfWork {
    pub fn new() -> Self {
        InMemoryUnitOfWork {
            products_repo: InMemoryProductRepository::new(),
            committed: false,
        }
    }
}

#[async_trait]
impl UnitOfWork for InMemoryUnitOfWork {
    fn products(&self) -> &dyn ProductRepository {
        &self.products_repo
    }

    async fn commit(&mut self) -> anyhow::Result<()> {
        self.committed = true;
        Ok(())
    }

    async fn rollback(&mut self) -> anyhow::Result<()> {
        Ok(())
    }
}

// Drop provides automatic rollback — if commit() was never called, changes are discarded.
// SQL implementations would call self.session.rollback() here.
impl Drop for InMemoryUnitOfWork {
    fn drop(&mut self) {
        if !self.committed {
            // rollback is synchronous in Drop; async implementations use a flag + background task
        }
    }
}

// Application handler
pub async fn allocate(
    cmd: &AllocateCommand,
    uow: &mut dyn UnitOfWork,
) -> anyhow::Result<String> {
    let mut product = uow                              // 1. open (caller owns the UoW scope)
        .products()
        .get(&cmd.sku)                                 // 2. load aggregate
        .await?
        .ok_or_else(|| anyhow::anyhow!("Unknown SKU: {}", cmd.sku))?;

    let batch_id = product.allocate(                  // 3. run domain operation
        &OrderLine {
            order_id: cmd.order_id.clone(),
            sku: cmd.sku.clone(),
            qty: cmd.qty,
        },
    )?;

    uow.commit().await?;                              // 4. flush all deferred writes
    Ok(batch_id)                                      // 5. respond (caller exits UoW scope)
}
```
