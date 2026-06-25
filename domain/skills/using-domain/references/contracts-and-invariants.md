# Contracts and Invariants

**Trigger:** Designing any API boundary, service interface, or domain operation signature.

## Process

### Step 1: Check the Glossary

Apply the glossary ability (`references/glossary.md`) to ensure all field names, types, and operation names use canonical terms. If `docs/ddd/glossary.md` does not exist, apply the glossary ability (`references/glossary.md`) to create it first before proceeding.

### Step 2: Define Contracts

For each operation, specify:

- **Input contract:** required fields, types, allowed values, and preconditions (conditions the caller must ensure before invoking)
- **Output contract:** response shape, postconditions (guarantees the operation provides after completion), and error cases (e.g., "400 if X is missing, 409 if Y already exists")

Contracts describe the observable data shape at boundaries. Invariants (Step 3) are different: they are business rules that must always be true, not just at operation boundaries.

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
```

Replace all `<...>` placeholders with actual values. Omit **Transactional note** entirely if no invariants can be transiently violated.

## Notes

- If the bounded context file does not exist, apply the domain-model ability (`references/domain-model.md`) first.
- All type names and field names must match glossary canonical terms.
- New entries in context files must be marked **[DRAFT]** until human-approved (see the Change Cadence Gate in `using-domain/SKILL.md`).
