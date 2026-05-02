# Entities, Value Objects, and Domain Service Functions — Python Reference

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
