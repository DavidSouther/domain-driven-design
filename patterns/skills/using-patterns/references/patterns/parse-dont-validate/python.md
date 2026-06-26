# Parse, Don't Validate — Python Reference

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
