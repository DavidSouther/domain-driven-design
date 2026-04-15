---
name: parse-dont-validate
description: Use when data crosses an API boundary, arrives as user input, comes from an external service, or is read from storage — any point where untyped or untrusted data enters the domain model. Applies when scattered null checks, repeated boolean guards, or "stringly typed" values indicate that validity proofs are not carried in the type system.
---

# Parse, Don't Validate

## Overview

Data at the boundary of a system is unsafe by nature — raw strings, unstructured JSON, untrusted input. Instead of validating (checking a boolean and proceeding), parse: transform the unsafe representation into a typed domain value whose *existence* is the proof of validity. A value of type `Email` cannot be created without passing the check — so domain code accepts `Email`, not `string`, and the guard is never needed again. This is the key insight from Alexis King's original formulation: a parsed type carries the proof; a boolean check does not.

This pattern is a specific application of "make illegal states unrepresentable" — the type system enforces the invariant instead of runtime discipline.

## When to Use

- Handling HTTP request bodies, query parameters, or headers
- Reading from external APIs, message queues, or file storage
- Processing form submissions or CLI arguments
- Deserializing configuration or environment variables
- Any point where `string`, `unknown`, or `any` must become a domain type

## Core Pattern

**Validation approach** — validity is checked but not preserved in the type; guards must be repeated everywhere.

**Parse approach** — the type itself encodes the validity proof. `parseEmail(raw)` either returns an `Email` or throws a user-friendly error. `sendWelcome(email: Email)` needs no guard — the type is the proof.

```
// Parse once at the HTTP boundary:
const email = parseEmail(req.body.email);
sendWelcome(email);  // no guard inside — the type guarantees validity
```

Errors must be specific to the failure mode. The caller of the parser must be able to understand the error and correct it.

For complete examples in TypeScript, Python, and Rust, see `references/parse-dont-validate.md`.

## Quick Reference

1. Receive raw input at the boundary (`string`, `unknown`, HTTP body, env var).
2. Call a dedicated parser that returns a typed domain value or signals failure clearly.
3. Pass the typed value into the domain, so no further guards needed.
4. Never pass raw strings into domain logic; never check the same invariant twice.

## Common Mistakes

- **Validating everywhere instead of parsing once** allows scattered boolean guards to assert validity, but that is never guaranteed by the type system.
- **Stringly typed domain models** that accept `string` for email, currency, or ID forces every path in the domain model to defensively re-check, defeating the pattern.
- **Parsing after construction** by building a domain object from raw data and validating it later lets invalid states exist inside the boundary. Parse before construction.
- **Silent failures** like returning `null` or `undefined` without a message delays diagnosis. Parsers must produce actionable errors.

## Composes With

- **`patterns:newtype`** — the return type of a parser is a newtype; `parseEmail` returns `Email`, not `string`. The parse function *is* the newtype constructor when the type has a format constraint.
- **`patterns:bootstrap-and-service`** — parsing happens in the adapter or application service, exactly at the boundary where untrusted data enters the domain.
