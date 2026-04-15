# DDD Skills Plugin Design

**Date:** 2026-04-14
**Plugin name:** `domain-driven-design` (invoked as `ddd:*`)
**Status:** Approved

---

## Overview

A Claude Code plugin that teaches LLM agents Domain-Driven Design practices through six discrete, invocable skills. Skills guide agents through the full DDD lifecycle: discovering a domain model, developing ubiquitous language, maintaining a glossary, defining contracts and invariants, and following the Arrow of Maturity to choose the right architectural stage.

---

## Plugin Structure

```
ddd_skill/
├── package.json
├── skills/
│   ├── using-ddd/
│   │   └── SKILL.md
│   ├── domain-model/
│   │   └── SKILL.md
│   ├── ubiquitous-language/
│   │   └── SKILL.md
│   ├── glossary/
│   │   └── SKILL.md
│   ├── contracts-and-invariants/
│   │   └── SKILL.md
│   └── arrow-of-maturity/
│       └── SKILL.md
└── references/
    └── arrow-of-maturity-stages.md
```

### `package.json`

```json
{
  "name": "domain-driven-design",
  "version": "1.0.0"
}
```

Skills are discovered automatically from the `skills/` directory by Claude Code. No explicit skills list is needed in the manifest.

### `references/arrow-of-maturity-stages.md`

Shared prose document describing the four architectural stages (Straight-Through Handler, Domain Model, Repository + Aggregates/UoW, Event-Sourced Microservices). Cited by `ddd:domain-model` and `ddd:arrow-of-maturity` to avoid duplication.

---

## Skills

### `ddd:using-ddd`: Bootstrap

**Loaded at session start.** Establishes the full DDD skill workflow and tells agents when to invoke each skill:

| Situation | Invoke |
|-----------|--------|
| Starting a new project, service, or feature with business logic | `ddd:domain-model` |
| Naming entities, operations, or concepts | `ddd:ubiquitous-language` |
| An ambiguous or potentially synonymous term appears | `ddd:glossary` |
| Designing any API boundary, service interface, or domain operation | `ddd:contracts-and-invariants` |
| Evaluating architecture, adding persistence, or feeling scaling pressure | `ddd:arrow-of-maturity` |

**Change cadence gate:** Any proposed change to `docs/ddd/` must be flagged for explicit human approval. Changes may be committed to the repo without human review, so long as they are clearly labeled "Draft". This should be in a git branch, but may be added directly with a clear textual label that it is still a draft. Domain design changes at a substantially lower cadence than feature work.

---

### `ddd:domain-model`: Domain Modeling

**Trigger:** Starting a new project, subdomain, or bounded context.

**Process:**
1. Identify subdomains. Use event storming or noun/verb extraction from requirements.
2. Draw bounded context boundaries. One context per coherent model, explicit about what crosses boundaries.
3. Classify each context:
   - **Core**: unique business differentiator; implement in the project plan
   - **Generic**: solved problem; find and use a library as-is
   - **Supporting**: necessary but not differentiating; use libraries, configure minimally
4. Record the domain map

**Output artifact:** `docs/ddd/domain-model.md`: a living document listing all subdomains, their classification, and their bounded context boundaries. One file per context at `docs/ddd/contexts/<context-name>.md`.

**Constraint:** Core domain context must appear in the implementation plan. Generic and Supporting contexts must be satisfied by existing libraries unless no suitable library exists.

---

### `ddd:ubiquitous-language`: Language Development

**Trigger:** When entities, operations, or domain concepts are being named or discovered.

**Process:**
1. **Research first** using internal knowledge bases to draft candidate terms. Many questions have likely been answered by existing literature. The codebase is not an appropriate place to find an answer, as the code itself may be wrong.
2. **Categorize questions** into these buckets.
   - *Ask a domain expert* Core domain specifics that cannot be derived from research (e.g., business rules unique to this organization, or requirements that haven't been recorded in internal documents.)
   - *Confirm with domain expert* Generic &Supporting domain terms that are likely standard but warrant human sign-off.
3. **Insist on human review** for generated requirements before being finalized, but terms may be added as draft.
4. **Add to glossary** every new term discovered. Write it into `docs/ddd/glossary.md`.

**Output:** A list of candidate terms (with definitions) and a categorized question list for domain experts.

---

### `ddd:glossary`, the Living Glossary

**Trigger:** Any time a term is undefined, ambiguous, or potentially synonymous with an existing term.

**Process:**
1. Check `docs/ddd/glossary.md` before introducing a new term or asking the user
2. If the term exists, use the canonical name from the glossary
3. If the term is synonymous with an existing term, add it as a marked synonym. Do not create duplicate entries.
4. If the term is new, add it with a definition and source (which bounded context or expert conversation introduced it).
5. If the term is ambiguous, resolve via the glossary first; only escalate to the user when the glossary cannot resolve it.

**Artifact** `docs/ddd/glossary.md` format

```markdown
## <Term>
**Definition:** ...
**Context:** <bounded context where this term is primary>
**Synonyms:** <term1>, <term2>  *(if any)*
**Source:** <expert conversation | research | codebase>
```

**Rule:** All other skills must check the glossary before introducing terminology.

---

### `ddd:contracts-and-invariants` Interface Design

**Trigger:** Designing any API boundary, service interface, or domain operation signature.

**Process:**
1. **Define contracts** specifying the format of incoming and outgoing data at the API edge.
   - Input contract: required fields, types, allowed values, preconditions
   - Output contract: response shape, error cases, postconditions
2. **Define invariants** as states that must hold true at all times at the API edge.
   - List invariants explicitly (e.g., "an Order must always have at least one line item")
   - Note that invariants may be transiently violated during transaction processing, but violations must never be observable externally. Effects are only visible once the transaction is complete.
3. **Record in bounded context file** the contracts and invariants as `docs/ddd/contexts/<context-name>.md`

**Output format:**

```markdown
### <Operation Name>
**Contract (input):** ...
**Contract (output):** ...
**Invariants:**
- <invariant 1>
- <invariant 2>
**Transactional note:** <any invariants that may be transiently violated mid-transaction>
```

---

### `ddd:arrow-of-maturity` Architectural Stage Guidance

**Trigger:** Architecture reviews, adding persistence, scaling discussions, or any time the current architecture creates friction.

**Stages (see `references/arrow-of-maturity-stages.md`):**

| Stage | Name | Move here when... |
|-------|------|-------------------|
| 0 | Prototype / Data Engineering | Exploring feasibility; minimal software lifecycle needed |
| 1 | Straight-Through Handler | First real code; pure CRUD with minimal business logic |
| 2a | Domain Model | Business logic accumulates; concepts need names |
| 2b | Extracted Repository | Persistence needs to be swapped or tested in isolation |
| 2c | Aggregates & Units of Work | Multi-entity operations with transactional integrity |
| 3 | Event-Sourced Microservices | Production scaling pressures; SLA requirements; time dimension matters |

**Rules:**
- Projects should move quickly from Stage 1 to Stage 2a (Domain Model). Don't stay in straight-through handlers once business logic appears.
- Extract a Repository (Stage 2b) before production. This is necessary for long-term codebase health.
- Introduce Aggregates and Unit of Work (Stage 2c) only when those domain operations are discovered, not speculatively.
- Do NOT rush to Stage 3. Event-sourced microservices are justified only by genuine production scaling pressure or the need to model the dimension of time.
- Advance only when the current stage creates genuine friction.

**Output:** A recommendation of the current stage, the signal that justifies advancing (or staying), and the next concrete step.

---

## Artifact Conventions

All DDD artifacts live under `docs/ddd/` in the project repository:

```
docs/ddd/
├── domain-model.md          # overall domain map; subdomains, classifications
├── glossary.md              # living glossary; all canonical terms
└── contexts/
    └── <context-name>.md    # one file per bounded context; contracts, invariants
```

**Change cadence:** Changes to any file under `docs/ddd/` are domain design changes. They require explicit human approval and should happen at a substantially lower cadence than feature work and bug fixes. They will likely be introduced, marked as draft, and iterated on before beinalized.

---

## Cross-Skill Dependencies

```
using-ddd
  └── routes to all other skills

domain-model
  ├── produces: docs/ddd/domain-model.md, docs/ddd/contexts/*.md
  ├── seeds: glossary (initial domain terms)
  └── consults: arrow-of-maturity-stages.md (to assess current stage)

ubiquitous-language
  ├── reads: docs/ddd/domain-model.md
  └── writes: docs/ddd/glossary.md

glossary
  ├── reads/writes: docs/ddd/glossary.md
  └── consulted by: ALL skills before introducing terminology

contracts-and-invariants
  ├── reads: docs/ddd/contexts/<context-name>.md
  └── appends: contracts and invariants to context file

arrow-of-maturity
  ├── reads: docs/ddd/domain-model.md
  └── references: references/arrow-of-maturity-stages.md
```

---

## Out of Scope

- Event storming tooling (skills describe the practice, not automate it)
- Code generation from domain models. Skills like Superpowers will take over for feature development.
- Integration with external modeling tools (Miro, Lucidchart, etc.)
- Enforcement of naming conventions in code (separate linting concern)
