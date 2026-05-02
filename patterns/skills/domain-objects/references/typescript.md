# Entities, Value Objects, and Domain Service Functions — TypeScript Reference

```typescript
// ENTITY — identity via id, mutable state, equality by id
class Batch {
  constructor(
    readonly id: string,           // identity — survives all mutations
    readonly sku: string,
    readonly eta: Date,
    private available: number,
  ) {}

  canAllocate(line: OrderLine): boolean {
    return this.sku === line.sku && this.available >= line.qty;
  }

  allocate(line: OrderLine): void {
    if (!this.canAllocate(line)) throw new Error("Cannot allocate");
    this.available -= line.qty;   // state changes; identity stays the same
  }
}

// VALUE OBJECT — no identity, equality by value, all fields readonly
class OrderLine {
  constructor(
    readonly orderId: string,
    readonly sku: string,
    readonly qty: number,
  ) {}

  equals(other: OrderLine): boolean {
    return this.orderId === other.orderId
        && this.sku === other.sku
        && this.qty === other.qty;
  }

  // "Mutation" produces a new instance; the original is never changed
  withQty(qty: number): OrderLine {
    return new OrderLine(this.orderId, this.sku, qty);
  }
}

// DOMAIN SERVICE FUNCTION — stateless; coordinates logic spanning multiple entities
function allocate(line: OrderLine, batches: Batch[]): string {
  const sorted = batches
    .filter(b => b.canAllocate(line))
    .sort((a, b) => a.eta.getTime() - b.eta.getTime()); // prefer earliest batch

  if (sorted.length === 0) throw new Error(`Out of stock: ${line.sku}`);

  const chosen = sorted[0];
  chosen.allocate(line);
  return chosen.id;
}
```
