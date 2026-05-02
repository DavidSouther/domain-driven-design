---
name: errors-typed-untyped
description: Use when designing an API that signals failure by throwing exceptions, returning Result, or producing error values. Applies when deciding whether to expose a typed error hierarchy callers can match on, or a stringly-typed error intended for a human reader. Distinguishes library boundaries (typed) from application boundaries (stringly), and covers the translation step between them.
---

# Errors: Typed vs Untyped

## Overview

An error type is part of an API. Choose its shape by who is on the other side of the call.

A library is consumed by other code. Its callers must dispatch on failure programmatically: retry on `Network`, surface to the user on `NotFound`, give up on `Parse`. The error type must therefore be a tagged, structured value the compiler can exhaust. This is the **typed** style.

An application is consumed by a human. Its "callers" are eyes on a screen or a log line on a dashboard. The reader needs context, not a discriminator. It answers "who, what, where" (when comes from logging, why and how are up to the incident reviewer). This is the **stringly-typed** style: a rich message, often with a cause chain, and rarely matched on programmatically.

The boundary between the two is a translation step. Typed library errors arrive at the application edge. The edge formats them, adds context, and emits a human-readable string.

## When to Use

- Designing the public API of a library, package, or module imported by other code.
- Choosing between a tagged union (`Result<T, E>`, `enum`, discriminated union) and a single `Error` class with a message.
- Reviewing code that catches typed errors only to re-throw them as `Error("something went wrong")`.
- Reviewing application code that defines a deep exception hierarchy no caller ever matches on.
- Deciding whether the wire format of an external API should carry a `code` field, a message, or both.

## Core Pattern

**Library, typed.** The failure modes are exhaustive, named, and compiler-checked. Each variant carries the data needed to react to it.

```
type FetchError =
  | { kind: "Network"; cause: Error }
  | { kind: "NotFound"; resource: string }
  | { kind: "Parse"; field: string; raw: string };
```

**Application, stringly.** The failure carries the entire context a human needs to act, in a single readable message. Cause chains are preserved by the runtime, not by the type.

```
throw new Error(`Could not load user ${id}: upstream returned 503 after 3 retries`);
```

**Translation at the boundary.** Library errors are caught at the application edge, such as an HTTP handler, a CLI command, or a job worker, and rendered to a string with the local context attached.

```
try {
  const user = await users.fetch(id);            // returns Result<User, FetchError>
} catch (e) {
  log.error(`load user ${id} failed: ${formatFetchError(e)}`);
  return reply.status(502).send("Upstream unavailable");
}
```

For complete examples, see [`references/typescript.md`](references/typescript.md), [`references/python.md`](references/python.md), and [`references/rust.md`](references/rust.md).

## Quick Reference

| Boundary                   | Error shape                                  | Example                                       |
|----------------------------|----------------------------------------------|-----------------------------------------------|
| Library public API         | Tagged union / discriminated enum            | `enum FetchError { Network, NotFound, Parse }`|
| Internal helper            | Whatever the caller can match on             | `Result<T, ValidationError>`                  |
| Application boundary       | Stringly typed, context-rich                 | `"load user 123 failed: 503 after 3 retries"` |
| External wire (HTTP/RPC)   | Stable code + human message                  | `{ code: "NOT_FOUND", message: "..." }`       |
| Iteration spike            | Untyped placeholder, marked for review       | `throw new Error("TODO: classify")`           |

## Iterating From Untyped to Typed

While the failure modes of a library are still being discovered, untyped errors are acceptable scaffolding. Throw, log, panic. Get the shape of the happy path right first.

When the library's surface stabilises, sweep the untyped throws into a tagged union. Each surviving call site that inspects the message becomes a variant. Each call site that ignores the error becomes a variant the caller is forced to handle. The review pass is where the type is born; do not skip it.

## Cross-Cutting Notes

- **Cause chains survive translation.** TypeScript: `new Error(msg, { cause })`. Rust: `anyhow::Error::new(e).context(msg)`. Python: `raise X(...) from e`. Use them.
- **Wire formats are their own boundary.** A JSON `{ "code": "NOT_FOUND", "message": "..." }` body is a stringly format with a stable code. The code is matched by clients; the message is read by humans. The mapping from internal typed error to wire `code` lives at the HTTP adapter, not in the domain. Protocol semantics (HTTP, gRPC, etc) are added by the framework.
- **The review pass.** The first iteration of a library may throw or panic with raw strings. That is acceptable scaffolding. Before the library is consumed by a second caller, sweep the untyped throws into a typed enumeration. Each call site inspecting a message becomes a variant.

## Common Mistakes

- **Catching typed errors and re-throwing as a generic `Error`.** Destroys the discriminator. Callers downstream cannot recover the variant. Re-throw with the original type, or translate at the application boundary, never in between.
- **Dispatching on error message text.** `if (e.message.includes("not found"))` makes the message part of the API. Translation, locale changes, or punctuation tweaks silently break callers. Match on a tag.
- **`Result<T, string>` in a library.** A string is unstructured. Callers will parse it, regret it, and pin themselves to its wording. Define a type.
- **A deep exception hierarchy in an application.** If no caller `catch`es a specific subclass, the hierarchy is decoration. Collapse it to a single class with a good message.
- **Losing the cause chain on translation.** When formatting a typed error to a string, include the underlying cause. Future debuggers will need it.

## Composes With

- **`patterns:parse-dont-validate`**: a parser's failure type *is* a typed error. `parseEmail(raw): Result<Email, EmailError>` exposes the failure modes (`Empty`, `MissingAt`, `InvalidDomain`) the caller must handle.
- **`patterns:newtype`**: newtype constructors fail; their error type is the typed error for that domain concept. `Cents.from(n)` returns `Result<Cents, MoneyError>`.
- **`patterns:bootstrap-and-service`**: the application shell is where typed library errors are translated into stringly-typed user output. The translation lives in the adapter, not in the domain.
