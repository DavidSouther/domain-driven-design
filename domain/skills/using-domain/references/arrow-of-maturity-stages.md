# Arrow of maturity: architectural stages

This document describes a common set of six architectural stages that domain driven design projects grow through. Referenced by `ddd:domain-model` and `ddd:arrow-of-maturity`.

---

## Stage 0: Prototype / data engineering

**Purpose:** explore feasibility. Understand the domain before committing to an architecture. Show an early demo of interesting possibilities. Identify areas of unexpected ease, difficulty, complexity, etc.

**Characteristics:**
- Scripts, notebooks, or exploratory code
- No production lifecycle (no CI/CD, monitoring, SLAs)
- Data transformations and ad hoc queries
- Minimal structure; engineers discard all code

**Move on when:** you validate the domain and are ready to build production-quality software. 

The domain-driven-design skill does not facilitate work at this stage, and you should not use it at this stage.

---

## Stage 1: Straight-through handler

**Purpose:** first real software. Process requests end-to-end with minimal structure.

**Characteristics:**
- Thin handlers (controllers, functions, lambdas) that call storage through an off the shelf ORM
- Pure CRUD; minimal business logic
- No domain objects or explicit domain model
- ORM data access with migrations
- Single deployable unit using off-the-shelf CI/CD
- Standard output logs monitoring
- No SLAs

**Move on when:** business logic begins accumulating; conditions, rules, or calculations that have domain meaning appear.

---

## Stage 2a: Domain model

**Purpose:** give names to domain concepts. Separate business logic from infrastructure.

**Characteristics:**
- Ubiquitous language describing the business entities and processes
- Domain objects (entities, value objects, service functions) with names from the ubiquitous language
- Business logic lives in domain objects, not in handlers
- Infrastructure (storage, messaging) called from an app/service layer
- Domain objects have no dependency on infrastructure

**Move on when:**
- You need to swap or test persistence in isolation → go to Stage 2b first
- Multi-entity operations require transactional integrity → go to Stage 2c (always implement 2b before 2c)

---

## Stage 2b: Extracted repository

**Purpose:** isolate persistence behind an interface for testability and replaceability.

**Characteristics:**
- Repository interface defined in the domain layer
- Repository implementation in the infrastructure layer
- Domain objects don't know how storage persists them
- Tests can use in-memory repository implementations

**Move on when:** multi-entity operations appear that must atomically succeed or fail → go to Stage 2c.

---

## Stage 2c: Aggregates and units of work

**Purpose:** model transactional consistency boundaries explicitly.

**Characteristics:**
- Aggregates enforce invariants within their boundary
- Unit of Work tracks changes across a transaction
- Repositories only expose aggregate roots
- Transactions span an aggregate's full lifecycle

**Move on when:** production scaling pressure appears: high throughput, SLA requirements, need for audit trails, or the domain genuinely models the dimension of time → go to Stage 3.

---

## Stage 3: Event-sourced microservices

**Purpose:** manage production scale, SLA requirements, and temporal domain queries.

**Characteristics:**
- State derived from an immutable event log
- Each microservice owns its domain and data
- Services communicate via domain events
- Full audit trail; time-travel queries are possible
- Complex operational requirements (distributed tracing, saga orchestration)

**Move on when:** genuine production scaling pressure exists, SLA requirements demand it, or the domain inherently models time (history, audit, replay).

**Warning:** this stage adds substantial operational and cognitive complexity. Do not introduce it speculatively.
