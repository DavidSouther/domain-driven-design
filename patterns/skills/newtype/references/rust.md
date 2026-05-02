# NewType — Rust Reference

Rust tuple structs are zero-cost newtypes — the compiler treats `AccountId` as distinct from `String` with no runtime overhead. Use `TryFrom` for fallible construction.

```rust
use std::convert::TryFrom;

#[derive(Debug, Clone, PartialEq, Eq, Hash)]
pub struct AccountId(String);

impl TryFrom<&str> for AccountId {
    type Error = String;

    fn try_from(raw: &str) -> Result<Self, Self::Error> {
        if !raw.starts_with("acc-") {
            return Err(format!("Invalid AccountId: {}", raw));
        }
        Ok(AccountId(raw.to_string()))
    }
}

impl std::fmt::Display for AccountId {
    fn fmt(&self, f: &mut std::fmt::Formatter<'_>) -> std::fmt::Result {
        self.0.fmt(f)
    }
}

#[derive(Debug, Clone, Copy, PartialEq, Eq, PartialOrd, Ord)]
pub struct Cents(u64);

impl Cents {
    pub fn new(value: u64) -> Self {
        Cents(value)
    }
}

pub fn transfer(from: AccountId, to: AccountId, amount: Cents) {
    // Compiler error if a plain String or u64 is passed — no runtime check needed.
    let _ = (from, to, amount);
}

// Correct:
let from = AccountId::try_from("acc-123").unwrap();
let to   = AccountId::try_from("acc-456").unwrap();
transfer(from, to, Cents::new(5000));
```
