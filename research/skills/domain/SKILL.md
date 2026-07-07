---
name: domain
description: "Use for questions about what the domain means. Include entities, relationships, rules, and DDD concepts. Don't use it for code questions or outside research."
---

# Overview

Domain answers research questions about the conceptual model. It covers what exists, what things mean, how they relate, and what rules apply. It uses `domain:` DDD skills when available, or domain artifacts from the codebase otherwise.

# When to use

- The question is about what a term, entity, or concept means in this domain
- The question is about structural relationships between domain objects
- The question is about invariants, contracts, or business rules
- The question requires understanding bounded contexts or aggregate boundaries

**Do NOT use** when the question is about how code implements a domain concept; use `research:codebase` instead. Also, don't use this when the domain is entirely undefined and you must source information from external references; use `research:public` instead.

# Query expansion (jeopardy search)

Before running any search, generate 3–5 query variants per concept:

- **Canonical term**: the term as stated in the question
- **Synonyms**: alternate words a domain expert might use
- **Ubiquitous language variants**: project-specific vocabulary for the same concept
- **Structural synonyms**: `entity` / `aggregate` / `object`; `rule` / `invariant` / `constraint`
- **File-name variants**: `glossary`, `model`, `domain`, `entities`, `context`

Run each variant; union the results before synthesizing.

# Strategy

## When `domain:` skills load

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

Use Jeopardy search variants across all artifact locations before concluding a concept lacks definition.

# Output format

Write findings to `.ailly/research/YYYY-MM-DD-A-<topic>/domain.md`. If the caller provides a task-scoped research folder such as `.ailly/developer/<session-slug>/research/`, write `domain.md` there instead.

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

# Common mistakes

- **Answering from code instead of the model**: if the only source is implementation files rather than domain artifacts or `domain:` skills, escalate to `research:codebase` or note the gap explicitly.
- **Skipping query expansion**: a concept named `Order` may also appear as `PurchaseOrder`, `SalesOrder`, or `order_aggregate`; always expand before concluding absence.
- **Conflating bounded contexts**: the same term can mean different things in different contexts; identify which bounded context applies before defining a term.
- **Finalizing domain changes without approval**: if research surfaces a needed correction to domain artifacts in `docs/ddd/`, mark it `[DRAFT]` and request human sign-off before finalizing.
