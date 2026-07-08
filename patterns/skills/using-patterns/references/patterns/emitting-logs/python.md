# Emitting logs: Python reference

`structlog` bound loggers hold per-request context.
`contextvars` spread it across `await` boundaries so each call doesn't need to attach it again.
The configuration skill's `_add_trace_context` processor adds `trace_id`/`span_id` from the active span.
Emit sites only add the per-event fields.
Render error chains with `log.exception(...)` to capture `sys.exc_info()`.
Add explicit `error.type` and `exception.type` keys for OTel grouping.

```python
from __future__ import annotations

import time
from dataclasses import dataclass
from typing import NewType
from uuid import UUID, uuid4

import structlog
from opentelemetry import trace

# Newtype-equivalent. the newtype pattern (`references/patterns/newtype.md`) owns the discipline; the logger reads
# through them via __str__.
UserId = NewType("UserId", UUID)
OrderId = NewType("OrderId", UUID)


@dataclass(frozen=True)
class CreateOrderReq:
    user_id: UserId
    items: tuple[str, ...]


class PlaceOrderError(Exception):
    """Boundary error type; chains via `raise X from e`."""


class InventoryError(Exception):
    """Lower-level cause."""


tracer = trace.get_tracer(__name__)
log = structlog.get_logger()


async def create_order(req: CreateOrderReq) -> tuple[int, OrderId]:
    # Bind the unit-of-work fields once via contextvars. Every event emitted
    # under this binding inherits the fields; the per-event call adds only
    # what is specific to the outcome.
    structlog.contextvars.clear_contextvars()
    structlog.contextvars.bind_contextvars(
        **{
            "http.request.method": "POST",
            "http.route": "/orders",
            "user.id": str(req.user_id),
        }
    )

    with tracer.start_as_current_span("create_order"):
        try:
            order_id = await _place_order(req)
            status = 201

            log.info(
                "order placed",
                event_name="order.placed",
                **{
                    "http.response.status_code": status,
                    "order.id": str(order_id),
                },
            )
            return status, order_id

        except PlaceOrderError:
            # Log the full chain once, at the boundary. `log.exception` captures
            # sys.exc_info() so `__cause__` / `__context__` are walked into
            # `exception.stacktrace`. `error.type` and `exception.type` are
            # the OTel keys the backend groups failures by.
            log.exception(
                "order placement failed",
                event_name="order.placement_failed",
                **{
                    "error.type": "PlaceOrderError",
                    "exception.type": "PlaceOrderError",
                },
            )
            raise  # bubbles to the framework; this is the only emit site


async def _place_order(req: CreateOrderReq) -> OrderId:
    if not req.items:
        try:
            raise InventoryError("no items in request")
        except InventoryError as cause:
            raise PlaceOrderError("inventory check failed") from cause
    return OrderId(uuid4())


# Hot-loop pattern: never per-iteration. Aggregate to one summary log per batch.
async def process_batch(items: tuple[str, ...]) -> None:
    started = time.perf_counter()
    succeeded = 0
    failed = 0

    for item in items:
        try:
            await _process_one(item)
            succeeded += 1
        except Exception:
            failed += 1

    log.info(
        "batch processed",
        event_name="batch.processed",
        **{
            "batch.size": len(items),
            "batch.succeeded": succeeded,
            "batch.failed": failed,
            "duration_ms": int((time.perf_counter() - started) * 1000),
        },
    )


async def _process_one(_: str) -> None:
    return None
```

`structlog.contextvars.bind_contextvars` plus an ASGI/WSGI middleware that calls it per request gives every emit site inside the request the same set of fields.
This eliminates the need for an explicit `log = log.bind(...)` call.
Pass kwargs that contain a dot through `**{}` so the field key carries the OTel semantic convention literally.
The message string stays free of interpolation.
