# AGENTS.md

Keep main clean. Always use worktrees for any work. Keep worktrees in `.worktrees/`. Do not use ClaudeCode's `EnterWorktree` until [anthropics/claude-code#48967](https://github.com/anthropics/claude-code/issues/48967) is resolved.

## Releases

Releases stay in the `2026.09.x` line, at `2026.09.3` or later. `2026.09.2` and `2026.10.0`+ belong to davidsouther/ailly. `.github/scripts/check_version_line.py` enforces this in CI.

@DEVELOPMENT.md
