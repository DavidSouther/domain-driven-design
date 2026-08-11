# Pi Tool Mapping

[Pi](https://github.com/badlogic/pi-mono) adapter for the harness contract in `developer:ailly`. When a skill reference names a tool that pi calls something else, use this table:

| Skill references | Pi equivalent |
|-----------------|----------------------|
| `Read` (file reading) | `read` |
| `Write` (file creation) | `write` |
| `Edit` (file editing) | `edit` |
| `Bash` (run commands) | `bash` |
| `Skill` tool (invoke a skill) | Skills load natively — pi surfaces the matching skill from its always-on description list, or invoke it explicitly with `/skill:<name>` |
| `TodoWrite` (task tracking) | `todo` tool (registered by `.pi/extensions/todo.ts`, bundled in this repo) |
| `Task` tool (dispatch subagent) | `ailly_subagent` tool (see [Subagent dispatch](#subagent-dispatch)) |
| Multiple `Task` calls (parallel) | Multiple `ailly_subagent` calls in the same assistant turn — pi executes sibling tool calls from one turn concurrently |
| `WebSearch` / `WebFetch` | No built-in equivalent. Use `bash` with `curl`/an installed search CLI, or a web-search/web-fetch pi extension if one is installed for the project |

## Packaging Adapter

This repository ships its own pi package resources directly: `developer/skills`, `general/skills`, `domain/skills`, `patterns/skills`, and `research/skills` are referenced from the root `package.json`'s `pi.skills` array (and, for local development inside this checkout, from `.pi/settings.json`). `prompts/` holds the slash-command surface (`/ailly` and its phase aliases), and `.pi/extensions/` holds the two custom tools this adapter depends on. None of this duplicates `.claude-plugin/` or `.codex-plugin/`; it is a third, independent packaging adapter alongside them, not a replacement.

## Subagent Dispatch

Pi has no built-in `Task` tool, so this repository registers one: `ailly_subagent`, defined in `.pi/extensions/ailly-subagent/index.ts`. It spawns an isolated `pi` subprocess per dispatch — a real separate context window, not a same-session role-play.

Two properties make it match Ailly's phase-isolation contract exactly, not just approximate it:

1. **One reference per dispatch.** The tool's `reference` parameter is a closed enum of Ailly's five phases (`research`, `design`, `plan`, `red-green-refactor` — also accepted as `build` — `cleanup`) plus its progressive abilities (`thinking`, `refactor`, `initialize`, `intent-review`). The tool reads exactly that one `references/<phase or ability>.md` file, writes it into the child process's system prompt, and instructs the child not to read any other Ailly reference. The parent (pi) session never reads the other four phase files either — it only ever calls this tool with the one it needs.
2. **Install-location independence.** The reference paths are resolved relative to the extension module's own file location (`import.meta.url`), not the caller's working directory and not `.pi/agents/` or `~/.pi/agent/agents/` discovery. This means the mapping still holds after this package is installed elsewhere (`pi install git:davidsouther/domain-driven-design`, a local path, or a project depending on it) — not only while developing this repo's own checkout. Ailly's phase-isolation contract has to survive packaging, so the mechanism that implements it must not depend on `.pi/agents/` conventions that only resolve inside the current project's own directory tree.

Use it like this from the coordinator's Phase Isolation step:

```
ailly_subagent({
  reference: "plan",
  task: "Session folder: .ailly/developer/2026-07-29-A-csv-export. <any additional context the phase needs>",
  model: "<the model general/skills/dispatching-agents/model-selection.md recommends>"
})
```

Per `general/skills/dispatching-agents/model-selection.md`'s mandate-with-announce rule: `model` is a confirmed model-selection mechanism for this tool (it is passed straight through to the child `pi` process's `--model` flag) — set it directly on every dispatch this skill package performs, and announce the model chosen to the developer either way.

For dispatch outside Ailly's five closed references — e.g. `general:dispatching-agents`' independent research/investigation tasks — call `ailly_subagent` is not applicable (its `reference` enum is deliberately closed to Ailly's own contract). Run those tasks inline within the current pi session instead, or extend `.pi/extensions/ailly-subagent/index.ts` locally with an open-ended `systemPrompt` mode if a project needs general-purpose subagent dispatch beyond Ailly's phases.

## Model Mandate

Pi's model selection is a CLI flag (`--model <pattern>`), not a per-tool-call schema field on a built-in dispatch tool — but because `ailly_subagent` is this repository's own extension, its `model` parameter is wired straight to that flag on the spawned child process. That makes pi one of the harnesses with a *confirmed* model-selection mechanism, not a degraded announce-only one: set `model` on every `ailly_subagent` call per the mandate-with-announce rule, and announce the choice either way.

## Skill Loading

Pi loads skills natively per the [Agent Skills specification](https://agentskills.io/specification) — the same `SKILL.md` format this repository already uses for Claude Code and Codex. No adapter shim is needed for skill content itself, only for the tool names a `SKILL.md` body references (this table) and for making sure pi can find the skills at all (see Packaging Adapter above and the root `README.md`'s pi setup section).
