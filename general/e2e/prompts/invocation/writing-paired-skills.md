Below is a single SKILL.md that has grown two cadences.
The front half explains how to configure a project's pre-commit hook framework (done once when the repository is set up).
The back half explains what to do every time a developer adds a new check (per change).

Split it into a paired pair — one wiring skill and one practice skill.
Produce both SKILL.md files in full, in order.
Give them distinct names.

Emit both files inline in your reply as fenced Markdown blocks.
This environment has no file system and no tools — do not call tools or write to disk; write the full content directly in your response.

```markdown
---
name: pre-commit-checks
description: Use when working with the project's pre-commit hook setup and when adding new checks to it.
---

# Pre-Commit Checks

## Overview
This project gates commits behind a pre-commit hook framework. The hook
layout is established once when the repository is first configured, and
individual checks are added to it as the codebase grows.

## Setting Up the Hook Framework
Install the pre-commit runner and create the config file at the repo root.
Choose the runner (pre-commit, husky, lefthook), pin its version in the
project manifest, and register the git hook so it fires on every commit.
Decide which stages each check runs at (commit, push, manual) and set the
default language versions the hooks resolve against. This establishes the
file that every check is later registered in.

## Adding a New Check
When you want a new check, add an entry to the config: give it an id, point
it at the script or linter, set the files glob it matches, and choose its
stage. Run it once across the whole repo to surface the existing baseline of
violations, fix or grandfather them, then commit the new entry. Keep each
check fast — a slow check trains developers to pass `--no-verify`.

## Tips
Keep the config readable. Order checks cheap-to-expensive so a fast failure
short-circuits the slow ones.
```
