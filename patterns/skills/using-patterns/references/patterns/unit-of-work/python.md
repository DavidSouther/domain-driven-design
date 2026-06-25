# Unit of Work — Python Reference

```python
from abc import ABC, abstractmethod

class AbstractUnitOfWork(ABC):
    products: AbstractProductRepository

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        if exc_type:
            self.rollback()   # automatic rollback on any unhandled exception
        return False          # never suppress exceptions

    @abstractmethod
    def commit(self): ...

    @abstractmethod
    def rollback(self): ...

    def collect_events(self):
        """Drain domain events from all tracked aggregates after commit."""
        for product in self.products.seen:
            yield from product.events


# SQLAlchemy implementation
class SqlUnitOfWork(AbstractUnitOfWork):
    def __init__(self, session_factory):
        self._session_factory = session_factory

    def __enter__(self):
        self._session = self._session_factory()
        self.products = SqlProductRepository(self._session)
        return super().__enter__()

    def commit(self):
        self._session.commit()

    def rollback(self):
        self._session.rollback()


# In-memory fake — enables fast unit tests with no database
class FakeUnitOfWork(AbstractUnitOfWork):
    def __init__(self):
        self.products = FakeProductRepository()
        self.committed = False

    def commit(self):
        self.committed = True

    def rollback(self):
        pass


# Application handler
def allocate(cmd: AllocateCommand, uow: AbstractUnitOfWork) -> str:
    with uow:                                              # 1. open transaction
        product = uow.products.get(cmd.sku)               # 2. load aggregate
        if product is None:
            raise UnknownSku(cmd.sku)
        batch_id = product.allocate(                      # 3. run domain operation
            OrderLine(cmd.order_id, cmd.sku, cmd.qty)
        )
        uow.commit()                                      # 4. flush all deferred writes
    return batch_id                                       # 5. respond (outside UoW)
```
