# Using feature flags in Rust

One toggle point reads the injected `Flags` port and branches. The default branch is today's behavior. The targeting stays in the provider behind the port. The test exercises both branches.

```rust
// checkout.rs — one toggle point, at the edge of the new path
use crate::flags::{FlagContext, Flags}; // installed by configuring-feature-flags

pub fn checkout(flags: &dyn Flags, ctx: &FlagContext, cart: &Cart) -> Receipt {
    if flags.enabled("release.checkout.new-flow", false, ctx) {
        new_checkout(cart)
    } else {
        current_checkout(cart) // the default branch is today's behavior
    }
}
```

```rust
// Both states ship, so both states are tested.
#[cfg(test)]
mod tests {
    use super::*;

    struct FakeFlags {
        on: bool,
    }

    impl Flags for FakeFlags {
        fn enabled(&self, _key: &str, _default: bool, _ctx: &FlagContext) -> bool {
            self.on
        }
    }

    fn ctx() -> FlagContext {
        FlagContext { environment: "test".into(), user_id: None }
    }

    #[test]
    fn flag_off_runs_the_current_flow() {
        let receipt = checkout(&FakeFlags { on: false }, &ctx(), &cart());
        assert_eq!(receipt.via, "current");
    }

    #[test]
    fn flag_on_runs_the_new_flow() {
        let receipt = checkout(&FakeFlags { on: true }, &ctx(), &cart());
        assert_eq!(receipt.via, "new");
    }
}
```

When the new flow is fully rolled out, delete the flag, the `if`, and `current_checkout`, leaving `checkout` as a direct call.

## Cargo features: compile-time toggle points

When the decision is made at build time rather than runtime, a Cargo feature replaces the runtime `Flags` port. The toggle point uses `#[cfg(feature = "...")]` instead of reading the injected port. The same discipline applies: one toggle point, default to current behavior, test both states.

```toml
# Cargo.toml — declare the feature before gating code on it
[features]
new-checkout = []
```

```rust
// checkout.rs — one compile-time toggle point
pub fn checkout(cart: &Cart) -> Receipt {
    #[cfg(feature = "new-checkout")]
    return new_checkout(cart);
    #[cfg(not(feature = "new-checkout"))]
    current_checkout(cart)  // default: today's behavior when feature is absent
}
```

```rust
// Both states ship, so test both in CI by running:
//   cargo test                             (feature absent — current path)
//   cargo test --features new-checkout     (feature present — new path)
#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn default_runs_current_checkout() {
        assert_eq!(checkout(&cart()).via, "current");
    }

    #[cfg(feature = "new-checkout")]
    #[test]
    fn feature_enabled_runs_new_checkout() {
        assert_eq!(checkout(&cart()).via, "new");
    }
}
```

A Cargo feature is appropriate when the toggle must not change without a rebuild. Examples include optional backend adapters, platform-specific code paths, or capabilities that have no runtime-flip requirement. It is not appropriate for release gates or experiments that need to change without a redeploy. Use the runtime `Flags` port for those. See `references/patterns/configuring-feature-flags/rust.md` for the full comparison.
