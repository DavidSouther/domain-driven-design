# Research: Soft-block Fable 5 in the Ailly model check

## Topic and Intent

Fable 5 (`claude-fable-5`) is too literal in judgment when acting as Ailly
coordinator or phase-runner: in a stellar_commander session it applied a
stored "always PR a session branch on first push" feedback rule verbatim to
a Figma-design-only session, opening an unwanted PR instead of recognizing
the rule's intent was scoped to code-bearing branches. Issue #29 asks for a
soft block — a check, not a gate — on Fable 5 for these roles until it
reaches Sonnet 4.6 / Opus 4.8 quality on applying stored feedback with
judgment. The issue's suggested mechanism targets
`developer/skills/ailly/references/checks/model-per-phase.md`, but that file
no longer exists; it must be reconciled against whichever file replaced it.

## Search/Expand

No external prior art applies here — this is an internal process-guardrail
change scoped entirely to this repo's own Ailly skill and its dispatch
guidance. No adjacent library or public project is relevant.

## Libraries & Skills

Before doing any work in this feature, load these skills via the active
harness's skill-loading mechanism: `developer:ailly` (owns the phase-entry
model check and subagent dispatch this issue modifies) and
`general:dispatching-agents` (owns `model-selection.md`, the file that now
carries what used to live in `model-per-phase.md`). No other library or
framework skill applies; this is a documentation/guardrail change with no
third-party dependency.

## Falsification/Refine

**Size:** a small documentation/guardrail change — edits to two reference
files plus one existing feature test, not a new feature or a bug fix in
application code. No off-the-shelf tool applies; this is bespoke process
guidance for this repo's own coordinator skill.

**Reconciliation finding (the key refine result):** `model-per-phase.md` was
removed in commit `701affe` ("Move subagent model selection to general
dispatching guidance", #32) and its content generalized into
`general/skills/dispatching-agents/model-selection.md`. That commit was a
deliberate architectural shift, not a rename:

- The old file pinned dated model names per phase (e.g. "Sonnet 4.6",
  "Opus 4.8", "Haiku 4.5"). The new file explicitly forbids that: "Express
  this as a bare alias, never a dated pinned version" (`opus`/`sonnet`/
  `haiku`), because a pinned version "is frozen the day it is written and
  goes stale the moment the provider ships a new generation."
- `developer/tests/test_subagent_model_mandate.py` (current, passing)
  enforces this at T2: it fails if the general guidance file hardcodes
  `"Haiku 4.5"`, `"Opus 4.8"`, or `"Sonnet 4.6"` as a durable recommendation.
  The one permitted dated artifact is a single, visibly-stamped "as of
  <date>" example table (T3), which the new file keeps ("Principle →
  Provider Example (as of 2026-07-03)").
- The phase-entry model check itself now lives inline in
  `developer/skills/ailly/SKILL.md` under a `**Model check.**` bullet
  (around line 190), not in a separate checks file: "Detect the running
  model and compare it to the model the guidance recommends for the
  dispatch about to happen... This is a check, not a gate." It points at
  `general/skills/dispatching-agents/model-selection.md` for the
  substance.
- `developer/tests/test_model_per_phase.py` and
  `test_phase_guardrails.py` (the pre-issue #32 contract tests) are already
  retired/removed, confirming the old file and its phase-keyed table are
  fully gone, not merely deprecated in place.

**Implication for design:** the issue's suggested mechanism ("add a soft-
block list... initially claude-fable-5") must attach to
`general/skills/dispatching-agents/model-selection.md` (the Frontier-Model
Caution section already gates *new/high-benchmark* models behind an eval
suite — a soft-block is the mirror case, gating a *known-regressed* model
out) and to the inline "Model check" bullet in `developer/skills/ailly/
SKILL.md`, not to a revived `model-per-phase.md`. The soft-block should name
the blocked model literally (`claude-fable-5` / "Fable") since that is
identifying a specific known-bad model, not recommending a specific dated
"good" one — so it does not reintroduce the T2 staleness problem the
mandate test guards against, and the design should confirm the wording it
adds does not trip that regex (it currently only matches the three retired
strings, so this is safe, but future edits to model-selection.md should
keep the blocked-model list separate from the "recommended" language).

**Smallest version that meets intent:** add a short "Soft-Blocked Models"
subsection to `model-selection.md` (list: `claude-fable-5` / "Fable", with
the stated reason and un-block condition), extend the SKILL.md Model check
bullet to consult it and to flag-not-satisfy on a match, and add one
assertion to `test_subagent_model_mandate.py` (or a small new test) pinning
the soft-block language and the "check not gate" behavior. No new file, no
revived deleted file.

## Scope

**In scope for design:**
- Soft-block list/subsection in `general/skills/dispatching-agents/
  model-selection.md` naming `claude-fable-5` ("Fable") with rationale and
  removal condition (parity with Sonnet 4.6/Opus 4.8 on applying stored
  feedback with judgment, not just its letter).
- Wording change to the "Model check" bullet in `developer/skills/ailly/
  SKILL.md` so a soft-blocked model is flagged explicitly rather than
  treated as satisfying/exceeding the phase recommendation.
- Ensuring phase-subagent dispatch does not silently inherit a soft-blocked
  model — dispatch should prefer the recommended alias for the phase per
  existing mandate-with-announce behavior, which already sets the model
  where the harness allows; the soft block is an additional check layered
  on that existing mechanism, not a new dispatch pathway.
- Test coverage: extend or add to `developer/tests/test_subagent_model_
  mandate.py` (or a sibling test file) for the soft-block behavior.

**Out of scope for design:**
- Reviving `model-per-phase.md` or any dated per-phase table structure.
- Any change to the alias-based selection principle itself.
- Automated detection/enforcement beyond a documented check (this stays a
  check, not a gate, per the issue's own explicit instruction).
- Removing the soft block (future work, contingent on Fable 5 quality
  parity — not this session's concern).

## Resolved Decisions

- **Resolved:** the target file for the soft-block mechanism is `general/
  skills/dispatching-agents/model-selection.md` plus the inline Model check
  bullet in `developer/skills/ailly/SKILL.md`, not a revived
  `model-per-phase.md`. Decided here (no human available in quickloop mode)
  because the file-removal history and the passing `test_subagent_model_
  mandate.py` unambiguously establish this as the current architecture.
- **Resolved:** the soft-block must name the model literally
  (`claude-fable-5` / "Fable") rather than in complexity-dimension terms,
  because it identifies a specific regressed model instance, which is a
  different concern from the alias/complexity-dimension recommendation
  system and does not conflict with the T2 anti-staleness guard (that guard
  only targets dated *recommended* model names).
- **Open for design:** the exact prose/placement of the soft-block
  subsection in `model-selection.md` (e.g., its own `## Soft-Blocked
  Models` heading vs. folding into "Frontier-Model Caution") and the exact
  test assertions to add. Left for the design phase's judgment; this is a
  small enough decision that it does not block moving forward.

## Sources

[1] Git commit `701affe`, "Move subagent model selection to general
dispatching guidance (#32)", this repository.
[2] `general/skills/dispatching-agents/model-selection.md`, this
repository, read 2026-07-03.
[3] `developer/skills/ailly/SKILL.md`, this repository, read 2026-07-03.
[4] `developer/tests/test_subagent_model_mandate.py`, this repository, read
2026-07-03 (executed, PASS).
[5] `.ailly/research/2026-07-03-A-llm-model-selection/codebase.md`, prior
research note in this repository documenting the pre-#32 `model-per-
phase.md` system (superseded but useful for contrast).
[6] GitHub issue #29, "Soft-block Fable 5 in the Ailly model-per-phase
check until Sonnet/Opus 4.8 quality parity."
