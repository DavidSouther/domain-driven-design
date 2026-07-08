# Configuring logging, TypeScript reference

`pino` for the formatter and writer; `@opentelemetry/sdk-node` for the OTLP exporter and the W3C propagator.
Both shapes share the same module; the differences sit in the options.

```ts
// package.json
// "pino": "^9",
// "@opentelemetry/api": "^1",
// "@opentelemetry/sdk-node": "^0.55",
// "@opentelemetry/exporter-trace-otlp-grpc": "^0.55",
// "@opentelemetry/resources": "^1",
// "@opentelemetry/semantic-conventions": "^1.27",
// "@opentelemetry/core": "^1",

import pino, { type Logger } from "pino";
import { NodeSDK } from "@opentelemetry/sdk-node";
import { OTLPTraceExporter } from "@opentelemetry/exporter-trace-otlp-grpc";
import { Resource } from "@opentelemetry/resources";
import {
  ATTR_SERVICE_NAME,
  ATTR_SERVICE_VERSION,
  ATTR_DEPLOYMENT_ENVIRONMENT_NAME,
  ATTR_PROCESS_EXECUTABLE_NAME,
  ATTR_PROCESS_RUNTIME_NAME,
  ATTR_PROCESS_PID,
} from "@opentelemetry/semantic-conventions/incubating";
import { W3CTraceContextPropagator } from "@opentelemetry/core";
import { propagation, trace, context } from "@opentelemetry/api";

export interface LoggingHandle {
  log: Logger;
  shutdown: () => Promise<void>;
}

/** Service-shape bootstrap. Call once from the entrypoint. */
export async function initLogging(): Promise<LoggingHandle> {
  // Enrich: install the W3C propagator globally so HTTP/gRPC instrumentations
  // pick up `traceparent` without per-call header work.
  propagation.setGlobalPropagator(new W3CTraceContextPropagator());

  // Enrich: resource attributes attach once.
  const resource = new Resource({
    [ATTR_SERVICE_NAME]: process.env.OTEL_SERVICE_NAME ?? "my-service",
    [ATTR_SERVICE_VERSION]: process.env.npm_package_version ?? "0.0.0",
    [ATTR_DEPLOYMENT_ENVIRONMENT_NAME]: process.env.DEPLOY_ENV ?? "dev",
  });

  // Export: OTLP exporter via the SDK. The SDK also wires the global
  // tracer provider so `trace.getActiveSpan()` returns a real span.
  const sdk = new NodeSDK({
    resource,
    traceExporter: new OTLPTraceExporter({
      url: process.env.OTEL_EXPORTER_OTLP_ENDPOINT,
    }),
  });
  sdk.start();

  // Filter: pino's level reads from env; map LOG_LEVEL onto pino's vocabulary.
  const level = (process.env.LOG_LEVEL ?? "info") as pino.Level;

  // Format + Filter + Enrich (per-record): pino emits JSON to stdout (12-Factor)
  // with a custom mixin that pulls the active span's trace/span IDs onto every
  // record. This is the call-site free way to get TraceId/SpanId on logs.
  const log = pino({
    level,
    formatters: {
      level: (label) => ({ level: label }), // human-readable severity name
    },
    mixin() {
      const span = trace.getSpan(context.active());
      if (!span) return {};
      const { traceId, spanId, traceFlags } = span.spanContext();
      return { trace_id: traceId, span_id: spanId, trace_flags: traceFlags };
    },
    redact: {
      // Allowlist by allowing nothing structural here, plus a backstop blocklist.
      // The primary control is upstream typing (the parse-dont-validate pattern (`references/patterns/parse-dont-validate.md`)).
      paths: ["password", "token", "*.password", "*.token", "headers.authorization"],
      censor: "[REDACTED]",
    },
  });

  // Shutdown: flush both pino and the OTel SDK with a hard timeout.
  const shutdown = async () => {
    const timeoutMs = 5_000;
    await Promise.race([
      Promise.allSettled([
        new Promise<void>((res) => log.flush(() => res())),
        sdk.shutdown(),
      ]),
      new Promise<void>((res) => setTimeout(res, timeoutMs)),
    ]);
  };

  // Service shape: SIGTERM is the orchestrator's signal.
  process.on("SIGTERM", () => {
    void shutdown().finally(() => process.exit(0));
  });

  return { log, shutdown };
}

// CLI variant: same module, different defaults:
//
//   - Resource keys: ATTR_PROCESS_EXECUTABLE_NAME, ATTR_PROCESS_RUNTIME_NAME,
//     ATTR_PROCESS_PID instead of service.* keys.
//   - Default level: "error". Map -v/-vv/-vvv onto warn/info/debug from your
//     argument parser; -q silences.
//   - Writer: pino.destination(2) (stderr), with `pino-pretty` piped through
//     when stderr is a TTY (process.stderr.isTTY) and --log-format=json is not set.
//   - OTLP exporter only constructed when --telemetry is passed.
//   - Shutdown: register on `SIGINT` (Ctrl-C) and on the `beforeExit` event;
//     same hard timeout.
```

`mixin` runs on every log call, so the `TraceId`/`SpanId` arrive without each emit-site mentioning them. `redact` is the defense-in-depth backstop; the primary control is upstream typing of secrets.
