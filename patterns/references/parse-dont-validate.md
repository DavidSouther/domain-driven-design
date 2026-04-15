# Parse, Don't Validate — Code Reference

Code examples for the `patterns:parse-dont-validate` skill. Referenced by `patterns/skills/parse-dont-validate/SKILL.md`.

---

## TypeScript

```typescript
// BAD: boolean guard must be repeated at every call site
function isValidEmail(s: string): boolean {
  return /^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(s);
}

function sendWelcome(email: string) {
  if (!isValidEmail(email)) throw new Error("invalid email"); // repeated everywhere
  smtp.send(email, "Welcome!");
}

// GOOD: parse once at the boundary; the type carries the proof
type Email = string & { readonly _brand: unique symbol };

function parseEmail(raw: string): Email {
  if (!/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(raw))
    throw new UserError(`"${raw}" is not a valid email address`);
  return raw as Email;
}

// Domain functions accept Email — illegal to pass an unvalidated string
function sendWelcome(email: Email) {
  smtp.send(email, "Welcome!"); // no guard needed; the type is the proof
}

// Parsing happens exactly once, at the HTTP boundary
app.post("/register", (req, res) => {
  const email = parseEmail(req.body.email); // throws with a user-friendly message
  sendWelcome(email);
});
```

---

## Python

```python
import re
from dataclasses import dataclass

# BAD: boolean guard scattered at every call site
def is_valid_email(s: str) -> bool:
    return bool(re.match(r"^[^\s@]+@[^\s@]+\.[^\s@]+$", s))

def send_welcome_bad(email: str) -> None:
    if not is_valid_email(email):
        raise ValueError("invalid email")  # repeated everywhere
    smtp.send(email, "Welcome!")


# GOOD: parse once at the boundary; the type carries the proof
@dataclass(frozen=True)
class Email:
    value: str

def parse_email(raw: str) -> Email:
    if not re.match(r"^[^\s@]+@[^\s@]+\.[^\s@]+$", raw):
        raise ValueError(f'"{raw}" is not a valid email address')
    return Email(raw)

# Domain functions accept Email — mypy rejects plain str
def send_welcome(email: Email) -> None:
    smtp.send(email.value, "Welcome!")  # no guard needed; the type is the proof

# Parsing happens exactly once, at the HTTP boundary
def register(body: dict) -> None:
    email = parse_email(body["email"])  # raises with a user-friendly message
    send_welcome(email)
```

---

## Rust

Rust's `FromStr` / `TryFrom` traits are the idiomatic parse boundary. The `Email` type cannot be constructed any other way, so domain functions need no guard.

```rust
use std::str::FromStr;

// BAD: validation returns bool — repeated at every call site
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

// Domain functions accept &Email — compiler rejects plain &str
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
