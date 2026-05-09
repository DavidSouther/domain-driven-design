# Emitting Logs — Python Reference

`structlog` bound loggers carry per-request context; `contextvars` propagate it across `await` boundaries without each call site re-attaching it. The configuration skill's `_add_trace_context` processor already attaches `trace_id`/`span_id` from the active span; emit sites only add the per-event fields. Error chains render via `log.exception(...)` (which captures `sys.exc_info()`) plus explicit `error.type` / `exception.type` keys for OTel grouping.

```python
from __future__ import annotations

import time
from dataclasses import dataclass
from typing import NewType
from uuid import UUID, uuid4

import structlog
from opentelemetry import trace

# Newtype-equivalent. `patterns:newtype` owns the discipline; the logger reads
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

`structlog.contextvars.bind_contextvars` plus an ASGI/WSGI middleware that calls it per request gives every emit site inside the request the same set of fields without an explicit `log = log.bind(...)` call. The kwargs that contain a dot are passed through `**{}` so the field key carries the OTel semantic convention literally; the message string stays free of interpolation.
