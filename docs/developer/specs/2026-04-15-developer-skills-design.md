# Developer Skills Plugin Design

## Problem Statement

The developer plugin needs a complete set of skills to guide an LLM agent through the full software development lifecycle: design, feature testing, planning, and test-driven implementation. Several skills exist as stubs or are absent entirely. This document specifies the content and behavior of each missing or incomplete skill.

## Prior Art

- `domain:` plugin — bootstrap + routing table pattern (`using-domain` → other skills)
- `superpowers:brainstorming` — clarifying-question-first design flow, draft gate, visual companion
- `superpowers:writing-plans` — spec-to-plan conversion, file map, task checklist format
- `developer:design-doc` — existing outer-loop design skill with draft gate and session stop
- `developer:code-review` — existing inner-loop review skill (unchanged by this work)
- Arrow of Maturity reference file pattern — shared prose in `references/` cited by multiple skills

## Metrics

- Each skill can be invoked in isolation and produces its stated output without requiring information not available to the agent at invocation time.
- The draft gate is enforced: big-step skills stop at session end and decline to continue into later phases.
- The thinking/red-green-refactor loop has an explicit abort condition that prevents infinite loops.
- The initialize skill produces a runnable project for each supported language using only the reference file for that language.

## Specification

### Architecture

Eleven skills organized across three loop levels:

```
Outer loop (design phase)
  developer:using-developer     bootstrap — routes to all other skills [existing, unchanged]
  developer:brainstorming       explore intent + produce design doc [existing, unchanged]
  developer:design-doc          structured design doc format [existing, unchanged]
  developer:run                 NEW — session init, loop coordination, draft gate enforcement

Middle loop (feature phase)
  developer:feature-test        NEW — write the integration/e2e test
  developer:planning            NEW — break passing the feature test into incremental steps

Inner loop (implementation phase)
  developer:red-green-refactor  STUB → full — type-first TDD cycle with thinking/abort
  developer:thinking            STUB → full — subagent for stuck moments
  developer:refactoring         STUB → full — post-green cleanup

Cross-cutting
  developer:initialize          NEW — project setup with language reference files and steps to verify the project is set up correctly
  developer:code-review         existing, unchanged
```

Skill files live at `developer/skills/<name>/SKILL.md`. Reference files live at `developer/skills/<name>/references/<lang>.md`.

---

### `developer:run`

**Role:** Session coordinator. Invoked at the start of any feature development session.

**Behavior:**
1. Prompts for a topic slug if not provided or obviously derived from the prompt.
2. Creates `docs/developer/YYYY-MM-DD-A-<topic>/` as the session folder.
3. Passes the session folder path to all subsequent skills in this session.
4. Walks the outer → middle → inner loops in sequence, invoking the appropriate skill at each stage.
5. Enforces the draft gate: after each big-step skill completes, stops and tells the user to review the draft, clear the `*Draft*` marker, and start a new session to continue.
6. On session start, checks if a session folder already exists for today's topic; if so, determines where in the loop to resume based on which draft files are present and whether their `*Draft*` markers have been cleared.

**Draft gate enforcement:** Big-step skills (design-doc, feature-test, planning) produce `*Draft*` outputs. `developer:run` must decline any request to proceed past a draft gate in the same session. It tells the user:
> "This step is complete. Review `<path>`, make any changes, then remove the `*Draft*` marker. Start a new session and run `developer:run` to continue."

---

### `developer:feature-test`

**Role:** Writes a single executable test that encodes a user story. This is the middle-loop entry point.

**Trigger:** Design doc draft has been cleared by a human.

**Behavior:**
1. Reads the cleared design doc to understand the feature.
2. Writes a user story in plain language (Given/When/Then or narrative form).
3. Writes an executable feature test — a test that runs end-to-end through the user story and asserts it completes as expected. Language-agnostic process; actual test code follows the language established by `developer:initialize`.
4. Saves both to `docs/developer/YYYY-MM-DD-A-<topic>/feature-test.md` (user story) and the appropriate test file in the project.
5. Marks the feature test file `*Draft YYYY-MM-DD*`.
6. Stops. Declines to implement any code to make the test pass.

**Scope note:** For complex UI features, Page Object abstractions are appropriate. For simple features, the test should be direct and flat.

---

### `developer:planning`

**Role:** Middle-loop planning. Triggered when the feature test is failing. Breaks passing it into incremental plan steps.

**Trigger:** Feature test draft has been cleared by a human; the test is currently failing.

**Behavior:**
1. Reads the feature test to understand what passing looks like.
2. Proactively considers a step 0 for domain object design — introduces any new domain objects needed, leaning on `patterns:` skills (especially `patterns:entities-value-objects-services`, `patterns:newtype`, `patterns:type-states`).
3. Breaks the path to a passing feature test into 3–7 incremental steps. Each step must leave the codebase in a runnable state and advance the feature test measurably closer to passing.
4. For each step: names it, describes what it implements, and identifies which part of the feature test it enables.
5. Saves the plan to `docs/developer/YYYY-MM-DD-A-<topic>/plan.md` marked `*Draft YYYY-MM-DD*`.
6. Stops. Declines to implement.

**Distinction from `developer:writing-plans`:** `developer:planning` is a middle-loop skill focused on making piecemeal progress toward a specific failing test. It is not a general spec-to-plan conversion tool.

---

### `developer:initialize`

**Role:** Prepares a project folder for development. Language-agnostic orchestration with language-specific details in reference files.

**Trigger:** Starting a new project or setting up a new language environment.

**Behavior:**
1. Identifies the target language/toolchain (Rust, Python, TypeScript, or Mise monorepo).
2. Reads the appropriate reference file: `developer/skills/initialize/references/<lang>.md`.
3. Validates the project folder: checks for required config files, directory layout, and tooling.
4. If validation fails, applies the fixes described in the reference file (scaffolding, config generation, dependency installation).
5. Configures the four development hooks:
   - **Format:** run formatter on every edited file
   - **Check:** run static analysis before running tests
   - **Test:** run tests after every change
   - **Lint:** run linter after every task
6. Verifies the project builds/starts cleanly.

**Reference files:**
- `references/rust.md` — Cargo, Clippy, `tests/` for feature tests, `src/` for main crate
- `references/python.md` — uv, ruff (format + lint), pyright, PyPA layout, feature test module
- `references/typescript.md` — vite/vitest, biome, strict TS settings, browser/server/edge distinction
- `references/mise.md` — mise monorepo, `mise format/test/check/lint/run/serve` task wiring

---

### `developer:red-green-refactor`

**Role:** The innermost development loop. Type-first TDD.

**Behavior:**
1. **Type-first:** Write class/function/method signatures with stub bodies (`todo!()`, `...`, or default return). Run check. Fix type errors before writing any tests.
2. **Test:** Add one test using `patterns:arrange-act-assert`. Run check, then run tests.
3. **Implement:** Replace the stub body with real code. Run check, then run tests.
4. **Repeat** edit → check → test until all tests pass and the feature test is passing up to the point expected by the current plan step.
5. **Green:** Commit. Invoke `developer:refactoring`. Then invoke `developer:code-review`.

**Thinking trigger:** Invoke `developer:thinking` when:
- The same error (or substantially the same) appears after a change intended to fix it.
- An error appears that is unrelated to the code added or changed in this step.

**Loop abort:** If `developer:thinking` has already been invoked for the current error and the same or equivalent error reappears after following its plan, do not invoke `developer:thinking` again. Instead, stop immediately and report:
- The current error
- The path to the thinking doc (`docs/developer/YYYY-MM-DD-A-<topic>/thinking/<problem>.md`)
- A suggestion to review the current diff or restore the working directory and try again

---

### `developer:thinking`

**Role:** Fresh-context subagent for stuck moments. Always runs as a subagent.

**Trigger:** Invoked by `developer:red-green-refactor` when stuck.

**Behavior:**
1. Receives a summary of the current situation: the error, the code added in this step, and the plan step being implemented. No editorialization.
2. May use `research:` skills to investigate the problem.
3. Must not edit any files or run any code.
4. Produces `docs/developer/YYYY-MM-DD-A-<topic>/thinking/<problem>.md` containing:
   - Summary of the situation
   - Analysis of the root cause
   - Concrete next-steps plan (specific changes to try, in order)
5. Returns control to `developer:red-green-refactor` with a pointer to the thinking doc.

---

### `developer:refactoring`

**Role:** Post-green cleanup. Runs only when tests are green and the working directory is clean.

**Guard:** If working directory is not clean, abort immediately. Tell the user they may restart the refactoring step once the directory is clean.

**Behavior:**
1. Identifies code smells in files touched in this loop and their logical neighbors (by responsibility, not physical proximity).
2. Makes an in-memory plan of specific refactorings to apply (extract function, rename, replace conditional with guard clause, group related parameters).
3. Applies each refactoring one at a time. After each: run check, run tests.
4. **Abort on repeated errors:** If a refactoring causes an error and a fix attempt causes the same or a new error, abort. Tell the user to review the current diff or restore the working directory and try again.
5. Stops when the smell is gone — not when the code is maximally elegant.
6. May produce a `docs/developer/YYYY-MM-DD-A-<topic>/deferred-refactoring.md` noting smells left for a later session.

**Constraint:** Never refactor behavior and structure simultaneously. If a test is failing, fix the code first — then refactor.

## Summary

Eight skill files to create or complete:

| File | Status |
|------|--------|
| `developer/skills/run/SKILL.md` | New |
| `developer/skills/feature-test/SKILL.md` | New |
| `developer/skills/planning/SKILL.md` | New |
| `developer/skills/initialize/SKILL.md` | New |
| `developer/skills/initialize/references/rust.md` | New |
| `developer/skills/initialize/references/python.md` | New |
| `developer/skills/initialize/references/typescript.md` | New |
| `developer/skills/initialize/references/mise.md` | New |
| `developer/skills/red-green-refactor/SKILL.md` | Stub → full |
| `developer/skills/thinking/SKILL.md` | Stub → full |
| `developer/skills/refactoring/SKILL.md` | Stub → full |

Deferred: improvement of `developer:code-review` (already functional; out of scope for this design).
