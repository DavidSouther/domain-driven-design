# Repository — Rust Reference

```rust
use async_trait::async_trait;
use std::collections::HashMap;
use std::sync::Mutex;

// domain/repository.rs — trait defined in the domain crate; no DB imports
#[async_trait]
pub trait ProductRepository: Send + Sync {
    async fn get(&self, sku: &str) -> anyhow::Result<Option<Product>>;
    async fn add(&self, product: Product) -> anyhow::Result<()>;
    async fn list(&self) -> anyhow::Result<Vec<Product>>;
}

// infrastructure/in_memory.rs — implements the domain trait
pub struct InMemoryProductRepository {
    store: Mutex<HashMap<String, Product>>,
}

impl InMemoryProductRepository {
    pub fn new() -> Self {
        InMemoryProductRepository {
            store: Mutex::new(HashMap::new()),
        }
    }
}

#[async_trait]
impl ProductRepository for InMemoryProductRepository {
    async fn get(&self, sku: &str) -> anyhow::Result<Option<Product>> {
        Ok(self.store.lock().unwrap().get(sku).cloned())
    }

    async fn add(&self, product: Product) -> anyhow::Result<()> {
        self.store.lock().unwrap().insert(product.sku.clone(), product);
        Ok(())
    }

    async fn list(&self) -> anyhow::Result<Vec<Product>> {
        Ok(self.store.lock().unwrap().values().cloned().collect())
    }
}

// domain/services.rs — depends only on the trait, never on InMemory or SQL
pub async fn allocate(
    order_line: &OrderLine,
    repo: &dyn ProductRepository,
) -> anyhow::Result<String> {
    let mut product = repo
        .get(&order_line.sku)
        .await?
        .ok_or_else(|| anyhow::anyhow!("Unknown SKU: {}", order_line.sku))?;
    product.allocate(order_line)?;
    repo.add(product).await?;
    Ok(order_line.sku.clone())
}
```
