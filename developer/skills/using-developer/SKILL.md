---
name: using-developer
description: Bootstrap skill to describe developer tasks. Directs which developer skill to invoke for design, feature testing, planning, implementation, or project setup.
---

# Using Developer Skills

## Three-Loop Architecture

Developer work is organized into three nested loops. Each loop has its own skill. Invoke the skill for the loop you are currently in.

```dot
digraph loops {
    start [shape=doublecircle label="New feature idea"];
    outer [shape=box label="Outer loop:\ndesign"];
    design_ok [shape=diamond label="Design approved"];
    middle [shape=box label="Middle loop:\nfeature test + plan"];
    plan_ok [shape=diamond label="Plan approved"];
    inner [shape=box label="Inner loop:\nred-green-refactor"];
    done [shape=doublecircle label="Feature test passes"];

    start -> outer;
    outer -> design_ok;
    design_ok -> middle [label="yes"];
    design_ok -> outer [label="revise"];
    middle -> plan_ok;
    plan_ok -> inner [label="yes"];
    plan_ok -> middle [label="revise"];
    inner -> done;
}
```

## Skill Routing Table

| Situation | Invoke |
|---|---|
| Starting a session for a new or in-progress feature | `developer:ailly` |
| Exploring a new idea, clarifying requirements, producing a design doc | `developer:brainstorming` |
| Formatting or structuring a design doc | `developer:design-doc` |
| Writing the feature test (design approved, no test yet) | `developer:feature-test` |
| Breaking a failing feature test into implementation steps | `developer:planning` |
| Implementing a plan step with TDD | `developer:red-green-refactor` |
| Stuck on a compiler error or test failure during TDD | `developer:thinking` |
| Tests are green; cleaning up code before finishing | `developer:refactoring` |
| Setting up a new project or language environment | `developer:initialize` |
| Converting a spec into a general implementation plan | `developer:writing-plans` |

## Draft Gates

The outer and middle loops produce `*Draft YYYY-MM-DD*` artifacts. A human must review and clear the draft marker before the next loop begins. `developer:run` enforces this — it will not proceed past a draft gate in the same session.

| Artifact | Location | Clears to enter |
|---|---|---|
| Design doc | `docs/developer/YYYY-MM-DD-A-<topic>/design.md` | Middle loop |
| Feature test | `docs/developer/YYYY-MM-DD-A-<topic>/feature-test.md` | Planning |
| Plan | `docs/developer/YYYY-MM-DD-A-<topic>/plan.md` | Inner loop |