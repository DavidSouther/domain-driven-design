# New type

## Overview

Wrap primitive types in named domain types so the type system enforces correct usage. Scalar types describe what data looks like. Domain types describe what data means. The compiler checks shape, not meaning. Two fields that are both floatint point numbers look identical without wrapping in a newtype. Using brands, the compiler erases the brand at runtime with zero performance overhead.

## When to use

- Two or more domain identifiers share the same primitive type. For example, `UserId`, `OrderId`, and `ProductId` are all UUIDs.
- A numeric quantity has units whose mixing would be incorrect (for example, `Meters` vs `Feet`, `Euros` vs `Dollars`).
- A string has a constrained format or security implications; validate them once at construction (`EmailAddress`, `Slug`, `SqlQuery`), preventing injection by making unsanitized strings unacceptable to domain APIs.
- A value crosses a bounded context boundary and its meaning must be explicit.

**when NOT to use:** purely internal scratch variables, loop counters, or values that have no domain meaning and are never passed between functions.

## Core pattern

**Before:** primitives leak domain intent; swapping `fromAccount` and `toAccount` (both `string`) compiles silently.

**After:** branded/wrapper types make the mistake unrepresentable. The constructor is the only sanctioned entry point; validation and coercion live there once.

```
type AccountId = string & { readonly _brand: "AccountId" };
// Type error: plain string is not assignable to AccountId:
transfer("acc-123", "acc-456", 5000);
// Correct: construction is explicit:
transfer(makeAccountId("acc-123"), makeAccountId("acc-456"), makeCents(5000));
```

For complete examples, see [`newtype/typescript.md`](newtype/typescript.md), [`newtype/python.md`](newtype/python.md), and [`newtype/rust.md`](newtype/rust.md).

## Quick reference

| Domain Concept   | Raw Type         | NewType                         |
|------------------|------------------|---------------------------------|
| User identity    | `string` (UUID)  | `UserId(UUID)`, `UserId(String)`|
| Monetary value   | `number`         | `Cents(u32)`, `Euros(u32)`      |
| Distance         | `number`         | `Kilometers(f64)`, `Miles(f32)` |
| Validated input  | `string`         | `EmailAddress(String)`, `Slug(String)`  |
| Timestamps       | `number`         | `UnixSeconds(Duration)`, `Milliseconds(u8)`|

## Common mistakes

- **Plain type alias instead of a brand** `type UserId = string` is fully transparent; the compiler treats it as identical to `string` and provides no safety.
- **Casting with `as` at call sites** writing `transfer(toId as AccountId, fromId as AccountId, ...)` defeats the pattern entirely. All `as` casts belong inside the constructor function, never at the call site.
- **Skipping the constructor or builder** directly casting raw values at every use site spreads unvalidated entry points across the codebase. Centralise construction so validation and coercion happen once.
- **Branding every incidental value** NewTypes belong on domain-meaningful concepts. Branding loop counters or local temporaries adds noise without benefit.

## Composes with

- **the parse-dont-validate pattern (`references/patterns/parse-dont-validate.md`):** Constructor functions, builders, and `impl TryFrom` *are* parsers; `makeEmail(raw)` validates and brands in one step, producing the typed value domain code consumes.
- **the domain-objects pattern (`references/patterns/domain-objects.md`):** Brand entity IDs (`UserId`, `OrderId`) and constrained value object fields (`Cents`, `EmailAddress`) so the type system enforces correct usage across the model.
