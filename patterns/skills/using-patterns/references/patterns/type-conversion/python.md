# Type conversion: Python reference

Python uses `classmethod` factories as the conversion entry points.
The `from_x` name marks a total conversion.
The `parse` or `try_from` name marks a partial conversion that may raise or return a union.

## Total: `from_x` classmethod

```python
from dataclasses import dataclass

@dataclass(frozen=True)
class Cents:
    value: int

    def __post_init__(self) -> None:
        if not isinstance(self.value, int) or self.value < 0:
            raise ValueError(f"invalid Cents: {self.value}")


@dataclass(frozen=True)
class Dollars:
    value: float

    @classmethod
    def from_cents(cls, c: Cents) -> "Dollars":
        return cls(c.value / 100)


d = Dollars.from_cents(Cents(2599))
```

The factory name `from_cents` makes the source explicit.
A reader sees the conversion in the call site rather than inferring it from arithmetic.

## Partial: `parse` raising a typed error

```python
class EmailError(ValueError):
    """Base class for email parse failures. Callers may match on subclasses."""

class EmptyEmail(EmailError): ...
class MissingAtSign(EmailError): ...


@dataclass(frozen=True)
class Email:
    value: str

    @classmethod
    def parse(cls, raw: str) -> "Email":
        if not raw:
            raise EmptyEmail(raw)
        if "@" not in raw:
            raise MissingAtSign(raw)
        return cls(raw)
```

The exception hierarchy lets callers `except MissingAtSign` to surface a specific message, while `except EmailError` catches the family at the boundary.

## Partial: `try_from` returning a union

When raising is undesirable (hot path, batch validation, structured response), return a `Result`-shaped union.

```python
from typing import Union

@dataclass(frozen=True)
class EmailParseFailure:
    raw: str
    reason: str


def try_email(raw: str) -> Union[Email, EmailParseFailure]:
    if not raw:
        return EmailParseFailure(raw, "empty")
    if "@" not in raw:
        return EmailParseFailure(raw, "missing @")
    return Email(raw)


result = try_email(req.json["email"])
match result:
    case Email():
        send_welcome(result)
    case EmailParseFailure(raw=r, reason=why):
        reply.status(400, f"bad email ({why}): {r}")
```

## Generic acceptance: `singledispatch`

```python
from functools import singledispatch

@singledispatch
def charge(amount) -> None:
    raise TypeError(f"unsupported amount: {type(amount).__name__}")

@charge.register
def _(amount: Cents) -> None:
    ...

@charge.register
def _(amount: int) -> None:
    charge(Cents(amount))


charge(Cents(500))
charge(500)
```

## Lifecycle reshape

```python
from datetime import datetime

@dataclass(frozen=True)
class DraftOrder:
    id: "OrderId"
    customer: "CustomerId"
    total: Cents


@dataclass(frozen=True)
class PlacedOrder:
    id: "OrderId"
    customer: "CustomerId"
    total: Cents
    placed_at: datetime

    @classmethod
    def from_draft(cls, draft: DraftOrder, placed_at: datetime) -> "PlacedOrder":
        return cls(
            id=draft.id,
            customer=draft.customer,
            total=draft.total,
            placed_at=placed_at,
        )
```

Note that the conversion passes the typed fields of `draft` through.
It does not unwrap and rewrap them.

## Anti-patterns

```python
# Wrong: __int__ lets arithmetic silently bypass the type.
@dataclass(frozen=True)
class Cents:
    value: int
    def __int__(self) -> int: return self.value   # invites `int(c) + 1`

# Wrong: a single Email constructor sometimes raises and sometimes does not.
#        Total and partial must not share a name.
Email("not an email")   # silent acceptance

# Wrong: extract and rewrap an already-valid value.
new_id = OrderId(draft.id.value)
```

## Single canonical direction

If `Cents.to_dollars` is canonical, the reverse is a separate named method that surfaces the rounding:

```python
@dataclass(frozen=True)
class Cents:
    value: int

    @classmethod
    def from_dollars_rounded(cls, d: Dollars) -> "Cents":
        return cls(round(d.value * 100))
```
