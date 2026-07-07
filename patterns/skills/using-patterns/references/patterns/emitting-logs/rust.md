# Logging in Rust

The `tracing` macros (`info!`, `error!`) attach structured fields directly. Use `#[instrument(skip_all, fields(...))]` to open a span; events inside inherit `TraceId` and `SpanId` from it. Define newtypes with `Display` impls to produce semantic-convention values. Use `Secret<T>` so its `Debug` impl renders `[REDACTED]`: the type, not the call site, carries the safety property.

```rust
use std::fmt;
use thiserror::Error;
use tracing::{error, info, instrument};

// Newtypes whose Display impls produce stable semantic-convention values.
// the newtype pattern (`references/patterns/newtype.md`) owns this; the logger reads through them.
#[derive(Clone, Copy)]
pub struct UserId(pub uuid::Uuid);
impl fmt::Display for UserId {
    fn fmt(&self, f: &mut fmt::Formatter<'_>) -> fmt::Result {
        write!(f, "{}", self.0.hyphenated())
    }
}

#[derive(Clone, Copy)]
pub struct OrderId(pub uuid::Uuid);
impl fmt::Display for OrderId {
    fn fmt(&self, f: &mut fmt::Formatter<'_>) -> fmt::Result {
        write!(f, "{}", self.0.hyphenated())
    }
}

#[derive(Debug, Error)]
pub enum PlaceOrderError {
    #[error("inventory check failed")]
    Inventory(#[source] InventoryError),
    #[error("payment authorization failed")]
    Payment(#[source] PaymentError),
}

#[derive(Debug, Error)]
#[error("inventory: {0}")]
pub struct InventoryError(String);

#[derive(Debug, Error)]
#[error("payment: {0}")]
pub struct PaymentError(String);

pub struct CreateOrderReq {
    pub user_id: UserId,
    pub items: Vec<String>,
}

pub struct OrderResponse {
    pub order_id: OrderId,
}

// Span scope is the unit of work. Fields on the span are inherited by every
// event inside, so `info!` and `error!` calls don't repeat them.
#[instrument(
    skip_all,
    fields(
        http.request.method = "POST",
        http.route = "/orders",
        user.id = %req.user_id,
    ),
)]
pub async fn create_order(
    req: CreateOrderReq,
) -> Result<(http::StatusCode, OrderResponse), PlaceOrderError> {
    let order_id = place_order(&req).await?;
    let status = http::StatusCode::CREATED;

    // Success: structured fields under semantic-convention keys; the message
    // body is stable; `name:` is the EventName the backend pivots on.
    info!(
        name: "order.placed",
        http.response.status_code = status.as_u16(),
        order.id = %order_id,
        "order placed",
    );

    Ok((status, OrderResponse { order_id }))
}

// Failure handler. Logs the full chain once, here, at the boundary where the
// error escapes the use case. `error = &err as &dyn std::error::Error` lets
// the subscriber walk Error::source() and render the chain as structured
// fields, not a flattened string. `error.type` / `exception.type` are the
// OpenTelemetry exception keys the backend groups failures by.
pub async fn handle(req: CreateOrderReq) -> http::StatusCode {
    match create_order(req).await {
        Ok((status, _)) => status,
        Err(err) => {
            error!(
                name: "order.placement_failed",
                error.type = std::any::type_name_of_val(&err),
                exception.type = std::any::type_name_of_val(&err),
                error = &err as &dyn std::error::Error,
                "order placement failed",
            );
            http::StatusCode::INTERNAL_SERVER_ERROR
        }
    }
}

async fn place_order(_: &CreateOrderReq) -> Result<OrderId, PlaceOrderError> {
    Ok(OrderId(uuid::Uuid::nil()))
}

// Hot-loop pattern: never per-iteration. Aggregate to one summary log per
// batch with the per-item count and total duration.
#[instrument(skip_all, fields(batch.size = items.len()))]
pub async fn process_batch(items: &[String]) {
    let started = std::time::Instant::now();
    let mut succeeded = 0usize;
    let mut failed = 0usize;

    for item in items {
        match process_one(item).await {
            Ok(()) => succeeded += 1,
            Err(_) => failed += 1,
        }
    }

    info!(
        name: "batch.processed",
        batch.succeeded = succeeded,
        batch.failed = failed,
        duration_ms = started.elapsed().as_millis() as u64,
        "batch processed",
    );
}

async fn process_one(_: &str) -> Result<(), ()> { Ok(()) }
```

`#[instrument(skip_all, fields(...))]` opts every argument out of the span by default and re-attaches only the values the convention asks for. `skip(...)` exists for *large* arguments, never to suppress secrets, wrapped secrets are already safe by their type's `Debug` impl.
