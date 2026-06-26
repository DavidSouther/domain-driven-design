# Aggregate — Python Reference

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
