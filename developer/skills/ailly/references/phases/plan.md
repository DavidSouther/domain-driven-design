# Plan phase

> Phase reference loaded by the coordinator (`developer:ailly`) when entered as `/ailly plan ...`.
> The coordinator hands this to an isolated phase runner that reads only this one reference through the active harness's isolation path.
> There is no standalone `developer:plan` skill; the coordinator enters the phase by argument.

## Overview

Middle-loop planning skill.
Given a cleared design and its failing feature test, defines the API surface area and breaks the path to making that test pass into 3–7 incremental steps.
Each step must leave the codebase in a runnable state and advance the feature test measurably.

**Announce at start:** "Using the developer:ailly plan phase to create the implementation plan for [summary of feature].
Per `general/skills/dispatching-agents/model-selection.md`, matched to the active provider with its effort qualifier verbatim.
Set the model directly when the harness's dispatch call allows it; announce the model chosen either way.
I'll continue on the current model either way."

**Trigger:** the coordinator has cleared the design draft marker.
The design records the project feature test, which is currently failing.

**Hard gate:** do not implement any step.
Do not write unit tests or implementation code.
Step 0 defines API signatures as stubs; later steps describe what to build and may sketch critical interfaces.
All code in steps 1+ is orientation for the builder; the builder re-derives it during build.
Decline any request to implement in this session.

**Distinction from `developer:writing-plans`:** this focuses on making piecemeal progress toward one specific failing test.
It is not a general spec-to-plan conversion tool.

## Behavior

1. Read the cleared design and its recorded feature test (and user story) from the session folder.
   If `design.md` (or `research.md`) names skills to load under a **Libraries & Skills** directive, load them via the active harness's skill-loading mechanism before planning, and carry that directive into `plan.md` so every red-green-refactor step loads the framework's skill while implementing.
2. Consider the API surface area changes needed.
   See step 0 below.
3. Break the path to a passing feature test into several (no more than 7) incremental steps.
  - If it seems a plan would require more than a few steps, encourage the user to go back to the design and simplify the size of the step.
  - If it seems a plan would require more than 7 steps, insist that the user go back to the design.
3a.
If the path from the failing test to a passing test isn't obvious, apply the forward-backward method.
Work backward from the passing test state, asking what must be true just before the failing assertion passes.
Work forward from the current code, identifying what you can derive or add without breaking anything, until the two sides connect into a complete sequence of steps.
Write each candidate step to a map file as you generate it.
Do not hold steps only in context.
See `developer/skills/ailly/references/abilities/forward-backward.md`.
4. For each step: name it, describe what it builds, and identify which assertion in the feature test it enables.
   Steps may include type/API sketches and notes on critical areas as orientation for the builder, but no implementation code.
   Each step is a description of what to build, not how to build it.
5. Save the plan as a draft.
   Perform a general review of the plan, including the intent-review ability (a recommended, dismissible default) per `references/abilities/intent-review.md`.
   Then stop.

## Step 0: API surface area

Before implementation steps, define the type and API surface area the feature test requires.
Step 0 establishes all new types and public function signatures as stubs:

- Introduce new entities, value objects, or services needed
- Run the dedicated "look for applicable patterns" beat.
  See `.ailly/prompts/plan-use-patterns.md`.
  Consult `patterns:using-patterns` and name the patterns that apply before fixing the surface.
- Consider these patterns for guidance: domain-objects (`patterns:using-patterns`, `references/patterns/domain-objects.md`), newtype (`references/patterns/newtype.md`), and type-states (`references/patterns/type-states.md`).
- Show type signatures and function signatures (not implementations) for new objects
- Keep this focused on the domain model, not persistence or UI

Step 0 contains code (type stubs and signatures), but no function bodies.
The feature test from the design tests everything in step 0.

## Step criteria

Each step must:
- Leave the codebase in a runnable state.
  Checks and tests pass, even if the feature test still fails.
- Make measurable progress toward the feature test passing.
- Include a suggested unit test for the happy path and a list of expected edge cases to test.
- Outline the main implementation (no error handling, bounds checking, etc.) to clarify where the work should go.

3 steps minimum (too few = steps are too large). 7 steps maximum (too many = over-engineering).
Encourage the user to go back to the design in those cases.

## Plan format

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

Describe what this step builds.
The feature test still fails but `<specific assertion>` no longer throws.

[Optional API sketch or note on a critical interface–re-derive during build.]

**Tests**

Describe the main test for this step.

```<lang>
test "happy path":
  systemUnderTest <- new System(configuration)

  result <- systemUnderTest.doAction(parameter)

  assert result hasSomeProperty()
```

- Edge scenario 1
- Edge scenario 2

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

[Repeat for each step.]
```

## Output Artifacts

Save `plan.md` to the session folder (`.ailly/developer/YYYY-MM-DD-A-<topic>/plan.md`) with `*Draft YYYY-MM-DD*` at the top.

## Stop Condition

After saving, tell the user:

> "Plan saved to `.ailly/developer/YYYY-MM-DD-A-<topic>/plan.md`. Review it and make any adjustments. When you're satisfied, remove the `*Draft YYYY-MM-DD*` marker. Start a new session and run `developer:ailly` (resumes at the Build phase) to begin implementation."

Do not implement any step. Do not run the feature test. Do not enter the Build (red-green-refactor) phase.
