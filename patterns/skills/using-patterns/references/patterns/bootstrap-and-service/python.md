# Bootstrap and service, Python reference

The four layers and their mandates:

| Layer | Mandate |
|---|---|
| **Domain** | Pure business rules, aggregates, value objects, domain services, errors as values; no I/O |
| **Application Service** | Orchestrates one use scenario: parses input, calls domain + repository ports, returns typed results; no HTTP or DB knowledge |
| **Adapter** | Implements a port interface defined by the service layer; translates protocol details (HTTP status codes, command-line flags) to/from service calls; no business logic |
| **Composition Root** | The only place that imports concrete classes; constructs and injects all dependencies; runs once at startup |

```python
# domain.py — pure logic, no I/O
from dataclasses import dataclass
from typing import Union

@dataclass
class Order:
    id: str
    total: float

@dataclass
class InsufficientFunds:
    kind: str = "InsufficientFunds"
    balance: float = 0.0

def place_order(order: Order, balance: float) -> Union[Order, InsufficientFunds]:
    if balance < order.total:
        return InsufficientFunds(balance=balance)
    return order


# ports.py — interfaces owned by the service layer
from abc import ABC, abstractmethod

class OrderRepository(ABC):
    @abstractmethod
    async def get_balance(self, customer_id: str) -> float: ...


# service.py — application service: orchestrates, does not own rules
class OrderService:
    def __init__(self, repo: OrderRepository) -> None:
        self._repo = repo

    async def place(self, raw: dict) -> Union[Order, InsufficientFunds, dict]:
        try:
            order = parse_order(raw)            # parse-don't-validate
        except ValueError as e:
            return {"kind": "ParseError", "message": str(e)}
        balance = await self._repo.get_balance(raw["customer_id"])
        return place_order(order, balance)      # domain function owns the rule


# adapter.py — thin HTTP adapter (FastAPI); maps protocol, calls service
from fastapi.responses import JSONResponse

async def handle_place_order(request: Request, service: OrderService) -> JSONResponse:
    body = await request.json()
    result = await service.place(body)
    if isinstance(result, InsufficientFunds):
        return JSONResponse({"error": "insufficient funds", "balance": result.balance}, status_code=422)
    if isinstance(result, dict) and result.get("kind") == "ParseError":
        return JSONResponse(result, status_code=400)
    return JSONResponse({"id": result.id, "total": result.total}, status_code=201)


# bootstrap.py — Composition Root; the only file that knows about Postgres
import os
from fastapi import FastAPI
from infrastructure.postgres_repo import PostgresOrderRepository

repo = PostgresOrderRepository(os.environ["DATABASE_URL"])
order_service = OrderService(repo)

app = FastAPI()
app.add_api_route("/orders", lambda req: handle_place_order(req, order_service), methods=["POST"])
```
