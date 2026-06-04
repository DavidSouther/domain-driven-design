---
name: ailly
description: Use when starting or resuming software development tasks.
---

# developer:ailly

## Overview

Session coordinator for a development loop. Creates and manages the session folder, passes it to each skill, enforces draft gates, and determines where to resume when re-entering an existing session.

**Announce at start:** "Using developer:ailly to coordinate this session."

## Session Folder

If it does not exist, create `docs/developer/YYYY-MM-DD-A-<topic>` where `A` is `A`, `B`, `C`, etc to manage multiple features started in the same day. If not already on a branch of the same name, use `developer:git-workflow` to suggest moving to that branch.

If the folder already exists for the current topic, determine resume point:

| Files present | Draft marker cleared? | Resume at |
|---|---|---|
| No files | — | Outer loop (design-doc) |
| `design.md` | No | Wait — ask user to clear the draft |
| `design.md` | Yes | Middle loop (feature-test) |
| `feature-test.md` | No | Wait — ask user to clear the draft |
| `feature-test.md` | Yes | Middle loop (planning) |
| `plan.md` | No | Wait — ask user to clear the draft |
| `plan.md` | Yes | Inner loop (red-green-refactor) |

A file has its draft cleared when it no longer contains the `*Draft` marker.

## Loop Structure

```dot
digraph run {
    start [shape=doublecircle label="Session start"];
    resume [shape=box label="Determine resume point"];
    design_doc [shape=box label="Outer loop:\ndeveloper:design-doc"];
    gate_design [shape=diamond label="Draft gate:\ndesign"];
    feature_test [shape=box label="Middle loop:\ndeveloper:feature-test"];
    gate_feature [shape=diamond label="Draft gate:\nfeature-test"];
    planning [shape=box label="Middle loop:\ndeveloper:planning"];
    gate_plan [shape=diamond label="Draft gate:\nplan"];
    rgr [shape=box label="Inner loop:\ndeveloper:red-green-refactor"];
    stop [shape=doublecircle label="Stop session"];

    start -> resume;
    resume -> design_doc;
    resume -> feature_test;
    resume -> planning;
    resume -> rgr;

    design_doc -> gate_design;
    gate_design -> stop [label="not cleared"];
    gate_design -> feature_test [label="cleared"];

    feature_test -> gate_feature;
    gate_feature -> stop [label="not cleared"];
    gate_feature -> planning [label="cleared"];

    planning -> gate_plan;
    gate_plan -> stop [label="not cleared"];
    gate_plan -> rgr [label="cleared"];

    rgr -> stop [label="feature test passes"];
}
```

## Draft Gate Enforcement

After any outer or middle loop skill (design-doc, feature-test, planning) produces output, stop the session and tell the user:

> "This step is complete. Review `<path>`, make any changes, then remove the `*Draft YYYY-MM-DD*` marker from the top of the file. Start a new session and run `developer:ailly` to continue."

**Do not proceed past a draft gate in the same session under any circumstances.** If the user asks to continue anyway, decline:

> "I can't continue past the draft gate in this session. The draft gate exists so you have a chance to review and refine before the next step builds on it."

## Skill Invocations

Pass the session folder path to each skill. The session folder is the single source of truth for all session artifacts.

- Outer loop: invoke `developer:brainstorming` or `developer:design-doc`
- Middle loop entry: invoke `developer:feature-test`
- Middle loop planning: invoke `developer:planning`
- Inner loop: invoke `developer:red-green-refactor`

## Topic Slug

If the user's prompt doesn't make the topic slug obvious, ask for one before creating the session folder:

> "What's a short slug for this session? (e.g., `user-auth`, `csv-export`)"

Use it to name the session folder: `docs/developer/YYYY-MM-DD-<topic>/`.

## Session Artifacts

All artifacts for a session live under `docs/developer/YYYY-MM-DD-A-<topic>/`.

- `design.md` is the overal design doc for a topic.
- `feature-test.md` is a specific plan for the feature test for this topic.
- `maps/<path>.md` contains the maps found during any forward/backward planning. 
- `thinking/` is a scratch pad area for the `thinking` skill to share its findings with the calling agent.

## Next Task

When finishing a session, append the next step to `docs/developer/TASKS.md`. When calling run, read `TASKS.md` first, then compare the user's input to the list of next steps. If the next step is obvious from context, run that. If there is no next step, start from the top. If the next step is ambiguous, ask whether they want to pick from a list or start a new developer task. When you start a task, remove it from `TASKS.md`. Ignore tasks in comments, either # lines or HTML section comments. When substantial context is needed for a task, create a `TASK-NOTES-<task>.md` file with the details, and include just a short overview to that in the TASKS file. Review NOTES when the task is selected.

When a topic is finished, use `developer:cleanup` to leave things tidy.

## Attribution

When creating git commit messages, attribute yourself. Include `Co-Authored-By: "Ailly <developer@ailly.dev>"`.
