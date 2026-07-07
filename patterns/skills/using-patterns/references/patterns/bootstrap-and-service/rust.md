# Bootstrap and service, Rust reference

The four layers and their mandates:

| Layer | Mandate |
|---|---|
| **Domain** | Pure business rules, aggregates, value objects, domain services, errors as values; no I/O |
| **Application Service** | Orchestrates one use scenario: parses input, calls domain + repository ports, returns typed results; no HTTP or DB knowledge |
| **Adapter** | Implements a port interface defined by the service layer; translates protocol details (HTTP status codes, command-line flags) to/from service calls; no business logic |
| **Composition Root** | The only place that imports concrete classes; constructs and injects all dependencies; runs once at startup |

```rust
// domain.rs: pure logic, no I/O
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

// ports.rs: traits owned by the service crate (not the adapter)
use async_trait::async_trait;

#[async_trait]
pub trait OrderRepository: Send + Sync {
    async fn get_balance(&self, customer_id: &str) -> anyhow::Result<f64>;
}

// service.rs: application service: orchestrates, does not own rules
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

// adapter.rs: thin Axum handler; maps protocol, calls service
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

// main.rs: Composition Root; the only file that knows about Postgres
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
