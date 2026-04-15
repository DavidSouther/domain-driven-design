# Entities, Value Objects, and Domain Service Functions — Code Reference

Code examples for the `patterns:entities-value-objects-services` skill. Referenced by `patterns/skills/entities-value-objects-services/SKILL.md`.

---

## TypeScript

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

---

## Python

```python
from dataclasses import dataclass
from datetime import date


# VALUE OBJECT — no identity, equality by value, frozen (immutable)
@dataclass(frozen=True)
class OrderLine:
    order_id: str
    sku: str
    qty: int

    def with_qty(self, qty: int) -> "OrderLine":
        # "Mutation" produces a new instance; the original is never changed
        return OrderLine(self.order_id, self.sku, qty)


# ENTITY — identity via id, mutable state, equality by id
class Batch:
    def __init__(self, id: str, sku: str, eta: date, available: int) -> None:
        self._id = id
        self._sku = sku
        self._eta = eta
        self._available = available

    @property
    def id(self) -> str:
        return self._id

    @property
    def eta(self) -> date:
        return self._eta

    def can_allocate(self, line: OrderLine) -> bool:
        return self._sku == line.sku and self._available >= line.qty

    def allocate(self, line: OrderLine) -> None:
        if not self.can_allocate(line):
            raise ValueError("Cannot allocate")
        self._available -= line.qty  # state changes; identity stays the same

    # Entities compare by identity, not by field values
    def __eq__(self, other: object) -> bool:
        if not isinstance(other, Batch):
            return NotImplemented
        return self._id == other._id

    def __hash__(self) -> int:
        return hash(self._id)


# DOMAIN SERVICE FUNCTION — stateless; coordinates logic spanning multiple entities
def allocate(line: OrderLine, batches: list[Batch]) -> str:
    eligible = sorted(
        (b for b in batches if b.can_allocate(line)),
        key=lambda b: b.eta,
    )
    if not eligible:
        raise ValueError(f"Out of stock: {line.sku}")
    chosen = eligible[0]
    chosen.allocate(line)
    return chosen.id
```

---

## Rust

```rust
use std::cmp::Ordering;

// VALUE OBJECT — no identity, equality by value, all fields public and cloneable
#[derive(Debug, Clone, PartialEq, Eq)]
pub struct OrderLine {
    pub order_id: String,
    pub sku: String,
    pub qty: u32,
}

impl OrderLine {
    /// "Mutation" produces a new instance; the original is unchanged.
    pub fn with_qty(&self, qty: u32) -> Self {
        OrderLine { qty, ..self.clone() }
    }
}

// ENTITY — identity via id, mutable state, equality by id
pub struct Batch {
    id: String,
    sku: String,
    pub eta: chrono::NaiveDate,
    available: u32,
}

impl Batch {
    pub fn new(id: &str, sku: &str, eta: chrono::NaiveDate, available: u32) -> Self {
        Batch {
            id: id.to_string(),
            sku: sku.to_string(),
            eta,
            available,
        }
    }

    pub fn id(&self) -> &str {
        &self.id
    }

    pub fn can_allocate(&self, line: &OrderLine) -> bool {
        self.sku == line.sku && self.available >= line.qty
    }

    pub fn allocate(&mut self, line: &OrderLine) -> Result<(), String> {
        if !self.can_allocate(line) {
            return Err("Cannot allocate".into());
        }
        self.available -= line.qty; // state changes; identity stays the same
        Ok(())
    }
}

// Entities compare by identity, not by field values
impl PartialEq for Batch {
    fn eq(&self, other: &Self) -> bool {
        self.id == other.id
    }
}

// DOMAIN SERVICE FUNCTION — stateless; coordinates logic spanning multiple entities
pub fn allocate(line: &OrderLine, batches: &mut [Batch]) -> Result<String, String> {
    // Sort eligible batches by earliest ETA
    let mut eligible: Vec<&mut Batch> = batches
        .iter_mut()
        .filter(|b| b.can_allocate(line))
        .collect();

    eligible.sort_by_key(|b| b.eta);

    let chosen = eligible
        .into_iter()
        .next()
        .ok_or_else(|| format!("Out of stock: {}", line.sku))?;

    chosen.allocate(line)?;
    Ok(chosen.id().to_string())
}
```
