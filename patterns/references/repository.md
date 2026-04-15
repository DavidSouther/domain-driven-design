# Repository — Code Reference

Code examples for the `patterns:repository` skill. Referenced by `patterns/skills/repository/SKILL.md`.

---

## Python

```python
# domain/repositories.py — lives in the domain layer; no ORM imports here
from abc import ABC, abstractmethod
from typing import Optional, List

class AbstractProductRepository(ABC):
    @abstractmethod
    def get(self, sku: str) -> Optional["Product"]: ...

    @abstractmethod
    def add(self, product: "Product") -> None: ...

    @abstractmethod
    def list(self) -> List["Product"]: ...


# infrastructure/repositories.py — implements the domain interface
class InMemoryProductRepository(AbstractProductRepository):
    def __init__(self):
        self._store: dict[str, "Product"] = {}

    def get(self, sku: str) -> Optional["Product"]:
        return self._store.get(sku)

    def add(self, product: "Product") -> None:
        self._store[product.sku] = product

    def list(self) -> List["Product"]:
        return list(self._store.values())


# domain/services.py — depends only on the abstract interface
def allocate(order_line, repo: AbstractProductRepository) -> str:
    product = repo.get(order_line.sku)
    if product is None:
        raise ValueError(f"Unknown SKU: {order_line.sku}")
    product.allocate(order_line)
    repo.add(product)
    return order_line.sku
```

Domain code receives the repository through dependency injection and calls only the abstract interface. It never references SQLAlchemy sessions, file handles, or HTTP clients.

---

## TypeScript

```typescript
// domain/repositories.ts — interface defined in the domain layer; no ORM imports
interface ProductRepository {
  get(sku: string): Promise<Product | null>;
  add(product: Product): Promise<void>;
  list(): Promise<Product[]>;
}

// infrastructure/repositories.ts — implements the domain interface
class InMemoryProductRepository implements ProductRepository {
  private store = new Map<string, Product>();

  async get(sku: string): Promise<Product | null> {
    return this.store.get(sku) ?? null;
  }

  async add(product: Product): Promise<void> {
    this.store.set(product.sku, product);
  }

  async list(): Promise<Product[]> {
    return [...this.store.values()];
  }
}

// domain/services.ts — depends only on the interface, never on InMemory or SQL
async function allocate(orderLine: OrderLine, repo: ProductRepository): Promise<string> {
  const product = await repo.get(orderLine.sku);
  if (!product) throw new Error(`Unknown SKU: ${orderLine.sku}`);
  product.allocate(orderLine);
  await repo.add(product);
  return orderLine.sku;
}
```

---

## Rust

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
