# Visibility: TypeScript reference

TypeScript has `private`, `readonly`, and `ReadonlyArray<T>`. Together they cover all four rules.

```typescript
// Before: every rule of the Order is enforceable only by convention.
class OrderLoose {
  status: "open" | "cancelled" | "shipped" = "open";
  lines: OrderLine[] = [];
  total = 0;
}

// Caller can do anything:
const o = new OrderLoose();
o.status = "shipped";          // skipped "open -> cancelled -> ?" rules
o.lines.push(line);            // total no longer matches
o.total = 0;                   // contradicts the lines

// After: the Order owns its rules.
type OrderStatus = "open" | "cancelled" | "shipped";

class Order {
  private _status: OrderStatus = "open";
  private readonly _lines: OrderLine[] = [];
  private _total: Cents = makeCents(0);

  // Constructor is private — only the builder can produce an Order.
  private constructor(readonly id: OrderId) {}

  // The builder is returned from a static method on Order, so the closure
  // can legitimately call `new Order(id)` against the private constructor.
  static builder(id: OrderId): OrderBuilder {
    const lines: OrderLine[] = [];
    const builder: OrderBuilder = {
      withLine(line: OrderLine) { lines.push(line); return builder; },
      build(): Order {
        if (lines.length === 0) throw new Error("order must have at least one line");
        const order = new Order(id);
        for (const line of lines) order.addLine(line);
        return order;
      },
    };
    return builder;
  }

  status(): OrderStatus { return this._status; }
  total(): Cents { return this._total; }

  // Reference-only getter: callers cannot mutate the returned array.
  lines(): ReadonlyArray<OrderLine> { return this._lines; }

  // Explicit mutation: invariants live inside the method.
  addLine(line: OrderLine): void {
    if (this._status !== "open") throw new Error("cannot modify a closed order");
    this._lines.push(line);
    this._total = sumLines(this._lines);
  }

  cancel(): void {
    if (this._status === "shipped") throw new Error("cannot cancel a shipped order");
    this._status = "cancelled";
  }
}

interface OrderBuilder {
  withLine(line: OrderLine): OrderBuilder;
  build(): Order;
}
```

Key details:
- Fields are `private`. There is no accidental write path from outside the class.
- `lines()` returns `ReadonlyArray<OrderLine>` — `.push` is a type error at the call site.
- `cancel()` and `addLine()` are the only writes; both check the invariants they protect.
- `status()` and `total()` compute their values; they are not assignable fields.
- The constructor is private; `Order.builder(...)` is the only sanctioned construction path.
