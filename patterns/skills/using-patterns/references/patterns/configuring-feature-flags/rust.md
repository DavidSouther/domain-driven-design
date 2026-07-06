# Configuring feature flags in Rust

The composition root builds one evaluation client behind a vendor-neutral port and injects it. Call sites receive the port, never a vendor SDK.

```rust
// flags.rs — the vendor-neutral port every call site reads through
pub struct FlagContext {
    pub environment: String,
    pub user_id: Option<String>,
}

pub trait Flags {
    fn enabled(&self, key: &str, default: bool, ctx: &FlagContext) -> bool;
}
```

```rust
// A backing that may fail. The fail-safe wrapper maps any error to the default.
pub trait FallibleFlags {
    fn try_enabled(&self, key: &str, ctx: &FlagContext) -> anyhow::Result<bool>;
}

pub struct FailSafe<P>(pub P);

impl<P: FallibleFlags> Flags for FailSafe<P> {
    fn enabled(&self, key: &str, default: bool, ctx: &FlagContext) -> bool {
        self.0.try_enabled(key, ctx).unwrap_or(default)
    }
}
```

```rust
// A fully runnable backing for local and CI.
use std::collections::HashMap;

pub struct StaticFlags {
    values: HashMap<String, bool>,
}

impl Flags for StaticFlags {
    fn enabled(&self, key: &str, default: bool, _ctx: &FlagContext) -> bool {
        self.values.get(key).copied().unwrap_or(default)
    }
}
```

```rust
// Built once at the composition root, then injected as a trait object.
pub fn build_flags(environment: &str) -> Box<dyn Flags> {
    // Production backs FallibleFlags with a vendor SDK or the OpenFeature Rust
    // SDK. If the backing evaluates asynchronously, make the trait method async.
    let mut values = HashMap::new();
    if environment == "local" {
        values.insert("release.checkout.new-flow".to_string(), true);
    }
    Box::new(StaticFlags { values })
}
```

The flag inventory (key, owner, expiry) lives beside this module, and a CI check fails any flag past its expiry.

## Cargo features: compile-time flags

Cargo features are Rust's built-in compile-time flag mechanism, declared in `Cargo.toml` under `[features]` and read with `#[cfg(feature = "...")]`. They are a different tool from the preceding runtime `Flags` port.

| Property | Cargo features | Runtime `Flags` port |
|---|---|---|
| Evaluated | At compile time | At runtime |
| Changes require | Rebuild and redeploy | Provider update (may be live) |
| Appropriate for | Optional deps, optional capabilities, library opt-ins | Release gates, experiments, ops stop switches, permissions |
| Provider needed | No (built into `cargo`) | Yes (static or remote) |

Use Cargo features for decisions fixed at compile time for a given binary. Examples include enabling an optional dependency, compiling in a backend adapter, or gating capabilities that have no business needing to flip at runtime. Use the runtime `Flags` port for anything that should change without a rebuild.

```toml
# Cargo.toml
[features]
default = []
openfeature-provider = ["dep:openfeature"]   # compile in the live flag provider
in-memory-flags = []                          # default for local and CI: no external provider
```

```rust
// composition root — select the backing at compile time, not runtime
#[cfg(feature = "openfeature-provider")]
pub fn build_flags(environment: &str) -> Box<dyn Flags> {
    Box::new(FailSafe(OpenFeatureAdapter::new(environment)))
}

#[cfg(not(feature = "openfeature-provider"))]
pub fn build_flags(_environment: &str) -> Box<dyn Flags> {
    Box::new(StaticFlags { values: HashMap::new() })
}
```

A Cargo feature that gates a user-visible capability is still a one-way door without the runtime harness: flipping it requires a redeploy. Treat it as an `ops` or `release` decision frozen at build time and record an expiry in the inventory the same way you would for a runtime flag.
