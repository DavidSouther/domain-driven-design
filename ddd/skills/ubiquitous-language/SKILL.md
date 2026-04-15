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

Read `docs/ddd/domain-model.md` (if it exists) to understand the established subdomains and bounded contexts. Then use other internal knowledge bases (requirements, design docs, domain literature) to draft candidate terms for those contexts.

- **Do NOT use the codebase as source of truth**, as the code itself may be wrong.
- Many domain questions have been answered in existing literature.
- Draft definitions with a **[DRAFT]** label and record the source (document name, section, or literature reference) for each term. The source is required in the output.

### Step 3: Categorize Questions

For each term not resolved by research, categorize:

| Category | When to use |
|----------|-------------|
| **Ask a domain expert** | Core domain specifics unique to this organization; business rules not recorded anywhere |
| **Confirm with domain expert** | Generic/Supporting domain terms that are likely standard but warrant human sign-off |

When in doubt, use **Ask** rather than **Confirm** — over-confirming is safe; under-asking risks incorrect domain language.

### Step 4: Present for Human Review

- Mark all generated terms as **[DRAFT]**.
- Present the candidate terms list and categorized question list to a domain expert.
- **Do NOT proceed to Step 5 until the domain expert provides explicit approval.**
- Do NOT finalize any term without explicit human sign-off.

### Step 5: Add to Glossary

For each confirmed term, invoke `ddd:glossary` to add it to `docs/ddd/glossary.md`.

## Output

1. **Candidate terms list** — each term with a draft definition and its research source
2. **Categorized question list** — questions for domain experts, grouped by category (Ask vs. Confirm)
