# Configuring logging - rust reference

`tracing` plus `tracing-subscriber` provides the five-layer stack.
`tracing-opentelemetry` bridges spans to OpenTelemetry; `opentelemetry-otlp` exports them.
The bootstrap function below is `bootstrap_logging()` for a service; the command-line tool variant follows.

```rust
// Cargo.toml
// tracing = "0.1"
// tracing-subscriber = { version = "0.3", features = ["env-filter", "json", "registry"] }
// tracing-opentelemetry = "0.27"
// opentelemetry = "0.26"
// opentelemetry-otlp = { version = "0.26", features = ["tonic", "trace"] }
// opentelemetry_sdk = { version = "0.26", features = ["rt-tokio"] }
// anyhow = "1"

use anyhow::Result;
use opentelemetry::{global, KeyValue};
use opentelemetry_otlp::WithExportConfig;
use opentelemetry_sdk::{
    propagation::TraceContextPropagator,
    runtime,
    trace::{self, Sampler},
    Resource,
};
use tracing_subscriber::{fmt, prelude::*, EnvFilter};

/// Service-shape bootstrap. Call once from `main`; never from a library.
pub fn bootstrap_logging() -> Result<ShutdownGuard> {
    // Enrich (1/2): install the W3C propagator once, globally. Any framework
    // middleware (axum's TraceLayer, tonic's interceptors) will then extract
    // `traceparent` on inbound calls and inject it on outbound ones without
    // call-site code.
    global::set_text_map_propagator(TraceContextPropagator::new());

    // Enrich (2/2): resource attributes attach once, never per record.
    let resource = Resource::new(vec![
        KeyValue::new("service.name", env!("CARGO_PKG_NAME")),
        KeyValue::new("service.version", env!("CARGO_PKG_VERSION")),
        KeyValue::new(
            "service.instance.id",
            std::env::var("HOSTNAME").unwrap_or_else(|_| "local".into()),
        ),
        KeyValue::new(
            "deployment.environment",
            std::env::var("DEPLOY_ENV").unwrap_or_else(|_| "dev".into()),
        ),
    ]);

    // Export: OTLP traces over gRPC. Head-based sampling on the parent;
    // a 10% sampler on roots. Coordinate this with the log sampler (here
    // the EnvFilter) so wide-event recovery holds.
    let tracer = opentelemetry_otlp::new_pipeline()
        .tracing()
        .with_exporter(
            opentelemetry_otlp::new_exporter()
                .tonic()
                .with_endpoint(
                    std::env::var("OTEL_EXPORTER_OTLP_ENDPOINT")
                        .unwrap_or_else(|_| "http://localhost:4317".into()),
                ),
        )
        .with_trace_config(
            trace::config()
                .with_resource(resource)
                .with_sampler(Sampler::ParentBased(Box::new(
                    Sampler::TraceIdRatioBased(0.1),
                ))),
        )
        .install_batch(runtime::Tokio)?;

    // Filter: noisy dependencies are explicitly quieted. Operators tune via
    // RUST_LOG without recompiling.
    let filter = EnvFilter::try_from_default_env()
        .unwrap_or_else(|_| EnvFilter::new("info,hyper=warn,h2=warn,tower=warn"));

    // Registry + Format + Filter + Enrich + Export. Five layers, one init.
    tracing_subscriber::registry()
        .with(filter)
        .with(fmt::layer().json().with_current_span(true).with_span_list(false))
        .with(tracing_opentelemetry::layer().with_tracer(tracer))
        .init();

    Ok(ShutdownGuard)
}

/// RAII guard that flushes the exporter on drop. SIGTERM handlers should also
/// call `global::shutdown_tracer_provider()` directly so the timeout fires
/// even if the runtime is mid-shutdown.
pub struct ShutdownGuard;

impl Drop for ShutdownGuard {
    fn drop(&mut self) {
        global::shutdown_tracer_provider();
    }
}

// CLI variant: the registry stays the same, the layers above it differ.
//
// fn bootstrap_logging_cli(verbosity: tracing::level_filters::LevelFilter) {
//     global::set_text_map_propagator(TraceContextPropagator::new());
//
//     let stderr_is_tty = std::io::IsTerminal::is_terminal(&std::io::stderr());
//     let want_json = std::env::var("LOG_FORMAT").as_deref() == Ok("json")
//         || !stderr_is_tty;
//
//     let filter = EnvFilter::builder()
//         .with_default_directive(verbosity.into())
//         .from_env_lossy()
//         .add_directive("hyper=warn".parse().unwrap())
//         .add_directive("reqwest=warn".parse().unwrap());
//
//     let resource = Resource::new(vec![
//         KeyValue::new("process.executable.name", env!("CARGO_PKG_NAME")),
//         KeyValue::new("process.runtime.name", "rust"),
//         KeyValue::new("process.pid", std::process::id() as i64),
//     ]);
//     // (resource is attached only if `--telemetry` enables an OTLP exporter)
//
//     let registry = tracing_subscriber::registry().with(filter);
//     if want_json {
//         registry
//             .with(fmt::layer().json().with_writer(std::io::stderr))
//             .init();
//     } else {
//         registry
//             .with(fmt::layer().with_writer(std::io::stderr).with_ansi(stderr_is_tty))
//             .init();
//     }
// }
```

The `clap-verbosity-flag` crate maps `-q`/`-v`/`-vv`/`-vvv`/`-vvvv` onto a `tracing::LevelFilter`; pass it into `bootstrap_logging_cli`.
Default is `ErrorLevel`, which surfaces ERROR and FATAL only, the clig.dev §Output convention.
