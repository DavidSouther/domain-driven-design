# AGENTS.md

Keep main clean. Always use worktrees for any work. Keep worktrees in `.worktrees/`. Do not use ClaudeCode's `EnterWorktree` until [anthropics/claude-code#48967](https://github.com/anthropics/claude-code/issues/48967) is resolved.

## Releases

ddd releases stay inside the `2026.09.x` line, at `2026.09.3` or later. `2026.09.2` and anything at or above `2026.10.0` belong to davidsouther/ailly, which shares the `ailly` marketplace name and version sequence. Run `python3 .github/scripts/check_version_line.py` before any version change; it must pass.

@DEVELOPMENT.md
