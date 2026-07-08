# Bootstrap and service

## Overview

Application services organize use cases: they parse input, call domain logic, and persist results.
Domain services capture business rules across aggregates.
External adapters translate protocol details (HTTP, command-line tools, queues) to and from service calls.
A Composition Root wires all implementations at startup and isolates infrastructure knowledge in one place.

## When to use

- Exposing HTTP, command-line tool, or message queue adapters to an app
- Separating domain logic from infrastructure (databases, HTTP frameworks, retry logic)
- Making business logic unit-testable without spinning up servers or databases
- Wiring concrete implementations at startup without polluting domain or service code

## Core pattern

Four layers, each with a strict mandate:

- **Domain**: pure business rules, aggregates, value objects, domain services, and domain errors as values; no I/O
- **Application Service**: orchestrates a single use scenario: parses input, calls domain and repository ports, returns typed results; no HTTP or DB knowledge
- **Adapter**: implements a port interface defined by the service layer; translates protocol details (HTTP status codes, command-line tool flags) to and from service calls; contains no business logic
- **Composition Root (Bootstrap)**: the only place that imports concrete classes; constructs and injects all dependencies; runs once at startup

```
// The dependency arrow always points inward:
//   Adapter → Service → Domain
//   Bootstrap → (all concrete impls)

// bootstrap.ts: Composition Root; the only file that knows about Postgres
const repo = new PostgresOrderRepository(process.env.DATABASE_URL);
const orderService = new OrderService(repo);
app.post("/orders", handlePlaceOrder);
```

For complete examples, see [`bootstrap-and-service/typescript.md`](bootstrap-and-service/typescript.md), [`bootstrap-and-service/python.md`](bootstrap-and-service/python.md), and [`bootstrap-and-service/rust.md`](bootstrap-and-service/rust.md).

## Quick reference

| Layer | Responsibilities |
|---|---|
| Composition Root | Reads config, constructs concretes, injects all deps |
| Application Service | Parses input, coordinates domain + ports, returns typed results |
| Adapter | Maps protocol (HTTP/command-line tool/queue) to service calls; implements a port |
| Domain | Business rules, aggregates, domain services, errors as values |

## Common mistakes

- **Domain logic in adapters**: validation, calculations, or branching in route handlers makes it untestable without an HTTP server
- **Protocol knowledge in services**: services that return status codes or accept `Request` objects prevent you from reusing them across adapters
- **No port interface**: calling adapters directly (not through an interface) prevents you from substituting them with fakes in unit tests; define the port in the service layer
- **Scattered wiring**: concrete dependencies constructed throughout the codebase instead of in one Composition Root make it impossible to swap implementations without touching many files

## Composes with

- **the parse-dont-validate pattern (`references/patterns/parse-dont-validate.md`)**: the app service is the first layer inside the boundary; it calls parsers before passing data to domain functions.
- **the repository pattern (`references/patterns/repository.md`)** + **the unit of work pattern (`references/patterns/unit-of-work.md`)**: the Composition Root wires concrete repositories into UoW factories; services receive the UoW through dependency injection.
- **the aggregate pattern (`references/patterns/aggregate.md`)**: app services orchestrate the aggregate lifecycle: open UoW, load aggregate, call one method, commit.
