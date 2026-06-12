A cleared design for a JSON-Lines filter CLI (`jq-lite`) is reproduced below. Its
`*Draft*` marker was removed after review. The design records the path of its one
feature test, `tests/test_jq_lite.py`, which lives in the project test tree and
is currently failing because no implementation exists. The project is Python and
tests run under `pytest`.

Produce the implementation plan. Write everything inline as your reply: do not
call any tools or emit tool-call JSON.

Cleared design — `.ailly/developer/2026-06-03-A-jq-lite/design.md`:

```markdown
# jq-lite — JSON-Lines Predicate Filter

## Purpose

A tiny, dependency-free filter that reads JSON-Lines on stdin, evaluates a
predicate expression (a small subset of jq) against each record, and writes the
matching records to stdout in input order. `grep` is blind to JSON structure and
full `jq` is heavier than a predicate-only need.

## Specification

- **Input.** JSON-Lines on stdin; a predicate expression as a single CLI
  argument.
- **Predicate language.** Field access (`status`, `user.id`), comparisons
  (`==` `!=` `<` `<=` `>` `>=`), boolean connectives (`and` `or` `not`), and
  parentheses. Literals: numbers, quoted strings, `true`/`false`/`null`.
- **Behaviour.** Parse each line as JSON; evaluate the predicate; if truthy,
  write the original line to stdout unchanged. Input order preserved.
- **Errors.** A line that fails to parse as JSON goes to stderr as a one-line
  warning and is skipped; processing continues.
- **Exit code.** `0` if every line parsed; `1` if any line was skipped.

## Summary

A small parser → evaluator → streaming-I/O loop, standard library only.
```

Feature test recorded by the design, living in the project at
`tests/test_jq_lite.py` and currently failing:

```markdown
# Feature Test — jq-lite (recorded in design.md)

## User Story

**Given** a stream of JSON-Lines on stdin and a predicate expression passed as a
single command-line argument,
**When** the user runs `jq-lite`,
**Then** the records whose evaluation of the predicate is truthy are written to
stdout in their original input order, and non-matching records are omitted.

## Test

The executable test runs the tool end-to-end: it feeds a small fixture of
JSON-Lines on stdin, passes a predicate argument that combines a field comparison
with a boolean connective, captures stdout, and asserts the captured lines are
exactly the records that satisfy the predicate, in input order. It fails at the
start because no implementation exists yet.
```
