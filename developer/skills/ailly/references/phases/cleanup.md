---
name: cleanup
description: Used when finished with an Ailly development topic to tidy up the workspace.
---

# Clean Up

Perform final refactoring and review passes for the topic. Check for lint findings, and include them in the refactor passes. Run automated formatters and lint fixers.

Extract deferred decisions from design.md via `developer:using-program-management` when a tracker is configured (it writes them as labeled tasks under the right parent); otherwise write them to `TASKS.md`, including any necessary TASK-NOTES.

For a **Project**-shape topic with a doc-system target configured, publish the accepted notes as long-lived docs via `developer:using-program-management` and mark them `completed:` before removing the local folder. A feature or bug leaves only its task record behind.

Remove the `.ailly/developer/YYYY-MM-DD-A-<topic>` folder.

Either open a PR, or prepare a squash merge, depending on the project configurations.