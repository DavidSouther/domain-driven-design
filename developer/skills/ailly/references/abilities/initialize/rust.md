# Rust project reference

Toolchain: cargo + Clippy + rustfmt

## Required layout

```
<project>/
  Cargo.toml
  Cargo.lock          # commit for binaries; .gitignore for libraries
  src/
    lib.rs            # or main.rs for binaries
  tests/
    <feature>.rs      # integration/feature tests live here
  .rustfmt.toml       # optional but recommended
```

## Required config files

### `Cargo.toml` (minimum)

```toml
[package]
name = "my-project"
version = "0.1.0"
edition = "2021"

[dependencies]

[dev-dependencies]
```

### `.rustfmt.toml` (recommended)

```toml
edition = "2021"
max_width = 100
```

## Validation checklist

- [ ] Verify `cargo` installation (`cargo --version`)
- [ ] Verify `rustfmt` installation (`rustfmt --version`)
- [ ] Verify `clippy` installation (`cargo clippy --version`)
- [ ] `Cargo.toml` exists with a valid `[package]` section
- [ ] `src/` directory exists
- [ ] `tests/` directory exists
- [ ] `cargo build` exits 0 with no warnings
- [ ] `cargo clippy -- -D warnings` exits 0

## Scaffolding (if validation fails)

```bash
# New project
cargo new --lib <name>
mkdir tests

# Add a placeholder feature test
cat > tests/feature.rs << 'EOF'
#[test]
fn feature_placeholder() {
    // Replace with feature test
}
EOF

# Verify
cargo build
cargo clippy -- -D warnings
cargo test
```

## Development hooks

| Hook | Command |
|---|---|
| Format | `rustfmt <edited-file>` |
| Check | `cargo clippy -- -D warnings` |
| Test | `cargo test` |
| Lint | `cargo clippy -- -D warnings` |

## Feature tests

Feature tests live in `tests/`.
Cargo compiles each file in `tests/` as a separate integration test binary.

```rust
// tests/user_login.rs
use my_project::App;

#[test]
fn user_logs_in_and_sees_dashboard() {
    let app = App::new_test();
    let response = app.post("/login", json!({ "email": "a@example.com", "password": "secret" }));
    assert_eq!(response.status, 302);
    assert_eq!(response.location(), "/dashboard");
}
```

## Verification command

```bash
cargo test -- --test-output immediate
```

Expected: all tests pass, no warnings in build output.
