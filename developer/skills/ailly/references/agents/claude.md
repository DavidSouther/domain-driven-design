# Claude Code Tool Mapping

Claude Code is the native adapter for Ailly's canonical tool vocabulary. When a skill reference names `Read`, `Edit`, `Bash`, `Task`, `Skill`, `TodoWrite`, `WebSearch`, or `WebFetch`, use the matching Claude Code tool directly.

## Packaging Adapter

The `.claude-plugin/` directories in this repository are Claude Code marketplace metadata. They package the same skill files that other agent ecosystems consume through their own skill-loading mechanisms; they are not a separate behavioral source of truth.

## Phase Isolation

Claude Code supports subagent dispatch through `Task`, so phase isolation uses one `Task` call per Ailly phase. Each phase task reads only its matching `references/phases/<phase>.md` file and receives the session folder path from the coordinator.
