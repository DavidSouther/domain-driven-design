---
name: builder
description: Use when constructing an object that requires multiple fields to be valid, where a many-parameter constructor is error-prone, optional vs required fields are ambiguous, or complex initialization logic must be isolated from the caller. Ensures objects are always fully initialized before use.
---

# Builder

## Overview

Use a dedicated builder object to accumulate configuration step-by-step and validate completeness before producing the final object. This prevents half-initialized objects from entering the system and makes required vs optional fields explicit in the API.

## When to Use

- A struct or class has three or more fields required for validity.
- Some fields are optional and defaults are non-obvious.
- Construction involves cross-field validation (e.g., `start` must be before `end`).
- The same base configuration is assembled in several slightly different ways.

**When NOT to use:** Simple value objects with one or two fields where a plain constructor is clear. If all fields are optional with sensible defaults, an options-object / named-parameter pattern is simpler and avoids the builder ceremony.

## Core Pattern

**Before** — positional constructor hides intent: `new HttpRequest("POST", url, undefined, body, 30000)` — easy to swap arguments, impossible to tell which `undefined` is headers.

**After** — Builder makes required fields mandatory at construction time and optional fields discoverable:

```
const req = HttpRequest.builder("POST", "https://api.example.com/orders")
  .withHeader("Content-Type", "application/json")
  .withBody(JSON.stringify(order))
  .withTimeout(30000)
  .build();
```

Key rules:
- Required fields go in `builder(...)`, not `build()`.
- `build()` performs cross-field validation before constructing the object.
- Copy mutable fields (headers, lists) in `build()` so re-using the builder does not alias state.
- The product constructor is private — every instance was validated by the builder.

For complete examples in TypeScript, Python, and Rust, see `references/builder.md`.

## Common Mistakes

- **Public constructor alongside builder.** Callers bypass validation. Make the product constructor private and expose only `static builder(...)`.
- **Skipping cross-field validation in `build()`.** Guards end up scattered in callers instead of centralized. Validate everything in `build()`.
- **Mutating the builder's collections in the product.** If `build()` passes `this.headers` directly, mutating the builder afterward corrupts existing instances. Always copy mutable fields.
- **Adding a builder to simple objects.** Two-field value objects with an obvious constructor do not benefit from a builder; the ceremony costs more than it saves.
- **Step-builder for truly required fields.** When several fields are all required (not just "supplied first"), a Step Builder encodes each required field as a distinct interface in the type system, making it impossible to call `build()` before supplying them all. Consider this for APIs used by many callers.

## Composes With

- **`patterns:newtype`** as fields are often newtypes; the builder's factory method is the natural place to call the newtype constructor and validate in one step.
- **`patterns:parse-dont-validate`** can use builders during parsing to "build up" the domain object, defering final validation until completing the builder.
- **`patterns:entities-value-objects-services`** — use a builder when constructing an entity or value object with three or more required fields to prevent partial initialization.
