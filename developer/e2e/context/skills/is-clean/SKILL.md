---
name: is-clean
description: Use when validating that a project is in a clean state for development.
---

Prepare a report to ensure the project is in a clean state for development work. All report entries must run an external command. If the command failed, the failure should be included in the report. Symbols: ✅ Success/⚠️ Warning/⛔️ Blocking/❗️Tool Error.

```
# Source Control
- Worktree: <"Unused" or worktree path>
- Branch: <branch name, warning if on main or master>
- Tracked Issue: <tracked issue if reported by gh or issue tracker, or "None">
- Working Directory: <"Clean" or `git status` counts (<m> modified, <a> added, <d> deleted, <u> untracked), skipping any with 0>

# Continuous Integration
- Formatting: ✅/⚠️/⛔️/❗️
- Linting: ✅/⚠️/⛔️/❗
- Type-Checking: ✅/⚠️/⛔️/❗
- Building: ✅/⚠️/⛔️/❗
- Testing: ✅/⚠️/⛔️/❗
- Diagnostics: ✅/⚠️/⛔️/❗
```

