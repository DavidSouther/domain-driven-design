# Unit of work, Rust reference

Rust uses the `Drop` trait for guaranteed rollback when the UoW goes out of scope without an explicit commit.

```rust
use async_trait::async_trait;

#[async_trait]
pub trait UnitOfWork: Send {
    fn products(&self) -> &dyn ProductRepository;
    async fn commit(&mut self) -> anyhow::Result<()>;
    async fn rollback(&mut self) -> anyhow::Result<()>;
}

// In-memory fake: fast unit tests without a database
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

// Drop provides automatic rollback: if commit() was never called, changes are discarded.
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
