---
name: plan
description: Use when the design draft is cleared and its recorded feature test is currently failing. Defines the API surface area and breaks down the design for passing the feature test into 3 to 7 descriptive implementation steps.
---

# developer:plan

## Overview

Middle-loop planning skill. Given a cleared design and its failing feature test, defines the API surface area and breaks the path to making that test pass into 3–7 incremental steps. Each step must leave the codebase in a runnable state and advance the feature test measurably.

**Announce at start:** "Using developer:plan to create the implementation plan for [summary of feature]. Name the recommended model for planning from the Phase by Provider table in developer/references/model-per-phase.md, matched to the active provider, with its effort qualifier verbatim. If you're not already on it, I'll switch when the harness allows; otherwise switch with `/model` (press `s` for session-only) as the fallback. I'll continue on the current model either way."

**Trigger:** The design draft marker has been cleared by a human. The design records the project feature test, which is currently failing.

**Hard gate:** Do not implement any step. Do not write unit tests or implementation code. Step 0 defines API signatures as stubs; later steps describe what to build and may sketch critical interfaces, but all code in steps 1+ is orientation for the builder and must be re-derived during build. Decline any request to implement in this session.

**Distinction from `developer:writing-plans`:** This is focused on making piecemeal progress toward one specific failing test. It is not a general spec-to-plan conversion tool.

## Behavior

1. Read the cleared design and its recorded feature test (and user story) from the session folder.
2. Consider the API surface area changes needed (step 0 — see below).
3. Break the path to a passing feature test into several (no more than 7) incremental steps.
  - If it seems a plan would require more than a few steps, encourage the user to go back to the design and simplify the size of the step.
  - If it seems a plan would require more than 7 steps, insist that the user go back to the design.
3a. If the path from the failing test to a passing test isn't obvious, apply the forward-backward method. Work backward from the passing test state (what must be true just before the failing assertion passes?) and forward from the current code (what can be derived or added without breaking anything?) until the two sides connect into a complete sequence of steps. Write each candidate step to a map file as it is generated — do not hold steps only in context. See `developer/references/forward_backward.md`.
4. For each step: name it, describe what it builds, and identify which assertion in the feature test it enables. Steps may include type/API sketches and notes on critical areas as orientation for the builder, but no implementation code — each step is a description of what to build, not how to build it.
5. Save the plan as a draft and stop.

## Step 0: API Surface Area

Before implementation steps, define the type and API surface area the feature test requires. Step 0 is where all new types and public function signatures are established as stubs:

- Introduce new entities, value objects, or services needed
- Lean on `patterns:entities-value-objects-services`, `patterns:newtype`, `patterns:type-states` for guidance
- Show type signatures and function signatures (not implementations) for new objects
- Keep this focused on the domain model, not persistence or UI

Step 0 contains code (type stubs and signatures), but no function bodies. Everything in step 0 is tested by the feature test from the design.

## Step Criteria

Each step must:
- Leave the codebase in a runnable state (check and tests pass, even if feature test still fails).
- Make measurable progress toward the feature test passing.
- Include a suggested unit test for the happy path, and a list of expected edge cases to test.
- Write an outline of the main implementation (no error handling, bounds checking, etc) to get a feel of where it should go.

3 steps minimum (too few = steps are too large). 7 steps maximum (too many = over-engineering). Encourage the user to go back to the design in those cases.

## Plan Format

```markdown
# Implementation Plan: <feature name>

*Draft YYYY-MM-DD*

**Feature test:** `<test-file-path>`
**User story:** Summarize in one sentence.
**Steps:**
- [ ] Step 0: API surface area
- [ ] Step 1: <Name>
- [ ] Step 2: <Name>

## Step 0: API surface area

New types and function signatures (stubs only, no bodies):

```<lang>
// type stubs and function signatures
```

## Step 1: <Name>

**Enables:** `<which assertion or part of the feature test>`

Describe what this step builds. The feature test will still fail but `<specific assertion>` will no longer throw.

[Optional: API sketch or note on a critical interface — re-derive during build.]

**Tests**

Describe the main test for this step.

```<lang>
test "happy path":
  systemUnderTest <- new System(configuration)

  result <- systemUnderTest.doAction(parameter)

  assert result hasSomeProperty()
```

- Edge case 1
- Edge case 2

**Implementation Outline**

Describe the overall algorithm or code to implement this step.

```<lang>
struct SystemUnderTest:
  method doAction with parameter:
    for property in parameter.details
      aggregate property
    return aggregate 
```

## Step 2: <Name>

...
```

## Output Artifacts

Save `plan.md` to the session folder (`.ailly/developer/YYYY-MM-DD-A-<topic>/plan.md`) with `*Draft YYYY-MM-DD*` at the top.

## Stop Condition

After saving, tell the user:

> "Plan saved to `.ailly/developer/YYYY-MM-DD-A-<topic>/plan.md`. Review it and make any adjustments. When you're satisfied, remove the `*Draft YYYY-MM-DD*` marker. Start a new session and run `developer:ailly` (or `developer:red-green-refactor`) to begin implementation."

Do not implement any step. Do not run the feature test. Do not invoke `developer:red-green-refactor`.
