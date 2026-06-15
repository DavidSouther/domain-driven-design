---
name: using-domain
description: Bootstrap skill for Domain-Driven Design. Loaded when brainstorming, researching, or designing, to ensure domain knowledge is available. Not loaded during implementation, as the domain knowledge has already been summarized in the prompt.
---

# Domain-Driven Design Workflow

You are working in a project that uses Domain-Driven Design practices. Invoke the appropriate skill for each situation:

| Situation | Invoke |
|-----------|--------|
| Starting a new project, service, or feature with business logic | `ddd:domain-model` |
| Naming entities, operations, or domain concepts | `ddd:ubiquitous-language` |
| An ambiguous or potentially synonymous term appears | `ddd:glossary` |
| Designing any API boundary, service interface, or domain operation | `ddd:contracts-and-invariants` |
| Evaluating architecture, adding persistence, or feeling scaling pressure | `ddd:arrow-of-maturity` |
| Reviewing changes to entities, value objects, aggregates, or bounded contexts | `ddd:domain-review` |

## Change Cadence Gate

This gate applies to DDD artifact files under `docs/ddd/` (domain model, glossary, and context files) — not to these skill files.

Any proposed change to `docs/ddd/` requires explicit human approval before being finalized.

- Changes may be introduced and committed as **[DRAFT]** without human review.
- Use a git branch for DDD changes when possible.
- Do not finalize domain changes by removing **[DRAFT]** labels without explicit human sign-off.
- Plan for longer review cycles before finalizing domain changes; they happen at a substantially lower cadence than feature work.
