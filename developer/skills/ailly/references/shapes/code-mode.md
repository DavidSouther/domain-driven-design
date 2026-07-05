# Code Mode

## When Code Mode Applies

Code Mode is for a small standalone script or automation, not an application
feature: a file-system loop, an orchestration wrapper over tools that already
exist, minimal logic and no application-feature surface. Before condensing
anything, apply the routing test — is this task script-shaped? An ambiguous
*feature* inside an app is not for Code Mode; it belongs to the standard loop
(or quick-loop once disambiguated). This script-vs-feature boundary is the
load-bearing distinction between Code Mode and every other shape here.

Code Mode is opt-in at session start, entered by a distinct trigger phrase, the
same way quick-loop and long-loop are entered ("code mode", "write a script to
..."). It is also reachable through `developer:ailly`'s Routing table, which
carries a row pointing back at this reference.

## Cursory Research

Before writing anything, make one `research:public` call to check whether an
off-the-shelf tool already fits the specific task, keeping Python, Shell, or PowerShell for
orchestration only and wrapping the tool that fits rather than hand-rolling it.
"Check spelling across these dozen files" should surface `vale.sh` as the tool
the script wraps, not a from-scratch spell checker. Record the finding — the
tool chosen, or "hand-written because none fits" — in the combined planning doc
below rather than a separate `research.md`.

## Combined Planning Doc

Research, design, and plan collapse into a single short document in the
session folder, in place of the standard loop's three separate artifacts. It
records what the script does, the tool it wraps (or why it is hand-written),
the model / tool-restriction / concurrency choices for any sub-sessions it
dispatches, and any clarifications. Genuine ambiguity is raised through
`intent-review.md`, worked backward from the original prompt exactly as the
standard loop uses it; the developer resolves each question at the single
draft gate below (intent-review never auto-clears a gate on its own). Code
Mode reuses `intent-review.md` as-is — it does not add a new sibling mechanism
for ambiguity.

## Gates

One human-cleared draft gate covers the combined planning doc; once the
developer clears it, Build runs. The standard human merge gate still applies
and is never auto-cleared. Code Mode does not auto-clear like quick-loop —
keeping this one human beat is precisely what lets Code Mode take on ambiguous
work that quick-loop must refuse.

## Build

Write the script, run it once, and inspect the output. There is no feature test
and no red-green-refactor TDD loop: Code Mode scripts stay trivial enough by
construction — minimal logic, simple file-system loops, no branching or design
patterns — that a human can review them at a glance instead. Code Mode scripts
typically land in a `scripts/` folder, or wherever else the project's
conventions put standalone automation.

## Guidance for Spawned Sessions

Any generated script that spawns further headless Claude sessions (the
vale-autofix shape this document's Worked Example walks through) follows four
concrete rules:

- **Headless dispatch.** Dispatch each session with `claude --print` (`-p`) in
  a non-prompting permission mode, not an interactive session.
- **Restricted tools.** Restrict each dispatched session with a minimal or
  empty `--allowedTools` set — no agents, tool access, or anything beyond what
  the specific task needs.
- **Bare-alias model.** Express the model as a bare alias, e.g. `haiku`, per
  `model-selection.md` — not a dated pin like `haiku-4.5`. A dated pin names one
  specific model rather than asking for "the latest," so the bare-alias rule
  still applies.
- **Capped concurrency.** Cap concurrency with `xargs -P N` (or a counting
  semaphore) rather than hand-rolled pool bookkeeping — for example `-P 8` to
  cap outstanding sessions at eight.

## Worked Example

This walks the vale-autofix scenario through the loop above, as an
illustration of the shape, not a build target — the script itself is tracked
in its own session.

The prompt asks for a coordination script that runs Vale across the repo,
writes per-file findings, and dispatches capped concurrent headless sessions
to fix the warnings, naming `haiku-4.5` as the model in the prompt's own
wording. Cursory research makes one `research:public` call and surfaces
`vale.sh` as an existing off-the-shelf linter, so the script wraps it instead
of hand-rolling a style checker. The combined planning doc records that wrap
plan, the per-file findings path `.ailly/prompts/vale/`, and the dispatch
shape `xargs -P 8 claude -p --model haiku --allowedTools ...` — normalizing
the prompt's `haiku-4.5` to the bare alias per the guidance above. The
developer clears the single draft gate on that doc, and Build writes and runs
the coordination script once, then inspects the per-file findings it
produced.
