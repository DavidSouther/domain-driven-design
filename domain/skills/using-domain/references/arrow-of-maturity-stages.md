# Arrow of maturity: design stages

This document describes six design stages for domain-driven design projects.
The `ddd:domain-model` and `ddd:arrow-of-maturity` skills reference this document.

---

## Stage 0: Prototype / data engineering

**Purpose:** explore feasibility.
Understand the domain before building production software.
Show early demos of promising ideas.
Find areas that are easy, hard, or complex.

**Characteristics:**
- Scripts, notebooks, or exploratory code
- No production setup (no CI/CD, monitoring, SLAs)
- Data work and quick queries
- Minimal structure; all code gets thrown away

**Move on when:** you validate the domain and are ready to build production software. 

The domain-driven-design skill does not apply at this stage.
Do not use it here.

---

## Stage 1: Straight-through handler

**Purpose:** build real software.
Process requests end-to-end with minimal structure.

**Characteristics:**
- Thin handlers (controllers, functions, lambdas) that use an off-the-shelf ORM for storage
- Pure CRUD and minimal business logic
- No domain objects or domain model
- ORM access with migrations
- One deployable unit with standard CI/CD
- Log-based monitoring
- No SLAs

**Move on when:** business logic builds up with conditions, rules, or calculations that have domain meaning.

---

## Stage 2a: Domain model

**Purpose:** name domain concepts.
Separate business logic from infrastructure.

**Characteristics:**
- Ubiquitous language that names business entities and processes
- Domain objects (entities, value objects, service functions) using names from ubiquitous language
- Business logic lives in domain objects, not in handlers
- An app or service layer calls infrastructure (storage, messaging)
- Domain objects don't depend on infrastructure

**Move on when:**
- You need to swap or test storage → go to Stage 2b first
- Multi-entity operations need all-or-nothing success → go to Stage 2c (always do 2b first)

---

## Stage 2b: Extracted repository

**Purpose:** isolate storage behind an interface for testing and swapping out implementations.

**Characteristics:**
- Repository interface defined in the domain layer
- Repository code in the infrastructure layer
- Domain objects don't know how storage works
- Tests can use in-memory repositories

**Move on when:** multi-entity operations need to all succeed or all fail together → go to Stage 2c.

---

## Stage 2c: Aggregates and units of work

**Purpose:** define clear boundaries for all-or-nothing operations.

**Characteristics:**
- Aggregates enforce rules within their boundary
- Unit of Work tracks changes in a transaction
- Repositories only show aggregate roots
- Transactions cover an aggregate's full lifecycle

**Move on when:** you face production pressure for high throughput, SLAs, audit trails, or need to model time → go to Stage 3.

---

## Stage 3: Event-sourced microservices

**Purpose:** manage production scale, SLA needs, and time-based queries.

**Characteristics:**
- State derived from an unchanging event log
- Each service owns its domain and data
- Services talk via domain events
- Full audit trail and time-travel queries
- Complex operations (distributed tracing, saga coordination)

**Move on when:** real production pressure exists, you have SLA needs, or the domain models time (history, audit, replay).

**Warning:** this stage adds real operational and cognitive complexity.
Do not introduce it without clear need.
