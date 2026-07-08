# Copilot command-line tool mapping

Maps Copilot command-line tools to the harness contract in `developer:ailly`.
When a skill reference names a tool that Copilot calls by a different name, use this table:

| Skill references | Copilot command-line tool equivalent |
|-----------------|----------------------|
| `Read` (file reading) | `view` |
| `Write` (file creation) | `create` |
| `Edit` (file editing) | `edit` |
| `Bash` (run commands) | `bash` |
| `Grep` (search file content) | `grep` |
| `Glob` (search files by name) | `glob` |
| `Skill` tool (invoke a skill) | `skill` |
| `WebFetch` | `web_fetch` |
| `Task` tool (dispatch subagent) | `task` (see [Agent types](#agent-types)) |
| Multiple `Task` calls (parallel) | Multiple `task` calls |
| Task status/output | `read_agent`, `list_agents` |
| `TodoWrite` (task tracking) | `sql` with built-in `todos` table |
| `WebSearch` | No equivalent; use `web_fetch` with a search engine URL |
| `EnterPlanMode` / `ExitPlanMode` | No equivalent; stay in the main session |

## Model mandate

Copilot command-line tool's `task` dispatch call lacks a confirmed model-selection field today.
This doesn't create a separate rule.
Instead, it triggers the mandate-with-announce rule in `general/skills/dispatching-agents/model-selection.md`.
This rule degrades automatically when no confirmed mechanism exists.
When degraded, the mandate half becomes a no-op and only the announce half applies.
Name the recommended model verbatim and invite a switch through Copilot's own equivalent of `/model`.
Never gate; continue on the current model either way.

## Async shell sessions

Copilot command-line tool supports persistent async shell sessions, which have no direct canonical Ailly equivalent:

| Tool | Purpose |
|------|---------|
| `bash` with `async: true` | Start a long-running command in the background |
| `write_bash` | Send input to a running async session |
| `read_bash` | Read output from an async session |
| `stop_bash` | Terminate an async session |
| `list_bash` | List all active shell sessions |

## Additional copilot command-line tools

| Tool | Purpose |
|------|---------|
| `store_memory` | Persist facts about the codebase for future sessions |
| `report_intent` | Update the UI status line with current intent |
| `sql` | Query the session's SQLite database (todos, metadata) |
| `fetch_copilot_cli_documentation` | Look up Copilot command-line tool documentation |
| GitHub MCP tools (`github-mcp-server-*`) | Native GitHub API access (issues, PRs, code search) |
