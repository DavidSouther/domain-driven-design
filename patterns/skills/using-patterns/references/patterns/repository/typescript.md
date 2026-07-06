# Repository: TypeScript reference

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
