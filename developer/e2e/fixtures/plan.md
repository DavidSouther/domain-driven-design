# Implementation Plan: jq-lite

**Feature test:** the end-to-end stdin → stdout survivor test for jq-lite.
**User story:** users filter a JSON-Lines stream with a small predicate language,
keeping the records whose predicate evaluates truthy.

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
boolean nodes. This step defines the AST node shapes and the parser entry point.
It does not evaluate anything against a record yet.

## Step 2: Predicate evaluator

**Enables:** deciding, for one parsed record, whether the predicate holds — the
truthiness decision the feature test asserts on.

Walk the AST against a single decoded JSON value and return a boolean. Field
access reads keys (and dotted paths) off the record; comparisons and boolean
connectives combine to a final verdict.

## Step 3: Streaming filter loop

**Enables:** the top-level feature-test assertion that captured stdout contains
exactly the survivor records in input order.

Read stdin line by line, decode each line as JSON, evaluate the parsed predicate,
and write the original line to stdout when the verdict is truthy. Wire the parser
and evaluator from steps 1 and 2 into the stream.

## Step 4: Malformed-line policy

**Enables:** the design's guarantee that a bad line is reported and skipped while
the stream continues, and that the exit code reflects whether any line was bad.

Catch a decode failure per line, write a one-line warning to stderr, continue
with the next line, and exit non-zero if any line was skipped.
