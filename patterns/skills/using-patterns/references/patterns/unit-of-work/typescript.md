# TypeScript Unit of Work

TypeScript uses `Symbol.asyncDispose` (ES2023 `await using`) for automatic rollback on scope exit.

```typescript
interface UnitOfWork extends AsyncDisposable {
  readonly products: ProductRepository;
  commit(): Promise<void>;
  rollback(): Promise<void>;
  collectEvents(): DomainEvent[];
}

// In-memory fake: fast unit tests without a database
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
