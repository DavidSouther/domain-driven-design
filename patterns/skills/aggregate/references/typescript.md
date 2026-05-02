# Aggregate — TypeScript Reference

```typescript
// Value object — no identity, equality by fields
class LineItem {
  constructor(
    readonly productId: string,
    readonly qty: number,
    readonly unitPrice: number,
  ) {
    if (qty <= 0) throw new Error("qty must be positive");
    if (unitPrice < 0) throw new Error("unitPrice must be non-negative");
  }
  get subtotal() { return this.qty * this.unitPrice; }
}

// Aggregate Root — single entry point for all mutations
class Order {
  private lines: LineItem[] = [];
  private status: "pending" | "placed" = "pending";

  private constructor(readonly id: string) {}

  static create(id: string): Order { return new Order(id); }

  // One method — enforces all invariants atomically or throws
  place(items: { productId: string; qty: number; unitPrice: number }[]): void {
    if (this.status !== "pending") throw new Error("Order already placed");
    if (items.length === 0) throw new Error("Order must have at least one item");

    const newLines = items.map(i => new LineItem(i.productId, i.qty, i.unitPrice));
    if (newLines.reduce((s, l) => s + l.subtotal, 0) <= 0) throw new Error("Total must be positive");

    this.lines = newLines;
    this.status = "placed";
  }

  get total(): number { return this.lines.reduce((s, l) => s + l.subtotal, 0); }
}

// Caller: load one aggregate, call one method, persist the result
const order = Order.create("ord-1");
order.place(cartItems);
await orderRepository.save(order);
// Side effects in other aggregates are triggered via domain events,
// not by calling into another aggregate from within Order.place.
```
