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
    plan_step [shape=doublecircle label="Plan step"];
    write_sigs [shape=box label="Type-first: write signatures"];
    run_check [shape=box label="Run check"];
    type_errors [shape=diamond label="Type errors?"];
    fix_types [shape=box label="Fix type errors"];
    write_test [shape=box label="Write one test (arrange-act-assert)"];
    run_check_test [shape=box label="Run check + test"];
    test_fails [shape=diamond label="Test fails as expected?"];
    implement [shape=box label="Implement (replace stubs)"];
    run_checks [shape=box label="Run check + tests"];
    all_pass [shape=diamond label="All pass?"];
    same_error [shape=diamond label="Same error after fix?"];
    invoke_thinking [shape=box label="Invoke developer:thinking"];
    tried_thinking [shape=diamond label="Already tried thinking for this error?"];
    abort [shape=doublecircle label="ABORT"];
    commit [shape=box label="Commit"];
    refactor [shape=box label="developer:refactor"];
    done [shape=doublecircle label="Done"];

    plan_step -> write_sigs;
    write_sigs -> run_check;
    run_check -> type_errors;
    type_errors -> fix_types [label="yes"];
    fix_types -> run_check;
    type_errors -> write_test [label="no"];
    write_test -> run_check_test;
    run_check_test -> test_fails;
    test_fails -> implement [label="yes"];
    test_fails -> write_test [label="no — fix test"];
    implement -> run_checks;
    run_checks -> all_pass;
    all_pass -> same_error [label="no"];
    same_error -> tried_thinking [label="yes"];
    tried_thinking -> abort [label="yes"];
    tried_thinking -> invoke_thinking [label="no"];
    invoke_thinking -> implement [label="follow thinking plan"];
    all_pass -> commit [label="yes"];
    commit -> refactor;
    refactor -> done;
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

Replace stub bodies with real code. Run check, then run tests. Repeat until all tests pass and the feature test is passing up to the point expected by the current plan step. Modify doc comments as needed.

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

> "Stuck on the same error after thinking. Error: `<error>`. Thinking doc at `docs/developer/YYYY-MM-DD-A-<topic>/thinking/<problem>.md`. Suggestion: review the current diff (`git diff`) or restore the working directory (`git restore .`) and try again."

Do not loop. Do not try a different approach on your own. Abort and report.

## Commit

When all tests are green:
1. `git add` only the files changed in this step.
2. Commit with a message describing what the step implemented.
3. Invoke `developer:refactor`.
4. Commit with a message describing the refactorings.