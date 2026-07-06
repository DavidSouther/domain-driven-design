# Domain model

**Trigger:** starting a new project, subdomain, or bounded context.

## Process

### Step 1: Check the Glossary

Apply the glossary ability (`references/glossary.md`) to review existing terminology. As you discover domain terms in Steps 2 through 4, validate each against the glossary before finalizing it in Step 5. Do not record a term in `docs/ddd/` until it is either found in the glossary or added to it.

### Step 2: identify subdomains

Use event storming or noun/verb extraction from requirements:
- **Event storming:** Identify domain events (things that happened), commands (requests that trigger them), and actors (who triggers them). Group related events into clusters.
- **Noun/verb extraction:** List all **nouns** (entities, concepts) and **verbs** (operations, processes) from requirements. Group related nouns and verbs into coherent clusters.
Either technique produces candidate subdomains.

### Step 3: draw bounded context boundaries

- Each subdomain cluster becomes a candidate bounded context
- A bounded context is a coherent model with a consistent internal language
- Be explicit about what crosses boundaries (data contracts, events, API calls)
- One context per coherent model; avoid contexts that share mutable state

### Step 4: classify each context

| Classification | Description | Implementation Strategy |
|----------------|-------------|-------------------------|
| **Core** | Unique business differentiator | Implement in the project plan |
| **Generic** | Solved problem | Find and use a library as-is |
| **Supporting** | Necessary but not differentiating | Use libraries, configure minimally |

### Step 5: record the domain map

Mark all newly created files as `**[DRAFT]**` at the top until human-approved. See the Change Cadence Gate in `using-domain/SKILL.md`. Create or update `docs/ddd/domain-model.md`:

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

Create one file per bounded context at `docs/ddd/contexts/<context-name>.md`. Use lowercase kebab-case for context names, for example `order-management` or `inventory`:

```markdown
# <Context Name>

**Classification:** Core / Generic / Supporting
**Responsibilities:** <what this context owns>
**Consumes:** <what it receives from other contexts>
**Produces:** <what it sends to other contexts>
```

## Constraints

Consult `../../../references/arrow-of-maturity-stages.md` when classifying contexts and placing Core contexts in the implementation plan. It helps you understand the current architectural stage and recommend the appropriate starting point.

- **Core** domain contexts MUST appear in the implementation plan.
- Satisfy **Generic** and **Supporting** contexts with existing libraries unless no suitable library exists.
- Mark all new files under `docs/ddd/` as **[DRAFT]** until human-approved. See the Change Cadence Gate in `using-domain/SKILL.md`.
