---
description: Run developer:ailly's build (red-green-refactor) phase
argument-hint: "<session folder>"
---
Read `developer/skills/ailly/SKILL.md`, then run its **build** phase (`references/phases/red-green-refactor.md`) through the pi harness (`references/agents/pi.md`), dispatching it via the `ailly_subagent` tool with `reference: "red-green-refactor"`, once per plan step, until the feature test is green.

Session: $ARGUMENTS
