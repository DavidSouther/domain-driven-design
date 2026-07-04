---
name: using-patterns
description: Bootstrap and routing skill for design patterns. Loaded at session start to decide which pattern applies to a design pressure — wrapping a primitive as a domain type (newtype), modeling entities and value objects (domain-objects), constructing many-field objects (builder), encapsulating fields (visibility), parsing untrusted input (parse-dont-validate), signalling failure with typed or stringly errors (errors-typed-untyped), encoding lifecycle phases (type-states), persisting without coupling to storage (repository), holding a transactional consistency boundary (aggregate), flushing changes atomically (unit-of-work), wiring a testable service layer (bootstrap-and-service), structuring tests (arrange-act-assert), forcing a real implementation (triangulate), converting between domain types (type-conversion), bootstrapping a logging pipeline (configuring-logging) versus emitting a log record (emitting-logs), and standing up a feature-flag harness (configuring-feature-flags) versus putting one feature behind a flag (using-feature-flags). Names the applicable pattern and points at its reference under references/patterns/.
---

# Design Patterns Workflow

You are working in a project that uses structured design patterns. This skill is the
routing surface for the whole pattern catalog. During design, plan, and review phases,
read the situation, name the pattern that fits, and open its reference under
`references/patterns/<name>.md` for the full teaching (overview, when-to-use, core
pattern, and language examples).

Each row below states the discriminator that selects the pattern and the reference
that holds it. Match the situation in the left column, then read the reference in the
right column. Do not apply all patterns upfront; start with the one that addresses the
immediate design pressure.

## Routing Table

| Situation (discriminator) | Pattern and reference |
|---------------------------|-----------------------|
| A single primitive (string, number, UUID) carries NO behavior and just needs a distinct type so it cannot be mixed with another primitive of the same shape (a `UserId` where an `OrderId` is expected, `Kilometers` added to `Miles`) | newtype — `references/patterns/newtype.md` |
| An object carries behavior or calculations (e.g. an `OrderLine` doing price math), or you are deciding what has identity (Entity), what is equal by value (Value Object), and what is a free function (Domain Service) | domain-objects — `references/patterns/domain-objects.md` |
| Constructing an object with many fields, a required-vs-optional distinction, or partial-initialization risk that a many-parameter constructor makes error-prone | builder — `references/patterns/builder.md` |
| A domain object exposes public fields, leaks mutable collections, or allows state changes via direct assignment instead of named methods | visibility — `references/patterns/visibility.md` |
| Untyped or untrusted data crosses a boundary (HTTP, user input, file, message queue, storage) and validity proofs should be carried in the type system rather than re-checked with scattered null/boolean guards | parse-dont-validate — `references/patterns/parse-dont-validate.md` |
| Designing how a library function or API signals failure — a typed error hierarchy the caller can match on (a function failing several ways the caller must match on routes HERE), versus a stringly-typed message for a human reader | errors-typed-untyped — `references/patterns/errors-typed-untyped.md` |
| A domain object has distinct lifecycle phases (open/closed, draft/published) and only a subset of operations is valid in each, so illegal state-plus-data combinations should be unrepresentable | type-states — `references/patterns/type-states.md` |
| Domain objects must be persisted or retrieved while the domain stays decoupled from a specific storage technology (in-memory, SQL, API, CSV), and tests must run without a real database | repository — `references/patterns/repository.md` |
| An invariant requires that a cluster of entities change together through one entry point, protecting a transactional consistency boundary where a partial mid-operation write would leave an illegal state | aggregate — `references/patterns/aggregate.md` |
| An application handler must load an aggregate, run a domain operation, and flush all changes atomically (commit together or roll back entirely), bridging the aggregate and the repository inside one durable transaction | unit-of-work — `references/patterns/unit-of-work.md` |
| Structuring the application layer, wiring concrete dependencies at startup, and keeping external adapters (HTTP, CLI, queue) thin and free of domain logic so the service stays testable without external processes | bootstrap-and-service — `references/patterns/bootstrap-and-service.md` |
| Writing or reviewing any test so it has a clear setup phase, a single action, and focused assertions; or untangling a test whose setup and assertions are interleaved | arrange-act-assert — `references/patterns/arrange-act-assert.md` |
| A UI screen or console is driven repeatedly across acceptance/e2e tests, and selector/wait duplication should localize behind verb-phrase actions | page-objects — `references/patterns/page-objects.md` |
| A fake (hardcoded) implementation passes the first test and the correct generalization is not yet obvious — write a second test that forces the real implementation rather than guessing the abstraction | triangulate — `references/patterns/triangulate.md` |
| Converting one domain type to another, extracting a wrapped primitive to rewrap as something else, or reshaping an aggregate across lifecycle stages — visible as `as` casts, primitive extraction, or duplicated `to_X`/`from_X` pairs | type-conversion — `references/patterns/type-conversion.md` |
| Bootstrapping a service's logging pipeline ONCE at process start — subscriber/registry, formatter/filter/enricher/exporter, resource attributes, installing a W3C trace propagator, sampling, redaction, graceful shutdown flush | configuring-logging — `references/patterns/configuring-logging.md` |
| Writing a single log call site INSIDE an already-running handler — choosing a severity, attaching structured fields under semantic conventions, scoping a span to a unit of work, recording an error chain once at a boundary, naming a business event | emitting-logs — `references/patterns/emitting-logs.md` |
| Standing up or revising a project's feature-flag system ONCE — a provider behind a vendor-neutral interface, fail-safe defaults, naming and ownership, environment resolution, a kill switch, stale-flag CI | configuring-feature-flags — `references/patterns/configuring-feature-flags.md` |
| Putting one feature behind a flag at its call site — its category, a name with owner and expiry, a default equal to current behavior, a single toggle point kept separate from the decision logic, both states tested, a removal plan | using-feature-flags — `references/patterns/using-feature-flags.md` |

## Discriminators That Are Easy to Confuse

These pairs route to different patterns. State the discriminator before choosing.

- **newtype vs domain-objects.** A single primitive carrying NO behavior — a bare
  `UserId`/`OrderId` that must not be mixed, a `Cents` that must not be added to
  `Meters` — routes to newtype (`references/patterns/newtype.md`). An object carrying
  behavior or calculations — an `OrderLine` doing unit-price-times-quantity, discount,
  and line-total math, or any decision about identity vs value vs service — routes to
  domain-objects (`references/patterns/domain-objects.md`). Wrapping a tuple that does
  price math is domain-objects, not newtype.

- **errors-typed-untyped (not parse-dont-validate).** A library function that can fail
  several ways the caller must match on — retry one, surface another, give up on a
  third — routes to errors-typed-untyped (`references/patterns/errors-typed-untyped.md`),
  which decides between a typed error hierarchy and a stringly-typed message. This is a
  failure-signalling decision, not an input-validation one; do not route it to
  parse-dont-validate.

- **configuring-logging vs emitting-logs.** Bootstrap or pipeline setup — including
  installing a W3C trace propagator at process start — runs ONCE and routes to
  configuring-logging (`references/patterns/configuring-logging.md`). A log line written
  INSIDE an already-running handler routes to emitting-logs
  (`references/patterns/emitting-logs.md`). The split is bootstrap-once versus
  per-record.

- **configuring-feature-flags vs using-feature-flags.** The same bootstrap-vs-per-use
  split. Standing up the flag harness (provider, defaults, naming, kill switch) runs
  ONCE and routes to configuring-feature-flags
  (`references/patterns/configuring-feature-flags.md`). Putting one feature behind one
  flag at one toggle point routes to using-feature-flags
  (`references/patterns/using-feature-flags.md`).

- **aggregate vs unit-of-work.** An invariant across multiple objects protected by a
  single root is aggregate (`references/patterns/aggregate.md`). The atomic, durable
  flush that wraps the aggregate operation at commit time is unit-of-work
  (`references/patterns/unit-of-work.md`).

- **type-states vs parse-dont-validate.** A field present only after a lifecycle
  transition (a `shippingAddress` that exists only once a cart is confirmed) is a
  distinct phase and routes to type-states (`references/patterns/type-states.md`).
  Untrusted data crossing a boundary routes to parse-dont-validate
  (`references/patterns/parse-dont-validate.md`).

- **type-conversion vs newtype.** Reshaping or rewrapping an existing typed value into
  another type — extract-and-rewrap, duplicated `to_X`/`from_X` — routes to
  type-conversion (`references/patterns/type-conversion.md`). First wrapping a bare
  primitive routes to newtype (`references/patterns/newtype.md`).

- **bootstrap-and-service vs repository.** Wiring the composition root and keeping
  adapters thin is bootstrap-and-service (`references/patterns/bootstrap-and-service.md`).
  Decoupling the domain from a storage technology is repository
  (`references/patterns/repository.md`).

- **triangulate vs arrange-act-assert.** Forcing a real implementation by writing a
  second test is triangulate (`references/patterns/triangulate.md`). Structuring any one
  test cleanly is arrange-act-assert (`references/patterns/arrange-act-assert.md`).

- **page-objects vs arrange-act-assert.** Encapsulating a reusable UI surface
  (a screen or console) behind verb-phrase actions, reused across many
  acceptance tests, routes to page-objects (`references/patterns/page-objects.md`).
  Structuring the arrange/act/assert phases of one test routes to
  arrange-act-assert (`references/patterns/arrange-act-assert.md`).

## Pattern Composition

Patterns compose in predictable ways. Recognise these combinations:

- **parse-dont-validate + newtype** — parse external input directly into domain types;
  the parsed type *is* the proof of validity. See
  `references/patterns/parse-dont-validate.md` and `references/patterns/newtype.md`.
- **repository + aggregate** — a persistence-ignorant domain model with clean
  consistency boundaries. Add unit-of-work when the operation must be atomic and
  durable. See `references/patterns/repository.md`, `references/patterns/aggregate.md`,
  and `references/patterns/unit-of-work.md`.
- **bootstrap-and-service** — the outer shell that wires repository, unit-of-work, and
  protocol adapters together at startup. Apply last. See
  `references/patterns/bootstrap-and-service.md`.
- **type-conversion + newtype** — newtype constructors *are* the canonical conversions;
  total constructors implement `From`, partial constructors implement `TryFrom`/`parse`,
  and call sites stop reaching into `.0` to rewrap. See
  `references/patterns/type-conversion.md` and `references/patterns/newtype.md`.
- **configuring-logging + emitting-logs** — the two halves of structured logging.
  Configuration sets the envelope and the exporter once; emission attaches the per-event
  fields under the semantic conventions the configuration enforces. Run them together;
  one without the other produces structured logs that are not queryable, or queryable
  logs that are not centralized. See `references/patterns/configuring-logging.md` and
  `references/patterns/emitting-logs.md`.
- **configuring-feature-flags + using-feature-flags** — the two halves of feature
  flagging. Configuration installs one vendor-neutral evaluation entry point with
  fail-safe defaults and naming, ownership, and expiry conventions. Usage puts one
  feature behind one flag at a single toggle point. Run them together. A flag without
  the harness scatters vendor SDKs across call sites, and a harness with no disciplined
  usage fills with stale flags. See `references/patterns/configuring-feature-flags.md`
  and `references/patterns/using-feature-flags.md`.

Do not apply all patterns upfront. Start with the one that addresses the immediate
design pressure, name it, and read its reference.
