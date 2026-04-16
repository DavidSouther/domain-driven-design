---
name: red-green-refactor
description: Use when implementing a plan step — type-first TDD cycle with a thinking trigger for stuck moments and an explicit abort condition
---

# developer:red-green-refactor

## Overview

The innermost development loop. Type-first TDD: write signatures before tests, tests before implementation, commit before refactoring. Has an explicit abort condition to prevent infinite loops.

**Announce at start:** "[Summary of the plan step.] Using developer:red-green-refactor for this step of the plan."

## The Loop

```dot
digraph rgr {
    "Plan step" [shape=doublecircle];
    "Type-first: write signatures" [shape=box];
    "Run check" [shape=box];
    "Type errors?" [shape=diamond];
    "Fix type errors" [shape=box];
    "Write one test (arrange-act-assert)" [shape=box];
    "Run check + test" [shape=box];
    "Test fails as expected?" [shape=diamond];
    "Implement (replace stubs)" [shape=box];
    "Run check + tests" [shape=box];
    "All pass?" [shape=diamond];
    "Same error after fix?" [shape=diamond];
    "Invoke developer:thinking" [shape=box];
    "Already tried thinking for this error?" [shape=diamond];
    "ABORT" [shape=doublecircle];
    "Commit" [shape=box];
    "developer:refactoring" [shape=box];
    "developer:code-review" [shape=box];
    "Done" [shape=doublecircle];

    "Plan step" -> "Type-first: write signatures";
    "Type-first: write signatures" -> "Run check";
    "Run check" -> "Type errors?" ;
    "Type errors?" -> "Fix type errors" [label="yes"];
    "Fix type errors" -> "Run check";
    "Type errors?" -> "Write one test (arrange-act-assert)" [label="no"];
    "Write one test (arrange-act-assert)" -> "Run check + test";
    "Run check + test" -> "Test fails as expected?" ;
    "Test fails as expected?" -> "Implement (replace stubs)" [label="yes"];
    "Test fails as expected?" -> "Write one test (arrange-act-assert)" [label="no — fix test"];
    "Implement (replace stubs)" -> "Run check + tests";
    "Run check + tests" -> "All pass?" ;
    "All pass?" -> "Same error after fix?" [label="no"];
    "Same error after fix?" -> "Already tried thinking for this error?" [label="yes"];
    "Already tried thinking for this error?" -> "ABORT" [label="yes"];
    "Already tried thinking for this error?" -> "Invoke developer:thinking" [label="no"];
    "Invoke developer:thinking" -> "Implement (replace stubs)" [label="follow thinking plan"];
    "All pass?" -> "Commit" [label="yes"];
    "Commit" -> "developer:refactoring";
    "developer:refactoring" -> "developer:code-review";
    "developer:code-review" -> "Done";
}
```

## Type-First

Write class/function/method signatures with stub bodies before writing any tests:

- Rust: `todo!()`
- Python: `...` or `raise NotImplementedError` or `return ""` (or appropriate default)
- TypeScript: `throw new Error("not implemented")` or `return "";` (or appropriate default)

Run check. Fix all type errors before writing any tests. A clean type check means the API contract is coherent.

## Test: Arrange-Act-Assert

Add one test per iteration using `patterns:arrange-act-assert`. The test should:
- Target one behavior of the current plan step
- Fail for the right reason (the implementation is a stub, not a type error)
- Triangulate implementation and edge cases, following `patterns:triangulate`

Run check, then run tests. Confirm the test fails as expected.

## Implement

Replace stub bodies with real code. Run check, then run tests. Repeat until all tests pass and the feature test is passing up to the point expected by the current plan step.

## Thinking Trigger

Invoke `developer:thinking` when:
- The same error (or substantially the same) appears after a change intended to fix it
- An error appears that is unrelated to the code added or changed in this step

Pass to the thinking subagent:
- The exact error message
- The code added or changed in this step
- The plan step being implemented

## Loop Abort

If `developer:thinking` has already been invoked for the current error and the same or equivalent error reappears after following its plan, do **not** invoke `developer:thinking` again. Stop immediately and report:

> "Stuck on the same error after thinking. Error: `<error>`. Thinking doc at `docs/developer/YYYY-MM-DD-<topic>/thinking/<problem>.md`. Suggestion: review the current diff (`git diff`) or restore the working directory (`git restore .`) and try again."

Do not loop. Do not try a different approach on your own. Abort and report.

## Commit

When all tests are green:
1. `git add` only the files changed in this step.
2. Commit with a message describing what the step implemented.
3. Invoke `developer:refactoring`.
4. After refactoring, invoke `developer:code-review`.
