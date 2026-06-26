# Long Loops

*Ailly with Dynamic Workflows*

When a topic is run autonomously at project scale, the five-phase lifecycle still runs unchanged. Only the crossing of each draft gate differs. Where the normal loop stops and waits for a human to clear the `*Draft*` marker, the long loop dispatches a research-and-decide reviewer through the active harness's isolation path. That reviewer resolves the gate's open questions and clears the marker, so the run proceeds without user intervention. It is the autonomous counterpart reached for instead of quick-loop when the work has ambiguities to resolve, which quick-loop is not built for. `developer:ailly` consults this reference when acting autonomously over project durations.

## 1. When the long loop applies

The long loop is opt-in at session start, declared once and applied for the run, recognized via phrasings like "run a long loop", "dynamic workflow", or "run \<project\> to completion". It is the inverse trade from quick-loop. Quick-loop skips the deliberation for small, low-stakes work with a narrow surface. The long loop **keeps** the deliberation and the full-fidelity artifacts and only removes the human intervention. Both run every phase through the active harness's isolation path. The long loop therefore does not inherit quick-loop's forbidden list (ambiguous, high-blast-radius, or security-sensitive work); that work is exactly what it is for.

## 2. The research-and-decide reviewer contract

At each draft gate the coordinator dispatches a fresh reviewer runner, scoped to a single artifact (document, code diff, or similar) and read cold. Its contract, stated as the dispatch instruction:

- Read the artifact cold without including prior session context.
- Find the artifact's open items (the "Open for human review" / "Summary / deferred decisions" / deferred-decisions slot) and research them using the `research:` skills and the repo conventions.
- Make the conservative default decision for each item.
- Record each decision with rationale in the artifact (format below).
- Escalate rather than decide when a trigger fires (rule in section 4): leave the gate uncleared and flag the item `ESCALATE: <why>`.
- Remove the `*Draft*` marker once every blocking item is decided.

This is a single cheap isolated reviewer per gate, not a fan-out ensemble. A standalone LLM reviewer suggests candidates to be validated rather than final truth, so one conservative decide-runner with a recorded audit trail is the cheap, low-risk default. Model choice is left to the coordinator; the reference stays model-agnostic.

## 3. The decision-recording format

Resolve each artifact's needed decisions in place. There is no separate `decisions.md`. Convert the open slot into a block headed `Resolved by the long-loop reviewer (YYYY-MM-DD)`, one entry per open item, in the format:

```
**N. <question or item title>. Decided: <the decision>.** <rationale, including
what was researched and why this is the conservative default>
```

Escalated items use the same block:

```
**N. <item title>. ESCALATE: <why this could not be decided conservatively>.**
```

A worked entry, taken from this session's own `research.md` (entry 1, "Where do the mechanics live?"):

> **1. Where do the mechanics live? Decided: a new
> `developer/skills/ailly/references/shapes/long-loop.md` that `developer/skills/ailly/SKILL.md`
> points to from a short "Long-loop Mode" section.** This matches the verified
> reference-delegation convention (Bugfix Shape → `bugfix.md`, Project Shape →
> `project-cycle.md`), and the contract, recording format, and gate mapping
> together exceed a section's worth and would bloat SKILL.md.

The cleanup phase already extracts deferred decisions from `design.md` into `TASKS.md` (or the configured tracker, when the program-management using reference `developer/skills/ailly/references/abilities/program-management/using.md` is wired), so the in-place block feeds that existing path. A separate decision log would split the audit trail.

## 4. The escalation rule (three concrete triggers)

The reviewer decides the conservative default unless a trigger fires, in which case it leaves the gate uncleared and flags `ESCALATE:`. The triggers:

- (a) **Irreversible.** The decision cannot be undone or cheaply reversed if wrong.
- (b) **Out of recorded scope.** The decision exceeds the scope the artifact itself records. An example is a decision that would change a system the artifact's Scope section excludes.
- (c) **Underdetermined.** The artifact and the repo conventions do not determine a reasonable conservative default.

The reviewer still clears the remaining gates if the escalated item is not a prerequisite for them. If it is, the gate stays uncleared and the run halts there for the human.

## 5. Project-cycle nested-gate interaction

A project loop has nested gates (`developer/skills/ailly/references/shapes/project/project-cycle.md`), and the reviewer contract maps onto both altitudes.

- **Project altitude.** The project-altitude **Review** phase is "the draft-gate period, the project-altitude equivalent of the `*Draft*` marker". The same reviewer contract applies, dispatched scoped to the project design doc at project altitude.
- **Per feature-step.** Each feature-step is itself a feature loop with its own design, plan, and cleanup gates. The reviewer is dispatched fresh per gate for each, cold-scoped to that feature's artifact.

A fresh per-gate dispatch (not one reviewer for the whole project) is the lower-blast-radius default, matching the cold-isolation rationale quick-loop already states.

Because project-cycle's "Sequential and Parallel Steps" defines a parallel step as one that "shares no dependency with its siblings", "prerequisite" is judged per feature-step, not per project: an escalation in one parallel feature does not halt independent siblings. Only steps that depend on the escalated output halt.

At project altitude, reuse the same `Resolved by the long-loop reviewer (YYYY-MM-DD)` heading and entry format from section 3, placed in the project design doc's Summary section (the same slot a feature design's Summary carries, which feeds the same `TASKS.md` cleanup extraction).

## 6. The never-auto-clear invariants

Two gates are never auto-cleared by any reviewer, in any mode.

- **The human merge gate.** The coordinator "pauses for human approval before the squash-merge or PR" (`developer/skills/ailly/SKILL.md` Session-Folder note and the loop diagram's `gate_merge`; `project-cycle.md` at project altitude). This gate is owned by the **coordinator**, not the cleanup body. In long-loop mode the cleanup phase still runs through the harness isolation path and produces the merge-ready state, but it hands back to the coordinator at this gate; the cleanup runner never approves or performs the merge on its own. The long-loop autonomy stops at the draft gates; the merge gate stays human regardless of mode.
- **The Closing Bell.** A human usability study; "the agent does not pass it on the user's behalf" (`developer/skills/ailly/references/shapes/project/closing-bell.md`). The reviewer never runs or passes it. When the project gets to the closing bell, the long loop is completed.

## 7. The end-of-run report

When the run reaches the human merge gate or otherwise finishes, the coordinator emits a report:

- **What was decided.** Per gate, the recorded-decision entries (or a pointer to each artifact's block).
- **What was done.** Per phase, the artifact produced and its location.
- **Where it stopped.** The merge gate (awaiting human approval).

The destination follows the loop's retention rule. For a feature loop the report is inline only, because the feature cleanup removes the session folder and a persisted file would earn nothing. For a project loop the coordinator also writes a `report.md` that becomes a supporting sub-page in the long-lived documents (`project-cycle.md`, "Long-Lived Documentation"), persisted alongside the design and the Closing Bell.
