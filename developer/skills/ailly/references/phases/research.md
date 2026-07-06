# Research phase

> Phase reference loaded by the coordinator (`developer:ailly`) when entered as
> `/ailly research ...`. The coordinator hands this to an isolated phase runner
> that reads only this one reference through the active harness's isolation path. There is no standalone `developer:research`
> skill; the coordinator enters the phase by argument.

## Overview

The first phase of the development lifecycle. A thin **delegating coordinator** that opens a topic by gathering and then narrowing context before any design exists. It owns the `research.md` artifact and the draft gate; `research:using-research` owns the search and falsification internals (the Jeopardy expand and the oppositional falsify). This skill does not re-implement search; it briefs and frames it.

**Announce at start:** "Using the developer:ailly research phase to gather and refine context for [summary of topic]. Per `general/skills/dispatching-agents/model-selection.md`, match this to the active provider with its effort or thinking qualifier verbatim. Set the model directly when the harness's dispatch call allows it; announce the model chosen either way. I'll continue on the current model either way."

**Trigger:** a new or vague development topic with nothing gathered yet. The intent is known loosely, but the supporting context, prior art, and scope are not.

## Dual lens

Every delegation to `research:using-research` carries two lenses at once:

- **General lens** — software-engineering practice broadly. What established engineering and public prior art say about this class of problem.
- **Specific lens** — this exact task and codebase. The user's precise intent and the code it touches.

The expand brief leans on the general lens. The refine brief leans on the specific lens.

## Behavior

1. **Open or continue the session folder** (`.ailly/developer/YYYY-MM-DD-A-<topic>/`). If a topic slug is not obvious from the prompt, ask for a short one before creating the folder.
2. **Tracker-origin intake**: when the topic originates from a tracker item, route its full thread through `thread-digest`. Fetch it per `program-management/using.md`'s full-thread fetch rule, or fetch it fresh here if the topic originates directly in this phase. Always do this, since a tracker thread is a conversational medium. Fold the result into the Expand/Refine context below alongside the body.
3. **Expand** — drive `research:using-research` with an explicit expand brief on the general lens: supporting complaints and complementary work, feature requests, user complaints, adjacent internal libraries and docs, public projects solving the same problem, and field research. A deep topic may spin off several ancillary supporting docs.
4. **Library docs review**: whenever the task touches a specific library or framework, do a focused docs review of *that* library before refining, not just a general links sweep. Consider any library named in the prompt, or any the codebase already depends on for this surface. For each such library, look specifically for: a **getting-started / authoring guide**, **similar examples or recipes** that show the closest worked example to what's being built. Search the package, its repo, and its `*.test.ts`/examples for these. Also seek **published agentic skills**: a `SKILL.md`, MCP server, or `skills/` directory shipped by the library or its local checkout. These frequently remain outside `node_modules`. Then do the general docs review for any other helpful links. The point of the original Astrolabe miss: Jiffies shipped a `using-jiffies-dom` skill that was never found, so the code dropped to raw DOM. Record every discovered skill in the **Libraries & Skills** section so downstream phases load it instead of reinventing the framework.
5. **Refine** — drive `research:using-research` with a refine brief on the specific lens to right-size the task and narrow it as far as it honestly can go. Select the refinements that fit the expand findings; this list is neither exhaustive nor mandatory. Consider: How large is this: a project of several features, a single feature, or a bug fix? Can an off-the-shelf tool already do it? Should another team be collaborating on it? What is the smallest version that still meets the intent?
6. **Write `research.md`** with the sections below, marked `*Draft YYYY-MM-DD*`. Review it for clarity, consistency, and conciseness. Check in particular whether the digested thread from step 2 contains a comment that postdates and materially reframes the original scoping. If it does, record that as a **note-only** line in `research.md`'s Resolved Decisions section; this is not a halt, and the phase proceeds normally either way. Collaborate with the user on the questions research did not resolve. Because this research is part of an Ailly development task, pass `.ailly/developer/YYYY-MM-DD-A-<topic>/research/` as the note destination for every delegated `research:` skill. Per-skill findings land there as `<skill>.md` with IEEE-style Sources, overriding the standalone `.ailly/research/` default from the `research:using-research` Research Notes Convention.
7. **Cite the wiring contract** — point at the source setup references (`research:using-research`, `references/configuring/<source>.md`) for source setup rather than re-teaching it. If the MCP research sources are insufficient (unavailable, or returning less than expected), raise a warning and suggest troubleshooting the connectors or refining the task.
8. **Stop at the draft gate.**

## Research.md sections

Write `research.md` with exactly these headings:

- **Topic and Intent** — first, an exact, **verbatim quote** of the user's original request (blockquoted or fenced), not a paraphrase; then the loosely stated goal in the user's own framing, added afterward as clearly separate prose. The verbatim quote is the durable anchor `references/abilities/intent-review.md` reads backward from at later draft gates to improve intent alignment.
- **Search/Expand** — what the expand pass surfaced under the general lens.
- **Libraries & Skills** — every library/framework this task touches, with the docs that matter (getting-started, the closest worked example/recipe, links) and, for each, **any published agentic skill to load** (its name and how to invoke it). Open with an explicit directive that downstream phases honor: *"Before doing any work in this feature, load these skills via the active harness's skill-loading mechanism: …"* Carry this directive **verbatim into `design.md` and `plan.md`** so design, plan, and every red-green-refactor step loads the framework's skill instead of reinventing it. If no relevant library skill exists, say so explicitly (so the omission is a finding, not a gap).
- **Falsification/Refine** — how the refine pass right-sized the task under the specific lens. What emerged: the task's size (project / feature / bug), whether an off-the-shelf tool could replace it, or what the smallest viable version looks like.
- **Scope** — what is in and out for the design phase that follows.
- **Resolved Decisions** — questions research answered, and the ones still open for the human.
- **Sources** — IEEE-style citations for every external claim.

The `research.md` produced by this very session folder is the working template.

## Output artifacts

Save to the session folder (`.ailly/developer/YYYY-MM-DD-A-<topic>/`):

- `research.md` — the six sections preceding, marked `*Draft YYYY-MM-DD*` after the title.
- Per-skill findings under `.ailly/developer/YYYY-MM-DD-A-<topic>/research/<skill>.md`. This follows the task-scoped `research:using-research` convention.

## Stop condition

After saving, tell the user:

> "Research gathered and refined, saved to `.ailly/developer/YYYY-MM-DD-A-<topic>/research.md`. Review it, resolve the open questions, and make any changes. When you're satisfied, remove the `*Draft YYYY-MM-DD*` marker. Start a new session and run `developer:ailly` (it resumes at the design phase) to continue."

Do not write a design or a feature test. Do not enter the design phase. Stop at the gate.
