# Implementation Plan: Soft-block Fable 5 in the Ailly Model Check

**Feature test:** `developer/tests/test_fable5_softblock.py`
**User story:** A developer running `developer:ailly` on a harness reporting `claude-fable-5` gets an explicit soft-block flag (reason + un-block condition + `/model` switch recommendation) from the phase-entry Model check, the loop continues regardless of their choice, and phase-subagent dispatch does not silently inherit the soft-blocked model.
**Steps:**
- [x] Step 0: API surface area
- [x] Step 1: `## Soft-Blocked Models` section in `model-selection.md` (T1, T2, T3)
- [x] Step 2: Extend the Model check bullet in `ailly/SKILL.md` (T4)
- [x] Step 3: Extend the same bullet with the no-silent-inheritance dispatch rule (T5)

**Build phase result:** Feature test `developer/tests/test_fable5_softblock.py`
is green (`PASS: Fable 5 soft-block contract holds`, exit 0). Sibling
regression test `developer/tests/test_subagent_model_mandate.py` remains
green — no dated version strings were introduced into
`model-selection.md`. Committed in three steps on branch
`2026-07-03-A-fable-5-softblock` (local only, no push): the
`## Soft-Blocked Models` section, the Model check bullet's soft-block
flag, and the no-silent-inheritance dispatch sentence.

## Step 0: API surface area

This is a documentation/guardrail change, not application code — there are no
new types, entities, or function signatures to stub. The "surface area" here
is the shape of the two prose edits the feature test pins:

- `general/skills/dispatching-agents/model-selection.md` gains one new `##`
  heading, sibling to `## Frontier-Model Caution`: `## Soft-Blocked Models`
  (stub heading, empty body — content added in Step 1).
- `developer/skills/ailly/SKILL.md`'s existing `- **Model check.**` bullet
  (line ~190) is extended in place — no new heading, no new bullet. Its
  current text stays; new sentences are appended (content added in Steps 2–3).

No code stubs apply; both artifacts are Markdown prose. The feature test
(`developer/tests/test_fable5_softblock.py`) already exists and is RED,
confirmed by running it: `T1 soft-block section: no `## Soft-Blocked
Model(s)` heading found`. It is the fixed target for Steps 1–3; no changes
to the test itself are in scope for this plan.

## Step 1: `## Soft-Blocked Models` section in `model-selection.md`

**Enables:** T1 (section exists, names `claude-fable-5` and "fable"), T2
(reason + un-block/parity language), T3 (recommends `sonnet`/`opus` by bare
alias, no dated version strings).

Add a new top-level section directly after `## Frontier-Model Caution`,
matching that section's tone and staying alias-only per this file's own
rule (design.md Specification: this can never trip
`test_subagent_model_mandate.py`'s T2 staleness check, which only scans for
the three retired dated strings).

Content to cover, in prose (no code):
- Name the blocked model both ways: `claude-fable-5` and its nickname
  "Fable" (T1 requires both strings, case-insensitively, in the section body).
- State the reason: it applies stored feedback too literally, missing the
  intent behind a rule rather than just its wording (must include one of
  "literal" / "intent" / "judgment" — cite the stellar_commander PR incident
  from design.md in one line, as prior art already frames it).
- State the un-block condition: parity with `sonnet`/`opus`-tier judgment
  on that same point (must include "parity" or "comparable").
- State the recommendation: switch via `/model` to `sonnet` or `opus` (bare
  alias only — must not contain "sonnet 4.6", "opus 4.8", or "haiku 4.5").
- Cross-reference `## Frontier-Model Caution` in one sentence to distinguish
  the two (unproven-new model vs. known-regressed model), per design.md's
  rejected-alternative note that they should stay adjacent, not merged.

**Tests**

No new automated test — this step targets existing T1–T3 in
`test_fable5_softblock.py`.

```
test "T1-T3 hold after step 1":
  run developer/tests/test_fable5_softblock.py
  assert failure reason has moved past T1/T2/T3 (now fails at T4, or passes if T4/T5 already satisfied)
```

- Edge case: heading regex `Soft-?Blocked Models?` must match — use the
  literal heading `## Soft-Blocked Models` (plural, hyphenated) to be safe.
- Edge case: do not let "sonnet" or "opus" appear only inside a larger word
  that a case-insensitive substring check would still catch correctly (not
  a real risk here, but keep the recommendation sentence explicit: "switch
  to `sonnet` or `opus`").
- Edge case: avoid accidentally including "Sonnet 4.6" or "Opus 4.8" if
  copying phrasing from the issue body verbatim — the issue's suggested
  message names dated versions; this section must not.

**Implementation Outline**

```
insert after "## Frontier-Model Caution" section's closing line, in model-selection.md:

## Soft-Blocked Models

<one paragraph: name claude-fable-5 / "Fable", the literal-rule-vs-intent
failure mode citing the stellar_commander incident, the parity condition
for lifting the block, and the switch-via-/model-to-sonnet-or-opus
recommendation, plus a one-line cross-reference to Frontier-Model Caution>
```

## Step 2: Extend the Model check bullet — name the soft block

**Enables:** T4 (Model check bullet mentions "soft" + "block", names
"fable", and keeps "check, not a gate" / "check not a gate" wording).

Edit the existing `- **Model check.**` bullet in `developer/skills/ailly/
SKILL.md` in place (do not add a new bullet or heading). Append a clause
(or a new sentence within the same bullet) stating: when the detected
running model matches the soft-block list, the check names Fable
explicitly and flags it rather than treating the match as satisfying the
phase's recommendation. Preserve the bullet's existing "This is a check,
not a gate" sentence verbatim (T4 checks for that exact phrase, case
insensitive) — do not paraphrase it away while editing around it.

**Tests**

No new automated test — this step targets T4 in
`test_fable5_softblock.py`.

```
test "T4 holds after step 2":
  run developer/tests/test_fable5_softblock.py
  assert failure reason has moved past T4 (now fails at T5, or passes if T5 already satisfied)
```

- Edge case: the bullet regex `^-\s+\*\*model check\.\*\*.*$` only matches
  the first line of the bullet (non-DOTALL) — make sure "soft", "block",
  "fable", and "check, not a gate" all land on that same first line, not a
  wrapped continuation line, or restructure the bullet as one long line/
  paragraph so the regex's single-line match still captures the new text.
- Edge case: keep "check, not a gate" and "fable" both inside the Model
  check bullet specifically, not merely somewhere else in `SKILL.md`
  (T4 scopes its checks to `model_check_bullet`, not the whole file).

**Implementation Outline**

```
edit developer/skills/ailly/SKILL.md, the "- **Model check.**" bullet:

- **Model check.** Detect the running model and compare it to the model
  the guidance recommends for the dispatch about to happen. On a mismatch,
  say so explicitly; set the model directly where the dispatch call
  supports it, and announce the choice either way. When the detected model
  matches the soft-blocked list in `model-selection.md` (initially Fable /
  claude-fable-5), flag it by name instead of treating the match as
  satisfying the recommendation. This is a check, not a gate — the loop
  never stalls. <continue with Step 3's dispatch sentence> Consult
  `general/skills/dispatching-agents/model-selection.md` for the selection
  principle, the complexity-dimension guidance, the soft-block list, and
  the dated example table.
```

## Step 3: No-silent-inheritance on phase-subagent dispatch

**Enables:** T5 (the same bullet states dispatch does not silently inherit
a soft-blocked model, and prefers the phase's recommended model/alias
instead).

Within the same Model check bullet edited in Step 2 (not a new bullet —
design.md's Specification calls this "the same bullet or its immediate
surrounding dispatch text"), add one sentence: a soft-blocked model is not
silently inherited by a dispatched phase subagent; dispatch prefers the
phase table's recommended alias, per the existing mandate-with-announce
rule in `## Phase Isolation`.

**Tests**

No new automated test — this step targets T5, the last failing check in
`test_fable5_softblock.py`. After this step the whole feature test should
be green.

```
test "feature test green after step 3":
  run developer/tests/test_fable5_softblock.py
  assert exit code 0
  assert stdout == "PASS: Fable 5 soft-block contract holds"
```

- Edge case: T5 requires one of "not inherit" / "does not inherit" / "not
  silently inherit" AND one of "prefer" / "recommended model" /
  "recommended alias" in the same bullet text — use both phrase families
  explicitly rather than paraphrasing (e.g. "does not silently inherit...
  prefers the phase's recommended alias").
- Edge case: re-run the full `developer/tests/test_fable5_softblock.py`
  and `developer/tests/test_subagent_model_mandate.py` after this step —
  the new prose must not accidentally introduce "Sonnet 4.6"/"Opus 4.8"/
  "Haiku 4.5" anywhere in `model-selection.md`, which would break the
  sibling mandate test's T2.

**Implementation Outline**

```
append within the Model check bullet, after the soft-block flag sentence
from Step 2:

  ... A dispatched phase subagent does not silently inherit a
  soft-blocked model; dispatch prefers the phase table's recommended
  alias instead, per the mandate-with-announce rule above.
```

## Notes for the Build phase

- No third-party libraries or frameworks apply (research.md, Libraries &
  Skills: `developer:ailly` and `general:dispatching-agents` are the two
  skills to have loaded; both are already active in this session lineage).
- Run `developer/tests/test_fable5_softblock.py` after each step to confirm
  incremental progress (it prints the first failing check by name); run
  `developer/tests/test_subagent_model_mandate.py` after Step 1 and Step 3
  as a regression check against the shared staleness rule (T2) and the
  Phase Isolation section (T5–T7 there are unaffected by this change but
  cost nothing to re-verify).
- No unit tests beyond the feature test itself are warranted: this is a
  two-file prose contract with one already-written contract test: writing
  a second, narrower unit test per step would just re-check substrings the
  feature test already covers.
