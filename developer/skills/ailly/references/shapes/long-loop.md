# Long loops

*Ailly with Dynamic Workflows*

When the long loop runs a topic autonomously at project scale, the five-phase lifecycle still runs unchanged.
Only the crossing of each draft gate differs.
Where the normal loop stops and waits for a human to clear the `*Draft*` marker, the long loop dispatches a research-and-decide reviewer through the active harness's isolation path.
That reviewer resolves the gate's open questions and clears the marker, so the run proceeds without user intervention.
It is the autonomous counterpart reached for instead of quick-loop when the work has ambiguities to resolve, which quick-loop is not built for.
`developer:ailly` consults this reference when acting autonomously over project durations.

## 1. When the long loop applies

The long loop is opt-in at session start, declared once and applied for the run, recognized via phrasings like "run a long loop," "dynamic workflow," or "run \<project\> to completion."
It is the inverse trade from quick-loop.
Quick-loop skips the deliberation for small, low-stakes, narrowly-scoped work.
The long loop **keeps** the deliberation and the full-fidelity artifacts and only removes the human intervention.
Both run every phase through the active harness's isolation path.
The long loop therefore does not inherit quick-loop's forbidden list.
Ambiguous, high-blast-radius, and security-sensitive work is exactly what it is for.

## 2. The research-and-decide reviewer contract

At each draft gate the coordinator dispatches a fresh reviewer runner, scoped to a single artifact (document, code diff, or similar) and read cold.
Its contract, stated as the dispatch instruction:

- Read the artifact cold without including prior session context.
- Find the artifact's open items, which you'll locate in the "Open for human review," "Summary / deferred decisions," or deferred-decisions slot.
  Research them using the `research:` skills and the repo conventions.
- Decide the conservative default for each item.
- Record each decision with rationale in the artifact (format below).
- Escalate rather than decide when a trigger fires (rule in section 4): leave the gate uncleared and flag the item `ESCALATE: <why>`.
- Remove the `*Draft*` marker once you have decided every blocking item.

This is a single cheap isolated reviewer per gate, not a fan-out ensemble.
A standalone LLM reviewer suggests candidates for the human to validate rather than providing final truth.
Use one conservative decide-runner with a recorded audit trail to keep costs low and risk minimal.
The coordinator chooses the model; the reference stays model-agnostic.

## 3. The decision-recording format

Resolve each artifact's needed decisions in place.
There is no separate `decisions.md`.
Convert the open slot into a block headed `Resolved by the long-loop reviewer (YYYY-MM-DD)`, one entry per open item, in the format:

```
**N. <question or item title>. Decided: <the decision>.** <rationale, including
what was researched and why this is the conservative default>
```

Escalated items use the same block:

```
**N. <item title>. ESCALATE: <why this could not be decided conservatively>.**
```

A worked entry, taken from this session's own `research.md` (entry 1, "Where do the mechanics live?"):

> **1.**
> **Where do the mechanics live?**
> **Decided: a new `developer/skills/ailly/references/shapes/long-loop.md` that `developer/skills/ailly/SKILL.md` points to from a short "Long-loop Mode" section.**
> This matches the verified reference-delegation convention.
> Bugfix Shape points to `bugfix.md`, and Project Shape points to `project-cycle.md`.
> The contract, recording format, and gate mapping together exceed what a section can hold, and including them would bloat `developer/skills/ailly/SKILL.md`.

The cleanup phase already extracts deferred decisions from `design.md` into `TASKS.md`.
When you wire the program-management using reference `developer/skills/ailly/references/abilities/program-management/using.md`, it uses the configured tracker instead.
The in-place block feeds that existing path.
A separate decision log would split the audit trail.

## 4. The escalation rule (three concrete triggers)

The reviewer decides the conservative default unless a trigger fires, in which situation it leaves the gate uncleared and flags `ESCALATE:`.
The triggers:

- (a) **Irreversible.**
  The decision cannot be undone or cheaply reversed if wrong.
- (b) **Out of recorded scope.**
  The decision exceeds what the artifact itself records as its scope.
  For example, the decision might change a system that the artifact's Scope section explicitly excludes.
- (c) **Underdetermined.**
  The artifact and the repo conventions do not determine a reasonable conservative default.

The reviewer still clears the remaining gates if the escalated item is not a prerequisite for them.
If it is, the gate stays uncleared and the run halts there for the human.

## 5. Project-cycle nested-gate interaction

A project loop has nested gates.
See `developer/skills/ailly/references/shapes/project/project-cycle.md` for details.
The reviewer contract maps onto both altitudes.

- **Project altitude.**
  The project-altitude **Review** phase serves as "the draft-gate period, the project-altitude equivalent of the `*Draft*` marker."
  Apply the same reviewer contract, dispatched to the project design doc at project altitude.
- **Per feature-step.**
  Each feature-step is itself a feature loop with its own design, plan, and cleanup gates.
  Dispatch a fresh reviewer per gate for each feature, cold-scoped to that feature's artifact.

A fresh per-gate dispatch (not one reviewer for the whole project) is the lower-blast-radius default, matching the cold-isolation rationale quick-loop already states.

Project-cycle's "Sequential and Parallel Steps" defines a parallel step as one that "shares no dependency with its siblings."
Judge "prerequisite" per feature-step, not per project.
An escalation in one parallel feature does not halt independent siblings.
Only steps that depend on the escalated output halt.

At project altitude, reuse the same `Resolved by the long-loop reviewer (YYYY-MM-DD)` heading and entry format from section 3.
Place it in the project design doc's Summary section.
A feature design's Summary carries the same slot and feeds the same `TASKS.md` cleanup extraction.

## 6. The never-auto-clear invariants

Two gates are never auto-cleared by any reviewer, in any mode.

- **The human merge gate.**
  The coordinator "pauses for human approval before the squash-merge or PR."
  See `developer/skills/ailly/SKILL.md` for the Session-Folder note and the loop diagram's `gate_merge`; also see `project-cycle.md` at project altitude.
  The **coordinator** owns this gate, not the cleanup body.
  In long-loop mode, the cleanup phase runs through the harness isolation path and produces the merge-ready state.
  It hands back to the coordinator at this gate.
  The cleanup runner never approves or performs the merge on its own.
  Long-loop autonomy stops at the draft gates.
  The merge gate remains human regardless of mode.
- **The Closing Bell.**
  A human usability study.
  As stated in `developer/skills/ailly/references/shapes/project/closing-bell.md`, "the agent does not pass it on the user's behalf."
  The reviewer never runs or passes it.
  When the project reaches the closing bell, the long loop completes.

## 7. The end-of-run report

When the run reaches the human merge gate or otherwise finishes, the coordinator emits a report with three components:

- **Decisions.**
  Per gate, the recorded-decision entries (or a pointer to each artifact's block).
- **What each phase produced.**
  Per phase, the artifact produced and its location.
- **Where it stopped.**
  The merge gate (awaiting human approval).

The destination follows the loop's retention rule.
For a feature loop, keep the report inline only, because the feature cleanup removes the session folder and a persisted file would serve no purpose.
For a project loop, the coordinator also writes a `report.md` that becomes a supporting sub-page in the long-lived documents.
See `project-cycle.md` under "Long-Lived Documentation."
Store it alongside the design and the Closing Bell.
