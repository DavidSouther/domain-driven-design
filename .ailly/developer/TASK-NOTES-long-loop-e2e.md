# Dry-Run Trace: long loop crossing one draft gate

This artifact is the feature test for the long-loop mode. Because the mode is
write-only skill prose (no executable runtime), the feature-test slot is filled
by a worked walkthrough that crosses one draft gate, plus the artifact-criteria
checklist in `design.md`. The trace asserts the observable outcomes that define
"green." It is **red** until `developer/references/long-loop.md` and the
ailly SKILL.md "Long-loop Mode" pointer section exist and a real run matches it;
it goes **green** when every assertion below holds against a real long-loop run
and the artifact-criteria checklist is satisfied.

The worked example is THIS session's own research-gate crossing. The session was
run as a long loop: the coordinator wrote `research.md` with open questions, then
dispatched a fresh reviewer subagent that read the artifact cold, researched the
open questions, recorded decisions in place, and cleared the marker. The
coordinator then proceeded to design (this phase). The merge gate is still human.

## Scenario

Operator request at session start:

> "Run a long loop for the long-loop coordination mode topic."

Mode: long loop (opt-in, declared at start). Topic: `2026-06-17-B-long-loop`.
The gate under test is the **research draft gate**.

## Trace

1. **Coordinator selects long loop.** The operator asked for a long loop at
   start, so the coordinator records the mode for the session. It does NOT
   inherit quick-loop's forbidden list (this topic is documentation work, low
   physical blast radius, but it touches the coordinator skill, so deliberation
   is kept).

2. **Coordinator runs the research phase in a subagent.** A research subagent
   invokes `developer:research`, produces
   `.ailly/developer/2026-06-17-B-long-loop/research.md` marked `*Draft*`, with a
   "Resolved Decisions" section split into "Resolved by the research" and an
   open slot ("Open for the long-loop reviewer" / equivalent unresolved items).

3. **Draft gate appears.** `research.md` carries the `*Draft 2026-06-17*` marker.
   In a normal session the coordinator would stop and wait for the human. In a
   long loop the coordinator instead dispatches the reviewer.

4. **Coordinator dispatches a FRESH research-and-decide reviewer subagent,
   scoped to ONE artifact.** The dispatch prompt instructs: "Read this artifact
   COLD, do not assume prior context. Research the open questions. Make
   conservative decisions. Record each decision with rationale in the artifact.
   Then remove the `*Draft*` marker. Escalate (leave uncleared, flag
   `ESCALATE:`) anything irreversible, out of recorded scope, or
   underdetermined."

5. **Reviewer reads cold and researches.** The reviewer opens `research.md`
   without prior session context, reads the cited internal files
   (`SKILL.md`, `project-cycle.md`, `bugfix.md`, the phase skills) and the open
   questions, and verifies the claims it needs to decide.

6. **Reviewer records decisions in place.** It converts the artifact's open slot
   into a "Resolved by the long-loop reviewer (2026-06-17)" block, one entry per
   open question, in the format
   `**N. <question>. Decided: <decision>.** <rationale>`. Six entries were
   recorded for this topic (mechanics location, recording format, project-cycle
   interaction, guardrails, eval-vs-trace, subagent isolation).

7. **Reviewer clears the marker.** Having decided every open question without
   needing to escalate, the reviewer removes the `*Draft 2026-06-17*` marker
   from `research.md`.

8. **Coordinator proceeds to the next phase.** The coordinator observes the
   cleared marker and dispatches the design phase in a subagent
   (`developer:design`, this phase), passing the session folder. No human was
   asked to clear the research gate.

9. **Merge gate stays human.** The trace stops at the research-to-design
   transition. The terminal human merge gate and the Closing Bell are never
   auto-cleared by any reviewer; they remain the operator's, regardless of mode.

## Assertions (observable outcomes that define green)

A real long-loop run is green when ALL of the following hold for the gate it
crosses:

- **A1 — Reviewer dispatched.** A distinct reviewer subagent was launched at the
  gate, separate from the phase subagent, scoped to the single artifact, with a
  cold-read instruction.
- **A2 — Decision recorded with rationale.** The artifact contains a "Resolved
  by the long-loop reviewer (YYYY-MM-DD)" block with one `**N. ... Decided:
  ...** <rationale>` entry per open question. No open question is silently
  dropped.
- **A3 — Marker cleared by the reviewer, not the human.** The `*Draft*` marker
  is gone from the artifact, and the clearing action is attributable to the
  reviewer subagent.
- **A4 — Escalations surfaced in place.** Any item the reviewer could not decide
  conservatively appears as `ESCALATE: <why>` in the same block, and its gate is
  left uncleared if the item is a prerequisite for the next phase.
- **A5 — Merge gate preserved.** No reviewer cleared the terminal human merge
  gate or passed the Closing Bell. The coordinator still pauses for human
  approval before the squash-merge or PR.
- **A6 — Coordinator proceeded only on a cleared marker.** The next phase began
  because the marker was cleared, following the same resume table the normal
  loop uses (`SKILL.md` Session Folder table), not by overriding the gate.
- **A7 — End-of-run report.** At the end of the run the coordinator emits a
  report listing what was done per phase and what was decided per gate
  (the recorded-decision blocks, with any escalations called out).

## Verification on THIS session

This session satisfies A1 through A4 and A6 for the research gate already:
`research.md` carries a "Resolved by the long-loop reviewer (2026-06-17)" block
with six `Decided:` entries and rationale, its `*Draft*` marker is cleared, and
the design phase (this one) was reached without a human clearing the research
gate. A5 holds by construction (no merge has occurred; the merge gate remains
human). A7 is asserted at end-of-run, not at a single gate.

The trace remains **red** as a feature test until the SKILL.md pointer section
and `developer/references/long-loop.md` exist, because A1, A2, and A7 reference
contracts that the reference doc must define before a future run can be checked
against them. It goes **green** when those exist and a real run matches every
assertion.
