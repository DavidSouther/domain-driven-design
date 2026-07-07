# Emitting logs: TypeScript reference

`pino` child loggers carry per-request context. The configuration skill's `mixin` already attaches `trace_id`/`span_id` from the active span; emit sites only add the per-event fields. Log errors via `logger.error({ err }, msg)`. pino serializes `Error.cause` chains automatically. Add semantic-convention keys explicitly under the OTel exception namespace.

```ts
import type { Logger } from "pino";
import { trace, SpanStatusCode } from "@opentelemetry/api";

// Newtype-equivalent: branded types keep ids from blurring at the type level.
// the newtype pattern (`references/patterns/newtype.md`) owns this; the logger reads through them.
type UserId = string & { readonly __brand: "UserId" };
type OrderId = string & { readonly __brand: "OrderId" };

interface CreateOrderReq {
  readonly userId: UserId;
  readonly items: readonly string[];
}

class PlaceOrderError extends Error {
  readonly name = "PlaceOrderError";
  constructor(message: string, options?: { cause?: unknown }) {
    super(message, options);
  }
}

interface OrderResponse {
  readonly orderId: OrderId;
}

export async function createOrder(
  req: CreateOrderReq,
  log: Logger,
): Promise<{ status: number; body: OrderResponse }> {
  // Child logger carries the unit-of-work fields once. Every emit on `req_log`
  // inherits them; the call site below adds only the outcome.
  const reqLog = log.child({
    "http.request.method": "POST",
    "http.route": "/orders",
    "user.id": req.userId,
  });

  // OTel span is the unit of work; `mixin` in the configured logger attaches
  // trace_id/span_id to every record automatically.
  const tracer = trace.getTracer("orders");
  return await tracer.startActiveSpan("create_order", async (span) => {
    try {
      const orderId = await placeOrder(req);
      const status = 201;

      reqLog.info(
        {
          event_name: "order.placed",
          "http.response.status_code": status,
          "order.id": orderId,
        },
        "order placed",
      );

      span.end();
      return { status, body: { orderId } };
    } catch (err) {
      // Log the full chain once, at the boundary. pino's standard error
      // serializer walks `Error.cause` and renders the chain as structured
      // fields. The OTel exception keys are added explicitly so the backend
      // can group failures without parsing the message.
      reqLog.error(
        {
          event_name: "order.placement_failed",
          "error.type": err instanceof Error ? err.name : "unknown",
          "exception.type": err instanceof Error ? err.name : "unknown",
          err,
        },
        "order placement failed",
      );

      span.setStatus({ code: SpanStatusCode.ERROR });
      span.recordException(err as Error);
      span.end();
      throw err; // bubbles to the framework's error handler; not log-and-rethrow
                 // because this is the only emit site for the chain.
    }
  });
}

async function placeOrder(req: CreateOrderReq): Promise<OrderId> {
  if (req.items.length === 0) {
    throw new PlaceOrderError("no items", {
      cause: new Error("inventory check failed"),
    });
  }
  return "00000000-0000-0000-0000-000000000000" as OrderId;
}

// Hot-loop pattern: never per-iteration. Aggregate to one summary log per batch.
export async function processBatch(items: readonly string[], log: Logger) {
  const started = process.hrtime.bigint();
  let succeeded = 0;
  let failed = 0;

  for (const item of items) {
    try {
      await processOne(item);
      succeeded += 1;
    } catch {
      failed += 1;
    }
  }

  log.info(
    {
      event_name: "batch.processed",
      "batch.size": items.length,
      "batch.succeeded": succeeded,
      "batch.failed": failed,
      duration_ms: Number((process.hrtime.bigint() - started) / 1_000_000n),
    },
    "batch processed",
  );
}

async function processOne(_: string): Promise<void> {
  /* ... */
}
```

`logger.child({...})` is the canonical way to bind unit of work context once; the per-event call adds only the outcome fields. `event_name` is the field name the OTel JS SDK uses for the log record's `EventName`. The underlying logs spec calls it `event.name`. Pin the field name to whatever the configured exporter understands.
