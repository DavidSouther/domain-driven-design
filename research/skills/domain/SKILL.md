---
name: domain
description: Use when a research question is about the conceptual model of the problem space — entities, bounded contexts, ubiquitous language, invariants, or DDD maturity — rather than how code implements those concepts. Applies when `domain:` skills are loaded or when domain artifacts exist in the codebase. Does not apply to implementation questions (use `research:codebase`) or to questions answerable only from external sources (use `research:public`).
---

# Overview

Domain answers research questions about the conceptual model: what things exist, what they mean, how they relate, and what rules govern them. It draws on `domain:` DDD skills when available, or on domain artifacts found in the codebase when they are not.

# When to Use

- The question is about what a term, entity, or concept means in this domain
- The question is about structural relationships between domain objects
- The question is about invariants, contracts, or business rules
- The question requires understanding bounded contexts or aggregate boundaries

**Do NOT use** when the question is about how code implements a domain concept (use `research:codebase`), or when the domain is entirely undefined and must be sourced from external references (use `research:public`).

# Query Expansion (Jeopardy! Search)

Before running any search, generate 3–5 query variants per concept:

- **Canonical term** — the term as stated in the question
- **Synonyms** — alternate words a domain expert might use
- **Ubiquitous language variants** — project-specific vocabulary for the same concept
- **Structural synonyms** — `entity` / `aggregate` / `object`; `rule` / `invariant` / `constraint`
- **File-name variants** — `glossary`, `model`, `domain`, `entities`, `context`

Run each variant; union the results before synthesizing.

# Strategy

## When `domain:` skills are loaded

1. Invoke `domain:glossary` to resolve unfamiliar or ambiguous terms.
2. Invoke `domain:ubiquitous-language` to understand how the domain names and talks about concepts.
3. Invoke `domain:domain-model` to understand entities, value objects, aggregates, and bounded contexts.
4. Invoke `domain:contracts-and-invariants` when the question concerns rules or guarantees.
5. Invoke `domain:arrow-of-maturity` when the question concerns DDD adoption stage or architectural fit.

## When `domain:` skills are NOT loaded

Search the codebase for domain artifacts:

- Model files: `**/domain/**`, `**/model/**`, `**/entities/**`
- Glossary files: `**/glossary*`, `**/ubiquitous*`, `**/vocabulary*`
- README or documentation files describing the domain
- Aggregate or bounded-context definitions in any documentation directory

Use Jeopardy! search variants across all artifact locations before concluding a concept is undefined.

# Output Format

Write findings to `.ailly/research/YYYY-MM-DD-A-<topic>/domain.md`, unless the caller provides a task-scoped research folder such as `.ailly/developer/<session-slug>/research/`; in that case write `domain.md` there.

Structure:

```
# Domain Research: <question>

## Findings
<narrative summary: what the domain model says about this concept>

## Key Concepts
- <Term>: <definition or relationship>

## Sources
- Domain skills consulted: <list>
- Artifact files consulted: <paths>
- DDD concepts applied: <list>
```

# Common Mistakes

- **Answering from code instead of the model** — if the only source is implementation files rather than domain artifacts or `domain:` skills, escalate to `research:codebase` or note the gap explicitly.
- **Skipping query expansion** — a concept named `Order` may also appear as `PurchaseOrder`, `SalesOrder`, or `order_aggregate`; always expand before concluding absence.
- **Conflating bounded contexts** — the same term can mean different things in different contexts; identify which bounded context applies before defining a term.
- **Finalizing domain changes without approval** — if research surfaces a needed correction to domain artifacts in `docs/ddd/`, mark it `[DRAFT]` and request human sign-off before finalizing.
