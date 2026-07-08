# Type conversion, rust reference

Rust ships the conversion pattern in the standard library.
A blanket impl pairs `From` and `Into`.
The same impl pairs `TryFrom` and `TryInto` for fallible conversions.
Implement the `From` side; the compiler generates the `Into` side.

## Total: `From` and `Into`

```rust
#[derive(Debug, Clone, Copy)]
pub struct Cents(pub u64);

#[derive(Debug, Clone, Copy)]
pub struct Dollars(pub f64);

impl From<Cents> for Dollars {
    fn from(c: Cents) -> Self {
        Dollars(c.0 as f64 / 100.0)
    }
}

// Generic acceptance: callers may pass anything convertible to Cents.
pub fn charge<A: Into<Cents>>(amount: A) {
    let cents: Cents = amount.into();
    let _ = Dollars::from(cents);
}

let c = Cents(2599);
let d: Dollars = c.into();   // via blanket Into
charge(Cents(500));
```

## Partial: `TryFrom` and `TryInto`

```rust
use std::convert::TryFrom;

#[derive(Debug, Clone, PartialEq, Eq)]
pub struct Email(String);

#[derive(Debug)]
pub enum EmailError {
    Empty,
    MissingAt,
}

impl TryFrom<&str> for Email {
    type Error = EmailError;

    fn try_from(raw: &str) -> Result<Self, EmailError> {
        if raw.is_empty() { return Err(EmailError::Empty); }
        if !raw.contains('@') { return Err(EmailError::MissingAt); }
        Ok(Email(raw.to_string()))
    }
}

// Boundary code propagates the typed error; never .unwrap() on user input.
fn handle(raw: &str) -> Result<Email, EmailError> {
    let email = Email::try_from(raw)?;
    Ok(email)
}
```

## Lifecycle reshape: aggregate stage transitions

A move from one lifecycle stage to the next is a total conversion when no domain rule rejects it, and a partial conversion when it can.

```rust
pub struct DraftOrder {
    pub id: OrderId,
    pub customer: CustomerId,
    pub total: Cents,
}

pub struct PlacedOrder {
    pub id: OrderId,
    pub customer: CustomerId,
    pub total: Cents,
    pub placed_at: DateTime<Utc>,
}

// Total: the only added information is the timestamp; nothing rejects the move.
impl PlacedOrder {
    pub fn from_draft(draft: DraftOrder, placed_at: DateTime<Utc>) -> Self {
        PlacedOrder {
            id: draft.id,
            customer: draft.customer,
            total: draft.total,
            placed_at,
        }
    }
}
```

Note that no field requires extraction and rewrapping.
The newtypes move through.

## Anti-patterns

```rust
// Wrong: silent lossy cast scattered through call sites.
let d = c.0 as f64 / 100.0;

// Wrong: panicking parser dressed as a total conversion.
fn parse_amount(s: &str) -> Cents { Cents(s.parse().unwrap()) }

// Wrong: extract-and-rewrap of an already-valid value.
let id = OrderId(draft.id.0.clone());
```

## Single canonical direction

If `Cents` to `Dollars` is canonical, do not also implement `From<Dollars> for Cents`.
The reverse is lossy and deserves an explicit method:

```rust
impl Dollars {
    pub fn round_to_cents(self) -> Cents {
        Cents((self.0 * 100.0).round() as u64)
    }
}
```

The name surfaces the rounding, so reviewers see the precision concern.
