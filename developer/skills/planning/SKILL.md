---
name: planning
description: Use when a feature test has been reviewed and cleared and is currently failing — breaks passing it into 3-7 incremental plan steps
---

# developer:planning

## Overview

Middle-loop planning skill. Given a failing feature test, breaks the path to making it pass into 3–7 incremental steps. Each step must leave the codebase in a runnable state and advance the feature test measurably.

**Announce at start:** "Using developer:planning to create the implementation plan for [summary of feature]."

**Trigger:** Feature test draft marker has been cleared by a human. The test is currently failing.

**Hard gate:** Do not implement any step. Do not write any code beyond type stubs shown in the plan. Decline any request to do so in this session.

**Distinction from `developer:writing-plans`:** This is focused on making piecemeal progress toward one specific failing test. It is not a general spec-to-plan conversion tool.

## Behavior

1. Read the feature test and user story from the session folder.
2. Consider whether domain objects are needed (step 0 — see below).
3. Break the path to a passing feature test into several (no more than 7) incremental steps.
  - If it seems a plan would require more than a few steps, encourage the user to go back to the design and simplify the size of the step.
  - If it seems a plan would require more than 7 steps, insist that the user go back to the design.
4. For each step: name it, describe what it implements, and identify which assertion in the feature test it enables.
5. Save the plan as a draft and stop.

## Step 0: Domain Object Design

Before implementation steps, consider whether the feature test introduces new domain objects. If it does, make step 0 a domain design step:

- Introduce new entities, value objects, or services needed
- Lean on `patterns:entities-value-objects-services`, `patterns:newtype`, `patterns:type-states` for guidance
- Show type signatures (not implementations) for the new objects
- Keep this step focused on the domain model, not persistence or UI

## Step Criteria

Each step must:
- Leave the codebase in a runnable state (check and tests pass, even if feature test still fails)
- Make measurable progress toward the feature test passing
- Be implementable in one `developer:red-green-refactor` session

3 steps minimum (too few = steps are too large). 7 steps maximum (too many = over-engineering). Encourage the user to go back to the design in those cases.

## Plan Format

```markdown
# Implementation Plan: <feature name>

*Draft YYYY-MM-DD*

**Feature test:** `<test-file-path>`
**User story:** Summarize in one sentence.

## Step 0: Domain model (if needed)

Introduce `<Type>` as a value object / entity / service.

Types:
- `UserId(uuid)` — newtype wrapping UUID, prevents mixing with other IDs
- `UserEmail(string)` — validated email address

## Step 1: <Name>

**Enables:** `<which assertion or part of the feature test>`

Implement `<what>`. The feature test will still fail but `<specific assertion>` will no longer throw.

## Step 2: <Name>

...
```

## Output Artifacts

Save `plan.md` to the session folder (`docs/developer/YYYY-MM-DD-<topic>/plan.md`) with `*Draft YYYY-MM-DD*` at the top.

## Stop Condition

After saving, tell the user:

> "Plan saved to `docs/developer/YYYY-MM-DD-<topic>/plan.md`. Review it and make any adjustments. When you're satisfied, remove the `*Draft YYYY-MM-DD*` marker. Start a new session and run `developer:run` (or `developer:red-green-refactor`) to begin implementation."

Do not implement any step. Do not run the feature test. Do not invoke `developer:red-green-refactor`.
