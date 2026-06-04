The cleared design for a JSON-Lines filter CLI (`jq-lite`) is reproduced below.
It has been reviewed and its `*Draft*` marker removed. No feature test has been
written yet, and no implementation exists. The project is Python and tests run
under `pytest`.

Produce the feature test for this design: the user story in plain language and
one executable test that encodes it end-to-end.

Cleared design — `docs/developer/2026-06-03-A-jq-lite/design.md`:

```markdown
# jq-lite — JSON-Lines Predicate Filter

## Problem Statement

Operators routinely pipe JSON-Lines (one JSON object per line) through shell
pipelines and need to keep only the records that satisfy a simple condition —
"status is 500", "retries greater than 3", "level is error and service is
checkout". `grep` matches text, not structure, so it both over- and
under-matches on JSON. The full `jq` grammar is far more than this task needs
and is a separate binary to install. The gap is a tiny, dependency-free filter
that understands just enough structure to evaluate a predicate per line.

## Prior Art

- `jq`: a complete JSON query language. Correct but heavyweight; the predicate
  use case is a sliver of its grammar.
- `grep`/`awk`: line-oriented and ubiquitous, but blind to JSON structure — a
  match on `"status": 500` also matches `"status": 5000`.
- Python one-liners: work, but are rewritten ad hoc every time and handle
  malformed lines inconsistently.

## Metrics

- A 1 MB JSON-Lines stream with a trivial predicate is filtered in well under a
  second on a developer laptop.
- A malformed line never aborts the stream: it is reported and skipped, and the
  remaining lines are still processed.
- The exit code distinguishes "ran cleanly" from "saw at least one bad line".

## Specification

- **Input.** JSON-Lines on stdin, one object per line. A predicate expression as
  a single command-line argument.
- **Predicate language.** Field access (`status`, `user.id`), the comparison
  operators `==` `!=` `<` `<=` `>` `>=`, the boolean connectives `and` `or`
  `not`, and parentheses for grouping. Literals are numbers, quoted strings, and
  the bare words `true`/`false`/`null`.
- **Behaviour.** For each input line: parse it as JSON; evaluate the predicate
  against the record; if the result is truthy, write the original line to stdout
  unchanged. Records are emitted in input order.
- **Errors.** A line that does not parse as JSON is written to stderr as a
  one-line warning (`line N: invalid JSON`) and skipped; processing continues.
- **Exit code.** `0` if every line parsed; `1` if any line was skipped as
  malformed.

## Alternatives

- **Embed `jq` itself.** Rejected: pulls a large grammar and an external binary.
- **Depend on a general expression-parser library.** Rejected: an unbounded
  grammar and a dependency, where a small purpose-built parser suffices.
- **Accept only equality, no boolean connectives.** Rejected: real filters need
  `and`/`or`.

## Summary

A small parser → evaluator → streaming-I/O loop, standard library only. No
persistence, no configuration file, no network.
```
