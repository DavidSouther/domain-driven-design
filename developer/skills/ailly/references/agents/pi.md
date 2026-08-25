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
| `Task` tool (dispatch subagent) | `ailly_subagent` for developer:ailly phases/abilities, `research_dispatch` for research:* skills, `review_run` for general:review's composed reviewers (see [Subagent dispatch](#subagent-dispatch)) |
| Multiple `Task` calls (parallel) | Pass multiple items to one call (`research_dispatch`'s `skills` array, `review_run`'s `specialists` array) or make multiple calls in the same assistant turn — pi executes sibling tool calls from one turn concurrently |
| `WebSearch` / `WebFetch` | No built-in equivalent. Use `bash` with `curl`/an installed search CLI, or a web-search/web-fetch pi extension if one is installed for the project |

## Packaging Adapter

This repository ships its own pi package resources directly: `developer/skills`, `general/skills`, `domain/skills`, `patterns/skills`, and `research/skills` are referenced from the root `package.json`'s `pi.skills` array (and, for local development inside this checkout, from `.pi/settings.json`). `prompts/` holds the slash-command surface (`/ailly` and its phase aliases), and `.pi/extensions/` holds the custom tools this adapter depends on. None of this duplicates `.claude-plugin/` or `.codex-plugin/`; it is a third, independent packaging adapter alongside them, not a replacement.

Sibling workflows outside the five-phase coordinator get the same dedicated-tool treatment for the same reason — pi has no `Task` tool, so their prose "dispatch a subagent" steps need a real mechanism too:

- `research:using-research` dispatches through `research_dispatch` (`.pi/extensions/research-subagent/`) — see that skill's own "Pi Workflow" section.
- `general:review` dispatches and converges through `review_run` (`.pi/extensions/review-subagent/`) — see that skill's own "Pi Workflow" section.
- `general:conversation`'s "investigate before you ask" step runs through `clarify` (`.pi/extensions/clarify/`) — see that skill's own "Pi Workflow" section and [Clarify](#clarify) below.
- Quick-loop Mode runs end to end through `ailly_quick_loop` (`.pi/extensions/ailly-quick-loop/`) — see the Quick-loop Mode section's own "Pi Workflow" note in this coordinator's `SKILL.md`.
- Long-loop Mode runs as a detached background process managed by `ailly_long_loop_start`/`_status`/`_stop` (`.pi/extensions/ailly-long-loop/`) — see `references/shapes/long-loop.md`'s own "Pi Workflow" section (8).

All six tools (`ailly_subagent`, `research_dispatch`, `review_run`, `clarify`, `ailly_quick_loop`, `ailly_long_loop_start`) share one spawning primitive, `.pi/extensions/lib/subprocess.ts`, so the isolation mechanics (temp-file system prompts, JSON-mode child parsing, abort handling) and the deterministic dated-notes-folder naming are implemented once, not six times. `ailly_quick_loop` and the long-loop driver reuse `ailly_subagent`'s and `review_run`'s own dispatch logic directly (`.pi/extensions/lib/ailly-phases.ts`, `.pi/extensions/lib/review.ts`) rather than re-implementing it, so all entry points — a single phase dispatch, a full quick loop, or an autonomous long loop — run the exact same phase-isolation and review contract.

`review_run`'s specialist reviewers resolve through a second shared module, `.pi/extensions/lib/skills.ts`: it looks up a specialist by pi's own skill `name`, searching the calling project's own `.pi/skills`/`.agents/skills` first, then this package's plugin skills, then user-global skills — the same precedence pi's own resource loader uses. This is why a project that installs this package can hand `review_run` a specialist it wrote itself, or one it got from an entirely different installed pi package, without editing this adapter or `general:review`.

## Subagent Dispatch

Pi has no built-in `Task` tool, so this repository registers one: `ailly_subagent`, defined in `.pi/extensions/ailly-subagent/index.ts`. It spawns an isolated `pi` subprocess per dispatch — a real separate context window, not a same-session role-play.

While the subprocess runs, its tool calls and assistant text stream back live through the tool's own progress channel (`.pi/extensions/lib/subprocess.ts`'s `onProgress`, fed by the child's `--mode json` event stream) instead of a static "Working..." spinner. `research_dispatch` and `review_run` multiplex several concurrent subprocesses' progress into one labeled view (`createProgressMultiplexer`) when dispatching more than one skill or reviewer at once. `ailly_quick_loop` forwards the same live view for whichever phase or review is currently running.

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

For dispatch outside Ailly's five closed references — e.g. `general:dispatching-agents`' independent research/investigation tasks — `ailly_subagent` is not applicable (its `reference` enum is deliberately closed to Ailly's own contract). Use `research_dispatch` for a specific research:* skill, `review_run` to compose reviewers, or `clarify` for a single ad hoc question that needs its own research-and-decide pass (see below).

## Clarify

`clarify` (`.pi/extensions/clarify/index.ts`) is the general-purpose counterpart to `ailly_subagent`: usable by any (sub)agent in this project — the top-level session, or any subagent dispatched by one of this package's own tools, since all of them are just `pi` processes with `clarify` available too — for one specific question that comes up mid-thinking rather than a named Ailly reference or research skill.

It dispatches a single isolated subagent with an open-ended system prompt, not a closed reference file: the subagent decides whether the question is local convention (check the repo directly), researchable (dispatch `research_dispatch` with whatever skill(s) fit), or a business/preference decision. Business questions are not assumed undiscoverable — they are frequently already made and recorded, so the subagent checks `research_dispatch`'s `internal` skill (Slack, Confluence, Linear, Notion, tickets, design docs) first; a prior decision found there, even a stale one, is a sourced answer, cited with its staleness risk noted. Only once that check comes up empty or contradictory (or there is no plausible internal source to check at all) does the question become NEEDS_HUMAN. It ends with exactly one contract line, `CLARIFY: ANSWERED` or `CLARIFY: NEEDS_HUMAN`, which `clarify` parses deterministically rather than trusting free-form text — a missing line is treated as unresolved, the same fail-safe direction as `research_dispatch`'s notes-file check. It also writes a note to `.ailly/clarify/YYYY-MM-DD-<letter>-<topic>.md` and verifies that file landed on disk.

```
clarify({
  question: "Should this field be camelCase or snake_case in the new endpoint?",
  context: "Adding a field to src/api/routes.ts; existing endpoints are mixed.",
  model: "<the model general/skills/dispatching-agents/model-selection.md recommends>"
})
```

On `NEEDS_HUMAN`, relay the returned question, findings, and recommended answer to the user per `general:conversation`'s Clarifying Questions guidance — present the recommendation as the suggestion to accept or correct, not a raw dump of the tool's output. `clarify` also fires a non-blocking `ctx.ui.notify` when running interactively, so the need for input is visible even before that turn's text renders.

## File Permissions Mode

`ailly-file-permissions` (`.pi/extensions/ailly-file-permissions/index.ts`) is not a tool the model calls; it registers a `tool_call` gate (the same pattern as `examples/extensions/protected-paths.ts` and `permission-gate.ts` in `@earendil-works/pi-coding-agent`) that blocks `read`/`grep`/`find`/`ls`/`write`/`edit`/destructive-`bash` calls whose target falls outside the current Ailly phase's allowed area, so a session cannot silently step outside the phase it is in. Every rule below is lifted from that phase's own reference doc's stated "Hard gate" or "Do not" clause, not invented for this extension.

The phase itself is not tracked by the extension — it is detected fresh on every gated call from the same on-disk signal `developer:ailly`'s own Resume table uses (`SKILL.md`'s "Session Folder" section: which of `research.md`/`design.md`/`plan.md` exist in the most recently touched `.ailly/developer/<session>/` folder, and whether each has cleared its `*Draft*` marker), so it stays correct across process restarts and isolated `ailly_subagent` dispatches without any extra state file.

- **Research phase**: `references/phases/research.md` ends with "Do not write a design or a feature test." — reads are unrestricted, writes/edits are confined to `.ailly/`.
- **Design phase**: reads are confined to `research/` and `.ailly/`. Writes are confined to `.ailly/` plus exactly one test-file path — `design.md`'s own "single exception to the no-code rule," the one feature test it records — enforced by refusing a second, different test-file path once the first is committed, so "exactly one executable feature test" holds under the gate too.
- **Plan phase**: `references/phases/plan.md`'s Hard gate — "Do not implement any step. Do not write unit tests or implementation code" — means every code sample in `plan.md`, including Step 0's API stubs, is markdown, never a real source file. Writes are confined to `.ailly/`; reads stay unrestricted.
- **Build phase (red-green-refactor)**: reads are unrestricted. Edits are confined to implementation files while the last test run this phase failed ("red" — the loop is trying to make it pass) and to test files while it last passed ("green" — the loop is writing the next one). The extension watches `bash` `tool_result` events for commands that look like a test runner (`npm test`, `pytest`, `cargo test`, `go test`, a `mise`/`just`/`bazel`/`task`/`nx`/`turbo` `test` task, and similar) to learn the current color; before any test has run this build phase, nothing is gated.
- **Cleanup phase**: `references/phases/cleanup.md` is the only phase whose job includes "Remove the `.ailly/developer/YYYY-MM-DD-A-<topic>` folder," so it is the only phase this mode lets delete anything under `.ailly/`. Every other phase has a `bash` call blocked if it looks destructive (`rm`, `git rm`, `find -delete`, a clobbering `>` redirect, …) and references a `.ailly` path — protecting research, design, and plan artifacts from being wiped mid-session. Reads and writes are otherwise unrestricted in cleanup, matching its own mandate to run formatters and refactor passes across the whole tree.

This is a simplification, not a full encoding of `references/phases/red-green-refactor.md`: `references/abilities/refactor.md`'s post-green implementation cleanup falls inside the "green" window the build-phase rule confines to test-only edits. Drop a `.ailly/.file-mode-override` marker file (any content) to disable every rule above — including the deletion guard — until the marker is removed again.

This is a simplification, not a full encoding of `references/phases/red-green-refactor.md`: `references/abilities/refactor.md`'s post-green implementation cleanup falls inside the "green" window this mode confines to test-only edits. Drop a `.ailly/.file-mode-override` marker file (any content) to disable the gate until it is removed again — e.g. for the duration of a refactor pass.

## Model Mandate

Pi's model selection is a CLI flag (`--model <pattern>`), not a per-tool-call schema field on a built-in dispatch tool — but because `ailly_subagent` is this repository's own extension, its `model` parameter is wired straight to that flag on the spawned child process. That makes pi one of the harnesses with a *confirmed* model-selection mechanism, not a degraded announce-only one: set `model` on every `ailly_subagent` call per the mandate-with-announce rule, and announce the choice either way.

## Skill Loading

Pi loads skills natively per the [Agent Skills specification](https://agentskills.io/specification) — the same `SKILL.md` format this repository already uses for Claude Code and Codex. No adapter shim is needed for skill content itself, only for the tool names a `SKILL.md` body references (this table) and for making sure pi can find the skills at all (see Packaging Adapter above and the root `README.md`'s pi setup section).
