# Cleanup phase

> Phase reference loaded by the coordinator (`developer:ailly`) when entered as `/ailly cleanup ...`.
> The coordinator hands this to an isolated phase runner that reads only this one reference through the active harness's isolation path.
> There is no standalone `developer:cleanup` skill; you enter the phase by argument.

## Clean up

Perform final refactoring and review passes for the topic.
Check for lint findings, and include them in the refactor passes.
Run automated formatters and lint fixers.

Extract deferred decisions from design.md via the program-management using reference (`references/abilities/program-management/using.md`).
When you configure a tracker, it writes them as labeled tasks under the right parent.
Otherwise, write them to `TASKS.md`, including any necessary TASK-NOTES.

For a **Project**-shape topic with a doc-system target configured, publish the accepted notes as long-lived docs.
Use the program-management using reference (`references/abilities/program-management/using.md`).
Mark them `completed:` before removing the local folder.
A feature or bug leaves only its task record behind.

Remove the `.ailly/developer/YYYY-MM-DD-A-<topic>` folder.

Either open a PR, or prepare a squash merge, depending on the project configurations.
