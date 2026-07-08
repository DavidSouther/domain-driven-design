# Type conversion

## Overview

A conversion is a named operation that takes a value of one type and produces a value of another.
Make every conversion explicit, total, or partial, and defined exactly once.
Domain code does not extract a primitive, cast it, and rewrap it; it asks the source type to convert itself, or asks the target type to construct from the source.
Conversions live in the language's standard mechanism so callers find them where they expect.
Rust uses `From`, `Into`, and `TryFrom` traits.
TypeScript uses a static `from` or `tryFrom` method.
Python uses a `classmethod` factory.

A total conversion never fails.
Every value of the source type maps to a value of the target.
A partial conversion can fail and must surface that fact in its return type.
The two are different operations and must not share a name.

## When to use

- A function takes a value of one domain type and produces another.
  Examples include `Cents` to `Dollars`, `DraftOrder` to `PlacedOrder`, and `EmailRaw` to `Email`.
- Code reaches into a newtype with `.0`, `.value`, or unbranding, then rewraps the inner value as another domain type.
- An `as` cast or implicit numeric coercion converts between domain units.
- A constructor accepts both validated and unvalidated input under the same name.
- Two functions exist named `to_x` and `from_x`.
  Both directions duplicate the conversion logic.
- A generic API wants to accept anything convertible to a domain type, such as `fn charge<A: Into<Cents>>(a: A)`.
- A test fixture builder threads `make_x(make_y(make_z(...)))` with intermediate primitives that the builder only rewraps.

**When NOT to use:** internal mutations on a value of the same type.
Standard-library conversions between language-runtime types where the platform already provides the canonical form, such as `int` to `bigint` or `str` to `bytes`.

## Core pattern

Every conversion answers two questions.
Can this fail?
Which type owns the conversion?

**Total, owned by the target.**
The conversion cannot fail.
Define it on the target with the canonical trait or factory.

```rust
impl From<Cents> for Dollars {
    fn from(c: Cents) -> Self { Dollars(c.0 as f64 / 100.0) }
}
let d: Dollars = cents.into();
```

**Partial, owned by the target.**
The conversion may fail.
Return a structured error.
Do not panic.

```rust
impl TryFrom<&str> for Email {
    type Error = EmailError;
    fn try_from(s: &str) -> Result<Self, EmailError> { /* parse and validate */ }
}
let email = Email::try_from(raw)?;
```

**Single canonical direction.**
Define `From<A> for B` or `From<B> for A`, not both.
The reverse direction either follows automatically through the partner trait, is genuinely symmetric (rare), or is a separate operation that deserves a distinct name.

**Generic acceptance.**
A function that accepts anything convertible to a target lets callers pass either form without an explicit cast at the call site.

```rust
fn charge<A: Into<Cents>>(amount: A) { let c: Cents = amount.into(); /* ... */ }
charge(500u64);            // u64 -> Cents via From
charge(Cents(500));        // identity
```

For complete examples, see [`type-conversion/typescript.md`](type-conversion/typescript.md), [`type-conversion/python.md`](type-conversion/python.md), and [`type-conversion/rust.md`](type-conversion/rust.md).

## Quick reference

| Language | Total | Partial | Generic Accept |
|---|---|---|---|
| Rust | `impl From<A> for B` (auto-derives `Into`) | `impl TryFrom<A> for B` with `type Error` | `fn f<A: Into<B>>(a: A)` |
| TypeScript | `static from(a: A): B` on the target class | `static tryFrom(a: A): Result<B, E>`, or throws a typed error | overload signatures, or `f(a: A \| B)` with an internal narrow |
| Python | `@classmethod from_a(cls, a: A) -> Self` | `@classmethod parse(cls, raw: str) -> Self` raising a specific exception, or returning a `Result`-shaped union | `functools.singledispatch`, or `Union[A, B]` with internal `match` |

## Common mistakes

- **`as` cast between domain types.**
  Writing `c.0 as f64 / 100.0` performs a silent, lossy primitive cast and bypasses any conversion the type owns.
  Define `From` or `Into`.
  The cast lives once, inside the impl, where reviewers see it.
- **Same name for total and partial.**
  `Cents::from(s)` that panics on bad input is a partial conversion wearing a total name.
  A total conversion never fails.
  A partial conversion returns `Result` or raises a typed error.
  Never share the name.
- **Two-way `From` pairs.**
  Defining `From<Cents> for Dollars` and `From<Dollars> for Cents` invites round-tripping through a lossy step.
  Pick the canonical direction.
  The other direction is either derived through the partner trait, or a separate named operation such as `Dollars::round_to_cents`.
- **Extract and rewrap.**
  `OrderId(draft.id.0.clone())` reaches into the newtype and reconstructs it.
  The original value was already valid, so move it.
  If you need a real conversion, define one.
- **Validation scattered across call sites.**
  Calling `parse_x` or `make_x` ad hoc throughout the codebase, or adding a back-door factory like `Email::from_validated_db_row(s)` that skips validation, both spread the parse step away from the boundary.
  Convert once at the edge.
  The rest of the system speaks the typed value.
  If an unsafe path is genuinely needed, name it `unchecked_from` and mark it `unsafe` or private.
  Propagate errors to the caller with `?`, or process them at the boundary where the data first entered.
- **`unwrap()` on a partial conversion.** `Email::try_from(raw).unwrap()` discards the typed error and panics on bad input.

## Composes with

- **the newtype pattern (`references/patterns/newtype.md`)**: newtype constructors are total conversions when input is already valid, and partial conversions when validation runs.
  Implementing `From<Inner> for NewType` is the canonical build path; implementing `TryFrom<&str> for NewType` is the canonical parse path.
- **the parse-dont-validate pattern (`references/patterns/parse-dont-validate.md`)**: a parser is a partial conversion from a raw boundary type to a domain type.
  The return type encodes the proof of validity.
- **the errors-typed-untyped pattern (`references/patterns/errors-typed-untyped.md`)**: a partial conversion's error is a typed library error. `TryFrom`'s associated `Error` type is the typed-error pattern applied at the conversion boundary.
- **the bootstrap-and-service pattern (`references/patterns/bootstrap-and-service.md`)**: partial conversions run inside boundary adapters such as HTTP handlers, command-line tool commands, and queue consumers.
  The app core handles only converted, typed values.
