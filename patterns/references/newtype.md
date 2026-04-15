# NewType — Code Reference

Code examples for the `patterns:newtype` skill. Referenced by `patterns/skills/newtype/SKILL.md`.

---

## TypeScript

Branded types erase at runtime — zero performance overhead.

```typescript
// Before: primitives leak domain intent
function transfer(fromAccount: string, toAccount: string, amount: number): void { /* ... */ }
// Compiles silently even when arguments are swapped:
transfer(toId, fromId, amountInCents);

// After: branded types make the mistake unrepresentable
type AccountId = string & { readonly _brand: "AccountId" };
type Cents     = number & { readonly _brand: "Cents" };

// Constructor is the only sanctioned entry point — validation lives here once.
function makeAccountId(raw: string): AccountId {
  if (!raw.startsWith("acc-")) throw new Error(`Invalid AccountId: ${raw}`);
  return raw as AccountId;
}
function makeCents(raw: number): Cents {
  if (!Number.isInteger(raw) || raw < 0) throw new Error(`Invalid Cents: ${raw}`);
  return raw as Cents;
}

function transfer(from: AccountId, to: AccountId, amount: Cents): void { /* ... */ }

// Type error — plain string is not assignable to AccountId:
transfer("acc-123", "acc-456", 5000);           // TS error

// Correct — construction is explicit:
transfer(makeAccountId("acc-123"), makeAccountId("acc-456"), makeCents(5000));
```

---

## Python

Python lacks compile-time branding, so newtypes use frozen dataclasses. mypy enforces the distinction; the `value` field carries the underlying primitive.

```python
from dataclasses import dataclass

@dataclass(frozen=True)
class AccountId:
    value: str

    def __post_init__(self) -> None:
        if not self.value.startswith("acc-"):
            raise ValueError(f"Invalid AccountId: {self.value}")

    def __str__(self) -> str:
        return self.value


@dataclass(frozen=True)
class Cents:
    value: int

    def __post_init__(self) -> None:
        if not isinstance(self.value, int) or self.value < 0:
            raise ValueError(f"Invalid Cents: {self.value}")


def transfer(from_account: AccountId, to_account: AccountId, amount: Cents) -> None:
    ...


# Type error (mypy) — plain str is not AccountId:
transfer("acc-123", "acc-456", 5000)  # mypy error

# Correct:
transfer(AccountId("acc-123"), AccountId("acc-456"), Cents(5000))
```

---

## Rust

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
