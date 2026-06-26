# Gemini CLI Tool Mapping

Gemini CLI adapter for the harness contract in `developer:ailly`. When a skill reference names a tool that Gemini calls something else, use this table:

| Skill references | Gemini CLI equivalent |
|-----------------|----------------------|
| `Read` (file reading) | `read_file` |
| `Write` (file creation) | `write_file` |
| `Edit` (file editing) | `replace` |
| `Bash` (run commands) | `run_shell_command` |
| `Grep` (search file content) | `grep_search` |
| `Glob` (search files by name) | `glob` |
| `TodoWrite` (task tracking) | `write_todos` |
| `Skill` tool (invoke a skill) | `activate_skill` |
| `WebSearch` | `google_web_search` |
| `WebFetch` | `web_fetch` |
| `Task` tool (dispatch subagent) | Gemini subagent dispatch (available as of 2026-04-15) |

## Subagent support

When Ailly asks for a phase subagent, dispatch a Gemini subagent with explicit context discipline:

1. Read only the selected `references/phases/<phase>.md` file.
2. Execute that phase against the session folder path passed by the coordinator.
3. Return the phase result to the coordinator and close the subagent context before moving to another phase.

For skills that rely on reviewer or thinking subagents, use the same dispatch discipline: read only the requested reference, write the requested artifact, and return to the coordinator flow.

## Additional Gemini CLI tools

These tools are available in Gemini CLI but have no direct canonical Ailly equivalent:

| Tool | Purpose |
|------|---------|
| `list_directory` | List files and subdirectories |
| `save_memory` | Persist facts to GEMINI.md across sessions |
| `ask_user` | Request structured input from the user |
| `tracker_create_task` | Rich task management (create, update, list, visualize) |
| `enter_plan_mode` / `exit_plan_mode` | Switch to read-only research mode before making changes |
