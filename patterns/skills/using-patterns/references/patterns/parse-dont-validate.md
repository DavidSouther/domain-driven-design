# Parse, don't validate

## Overview

Data at the boundary of a system is unsafe.
This includes raw strings, unstructured JSON, and untrusted input.
Do not just validate (check a boolean and proceed).
Instead, parse: transform the unsafe representation into a typed domain value.
The *existence* of this value is the proof of validity.
You cannot create a value of type `Email` without passing the check.
Domain code accepts `Email`, not `string`, so the guard is never needed again.
This is the key insight from Alexis King's original formulation: a parsed type carries the proof; a boolean check does not.

This pattern applies the principle of "make illegal states unrepresentable."
The type system enforces the invariant instead of runtime discipline.

## When to use

- Handling HTTP request bodies, query parameters, or headers
- Reading from external APIs, message queues, or file storage
- Processing form submissions or command-line arguments
- Deserializing configuration or environment variables
- Any point where `string`, `unknown`, or `any` must become a domain type

## Core pattern

**Validation approach.**
The check verifies validity but doesn't preserve it in the type.
You must repeat guards everywhere.

**Parse approach.**
The type itself encodes the validity proof.
`parseEmail(raw)` either returns an `Email` or throws a user-friendly error.
`sendWelcome(email: Email)` needs no guard because the type is the proof.

```
// Parse once at the HTTP boundary:
const email = parseEmail(req.body.email);
sendWelcome(email);  // no guard inside: the type guarantees validity
```

Errors must be specific to the failure mode.
The caller of the parser must be able to understand the error and correct it.

For complete examples, see [`parse-dont-validate/typescript.md`](parse-dont-validate/typescript.md), [`parse-dont-validate/python.md`](parse-dont-validate/python.md), and [`parse-dont-validate/rust.md`](parse-dont-validate/rust.md).

## Quick reference

1. Receive raw input at the boundary (`string`, `unknown`, HTTP body, env var).
2. Call a dedicated parser that returns a typed domain value or signals failure clearly.
3. Pass the typed value into the domain, so no further guards needed.
4. Never pass raw strings into domain logic; never check the same invariant twice.

## Common mistakes

- **Validating everywhere instead of parsing once** allows scattered boolean guards to assert validity, but that is never guaranteed by the type system.
- **Stringly typed domain models** that accept `string` for email, currency, or ID forces every path in the domain model to defensively re-check, defeating the pattern.
- **Parsing after construction** by building a domain object from raw data and validating it later lets invalid states exist inside the boundary.
  Parse before construction.
- **Silent failures** like returning `null` or `undefined` without a message delays diagnosis.
  Parsers must produce actionable errors.

## Composes with

- **the newtype pattern (`references/patterns/newtype.md`)**: the return type of a parser is a newtype.
  `parseEmail` returns `Email`, not `string`.
  The parse function *is* the newtype constructor when the type has a format constraint.
- **the bootstrap-and-service pattern (`references/patterns/bootstrap-and-service.md`)**: parsing happens in the adapter or app service, exactly at the boundary where untrusted data enters the domain.
