# Errors: typed vs. untyped

## Overview

An error type is part of an API. Choose its shape by who is on the other side of the call.

Other code consumes a library. Its callers must dispatch on failure programmatically: retry on `Network`, surface to the user on `NotFound`, give up on `Parse`. The error type must therefore be a tagged, structured value the compiler can exhaust. This is the **typed** style.

A human consumes an app. Its "callers" are eyes on a screen or a log line on a dashboard. The reader needs context, not a discriminator. It answers "who, what, where." When it comes from logging, why, and how are up to the incident reviewer. This is the **stringlytyped** style: a rich message, frequently with a cause chain, and rarely matched on programmatically.

The boundary between the two is a translation step. Typed library errors arrive at the app edge. The edge formats them, adds context, and emits a human-readable string.

## When to use

- Designing the public API of a library, package, or module imported by other code.
- Choosing between a tagged union (`Result<T, E>`, `enum`, discriminated union) and a single `Error` class with a message.
- Reviewing code that catches typed errors only to re-throw them as `Error("something went wrong")`.
- Reviewing app code that defines a deep exception hierarchy no caller ever matches on.
- Deciding whether the wire format of an external API should carry a `code` field, a message, or both.

## Core pattern

**Library, typed.** The failure modes are exhaustive, named, and compiler-checked. Each variant carries the data needed to react to it.

```
type FetchError =
  | { kind: "Network"; cause: Error }
  | { kind: "NotFound"; resource: string }
  | { kind: "Parse"; field: string; raw: string };
```

**Application, stringly.** The failure carries the entire context a human needs to act, in a single readable message. The runtime preserves cause chains, not the type.

```
throw new Error(`Could not load user ${id}: upstream returned 503 after 3 retries`);
```

**Translation at the boundary.** HTTP handlers, command-line tools, and job workers catch library errors at the app edge and render them to a string with the local context attached.

```
try {
  const user = await users.fetch(id);            // returns Result<User, FetchError>
} catch (e) {
  log.error(`load user ${id} failed: ${formatFetchError(e)}`);
  return reply.status(502).send("Upstream unavailable");
}
```

For complete examples, see [`errors-typed-untyped/typescript.md`](errors-typed-untyped/typescript.md), [`errors-typed-untyped/python.md`](errors-typed-untyped/python.md), and [`errors-typed-untyped/rust.md`](errors-typed-untyped/rust.md).

## Quick reference

| Boundary                   | Error shape                                  | Example                                       |
|----------------------------|----------------------------------------------|-----------------------------------------------|
| Library public API         | Tagged union / discriminated enum            | `enum FetchError { Network, NotFound, Parse }`|
| Internal helper            | Whatever the caller can match on             | `Result<T, ValidationError>`                  |
| Application boundary       | Stringly typed, context-rich                 | `"load user 123 failed: 503 after 3 retries"` |
| External wire (HTTP/RPC)   | Stable code + human message                  | `{ code: "NOT_FOUND", message: "..." }`       |
| Iteration spike            | Untyped placeholder, marked for review       | `throw new Error("TODO: classify")`           |

## Iterating from untyped to typed

While discovering a library's failure modes, untyped errors are acceptable scaffolding. Throw, log, panic. Get the shape of the happy path right first.

When the library's surface stabilises, sweep the untyped throws into a tagged union. Each surviving call site that inspects the message becomes a variant. Each call site that ignores the error becomes a variant callers must process. The review pass finalizes the type; do not skip it.

## Cross-cutting notes

- **Cause chains survive translation.** TypeScript: `new Error(msg, { cause })`. Rust: `anyhow::Error::new(e).context(msg)`. Python: `raise X(...) from e`. Use them.
- **Wire formats are their own boundary.** A JSON `{ "code": "NOT_FOUND", "message": "..." }` body is a stringly format with a stable code. Clients match the code; humans read the message. The mapping from internal typed error to wire `code` lives at the HTTP adapter, not in the domain. The framework adds protocol semantics (HTTP, gRPC, etc).
- **The review pass.** The first iteration of a library may throw or panic with raw strings. That is acceptable scaffolding. Before a second caller consumes the library, sweep the untyped throws into a typed enumeration. Each call site inspecting a message becomes a variant.

## Common mistakes

- **Catching typed errors and re-throwing as a generic `Error`.** Destroys the discriminator. Callers downstream cannot recover the variant. Re-throw with the original type, or translate at the app boundary, never in between.
- **Dispatching on error message text.** `if (e.message.includes("not found"))` makes the message part of the API. Translation, locale changes, or punctuation tweaks silently break callers. Match on a tag.
- **`Result<T, string>` in a library.** Strings lack structure. Callers parse them, regret it, and pin themselves to their wording. Define a type.
- **A deep exception hierarchy in an app.** If no caller `catch`es a specific subclass, the hierarchy is decoration. Collapse it to a single class with a good message.
- **Losing the cause chain on translation.** When formatting a typed error to a string, include the underlying cause. Future debuggers need it.

## Composes with

- **the parse-dont-validate pattern (`references/patterns/parse-dont-validate.md`)**: a parser's failure type *is* a typed error. `parseEmail(raw): Result<Email, EmailError>` exposes the failure modes (`Empty`, `MissingAt`, `InvalidDomain`) the caller must process.
- **the newtype pattern (`references/patterns/newtype.md`)**: newtype constructors fail; their error type is the typed error for that domain concept. `Cents.from(n)` returns `Result<Cents, MoneyError>`.
- **the bootstrap-and-service pattern (`references/patterns/bootstrap-and-service.md`)**: the app shell translates typed library errors into stringlytyped user output. The translation lives in the adapter, not in the domain.
