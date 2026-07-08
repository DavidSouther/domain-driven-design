# Emitting logs

## Overview

A log record is a wide structured event that maps to the OpenTelemetry log data model.
Every emit site is constructing one of these events.
The call site's job is small and fixed: choose a severity, attach the right fields under the right keys, and name it.
Trace context (`TraceId`, `SpanId`, `TraceFlags`) comes from the active span.
The collector configuration manages the record destination.

## When to use

- Tracing the inputs to a request, command, or unit of work in domain or app code.
- Recording the outcome of a request, command, or unit of work in domain or app code.
- Surfacing an error at the boundary where it escapes a scenario or situation.
- Naming a business event the backend can count.
  Examples include `order.placed`, `payment.declined`, and `feature_flag.evaluated`.
- During review, code that uses `println!`, `console.log`, `print()`, or `info!("…{}…", x)` interpolation.

**When NOT to use:** to set up the pipeline, attach resource attributes, install propagators, or configure exporters.
Those belong in the configuring-logging pattern (`references/patterns/configuring-logging.md`).
A log call site never names the logging destination.

## Core pattern

Structured fields, never string interpolation.
Field names come from the OpenTelemetry semantic conventions; the message body is a stable human-readable string and never carries variable values.
When the event represents a business occurrence, give it an `EventName` so the backend can count it without parsing the body.

```rust
// Span scope is the unit of work; events inside inherit TraceId and SpanId.
#[tracing::instrument(skip_all, fields(http.route = "/orders", user.id = %req.user_id))]
async fn create_order(req: CreateOrderReq) -> Result<OrderId, PlaceOrderError> {
    let order_id = orders::place(&req).await?;

    // Success: structured fields under semantic-convention keys; the message
    // is stable; the EventName is the business name in ubiquitous language.
    tracing::info!(
        name: "order.placed",
        http.request.method = "POST",
        http.response.status_code = 201,
        order.id = %order_id,
        "order placed"
    );
    Ok(order_id)
}

// Failure: log the full chain once, here, at the boundary. Render via
// `error = &err as &dyn std::error::Error` and let the subscriber walk
// `Error::source()`. Attach the error type explicitly under the OTel
// exception conventions; do not log-and-rethrow.
match create_order(req).await {
    Err(err) => tracing::error!(
        name: "order.placement_failed",
        error.type = std::any::type_name_of_val(&err),
        exception.type = std::any::type_name_of_val(&err),
        error = &err as &dyn std::error::Error,
        "order placement failed"
    ),
    _ => {}
}
```

The newtype's `Display` impl renders the user identifier.
See the newtype pattern for details (`references/patterns/newtype.md`).
A `Secret<T>` renders `[REDACTED]` automatically because the type carries the safety property.
Never use `expose_secret()` on the way to a log call.
For complete examples, see [`emitting-logs/rust.md`](emitting-logs/rust.md), [`emitting-logs/typescript.md`](emitting-logs/typescript.md), and [`emitting-logs/python.md`](emitting-logs/python.md).

## Quick reference

### Severity

| `SeverityNumber` | Name  | Policy | Command-line tool verbosity |
|---|---|---|---|
| 1–4   | TRACE | Per-iteration loops, fine-grained internal state. Off by default everywhere. | `-vvvv` |
| 5–8   | DEBUG | Decisions a developer needs while diagnosing. Off in production by default. | `-vvv` |
| 9–12  | INFO  | One per unit of work: request handled, command completed, job finished. | `-vv` |
| 13–16 | WARN  | Recoverable surprise: retry hit, fallback used, deprecated path. | `-v` |
| 17–20 | ERROR | A use scenario failed. The exit code reports; the log explains. | default |
| 21–24 | FATAL | Process cannot continue. Followed by exit. | default |

Command-line tool defaults follow `clap-verbosity-flag` and clig.dev §Output: error is the surfaced floor; `-q` silences.
A two-level policy (INFO + ERROR only) is also fine for services that prefer span attributes over WARN/DEBUG records.
Choose this for the project and record it in the project's DEVELOPER.md or similar documentation.

### Field selection (OpenTelemetry semantic conventions)

| Operation | Keys |
|---|---|
| HTTP server / client | `http.request.method`, `http.route`, `http.response.status_code`, `url.path`, `url.scheme`, `network.peer.address` |
| Database | `db.system.name`, `db.namespace`, `db.collection.name`, `db.operation.name`, `db.query.summary` |
| RPC | `rpc.system`, `rpc.service`, `rpc.method`, `rpc.grpc.status_code` |
| Messaging | `messaging.system`, `messaging.destination.name`, `messaging.operation.name` |
| Exception | `exception.type`, `exception.message`, `exception.stacktrace` |
| Errors (general) | `error.type` |
| Identity (your domain) | `user.id`, `session.id`, `tenant.id` (or your bounded-context equivalent) |
| Business event | `EventName`. Examples: `order.placed`, `payment.declined`, `auth.denied`. |

Hard-code nothing in the response, the framework, or the domain object can supply.
`http.response.status_code` reads from the actual `StatusCode` value; `user.id` reads through a `UserId` newtype's `Display` impl.
Drift between log fields and reality starts the moment a call site embeds a literal `201` next to a response that may someday return `202`.

## Emit-site practices

### Spans and units of work

Open a span at every unit of work: request entry, RPC call, DB transaction, background-job iteration.
Every event emitted inside the span inherits its `TraceId` and `SpanId` automatically.
Use `#[instrument(skip_all, fields(...))]` to mark your span.
Equivalent approaches use `with_span` in Pino and `structlog.contextvars` in Python.
Pull the right fields onto the span itself so child events do not need to repeat them.

`#[instrument(skip(...))]` exists to omit *large* arguments for performance, never to suppress secrets.
Wrapped secrets are already safe by type.
If reaching for `skip` near a `Secret<T>` feels load-bearing, the upstream parse boundary is what is wrong, not the log line.

### Error chains

Log the full chain once at the boundary where the error escapes the use scenario.
When you pass the structured `error` field, the subscriber walks `Error::source()` in Rust, `cause` in TypeScript, or `__cause__` in Python.
For TypeScript, use the `Error` interface with the `cause:` option; for Python, use `raise X from e`.
Attach `error.type` and `exception.type` explicitly so the backend can group failures without parsing the message.

Do not log-and-rethrow.
Each emit duplicates the chain; the second copy is grep-noise and the dashboards count one failure as two.
If a caller needs context, attach it via the error type's `from`/`context` constructor, not via a second log call.

### Business events

A business event carries a stable name in the ubiquitous language: `order.placed`, `payment.declined`, `feature_flag.evaluated`, `auth.denied`.
The OpenTelemetry `EventName` field specifies this.
In Rust `tracing` macros, use the `name:` directive.
In Pino, use the `event_name` mixin.
In structlog, add a key in the bound context.
The backend pivots on this field to derive metrics.
The body of the message is for humans; the `EventName` is for the count, the rate, and the SLO.

### Hot loops

Never emit per iteration.
Aggregate to one summary log per batch with the per-item count, success/failure breakdown, and total duration as fields.
Pair this summary with a progress UI: `indicatif` or `tracing-indicatif` for command-line tools, or a metric counter for services.

### Severity policy

Pick a policy and write it down.
Two policies are common.
The full ladder of TRACE/DEBUG/INFO/WARN/ERROR/FATAL is useful when WARN is operationally meaningful.
A two-level version uses INFO and ERROR and is useful when WARN is not worth distinguishing.
Reviewing severities is easier when "level by mood" is not on the table.

## Common mistakes

- **String interpolation in the message body.**
  `info!("handled {} for {}", req.path, user_id)` flattens the structured event into a free-text line.
  Move the values to fields under semantic-convention keys; keep the body stable.
- **Ad-hoc field names.**
  You invent `method = "POST"` as custom vocabulary; `http.request.method` is the OpenTelemetry semantic convention.
  The backend knows the latter; metrics derive from it.
  Use the table preceding this as the lookup.
- **Hard-coded literals where the value is in scope.**
  `status = 201` next to a response that *might* return `202` desyncs silently.
  Read `http.response.status_code` from the actual response value.
- **Logging an unwrapped secret.**
  `expose_secret()` near a logger is evidence of an upstream parse-boundary failure.
  Fix it at the boundary; secrets carry their `[REDACTED]` `Debug` impl through to every emit site.
  Refer to the parse-dont-validate pattern (`references/patterns/parse-dont-validate.md`).
- **Log-and-rethrow.**
  A failure logged at the inner layer and again at the outer layer counts twice on the dashboard.
  Log the chain once at the boundary that owns the scenario or situation.
- **Level by mood.**
  Severity is a policy, not a feeling.
  Either the full ladder or two-level (INFO + ERROR); write it down.
- **Per-iteration in hot loops.**
  A million-row loop emitting one log per row is a denial of service against your own backend.
  Aggregate to one summary; pair with a progress UI.
- **Defaulting command-line tool output to INFO.**
  `clap-verbosity-flag` and clig.dev §Output put ERROR at the floor for command-line tools.
  INFO is `-vv`, not the default.
- **Embedding non-deterministic fields in command-line tool stdout.**
  Timestamps, trace IDs, and durations turn snapshot tests into flake generators.
  Honor `SOURCE_DATE_EPOCH` or expose `--no-timestamps` for tests; keep diagnostics on stderr where they belong.
- **Treating `error!` as the failure signal.**
  A command-line tool's failure signal is the exit code.
  Refer to sysexits.h for conventions: `EX_USAGE=64`, `EX_DATAERR=65`, `EX_NOINPUT=66`, and others.
  The log explains the problem; the exit code is the final output.
- **Skipping `EventName` on a business outcome.**
  Without an `EventName`, the event has a body but no name; the backend cannot count it as a specific object or concept without parsing strings.
  Name it in the ubiquitous language.

## Composes with

- **the configuring-logging pattern (`references/patterns/configuring-logging.md`)**: the bootstrap partner.
  Configuration sets the envelope, the exporter, and the propagator.
  Emission attaches the per-event fields the configuration enforces.
  One without the other produces structured logs that are not queryable, or queryable logs that are not centralized.
- **the errors-typed-untyped pattern (`references/patterns/errors-typed-untyped.md`)**: typed errors render via `error.type` and `exception.*`.
  The chain is the API; the emit site is where the chain becomes a record.
- **the newtype pattern (`references/patterns/newtype.md`)**: newtype `Display` impls produce stable, semantic-convention-shaped attribute values (`UserId` → `user.id`, `OrderId` → `order.id`).
  Identifiers do not become strings until the moment of emission.
- **the domain-objects pattern (`references/patterns/domain-objects.md`)**: entities and value objects supply the field values; `Secret<T>` arrives wrapped, never unwrapped near a logger.
