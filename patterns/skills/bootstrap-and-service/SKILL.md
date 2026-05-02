---
name: bootstrap-and-service
description: Use when building a service layer that must remain testable without external processes (HTTP, databases, message buses), and when external adapters (HTTP handlers, CLI commands, queue consumers) need to be kept thin and free of domain logic.
---

# Bootstrap and Service

## Overview

Application services orchestrate use cases — parsing input, calling domain logic, persisting results — while domain services capture business rules that span aggregates. External adapters translate protocol details (HTTP, CLI, queues) to and from service calls. A single Composition Root wires all concrete implementations at startup, keeping every other layer free of infrastructure knowledge.

## When to Use

- Exposing HTTP, CLI, or message queue adapters to an application
- Separating domain logic from infrastructure (databases, HTTP frameworks, retry logic)
- Making business logic unit-testable without spinning up servers or databases
- Wiring concrete implementations at startup without polluting domain or service code

## Core Pattern

Four layers, each with a strict mandate:

- **Domain** — pure business rules, aggregates, value objects, domain services, and domain errors as values; no I/O
- **Application Service** — orchestrates a single use case: parses input, calls domain and repository ports, returns typed results; no HTTP or DB knowledge
- **Adapter** — implements a port interface defined by the service layer; translates protocol details (HTTP status codes, CLI flags) to and from service calls; contains no business logic
- **Composition Root (Bootstrap)** — the only place that imports concrete classes; constructs and injects all dependencies; runs once at startup

```
// The dependency arrow always points inward:
//   Adapter → Service → Domain
//   Bootstrap → (all concrete impls)

// bootstrap.ts — Composition Root; the only file that knows about Postgres
const repo = new PostgresOrderRepository(process.env.DATABASE_URL);
const orderService = new OrderService(repo);
app.post("/orders", handlePlaceOrder);
```

For complete examples, see [`references/typescript.md`](references/typescript.md), [`references/python.md`](references/python.md), and [`references/rust.md`](references/rust.md).

## Quick Reference

| Layer | Responsibilities |
|---|---|
| Composition Root | Reads config, constructs concretes, injects all deps |
| Application Service | Parses input, coordinates domain + ports, returns typed results |
| Adapter | Maps protocol (HTTP/CLI/queue) to service calls; implements a port |
| Domain | Business rules, aggregates, domain services, errors as values |

## Common Mistakes

- **Domain logic in adapters** — validation, calculations, or branching in route handlers makes it untestable without an HTTP server
- **Protocol knowledge in services** — services that return status codes or accept `Request` objects cannot be reused across adapters
- **No port interface** — adapters that are called directly (not through an interface) cannot be substituted with fakes in unit tests; define the port in the service layer
- **Scattered wiring** — concrete dependencies constructed throughout the codebase instead of in one Composition Root make it impossible to swap implementations without touching many files

## Composes With

- **`patterns:parse-dont-validate`** — the application service is the first layer inside the boundary; it calls parsers before passing data to domain functions.
- **`patterns:repository`** + **`patterns:unit-of-work`** — the Composition Root wires concrete repositories into UoW factories; services receive the UoW through dependency injection.
- **`patterns:aggregate`** — application services orchestrate the aggregate lifecycle: open UoW, load aggregate, call one method, commit.
