---
name: using-developer
description: Bootstrap skill to describe developer tasks. Directs which developer skill to invoke for design, feature testing, planning, implementation, or project setup.
---

# Using Developer Skills

## Five-Phase Lifecycle

Developer work runs through five phases: Research, Design, Plan, Build, Cleanup. Each of the first three is separated from the next by a human-review draft gate, and red-green-refactor is the Build loop. Invoke the skill for the phase you are in.

```dot
digraph phases {
    start [shape=doublecircle label="New topic"];
    research [shape=box label="Research:\ndeveloper:research"];
    rg [shape=diamond label="Research cleared"];
    design [shape=box label="Design (+ feature test):\ndeveloper:design"];
    dg [shape=diamond label="Design cleared"];
    plan [shape=box label="Plan:\ndeveloper:plan"];
    pg [shape=diamond label="Plan cleared"];
    build [shape=box label="Build:\ndeveloper:red-green-refactor"];
    cleanup [shape=box label="Cleanup:\ndeveloper:cleanup"];
    done [shape=doublecircle label="Approved + squash-merged"];

    start -> research;
    research -> rg;
    rg -> design [label="yes"];
    rg -> research [label="revise"];
    design -> dg;
    dg -> plan [label="yes"];
    dg -> design [label="revise"];
    plan -> pg;
    pg -> build [label="yes"];
    pg -> plan [label="revise"];
    build -> cleanup [label="feature test passes"];
    cleanup -> done [label="human approval"];
}
```

## Skill Routing Table

| Situation | Invoke |
|---|---|
| Starting a session for a new or in-progress feature | `developer:ailly` |
| Gathering and refining context for a vague new topic, with nothing written yet | `developer:research` |
| Exploring a new idea, clarifying requirements, and producing a formal design doc plus its one feature test | `developer:design` |
| Breaking a failing feature test into implementation steps | `developer:plan` |
| Implementing a plan step with TDD | `developer:red-green-refactor` |
| Debugging a compiler error or test failure during TDD | `developer:thinking` |
| Cleaning up green code mid-build, without changing behavior | `developer:refactor` |
| Finishing the topic: final review, extract deferred tasks, prepare the squash-merge | `developer:cleanup` |
| Setting up a new project or language environment | `developer:initialize` |

## Draft Gates

The research, design, and plan phases each produce a `*Draft YYYY-MM-DD*` artifact. A human must review and clear the draft marker before the next phase begins. `developer:ailly` enforces this and will not proceed past a draft gate in the same session. Cleanup adds a final human-approval gate before the squash-merge.

| Gate | Location | Clears to enter |
|---|---|---|
| Research notes | `docs/developer/YYYY-MM-DD-A-<topic>/research.md` | Design phase |
| Design doc (with feature test) | `docs/developer/YYYY-MM-DD-A-<topic>/design.md` | Plan phase |
| Plan | `docs/developer/YYYY-MM-DD-A-<topic>/plan.md` | Build (red/green/refactor) |
| Cleanup approval (human sign-off, not a draft file) | — | Squash-merge or PR |