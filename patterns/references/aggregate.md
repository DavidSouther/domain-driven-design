# Aggregate — Code Reference

Code examples for the `patterns:aggregate` skill. Referenced by `patterns/skills/aggregate/SKILL.md`.

---

## TypeScript

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

---

## Python

```python
from dataclasses import dataclass
from typing import Literal

@dataclass
class LineItem:
    product_id: str
    qty: int
    unit_price: float

    def __post_init__(self) -> None:
        if self.qty <= 0:
            raise ValueError("qty must be positive")
        if self.unit_price < 0:
            raise ValueError("unit_price must be non-negative")

    @property
    def subtotal(self) -> float:
        return self.qty * self.unit_price


class Order:
    def __init__(self, id: str) -> None:
        self._id = id
        self._lines: list[LineItem] = []
        self._status: Literal["pending", "placed"] = "pending"

    @property
    def id(self) -> str:
        return self._id

    @classmethod
    def create(cls, id: str) -> "Order":
        return cls(id)

    def place(self, items: list[dict]) -> None:
        """Enforces all invariants atomically or raises."""
        if self._status != "pending":
            raise ValueError("Order already placed")
        if not items:
            raise ValueError("Order must have at least one item")

        new_lines = [LineItem(**i) for i in items]
        if sum(l.subtotal for l in new_lines) <= 0:
            raise ValueError("Total must be positive")

        self._lines = new_lines
        self._status = "placed"

    @property
    def total(self) -> float:
        return sum(l.subtotal for l in self._lines)


# Caller: load one aggregate, call one method, persist the result
order = Order.create("ord-1")
order.place(cart_items)
order_repository.save(order)
# Side effects in other aggregates are triggered via domain events,
# not by calling into another aggregate from within order.place.
```

---

## Rust

```rust
pub struct LineItem {
    product_id: String,
    qty: u32,
    unit_price_cents: u64,
}

impl LineItem {
    pub fn new(product_id: &str, qty: u32, unit_price_cents: u64) -> Result<Self, String> {
        if qty == 0 {
            return Err("qty must be positive".into());
        }
        Ok(LineItem {
            product_id: product_id.to_string(),
            qty,
            unit_price_cents,
        })
    }

    pub fn subtotal(&self) -> u64 {
        self.qty as u64 * self.unit_price_cents
    }
}

#[derive(PartialEq)]
enum OrderStatus {
    Pending,
    Placed,
}

pub struct Order {
    id: String,
    lines: Vec<LineItem>,
    status: OrderStatus,
}

impl Order {
    pub fn create(id: &str) -> Self {
        Order {
            id: id.to_string(),
            lines: Vec::new(),
            status: OrderStatus::Pending,
        }
    }

    /// One method — enforces all invariants atomically or returns Err.
    pub fn place(&mut self, items: Vec<(&str, u32, u64)>) -> Result<(), String> {
        if self.status != OrderStatus::Pending {
            return Err("Order already placed".into());
        }
        if items.is_empty() {
            return Err("Order must have at least one item".into());
        }

        let new_lines: Result<Vec<LineItem>, _> = items
            .into_iter()
            .map(|(id, qty, price)| LineItem::new(id, qty, price))
            .collect();
        let new_lines = new_lines?;

        if new_lines.iter().map(|l| l.subtotal()).sum::<u64>() == 0 {
            return Err("Total must be positive".into());
        }

        self.lines = new_lines;
        self.status = OrderStatus::Placed;
        Ok(())
    }

    pub fn total(&self) -> u64 {
        self.lines.iter().map(|l| l.subtotal()).sum()
    }
}

// Caller: load one aggregate, call one method, persist the result
// order.place(cart_items)?;
// order_repository.save(&order).await?;
// Side effects in other aggregates are triggered via domain events.
```
