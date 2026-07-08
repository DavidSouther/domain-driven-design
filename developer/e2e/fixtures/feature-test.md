# Feature Test — jq-lite

## User Story

**Given** a stream of JSON-Lines on stdin and a predicate expression passed as a single command-line argument, **When** the user runs `jq-lite`, **Then** the records whose evaluation of the predicate is truthy are written to stdout in their original input order, and records that do not match are omitted.

## Test

The executable test runs the tool end-to-end as the user would: it feeds a small fixture of JSON-Lines on stdin, passes a predicate argument, captures stdout, and asserts that the captured lines are exactly the records that satisfy the predicate, in input order.
It exercises one predicate that combines a field comparison with a boolean connective, so the single end-to-end path covers parsing, evaluation, and streaming together.

The test lives in the project's test suite and runs under the project's test runner.
It fails at the start because no implementation exists yet.
