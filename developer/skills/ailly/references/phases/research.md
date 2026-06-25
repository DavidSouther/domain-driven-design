# Research Phase

> Phase reference loaded by the coordinator (`developer:ailly`) when entered as
> `/ailly research ...`. The coordinator hands this to an isolated phase subagent
> that reads only this one reference. There is no standalone `developer:research`
> skill; the phase is entered by argument.

## Overview

The first phase of the development lifecycle. A thin **delegating coordinator** that opens a topic by gathering and then narrowing context before any design exists. It owns the `research.md` artifact and the draft gate; `research:using-research` owns the search and falsification internals (the Jeopardy! expand and the oppositional falsify). This skill does not re-implement search; it briefs and frames it.

**Announce at start:** "Using the developer:ailly research phase to gather and refine context for [summary of topic]. Name the recommended model for research from the Phase by Provider table in developer/references/model-per-phase.md, matched to the active provider, with its effort or thinking qualifier verbatim. If you're not already on it, I'll switch when the harness allows; otherwise switch with `/model` (press `s` for session-only) as the fallback. I'll continue on the current model either way."

**Trigger:** A new or vague development topic with nothing gathered yet. The intent is known loosely, but the supporting context, prior art, and scope are not.

## Dual Lens

Every delegation to `research:using-research` carries two lenses at once:

- **General lens** — software-engineering practice broadly. What established engineering and public prior art say about this class of problem.
- **Specific lens** — this exact task and codebase. The user's precise intent and the code it touches.

The expand brief leans on the general lens. The refine brief leans on the specific lens.

## Behavior

1. **Open or continue the session folder** (`.ailly/developer/YYYY-MM-DD-A-<topic>/`). If a topic slug is not obvious from the prompt, ask for a short one before creating the folder.
2. **Expand** — drive `research:using-research` with an explicit expand brief on the general lens: supporting complaints and complementary work, feature requests, user complaints, adjacent internal libraries and docs, public projects doing the same thing, and field research. A deep topic may spin off several ancillary supporting docs.
3. **Refine** — drive `research:using-research` with a refine brief on the specific lens to right-size the task and narrow it as far as it honestly will go. Select the refinements that fit the expand findings; this list is neither exhaustive nor mandatory: how large is this — a project of several features, a single feature, or a bug fix — can an off-the-shelf tool already do it, should another team be collaborating on it, what is the smallest version that still meets the intent?
4. **Write `research.md`** with the sections below, marked `*Draft YYYY-MM-DD*`. Then review it for clarity, consistency, and conciseness, and collaborate with the user on the questions research did not resolve. Per-skill findings land under `docs/research/YYYY-MM-DD-A-<topic>/<skill>.md` with IEEE-style Sources, following the `research:using-research` Research Notes Convention.
5. **Cite the wiring contract** — point at the source setup references (`research:using-research`, `references/configuring/<source>.md`) for source setup rather than re-teaching it. If the MCP research sources are insufficient (unavailable, or returning less than expected), raise a warning and suggest troubleshooting the connectors or refining the task.
6. **Stop at the draft gate.**

## research.md Sections

Write `research.md` with exactly these headings:

- **Topic and Intent** — the loosely-stated goal in the user's own framing.
- **Search/Expand** — what the expand pass surfaced under the general lens.
- **Falsification/Refine** — how the refine pass right-sized the task under the specific lens (size: project / feature / bug, off-the-shelf, smallest version).
- **Scope** — what is in and out for the design phase that follows.
- **Resolved Decisions** — questions research answered, and the ones still open for the human.
- **Sources** — IEEE-style citations for every external claim.

The `research.md` produced by this very session folder is the working template.

## Output Artifacts

Save to the session folder (`.ailly/developer/YYYY-MM-DD-A-<topic>/`):

- `research.md` — the six sections above, marked `*Draft YYYY-MM-DD*` after the title.
- Per-skill findings under `docs/research/YYYY-MM-DD-A-<topic>/<skill>.md` (the `research:using-research` convention).

## Stop Condition

After saving, tell the user:

> "Research gathered and refined, saved to `.ailly/developer/YYYY-MM-DD-A-<topic>/research.md`. Review it, resolve the open questions, and make any changes. When you're satisfied, remove the `*Draft YYYY-MM-DD*` marker. Start a new session and run `developer:ailly` (it resumes at the design phase) to continue."

Do not write a design or a feature test. Do not enter the design phase. Stop at the gate.
