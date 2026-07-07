# Python repository reference

```python
# domain/repositories.py: lives in the domain layer; no ORM imports here
from abc import ABC, abstractmethod
from typing import Optional, List

class AbstractProductRepository(ABC):
    @abstractmethod
    def get(self, sku: str) -> Optional["Product"]: ...

    @abstractmethod
    def add(self, product: "Product") -> None: ...

    @abstractmethod
    def list(self) -> List["Product"]: ...


# infrastructure/repositories.py: implements the domain interface
class InMemoryProductRepository(AbstractProductRepository):
    def __init__(self):
        self._store: dict[str, "Product"] = {}

    def get(self, sku: str) -> Optional["Product"]:
        return self._store.get(sku)

    def add(self, product: "Product") -> None:
        self._store[product.sku] = product

    def list(self) -> List["Product"]:
        return list(self._store.values())


# domain/services.py: depends only on the abstract interface
def allocate(order_line, repo: AbstractProductRepository) -> str:
    product = repo.get(order_line.sku)
    if product is None:
        raise ValueError(f"Unknown SKU: {order_line.sku}")
    product.allocate(order_line)
    repo.add(product)
    return order_line.sku
```

Domain code gets the repository and calls only the abstract interface. It does not use SQLAlchemy sessions, file handles, or HTTP clients.
