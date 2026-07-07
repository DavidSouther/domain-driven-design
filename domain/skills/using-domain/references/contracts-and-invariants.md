# Contracts and Invariants

**Trigger:** when you define API contracts.

## Process

### Step 1: Check the Glossary

Apply the glossary ability (`references/glossary.md`) to ensure all field names, types, and operation names use canonical terms. If `docs/ddd/glossary.md` does not exist, create it first by applying the glossary ability, then proceed.

### Step 2: Define contracts

For each operation, specify:

- **Input contract:** required fields, types, allowed values, and preconditions. Preconditions are conditions the caller must meet before calling the operation.
- **Output contract:** response shape, postconditions, and error cases. Postconditions show what the operation guarantees after completion. Error cases might include: "400 if X is missing, 409 if Y already exists."

Contracts describe the observable data shape at boundaries. Invariants (in Step 3) are different. They are business rules that must always hold true—not just when operations start or end.

### Step 3: Define Invariants

List states that must always hold true at the API edge.

- Example: "An Order must always have at least one line item."
- Invariants may be **transiently violated** during transaction processing.
- Never let violations show to users. Effects only appear after the transaction is complete.

### Step 4: Record in bounded context file

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

- If the bounded context file does not exist, create it first by applying the domain-model ability (`references/domain-model.md`).
- All type names and field names must match the glossary canonical terms.
- Mark new entries with **[DRAFT]** until they are approved. See the Change Cadence Gate in `using-domain/SKILL.md` for the approval process.
