# Parse, don't validate. Rust reference

Rust's `FromStr` / `TryFrom` traits are the idiomatic parse boundary. Only `from_str` constructs the `Email` type, so domain functions need no guard.

```rust
use std::str::FromStr;

// BAD: validation returns bool. Repeated at every call site
fn is_valid_email(s: &str) -> bool {
    // simplified check for illustration
    s.contains('@') && s.contains('.')
}

fn send_welcome_bad(email: &str) {
    assert!(is_valid_email(email), "invalid email"); // repeated everywhere
}

// GOOD: parse once at the boundary; the type carries the proof
#[derive(Debug, Clone)]
pub struct Email(String);

impl FromStr for Email {
    type Err = String;

    fn from_str(raw: &str) -> Result<Self, Self::Err> {
        if !raw.contains('@') || !raw.contains('.') {
            return Err(format!("\"{}\" is not a valid email address", raw));
        }
        Ok(Email(raw.to_string()))
    }
}

// Domain functions accept &Email. Compiler rejects plain &str
pub fn send_welcome(email: &Email) {
    smtp_send(&email.0, "Welcome!"); // no guard needed; the type is the proof
}

// Parsing happens exactly once, at the HTTP/CLI boundary
fn handle_register(body: &serde_json::Value) -> Result<(), String> {
    let email: Email = body["email"]
        .as_str()
        .ok_or("email field required")?
        .parse()?; // returns user-friendly Err on failure
    send_welcome(&email);
    Ok(())
}
```
