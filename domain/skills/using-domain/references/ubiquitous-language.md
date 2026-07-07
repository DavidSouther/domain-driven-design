# Ubiquitous language

**Trigger:** when you name or discover entities, operations, or domain concepts.

## Process

### Step 1: Check the glossary first

Apply the glossary ability (`references/glossary.md`) before introducing any term. If the term already exists, use the canonical name.

### Step 2: Research

Read `docs/ddd/domain-model.md` (if it exists) to understand the established subdomains and bounded contexts. Then use other internal knowledge bases (requirements, design docs, domain literature) to draft candidate terms for those contexts.

- **Do NOT use the codebase as source of truth**, as the code itself may be wrong.
- Existing literature answers many domain questions.
- Draft definitions with a **[DRAFT]** label and record the source (document name, section, or literature reference) for each term. You must include the source in the output.

### Step 3: Categorize questions

For each term not resolved by research, categorize:

| Category | When to use |
|----------|-------------|
| **Ask a domain expert** | Core domain specifics unique to this organization; business rules not recorded anywhere |
| **Confirm with domain expert** | Generic/Supporting domain terms that are likely standard but warrant human sign-off |

When in doubt, use **Ask** rather than **Confirm**. Over-confirming is safe. Under-asking risks incorrect domain language.

### Step 4: Present for human review

- Mark all generated terms as **[DRAFT]**.
- Present the candidate terms list and categorized question list to a domain expert.
- **Do NOT proceed to Step 5 until the domain expert provides explicit approval.**
- Do NOT finalize any term without explicit human sign-off.

### Step 5: Add to Glossary

For each confirmed term, apply the glossary ability (`references/glossary.md`) to add it to `docs/ddd/glossary.md`.

## Output

1. **Candidate terms list**: each term with a draft definition and its research source
2. **Categorized question list**: questions for domain experts, grouped by category (Ask vs. Confirm)
