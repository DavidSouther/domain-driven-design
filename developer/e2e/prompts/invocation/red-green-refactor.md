A cleared design, feature test, and implementation plan for a JSON-Lines filter
CLI (`jq-lite`) are reproduced below. All three have been reviewed and their
`*Draft*` markers removed. The project is Python and tests run under `pytest`.

Execute **only Step 1 of the plan** (the predicate parser) as a single
red-green-refactor cycle: write the type-first signatures with stub bodies,
write one arrange-act-assert test that fails for the right reason, then implement
until that single test passes. Do not start Step 2. Show the code you write at
each part of the cycle.

Cleared design — `.ailly/developer/2026-06-03-A-jq-lite/design.md`:

```markdown
# jq-lite — JSON-Lines Predicate Filter

Reads JSON-Lines on stdin, evaluates a predicate expression (a small subset of
jq) against each record, writes matching records to stdout in input order.

## Predicate language

Field access (`status`, `user.id`), comparisons (`==` `!=` `<` `<=` `>` `>=`),
boolean connectives (`and` `or` `not`), and parentheses. Literals: numbers,
quoted strings, `true`/`false`/`null`. Standard library only.
```

Cleared feature test — `.ailly/developer/2026-06-03-A-jq-lite/feature-test.md`:

```markdown
# Feature Test — jq-lite

**Given** JSON-Lines on stdin and a predicate expression as a CLI argument,
**When** the user runs jq-lite,
**Then** records whose predicate is truthy are written to stdout in input order.

The executable test feeds JSON-Lines on stdin, passes a predicate that combines
a field comparison with a boolean connective, captures stdout, and asserts the
survivors match in order. It fails at the start because no implementation exists.
```

Cleared plan — `.ailly/developer/2026-06-03-A-jq-lite/plan.md`:

```markdown
# Implementation Plan: jq-lite

**Steps:**
- [ ] Step 1: Predicate parser
- [ ] Step 2: Predicate evaluator
- [ ] Step 3: Streaming filter loop
- [ ] Step 4: Malformed-line policy

## Step 1: Predicate parser

**Enables:** turning the predicate string into a structure the evaluator can
walk — the precondition for any record to be matched at all.

Build a small recursive-descent parser that turns a predicate string
(`status == 500 and retries > 3`) into an abstract syntax tree of comparison and
boolean nodes. Define the AST node shapes and the parser entry point. Do not
evaluate against a record yet.

## Step 2: Predicate evaluator

**Enables:** the truthiness decision the feature test asserts on. Walk the AST
against a decoded record and return a boolean.
```
