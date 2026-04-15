---
name: domain-model
description: Guide domain modeling for a new project, subdomain, or bounded context. Identifies subdomains, draws bounded context boundaries, and classifies each as Core, Generic, or Supporting.
---

# Domain Modeling

**Trigger:** Starting a new project, subdomain, or bounded context.

## Process

### Step 1: Check the Glossary

Invoke `ddd:glossary` to review existing terminology. As you discover domain terms in Steps 2–4, validate each against the glossary before finalizing it in Step 5. Do not record a term in `docs/ddd/` until it is either found in the glossary or added to it.

### Step 2: Identify Subdomains

Use event storming or noun/verb extraction from requirements:
- **Event storming:** Identify domain events (things that happened), commands (requests that trigger them), and actors (who triggers them). Group related events into clusters.
- **Noun/verb extraction:** List all **nouns** (entities, concepts) and **verbs** (operations, processes) from requirements. Group related nouns and verbs into coherent clusters.
Either technique produces candidate subdomains.

### Step 3: Draw Bounded Context Boundaries

- Each subdomain cluster becomes a candidate bounded context
- A bounded context is a coherent model with a consistent internal language
- Be explicit about what crosses boundaries (data contracts, events, API calls)
- One context per coherent model; avoid contexts that share mutable state

### Step 4: Classify Each Context

| Classification | Description | Implementation Strategy |
|----------------|-------------|-------------------------|
| **Core** | Unique business differentiator | Implement in the project plan |
| **Generic** | Solved problem | Find and use a library as-is |
| **Supporting** | Necessary but not differentiating | Use libraries, configure minimally |

### Step 5: Record the Domain Map

Mark all newly created files as `**[DRAFT]**` at the top until human-approved (see `ddd:using-ddd`). Create or update `docs/ddd/domain-model.md`:

```markdown
# Domain Model

## Subdomains

| Subdomain | Classification | Bounded Context | Notes |
|-----------|----------------|-----------------|-------|
| <name>    | Core | <context-name> | <why it's core> |

## Boundary Map

<Describe what flows between each pair of contexts: events, data contracts, API calls>

Example: "Orders context → Inventory context: `OrderPlaced` event carrying `{orderId, lineItems[{skuId, qty}]}`"
```

Create one file per bounded context at `docs/ddd/contexts/<context-name>.md` (use lowercase kebab-case for context names, e.g., `order-management`, `inventory`):

```markdown
# <Context Name>

**Classification:** Core / Generic / Supporting
**Responsibilities:** <what this context owns>
**Consumes:** <what it receives from other contexts>
**Produces:** <what it sends to other contexts>
```

## Constraints

When classifying contexts and placing Core contexts in the implementation plan, consult `references/arrow-of-maturity-stages.md` to understand the current architectural stage and recommend the appropriate starting point.

- **Core** domain contexts MUST appear in the implementation plan.
- **Generic** and **Supporting** contexts MUST be satisfied by existing libraries unless no suitable library exists.
- All new files under `docs/ddd/` must be marked **[DRAFT]** until human-approved (see `ddd:using-ddd`).
