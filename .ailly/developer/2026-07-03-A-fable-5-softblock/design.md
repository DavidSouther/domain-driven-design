# Design: Soft-block Fable 5 in the Ailly Model Check

## Purpose

Fable 5 (`claude-fable-5`) has shown, in production use as an Ailly
coordinator/phase-runner, that it applies stored feedback rules too
literally — following a rule's letter (e.g. "always PR a session branch on
first push") instead of its intent (scoped to code-bearing branches), which
opened an unwanted PR on a Figma-design-only session. Issue #29 asks for a
soft block: the phase-entry model check and phase-subagent dispatch should
flag Fable 5 explicitly rather than silently accepting or inheriting it,
while still letting the developer continue if they decline to switch. The
block lifts once Fable 5 reaches Sonnet/Opus-tier judgment on applying
stored feedback's intent, not just its wording.

## Prior Art

- **Frontier-Model Caution** (`general/skills/dispatching-agents/model-
  selection.md`) already gates the mirror case: a *new, high-benchmark*
  model is withheld from a recommendation until it clears an eval suite.
  This design adds the inverse gate — a *known-regressed* model flagged out
  — using the same check-not-gate posture and the same file's alias
  philosophy (never a dated pinned version as the durable recommendation).
- **Tool readiness** (`developer/skills/ailly/references/checks/tool-
  failure.md`, referenced from the Model check's sibling bullet in `ailly/
  SKILL.md`) is the existing pattern for "flag explicitly, then let the
  human decide" checks inside the coordinator — the soft block follows the
  same shape.
- Issue #29's suggested mechanism targeted `references/checks/model-per-
  phase.md`; that file was removed in commit `701affe` and its content now
  lives in `general/skills/dispatching-agents/model-selection.md` plus an
  inline "Model check" bullet in `developer/skills/ailly/SKILL.md`
  (research.md, Reconciliation finding). This design attaches to those two
  current locations instead of reviving the deleted file.

## User Journey and Metrics

- A developer runs `developer:ailly` (any phase) while their harness is
  running Fable 5. The phase-entry **Model check** detects the running
  model, matches it against a documented soft-block list, and says so
  explicitly: it recommends switching to `sonnet` or `opus` via `/model`,
  naming the reason (stored-feedback judgment gap) and the un-block
  condition (quality parity on applying a rule's intent, not just its
  text).
- The developer may decline. The loop continues on Fable 5 regardless —
  this is a check, not a gate, matching the existing Model check and Tool
  readiness checks' posture.
- When the coordinator dispatches a phase subagent, it does not silently
  hand the subagent the same soft-blocked model; it prefers the phase
  table's recommended alias per the existing mandate-with-announce
  behavior in `model-selection.md`.
- **Metric:** every phase-entry Model check performed while the soft-block
  list has a match produces the explicit flag wording (not the ordinary
  "matches/exceeds recommendation" silence); the loop's continuation is
  unaffected by the flag.

## Specification

- **`general/skills/dispatching-agents/model-selection.md`:** add a
  `## Soft-Blocked Models` subsection, separate from Frontier-Model
  Caution (that section governs *unproven new* models; this one governs a
  *specific known-regressed* one — different justification, kept visually
  distinct rather than folded together). Content: a short list entry naming
  `claude-fable-5` ("Fable"), the observed failure mode (applies stored
  feedback literally rather than by its underlying intent — cites the
  stellar_commander incident in one line), and the removal condition
  (parity with `sonnet`/`opus` on that same judgment). Per the file's own
  alias rule, the entry recommends switching to `sonnet` or `opus` — bare
  aliases, not a dated version string — so this new subsection cannot ever
  trip `test_subagent_model_mandate.py`'s T2 staleness check (which scans
  this same file for the literal strings "Sonnet 4.6" / "Opus 4.8" /
  "Haiku 4.5"). This is a resolved design decision, not deferred: the
  issue's own suggested message names dated versions, but writing them into
  this durable guidance file would recreate the exact staleness problem the
  file exists to prevent, so the flag wording here stays alias-based.
- **`developer/skills/ailly/SKILL.md`, "Model check" bullet:** extend it so
  that when the detected running model matches the soft-block list, the
  check flags it explicitly (naming the model, the reason, and the /model
  switch suggestion) instead of treating the match as satisfying or
  exceeding the phase's recommended model. State plainly that this remains
  a check, not a gate — the loop does not stall if the developer declines.
- **Phase-subagent dispatch:** the same bullet (or its immediate
  surrounding dispatch text) states that a soft-blocked model is not
  silently inherited by a dispatched phase subagent; dispatch prefers the
  phase table's recommended alias per the existing mandate-with-announce
  rule, rather than propagating the coordinator's own soft-blocked model
  into the subagent call.
- **Test:** one new feature test, `developer/tests/test_fable5_softblock.py`,
  following the sibling contract-test convention already established by
  `test_subagent_model_mandate.py` (no pytest, no model required, script
  exits 0 when every rule holds or 1 with one reason line). See "Feature
  Test" below for its path and shape.

## Alternatives

- **Revive `model-per-phase.md` as the issue literally suggests.** Rejected
  — the reconciliation in research.md shows that file was deliberately
  replaced; reviving it would split model guidance back into two
  conflicting homes and undo commit #32's consolidation.
- **Fold the soft-block into the existing Frontier-Model Caution section**
  instead of a new heading. Rejected as the primary approach — Frontier-
  Model Caution is about withholding a recommendation from an *unproven*
  model; a soft block is about *actively flagging* a specific *known*
  regression. Conflating the two would blur a caution ("wait for evals")
  with a warning ("this one has an observed problem"). Kept as two
  adjacent, cross-referencing sections instead.
- **Recommended:** a new `## Soft-Blocked Models` subsection in `model-
  selection.md`, an extended Model check bullet in `ailly/SKILL.md`, and
  one new feature test — the smallest change that satisfies the issue's
  three asks (flag at phase entry, check not gate, no silent inheritance
  on dispatch) without touching the alias/complexity-dimension system
  itself.

## Summary

A small, two-file guardrail addition plus one new contract test: name
`claude-fable-5` as soft-blocked in `model-selection.md` using alias-only
language, extend the `ailly/SKILL.md` Model check bullet to flag it
explicitly and to keep phase-subagent dispatch from silently inheriting it,
and add `developer/tests/test_fable5_softblock.py` to pin this behavior.
Deferred: removing the soft block once Fable 5 reaches judgment parity is
future work, contingent on model quality, not part of this change.

### Open Artifact Decisions

**Heading/placement of the soft-block content in `model-selection.md`:**
whether it is its own `## Soft-Blocked Models` section (this design's
choice) versus a subsection folded under Frontier-Model Caution.
Proposed: a separate top-level `##` section, adjacent to Frontier-Model
Caution, since the two check different things (unproven-new vs.
known-regressed) even though they share the check-not-gate posture.

**Test file name/path:** `developer/tests/test_fable5_softblock.py` is not
prescribed by any skill template; it follows the existing sibling files'
naming convention (`test_<topic>.py`, flat under `developer/tests/`) but
the exact name is this design's choice, not a derived requirement.
Proposed: keep the name above; it reads clearly next to
`test_subagent_model_mandate.py`, which it extends in spirit without
editing.

## Feature Test

**User story:** Given a developer running `developer:ailly` on a harness
currently reporting `claude-fable-5` as the active model, when the
coordinator performs its phase-entry Model check and later dispatches a
phase subagent, then the check names Fable 5 as soft-blocked with a reason
and an un-block condition, recommends `sonnet` or `opus` via `/model`,
continues the loop regardless of the developer's choice, and does not let
a dispatched phase subagent silently inherit the soft-blocked model.

**Test path:** `developer/tests/test_fable5_softblock.py`

This is a contract check on the source-of-truth files (mirroring
`test_subagent_model_mandate.py`'s shape): it asserts `general/skills/
dispatching-agents/model-selection.md` carries a soft-block section naming
`claude-fable-5`/"Fable" with a reason and removal condition, phrased with
bare aliases (not dated versions, so it cannot trip the sibling test's
staleness check); and that `developer/skills/ailly/SKILL.md`'s Model check
bullet names the soft block, keeps the existing "check, not a gate"
language, and states dispatch does not silently inherit a soft-blocked
model. It needs no model and no pytest, and exits 0 (all rules hold) or 1
with a single reason line. It starts RED: today neither file mentions
`claude-fable-5`, "Fable", or a soft block at all.
