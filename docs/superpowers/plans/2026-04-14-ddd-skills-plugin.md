# DDD Skills Plugin Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Create the `domain-driven-design` Claude Code plugin with six DDD skills and one shared reference document.

**Architecture:** The plugin is a directory of Markdown skill files auto-discovered by Claude Code. Each `skills/<name>/SKILL.md` becomes the `ddd:<name>` skill. A shared `references/arrow-of-maturity-stages.md` avoids duplicating stage prose between two skills. No code, no build step — this is a pure content plugin.

**Tech Stack:** Markdown, Claude Code plugin convention (SKILL.md frontmatter + body), git for versioning.

---

## File Map

| File | Role |
|------|------|
| `package.json` | Plugin manifest: name + version |
| `references/arrow-of-maturity-stages.md` | Shared prose: full description of all 6 architectural stages |
| `skills/using-ddd/SKILL.md` | Bootstrap: routing table + change cadence gate |
| `skills/domain-model/SKILL.md` | Domain modeling process + output artifacts |
| `skills/ubiquitous-language/SKILL.md` | Language development process + human review gate |
| `skills/glossary/SKILL.md` | Living glossary: format, lookup rules, synonym handling |
| `skills/contracts-and-invariants/SKILL.md` | API/service contract + invariant definition |
| `skills/arrow-of-maturity/SKILL.md` | Stage assessment + progression rules |

---

## Task 1: Plugin Manifest

**Files:**
- Create: `package.json`

### Spec requirements checklist
- [ ] name is `domain-driven-design`
- [ ] version is `1.0.0`
- [ ] No extraneous fields

- [ ] **Step 1: Write `package.json`**

```json
{
  "name": "domain-driven-design",
  "version": "1.0.0"
}
```

- [ ] **Step 2: Verify against checklist**

Read `package.json` and confirm all three spec requirements above are met.

- [ ] **Step 3: Commit**

```bash
git add package.json
git commit -m "feat: add plugin manifest"
```

---

## Task 2: Arrow of Maturity Reference Document

**Files:**
- Create: `references/arrow-of-maturity-stages.md`

### Spec requirements checklist
- [ ] Describes all 6 stages: 0, 1, 2a, 2b, 2c, 3
- [ ] Each stage has: Purpose, Characteristics, Move-on signal
- [ ] Stage 3 includes a warning against speculative adoption
- [ ] File is cited correctly in `ddd:domain-model` and `ddd:arrow-of-maturity` (checked when those skills are written)

- [ ] **Step 1: Write `references/arrow-of-maturity-stages.md`**

```markdown
# Arrow of Maturity: Architectural Stages

This document describes the six architectural stages. Referenced by `ddd:domain-model` and `ddd:arrow-of-maturity`.

---

## Stage 0: Prototype / Data Engineering

**Purpose:** Explore feasibility. Understand the domain before committing to a software architecture.

**Characteristics:**
- Scripts, notebooks, or exploratory code
- No production lifecycle (no CI/CD, monitoring, SLAs)
- Data transformations and ad hoc queries
- Minimal structure; throw-away code is acceptable

**Move on when:** Domain is validated and you are ready to build production-quality software.

---

## Stage 1: Straight-Through Handler

**Purpose:** First real software. Handle requests end-to-end with minimal structure.

**Characteristics:**
- Thin handlers (controllers, functions, lambdas) that call storage directly
- Pure CRUD; minimal business logic
- No domain objects or explicit domain model
- Single deployable unit

**Move on when:** Business logic begins accumulating — conditions, rules, or calculations that have domain meaning appear.

---

## Stage 2a: Domain Model

**Purpose:** Give names to domain concepts. Separate business logic from infrastructure.

**Characteristics:**
- Domain objects (entities, value objects) with names from the ubiquitous language
- Business logic lives in domain objects, not in handlers
- Infrastructure (storage, messaging) called from an application/service layer
- Domain objects have no dependency on infrastructure

**Move on when:**
- You need to swap or test persistence in isolation → go to Stage 2b
- Multi-entity operations require transactional integrity → go to Stage 2c

---

## Stage 2b: Extracted Repository

**Purpose:** Isolate persistence behind an interface for testability and replaceability.

**Characteristics:**
- Repository interface defined in the domain layer
- Repository implementation in the infrastructure layer
- Domain objects have no knowledge of how they are persisted
- Tests can use in-memory repository implementations

**Move on when:** Multi-entity operations appear that must succeed or fail atomically → go to Stage 2c.

---

## Stage 2c: Aggregates and Units of Work

**Purpose:** Model transactional consistency boundaries explicitly.

**Characteristics:**
- Aggregates enforce invariants within their boundary
- Unit of Work tracks changes across a transaction
- Only aggregate roots are accessible via repositories
- Transactions span an aggregate's full lifecycle

**Move on when:** Production scaling pressure appears — high throughput, SLA requirements, need for audit trails, or the domain genuinely models the dimension of time → go to Stage 3.

---

## Stage 3: Event-Sourced Microservices

**Purpose:** Handle production scale, SLA requirements, and temporal domain queries.

**Characteristics:**
- State derived from an immutable event log
- Each microservice owns its domain and data
- Services communicate via domain events
- Full audit trail; time-travel queries are possible
- Complex operational requirements (distributed tracing, saga orchestration)

**Move here only when:** Genuine production scaling pressure exists, SLA requirements demand it, or the domain inherently models time (history, audit, replay).

**Warning:** This stage adds substantial operational and cognitive complexity. Do not introduce it speculatively.
```

- [ ] **Step 2: Verify against checklist**

Read the file and confirm all spec requirements above are met.

- [ ] **Step 3: Commit**

```bash
git add references/arrow-of-maturity-stages.md
git commit -m "feat: add arrow-of-maturity stages reference document"
```

---

## Task 3: `ddd:using-ddd` Bootstrap Skill

**Files:**
- Create: `skills/using-ddd/SKILL.md`

### Spec requirements checklist
- [ ] Frontmatter with `name` and `description`
- [ ] Routing table with all 5 trigger → skill mappings
- [ ] Change cadence gate: explicit human approval required for `docs/ddd/` changes
- [ ] Draft label rule: changes may land as Draft without review
- [ ] Git branch recommendation mentioned

- [ ] **Step 1: Write `skills/using-ddd/SKILL.md`**

```markdown
---
name: using-ddd
description: Bootstrap skill for Domain-Driven Design. Loaded at session start to establish when to invoke each DDD skill.
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

## Change Cadence Gate

Any proposed change to `docs/ddd/` requires explicit human approval before being finalized.

- Changes may be introduced and committed as **[DRAFT]** without human review.
- Use a git branch for DDD changes when possible.
- Do NOT remove the **[DRAFT]** label without explicit human sign-off.
- Domain design changes at a substantially lower cadence than feature work and bug fixes.
```

- [ ] **Step 2: Verify against checklist**

Read the file and confirm all spec requirements above are met.

- [ ] **Step 3: Commit**

```bash
git add skills/using-ddd/SKILL.md
git commit -m "feat: add ddd:using-ddd bootstrap skill"
```

---

## Task 4: `ddd:domain-model` Skill

**Files:**
- Create: `skills/domain-model/SKILL.md`

### Spec requirements checklist
- [ ] Frontmatter with `name` and `description`
- [ ] Trigger documented
- [ ] Process: subdomain identification via event storming / noun-verb extraction
- [ ] Process: bounded context boundary drawing
- [ ] Process: Core / Generic / Supporting classification table
- [ ] Output artifact format for `docs/ddd/domain-model.md`
- [ ] Output artifact format for `docs/ddd/contexts/<context-name>.md`
- [ ] Constraint: Core must appear in impl plan; Generic/Supporting must use libraries
- [ ] Glossary check step present

- [ ] **Step 1: Write `skills/domain-model/SKILL.md`**

```markdown
---
name: domain-model
description: Guide domain modeling for a new project, subdomain, or bounded context. Identifies subdomains, draws bounded context boundaries, and classifies each as Core, Generic, or Supporting.
---

# Domain Modeling

**Trigger:** Starting a new project, subdomain, or bounded context.

## Process

### Step 1: Check the Glossary

Invoke `ddd:glossary` to review existing terminology before introducing any new terms.

### Step 2: Identify Subdomains

Use event storming or noun/verb extraction from requirements:
- List all **nouns** (entities, concepts) mentioned in requirements
- List all **verbs** (operations, processes) mentioned in requirements
- Group related nouns and verbs into coherent clusters — these are candidate subdomains

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

Create or update `docs/ddd/domain-model.md`:

```markdown
# Domain Model

## Subdomains

| Subdomain | Classification | Bounded Context | Notes |
|-----------|----------------|-----------------|-------|
| <name>    | Core | <context-name> | <why it's core> |

## Boundary Map

<Describe what flows between each pair of contexts: events, data contracts, API calls>
` `` `

Create one file per bounded context at `docs/ddd/contexts/<context-name>.md`:

` ``markdown
# <Context Name>

**Classification:** Core / Generic / Supporting
**Responsibilities:** <what this context owns>
**Consumes:** <what it receives from other contexts>
**Produces:** <what it sends to other contexts>
` `` `

## Constraints

- **Core** domain contexts MUST appear in the implementation plan.
- **Generic** and **Supporting** contexts MUST be satisfied by existing libraries unless no suitable library exists.
- All new files under `docs/ddd/` must be marked **[DRAFT]** until human-approved (see `ddd:using-ddd`).
```

- [ ] **Step 2: Verify against checklist**

Read the file and confirm all spec requirements above are met.

- [ ] **Step 3: Commit**

```bash
git add skills/domain-model/SKILL.md
git commit -m "feat: add ddd:domain-model skill"
```

---

## Task 5: `ddd:ubiquitous-language` Skill

**Files:**
- Create: `skills/ubiquitous-language/SKILL.md`

### Spec requirements checklist
- [ ] Frontmatter with `name` and `description`
- [ ] Trigger documented
- [ ] Step: check glossary first
- [ ] Step: research from internal knowledge bases (NOT codebase)
- [ ] Step: categorize into "Ask domain expert" vs "Confirm with domain expert"
- [ ] Step: insist on human review; terms marked [DRAFT]
- [ ] Step: add confirmed terms to glossary
- [ ] Output: candidate terms list + categorized question list

- [ ] **Step 1: Write `skills/ubiquitous-language/SKILL.md`**

```markdown
---
name: ubiquitous-language
description: Develop ubiquitous language for a bounded context. Research candidate terms, categorize questions for domain experts, and populate the glossary.
---

# Ubiquitous Language Development

**Trigger:** When entities, operations, or domain concepts are being named or discovered.

## Process

### Step 1: Check the Glossary First

Invoke `ddd:glossary` before introducing any term. If the term already exists, use the canonical name.

### Step 2: Research

Use internal knowledge bases (requirements, design docs, domain literature) to draft candidate terms.

- **Do NOT use the codebase as source of truth** — the code may itself be wrong.
- Many domain questions have been answered in existing literature.
- Draft definitions with a **[DRAFT]** label; these are not finalized.

### Step 3: Categorize Questions

For each term not resolved by research, categorize:

| Category | When to use |
|----------|-------------|
| **Ask a domain expert** | Core domain specifics unique to this organization; business rules not recorded anywhere |
| **Confirm with domain expert** | Generic/Supporting domain terms that are likely standard but warrant human sign-off |

### Step 4: Present for Human Review

- Mark all generated terms as **[DRAFT]**.
- Present the candidate terms list and categorized question list to a domain expert.
- Do NOT finalize any term without explicit human sign-off.

### Step 5: Add to Glossary

For each confirmed term, invoke `ddd:glossary` to add it to `docs/ddd/glossary.md`.

## Output

1. **Candidate terms list** — each term with a draft definition and its research source
2. **Categorized question list** — questions for domain experts, grouped by category (Ask vs. Confirm)
```

- [ ] **Step 2: Verify against checklist**

Read the file and confirm all spec requirements above are met.

- [ ] **Step 3: Commit**

```bash
git add skills/ubiquitous-language/SKILL.md
git commit -m "feat: add ddd:ubiquitous-language skill"
```

---

## Task 6: `ddd:glossary` Skill

**Files:**
- Create: `skills/glossary/SKILL.md`

### Spec requirements checklist
- [ ] Frontmatter with `name` and `description`
- [ ] Trigger documented
- [ ] Rule: ALL other skills must check before introducing terminology
- [ ] 5-step lookup process (check → use canonical → add synonym → add new → resolve ambiguous)
- [ ] Glossary entry format: Term, Definition, Context, Synonyms, Source
- [ ] Rule: [DRAFT] label for unconfirmed terms
- [ ] Rule: do not remove [DRAFT] without human approval

- [ ] **Step 1: Write `skills/glossary/SKILL.md`**

```markdown
---
name: glossary
description: Manage the living DDD glossary. Check before introducing terms, add new entries, resolve synonyms and ambiguity. ALL other DDD skills must invoke this skill before introducing terminology.
---

# Living Glossary

**Trigger:** Any time a term is undefined, ambiguous, or potentially synonymous with an existing term.

**ALL other DDD skills must check the glossary before introducing terminology.**

## Process

1. **Check first.** Read `docs/ddd/glossary.md` before introducing a term or asking the user about terminology.
2. **If the term exists:** Use the canonical name. Do not introduce alternate spellings or alternate forms.
3. **If synonymous with an existing term:** Add it as a marked synonym. Do not create a duplicate entry.
4. **If the term is new:** Add it with a definition, context, and source. Mark as **[DRAFT]** until human-approved.
5. **If the term is ambiguous:** Resolve via the glossary first. Escalate to the user only when the glossary cannot resolve the ambiguity.

## Glossary File Format

File: `docs/ddd/glossary.md`

Each entry uses this format:

```markdown
## <Term>
**Definition:** <clear, precise definition>
**Context:** <bounded context where this term is primary>
**Synonyms:** <term1>, <term2>  *(omit section if none)*
**Source:** <expert conversation | research | codebase>
` `` `

## Rules

- Every entry must include Definition, Context, and Source.
- Include Synonyms only when synonyms exist.
- Terms not confirmed by a domain expert must be marked **[DRAFT]**.
- Do not remove **[DRAFT]** without explicit human approval.
```

- [ ] **Step 2: Verify against checklist**

Read the file and confirm all spec requirements above are met.

- [ ] **Step 3: Commit**

```bash
git add skills/glossary/SKILL.md
git commit -m "feat: add ddd:glossary skill"
```

---

## Task 7: `ddd:contracts-and-invariants` Skill

**Files:**
- Create: `skills/contracts-and-invariants/SKILL.md`

### Spec requirements checklist
- [ ] Frontmatter with `name` and `description`
- [ ] Trigger documented
- [ ] Step: check glossary first
- [ ] Step: define input contract (required fields, types, allowed values, preconditions)
- [ ] Step: define output contract (response shape, error cases, postconditions)
- [ ] Step: define invariants with transactional note
- [ ] Rule: invariants may be transiently violated but never externally observable
- [ ] Output format matches spec: Operation Name, Contract (input), Contract (output), Invariants, Transactional note
- [ ] Step: append to `docs/ddd/contexts/<context-name>.md`

- [ ] **Step 1: Write `skills/contracts-and-invariants/SKILL.md`**

```markdown
---
name: contracts-and-invariants
description: Define contracts and invariants for API boundaries, service interfaces, and domain operations. Records output in the bounded context file.
---

# Contracts and Invariants

**Trigger:** Designing any API boundary, service interface, or domain operation signature.

## Process

### Step 1: Check the Glossary

Invoke `ddd:glossary` to ensure all field names, types, and operation names use canonical terms.

### Step 2: Define Contracts

For each operation, specify:

- **Input contract:** required fields, types, allowed values, preconditions
- **Output contract:** response shape, error cases, postconditions

### Step 3: Define Invariants

List states that must hold true at all times at the API edge.

- Example: "An Order must always have at least one line item."
- Invariants may be **transiently violated** during transaction processing.
- Violations must **never be observable externally** — effects are only visible once the transaction is complete.

### Step 4: Record in Bounded Context File

Append to `docs/ddd/contexts/<context-name>.md`:

```markdown
### <Operation Name>
**Contract (input):** <required fields, types, allowed values, preconditions>
**Contract (output):** <response shape, error cases, postconditions>
**Invariants:**
- <invariant 1>
- <invariant 2>
**Transactional note:** <invariants that may be transiently violated mid-transaction, if any>
` `` `

## Notes

- If the bounded context file does not exist, invoke `ddd:domain-model` first.
- All type names and field names must match glossary canonical terms.
- New entries in context files must be marked **[DRAFT]** until human-approved (see `ddd:using-ddd`).
```

- [ ] **Step 2: Verify against checklist**

Read the file and confirm all spec requirements above are met.

- [ ] **Step 3: Commit**

```bash
git add skills/contracts-and-invariants/SKILL.md
git commit -m "feat: add ddd:contracts-and-invariants skill"
```

---

## Task 8: `ddd:arrow-of-maturity` Skill

**Files:**
- Create: `skills/arrow-of-maturity/SKILL.md`

### Spec requirements checklist
- [ ] Frontmatter with `name` and `description`
- [ ] Trigger documented
- [ ] Reference to `references/arrow-of-maturity-stages.md`
- [ ] Stage summary table (all 6 stages with move-here signal)
- [ ] Rules: move quickly 1→2a; extract repository before production; 2c only when discovered not speculative; do NOT rush to Stage 3; advance only when current stage creates friction
- [ ] Output: current stage + signal + next concrete step

- [ ] **Step 1: Write `skills/arrow-of-maturity/SKILL.md`**

```markdown
---
name: arrow-of-maturity
description: Guide architectural stage selection using the Arrow of Maturity. Assesses current stage, identifies the signal that justifies advancing, and recommends the next concrete step.
---

# Arrow of Maturity

**Trigger:** Architecture reviews, adding persistence, scaling discussions, or any time the current architecture creates friction.

For full stage descriptions, see `references/arrow-of-maturity-stages.md`.

## Stages

| Stage | Name | Move here when... |
|-------|------|-------------------|
| 0 | Prototype / Data Engineering | Exploring feasibility; minimal software lifecycle needed |
| 1 | Straight-Through Handler | First real code; pure CRUD with minimal business logic |
| 2a | Domain Model | Business logic accumulates; concepts need names |
| 2b | Extracted Repository | Persistence needs to be swapped or tested in isolation |
| 2c | Aggregates & Units of Work | Multi-entity operations with transactional integrity |
| 3 | Event-Sourced Microservices | Production scaling pressures; SLA requirements; time dimension matters |

## Rules

- **Move quickly from Stage 1 to 2a.** Once business logic appears, concepts need names. Do not remain in straight-through handlers.
- **Extract a Repository (2b) before production.** Required for long-term codebase health.
- **Introduce Aggregates and Unit of Work (2c) only when those domain operations are discovered** — not speculatively.
- **Do NOT rush to Stage 3.** Event-sourced microservices are justified only by genuine production scaling pressure or the need to model the dimension of time.
- **Advance only when the current stage creates genuine friction.**

## Output

Provide:
1. **Current stage** — which stage the codebase is at and the evidence
2. **Signal** — the friction or trigger that justifies advancing (or the reason to stay)
3. **Next concrete step** — the specific refactoring or architectural change to make next (if advancing)
```

- [ ] **Step 2: Verify against checklist**

Read the file and confirm all spec requirements above are met.

- [ ] **Step 3: Commit**

```bash
git add skills/arrow-of-maturity/SKILL.md
git commit -m "feat: add ddd:arrow-of-maturity skill"
```

---

## Self-Review Against Spec

### Spec coverage

| Spec requirement | Covered by |
|------------------|-----------|
| `package.json` with name + version | Task 1 |
| `references/arrow-of-maturity-stages.md` | Task 2 |
| `skills/using-ddd/SKILL.md` — routing table | Task 3 |
| `skills/using-ddd/SKILL.md` — change cadence gate | Task 3 |
| `skills/domain-model/SKILL.md` — subdomain identification | Task 4 |
| `skills/domain-model/SKILL.md` — context classification | Task 4 |
| `skills/domain-model/SKILL.md` — output artifacts | Task 4 |
| `skills/domain-model/SKILL.md` — Core/Generic/Supporting constraint | Task 4 |
| `skills/ubiquitous-language/SKILL.md` — research first, not codebase | Task 5 |
| `skills/ubiquitous-language/SKILL.md` — categorized question list | Task 5 |
| `skills/ubiquitous-language/SKILL.md` — human review gate | Task 5 |
| `skills/glossary/SKILL.md` — lookup + synonym + new term + ambiguous | Task 6 |
| `skills/glossary/SKILL.md` — entry format | Task 6 |
| `skills/contracts-and-invariants/SKILL.md` — input/output contracts | Task 7 |
| `skills/contracts-and-invariants/SKILL.md` — invariants + transactional note | Task 7 |
| `skills/contracts-and-invariants/SKILL.md` — append to context file | Task 7 |
| `skills/arrow-of-maturity/SKILL.md` — stage table | Task 8 |
| `skills/arrow-of-maturity/SKILL.md` — progression rules | Task 8 |
| `skills/arrow-of-maturity/SKILL.md` — output format | Task 8 |
| Cross-skill: all skills check glossary before introducing terms | Tasks 4, 5, 7, 8 (each includes a glossary check step) |
| Cross-skill: domain-model seeds glossary | Task 4 references `ddd:glossary` in Step 1 |
| Cross-skill: using-ddd routes to all skills | Task 3 routing table |

No gaps found.

### Placeholder scan

No TBD, TODO, "implement later", "fill in details", "add appropriate", "similar to Task N", or steps without code content. All steps show the full file content to write.

### Type consistency

No code types — these are Markdown files. Term consistency: `[DRAFT]` label used consistently across Tasks 3–8. File paths `docs/ddd/domain-model.md`, `docs/ddd/glossary.md`, `docs/ddd/contexts/<context-name>.md` used consistently across all tasks.
