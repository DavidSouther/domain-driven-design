# Visibility: Python reference

Python doesn't enforce privacy.
The convention has multiple ways: leading underscores mark "do not tap," `@property` gives read-only access, `MappingProxyType` or tuples give immutable collections, and frozen dataclasses protect value objects.

```python
from dataclasses import dataclass, field
from types import MappingProxyType
from typing import Sequence


@dataclass(frozen=True)
class OrderLine:
    sku: str
    qty: int
    cents: int


class Order:
    # Private constructor convention: callers go through Order.builder(...)
    def __init__(self, order_id: str) -> None:
        self._id = order_id
        self._status: str = "open"
        self._lines: list[OrderLine] = []
        self._total: int = 0

    @classmethod
    def builder(cls, order_id: str) -> "OrderBuilder":
        return OrderBuilder(order_id)

    @property
    def id(self) -> str:
        return self._id

    @property
    def status(self) -> str:
        return self._status

    @property
    def total(self) -> int:
        return self._total

    # Reference-only getter: tuple is immutable, so callers cannot append.
    @property
    def lines(self) -> Sequence[OrderLine]:
        return tuple(self._lines)

    def add_line(self, line: OrderLine) -> None:
        if self._status != "open":
            raise ValueError("cannot modify a closed order")
        self._lines.append(line)
        self._total = sum(l.cents * l.qty for l in self._lines)

    def cancel(self) -> None:
        if self._status == "shipped":
            raise ValueError("cannot cancel a shipped order")
        self._status = "cancelled"


class OrderBuilder:
    def __init__(self, order_id: str) -> None:
        self._id = order_id
        self._lines: list[OrderLine] = []

    def with_line(self, line: OrderLine) -> "OrderBuilder":
        self._lines.append(line)
        return self

    def build(self) -> Order:
        if not self._lines:
            raise ValueError("order must have at least one line")
        order = Order(self._id)
        for line in self._lines:
            order.add_line(line)
        return order
```

Key details:
- Underscore-prefixed names signal "private" to humans and to linters; tools such as Pyright respect the convention.
- `@property` exposes a read path with no setter.
  Assignment from outside raises `AttributeError`.
- `lines` returns a `tuple`, so `.append` is unavailable.
  For dictionaries, return `MappingProxyType(self._dict)`.
- `add_line` and `cancel` enforce invariants before mutating.
- Construction goes through `Order.builder(...)`; calling `Order(...)` directly is possible but flagged as private by convention and tooling.
- For immutable value objects, `@dataclass(frozen=True)` is the strongest form.
  There is no mutation surface to control.
