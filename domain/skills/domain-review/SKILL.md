---
name: domain-review
description: Use when reviewing changes to a domain model — entities, value objects, aggregates, domain services, or bounded context boundaries. Also applies when ubiquitous language terms were introduced or modified. Produces a critique document, not edits to the code.
---

# Domain Review

Review domain model changes for alignment with DDD principles and the project's ubiquitous language. The artifact is a critique document. Do not edit code.

## When to Use

- Entities, value objects, aggregates, or domain services were added or modified.
- Bounded context boundaries changed, or cross-context calls were introduced.
- New terms were introduced in code that may not match the glossary.
- A reviewer suspects domain logic leaked into the wrong layer.

**When NOT to use:** general code correctness, performance, or style. This is a domain model review, not a code review.

## Review Criteria

Evaluate the following. For each finding, name the file and line, quote the relevant code, state what principle is violated, and recommend an action.

**Identity and value semantics** — Each object should be either identity-bearing (Entity) or equality-by-value (Value Object), not both and not neither. Flag an Entity that exposes no stable identity, a Value Object that carries mutable state, or an object whose role is ambiguous. See the domain-objects pattern (`patterns:using-patterns`, `references/patterns/domain-objects.md`).

**Invariant placement** — Business rules that must always hold should be enforced by the object that owns the state, not by callers. Flag validation or guard logic that lives outside the domain object it protects, or an object whose constructor accepts inputs it never rejects.

**Aggregate boundary** — An Aggregate root should protect its invariants across the cluster of objects it owns. Flag direct manipulation of an Aggregate's internal objects from outside the root, an Aggregate that reaches into another Aggregate's internals, or an Aggregate boundary so large it requires cross-cutting locks.

**Domain service necessity** — A Domain Service is appropriate when an operation spans multiple Aggregates and cannot logically belong to any one of them. Flag a Domain Service that wraps a single Aggregate's operation (it belongs on the Aggregate), and flag domain logic on an Entity that reaches outside its own cluster (it belongs in a service).

**Ubiquitous language consistency** — Code identifiers (class names, method names, field names) should match the glossary terms for this bounded context. Flag identifiers that use synonyms, technical substitutions (e.g., `record` for `Order`), or terms from a different bounded context without an explicit translation.

**Bounded context respect** — Objects from one bounded context should not be passed directly into another. Cross-context calls should go through a published interface, an anti-corruption layer, or a translation step. Flag raw domain objects leaking across context boundaries.

**Layer discipline** — Domain objects should not import from application, infrastructure, or UI layers. Flag a domain object that depends on a repository interface, an HTTP client, a logger, or any framework type.

## Output Format

Produce a critique document. Group findings by criterion. For each finding:

1. File and line reference.
2. Quoted code (one to three lines).
3. Which criterion is violated and why.
4. Recommended action: move, rename, extract, collapse, or no change with rationale.

If a criterion has no findings, write "No findings." Do not omit it silently.

## Common Mistakes

- **Conflating Entity and Value Object identity** — flagging every object without an `id` field as an Entity violation. Value Objects intentionally have no identity field.
- **Over-applying Aggregate boundaries** — recommending that all related objects become one Aggregate. Small, tight Aggregates with explicit cross-Aggregate references are the correct direction.
- **Prescribing the glossary** — the review checks consistency with the existing glossary, not correctness of the glossary itself. Glossary changes are a separate `domain:glossary` session.
- **Reviewing infrastructure adapters** — repository implementations, HTTP handlers, and ORM mappings are not domain objects. Do not apply domain model criteria to them.
