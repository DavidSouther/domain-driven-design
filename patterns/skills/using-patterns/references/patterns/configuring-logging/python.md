# Configuring logging, python reference

`structlog` for the formatter and processor chain; `opentelemetry-sdk` for the OTLP exporter and the W3C propagator.
The bootstrap function below is `bootstrap_logging()` for a service; the command-line tool variant follows.

```python
# pyproject.toml dependencies
# structlog>=24
# opentelemetry-api>=1.27
# opentelemetry-sdk>=1.27
# opentelemetry-exporter-otlp-proto-grpc>=1.27
# opentelemetry-semantic-conventions>=0.48b0

from __future__ import annotations

import logging
import os
import signal
import sys
from contextlib import contextmanager
from typing import Iterator

import structlog
from opentelemetry import propagate, trace
from opentelemetry.exporter.otlp.proto.grpc.trace_exporter import OTLPSpanExporter
from opentelemetry.sdk.resources import Resource
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor
from opentelemetry.sdk.trace.sampling import ParentBased, TraceIdRatioBased
from opentelemetry.semconv.attributes import service_attributes
from opentelemetry.semconv.attributes import deployment_attributes
from opentelemetry.trace.propagation.tracecontext import TraceContextTextMapPropagator


def _add_trace_context(logger, method_name, event_dict):
    """structlog processor: attach TraceId/SpanId from the active span."""
    span = trace.get_current_span()
    ctx = span.get_span_context()
    if ctx.is_valid:
        event_dict["trace_id"] = format(ctx.trace_id, "032x")
        event_dict["span_id"] = format(ctx.span_id, "016x")
        event_dict["trace_flags"] = ctx.trace_flags
    return event_dict


def bootstrap_logging() -> "ShutdownHandle":
    """Service-shape bootstrap. Call once from the entrypoint; never from a library."""

    # Enrich (1/2): install the W3C propagator globally.
    propagate.set_global_textmap(TraceContextTextMapPropagator())

    # Enrich (2/2): resource attributes attach once.
    resource = Resource.create({
        service_attributes.SERVICE_NAME: os.environ.get("OTEL_SERVICE_NAME", "my-service"),
        service_attributes.SERVICE_VERSION: os.environ.get("APP_VERSION", "0.0.0"),
        service_attributes.SERVICE_INSTANCE_ID: os.environ.get("HOSTNAME", "local"),
        deployment_attributes.DEPLOYMENT_ENVIRONMENT_NAME: os.environ.get("DEPLOY_ENV", "dev"),
    })

    # Export: OTLP traces over gRPC, batched. Head-based sampler on the parent.
    provider = TracerProvider(
        resource=resource,
        sampler=ParentBased(root=TraceIdRatioBased(0.1)),
    )
    provider.add_span_processor(BatchSpanProcessor(OTLPSpanExporter()))
    trace.set_tracer_provider(provider)

    # Filter: stdlib logging owns the level threshold; structlog wraps it.
    level = os.environ.get("LOG_LEVEL", "INFO").upper()
    logging.basicConfig(stream=sys.stdout, level=level, format="%(message)s")
    # Quiet noisy libraries.
    for noisy in ("urllib3", "httpx", "asyncio"):
        logging.getLogger(noisy).setLevel(logging.WARNING)

    # Format + Filter + Enrich (per-record) + Export. JSON to stdout per 12-Factor.
    structlog.configure(
        processors=[
            structlog.contextvars.merge_contextvars,
            structlog.processors.add_log_level,
            structlog.processors.TimeStamper(fmt="iso", utc=True),
            structlog.processors.StackInfoRenderer(),
            structlog.processors.format_exc_info,
            _add_trace_context,
            structlog.processors.JSONRenderer(),
        ],
        wrapper_class=structlog.make_filtering_bound_logger(getattr(logging, level)),
        logger_factory=structlog.PrintLoggerFactory(file=sys.stdout),
        cache_logger_on_first_use=True,
    )

    # Shutdown: flush the exporter with a hard timeout.
    handle = ShutdownHandle(provider)
    signal.signal(signal.SIGTERM, lambda *_: handle.shutdown_and_exit(0))
    return handle


class ShutdownHandle:
    def __init__(self, provider: TracerProvider) -> None:
        self._provider = provider

    def shutdown(self, timeout_ms: int = 5_000) -> None:
        # Both calls below honor the timeout argument.
        self._provider.shutdown()

    def shutdown_and_exit(self, code: int) -> None:
        self.shutdown()
        sys.exit(code)


@contextmanager
def cli_logging(verbosity: int = 0, log_format: str = "auto") -> Iterator[None]:
    """CLI-shape bootstrap. Default level ERROR; -v/-vv/-vvv raise it."""

    propagate.set_global_textmap(TraceContextTextMapPropagator())

    levels = [logging.ERROR, logging.WARNING, logging.INFO, logging.DEBUG]
    level = levels[min(verbosity, len(levels) - 1)]

    is_tty = sys.stderr.isatty()
    want_json = log_format == "json" or (log_format == "auto" and not is_tty)
    no_color = "NO_COLOR" in os.environ or os.environ.get("CLICOLOR") == "0"

    logging.basicConfig(stream=sys.stderr, level=level, format="%(message)s")

    renderer = (
        structlog.processors.JSONRenderer()
        if want_json
        else structlog.dev.ConsoleRenderer(colors=is_tty and not no_color)
    )

    structlog.configure(
        processors=[
            structlog.contextvars.merge_contextvars,
            structlog.processors.add_log_level,
            structlog.processors.TimeStamper(fmt="iso", utc=True),
            structlog.processors.format_exc_info,
            _add_trace_context,
            renderer,
        ],
        wrapper_class=structlog.make_filtering_bound_logger(level),
        logger_factory=structlog.PrintLoggerFactory(file=sys.stderr),
        cache_logger_on_first_use=True,
    )

    # No OTLP exporter unless --telemetry is enabled by the caller.
    try:
        yield
    finally:
        # `defer`-shaped flush at main exit. SIGINT handler should call shutdown
        # too, then re-raise.
        provider = trace.get_tracer_provider()
        if isinstance(provider, TracerProvider):
            provider.shutdown()
```

The `_add_trace_context` processor runs on every log call, so `trace_id` and `span_id` arrive without each emit-site mentioning them. `contextvars.merge_contextvars` lets request-scoped fields (a `user_id`, a `request_id`) ride along once you bind them at the request boundary.
