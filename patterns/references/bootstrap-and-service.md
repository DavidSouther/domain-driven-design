# Bootstrap and Service — Code Reference

Code examples for the `patterns:bootstrap-and-service` skill. Referenced by `patterns/skills/bootstrap-and-service/SKILL.md`.

The four layers and their mandates:

| Layer | Mandate |
|---|---|
| **Domain** | Pure business rules, aggregates, value objects, domain services, errors as values; no I/O |
| **Application Service** | Orchestrates one use case: parses input, calls domain + repository ports, returns typed results; no HTTP or DB knowledge |
| **Adapter** | Implements a port interface defined by the service layer; translates protocol details (HTTP status codes, CLI flags) to/from service calls; no business logic |
| **Composition Root** | The only place that imports concrete classes; constructs and injects all dependencies; runs once at startup |

---

## TypeScript

```typescript
// domain.ts — pure logic, no I/O
export type Order = { id: string; total: number };
export type InsufficientFunds = { kind: "InsufficientFunds"; balance: number };

export function placeOrder(order: Order, balance: number): Order | InsufficientFunds {
  if (balance < order.total) return { kind: "InsufficientFunds", balance };
  return order;
}

// ports.ts — interfaces owned by the service layer (not the adapter)
export interface OrderRepository {
  getBalance(customerId: string): Promise<number>;
}

// service.ts — application service: orchestrates, does not own rules
export class OrderService {
  constructor(private readonly repo: OrderRepository) {}

  async place(raw: unknown): Promise<Order | InsufficientFunds | ParseError> {
    const parsed = parseOrder(raw); // parse-don't-validate
    if (parsed.kind === "ParseError") return parsed;
    const balance = await this.repo.getBalance(parsed.customerId);
    return placeOrder(parsed, balance); // domain function owns the rule
  }
}

// adapter.ts — thin HTTP adapter; maps protocol, calls service
async function handlePlaceOrder(req: Request, res: Response) {
  const result = await orderService.place(req.body);
  if (result.kind === "InsufficientFunds") return res.status(422).json(result);
  if (result.kind === "ParseError") return res.status(400).json(result);
  res.status(201).json(result);
}

// bootstrap.ts — Composition Root; the only file that knows about Postgres
const repo = new PostgresOrderRepository(process.env.DATABASE_URL);
const orderService = new OrderService(repo);
app.post("/orders", handlePlaceOrder);
```

---

## Python

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

---

## Rust

```rust
// domain.rs — pure logic, no I/O
#[derive(Debug, serde::Serialize)]
pub struct Order { pub id: String, pub total: f64 }

#[derive(Debug)]
pub enum PlaceResult {
    Success(Order),
    InsufficientFunds { balance: f64 },
}

pub fn place_order(order: Order, balance: f64) -> PlaceResult {
    if balance < order.total {
        PlaceResult::InsufficientFunds { balance }
    } else {
        PlaceResult::Success(order)
    }
}

// ports.rs — traits owned by the service crate (not the adapter)
use async_trait::async_trait;

#[async_trait]
pub trait OrderRepository: Send + Sync {
    async fn get_balance(&self, customer_id: &str) -> anyhow::Result<f64>;
}

// service.rs — application service: orchestrates, does not own rules
use std::sync::Arc;

pub struct OrderService {
    repo: Arc<dyn OrderRepository>,
}

impl OrderService {
    pub fn new(repo: Arc<dyn OrderRepository>) -> Self {
        OrderService { repo }
    }

    pub async fn place(&self, raw: &serde_json::Value) -> anyhow::Result<PlaceResult> {
        let order = parse_order(raw)?;                      // parse-don't-validate
        let customer_id = raw["customer_id"]
            .as_str()
            .ok_or_else(|| anyhow::anyhow!("customer_id required"))?;
        let balance = self.repo.get_balance(customer_id).await?;
        Ok(place_order(order, balance))                     // domain function owns the rule
    }
}

// adapter.rs — thin Axum handler; maps protocol, calls service
use axum::{extract::State, http::StatusCode, response::IntoResponse, Json};
use serde_json::json;

pub async fn handle_place_order(
    State(svc): State<Arc<OrderService>>,
    Json(body): Json<serde_json::Value>,
) -> impl IntoResponse {
    match svc.place(&body).await {
        Ok(PlaceResult::Success(order)) =>
            (StatusCode::CREATED, Json(order)).into_response(),
        Ok(PlaceResult::InsufficientFunds { balance }) =>
            (StatusCode::UNPROCESSABLE_ENTITY, Json(json!({ "balance": balance }))).into_response(),
        Err(e) =>
            (StatusCode::BAD_REQUEST, e.to_string()).into_response(),
    }
}

// main.rs — Composition Root; the only file that knows about Postgres
#[tokio::main]
async fn main() {
    let repo = Arc::new(PostgresOrderRepository::new(
        &std::env::var("DATABASE_URL").expect("DATABASE_URL must be set"),
    ));
    let svc = Arc::new(OrderService::new(repo));

    let app = axum::Router::new()
        .route("/orders", axum::routing::post(handle_place_order))
        .with_state(svc);

    let listener = tokio::net::TcpListener::bind("0.0.0.0:3000").await.unwrap();
    axum::serve(listener, app).await.unwrap();
}
```
