# Implementation Plan: Developer Plugin Structural Refactor (five-phase shape)

**Feature test:** `developer/e2e/ci.sh`
**User story:** An operator runs `developer:ailly` for a topic and is routed through Research, Design, Plan, Build, Cleanup with draft gates after research, design, and plan, and the developer e2e harness proves the new routing and output shapes while the falsification gate holds (`improved > 0`, `regressed == 0`).

**Feature-test phase skipped (user decision, 2026-06-12).** No freestanding `feature-test.md` is written. The `developer/e2e/` harness is the acceptance test, and reworking it (design Specification group 8) is folded into the steps below rather than written first. Regressions are caught by `ci.sh`.

**Steps:**
- [ ] Step 0: Domain model (not applicable; see note)
- [x] Step 1: Add the Research phase and pivot the invocation/baseline suite from feature-test to research
- [x] Step 2: Merge feature-test into design and retire the feature-test skill
- [x] Step 3: Remove is-clean and git-workflow, elevate Cleanup to the terminal phase
- [x] Step 4: Finalize five-phase coordination, add the bugfix reference and quick-loop mode, drive ci.sh green

---

## Step 0: Domain model (not applicable)

This refactor introduces no code-level domain objects, so there is no entity, value object, or service to define ahead of the slices. The closest analog to "type definitions" for a skills refactor is the pair of contracts the harness scores: the per-skill frontmatter `description` (the routing surface the model selects from, vended into `disclosure.md`) and the structural check-script rules under `developer/e2e/evals/scripts/`. Those contracts cannot all land first, because two hard harness constraints couple each contract to the skill it scores:

- **HC1 (matrix load).** `assemblies/invocation.yaml` and `assemblies/baseline.yaml` load `context/skills/{{ skill }}/SKILL.md` for every name in their `matrix.skill`. A matrix name with no `SKILL.md` makes `ailly assemble` fail outright, so a skill must exist before its matrix entry, and a matrix entry must be removed before its skill directory is deleted.
- **HC2 (counts).** `ci.sh` `expected_count` asserts invocation 9, baseline 9, discovery 8 at every run. Each step keeps those exact counts, so additions and removals are swapped in the same step rather than staged.

Each step below therefore carries its own contract changes (frontmatter description, check script, matrix entry, judge prompt) as a vertical slice. Every step boundary leaves all three suites assembling at 9/9/8 with no missing-skill load. Intermediate steps may leave some `ci.sh` assertions red; the suite is fully green only after Step 4.

The path from red to green is a direct sequence, so no forward-backward map files are needed.

---

## Step 1: Add the Research phase and pivot the invocation/baseline suite from feature-test to research

**Enables:** the new `research` invocation assertion (`check_research.py` plus the research judge) passes in the invocation arm and fails in the baseline arm, keeping the falsification gate satisfiable; the retired `feature-test` invocation assertion is removed. Counts stay 9/9/8.

Create the new skill body and its harness wiring as one count-balanced swap (research in, feature-test invocation out).

**New skill `developer/skills/research/SKILL.md`** (delegating coordinator, design group 1). Frontmatter contract only at plan time:

```yaml
---
name: research
description: >-
  Use when a development topic is vague and nothing has been gathered yet.
  Drives research:using-research with a dual lens (software-engineering
  practice generally, plus this exact task and codebase): an expand pass for
  supporting complaints and complementary work, then a refine pass that asks
  whether this is a bug rather than a feature, whether an off-the-shelf tool
  already does it, and what the smallest version is. Writes research.md as a
  draft and stops at the gate.
---
```

The description must route a vague, nothing-gathered prompt here and away from `design` (the `research-vs-design` discovery case added in Step 2 scores this). Body documents the six-step behavior from design group 1 (open or continue the session folder; drive an expand brief on the general lens; drive a refine brief on the specific lens; write `research.md` with sections Topic and Intent, Search/Expand, Falsification/Refine, Scope, Resolved Decisions, Sources, marked `*Draft YYYY-MM-DD*`; cite the `research:configuring-*` wiring contract rather than re-teaching source setup, and warn if MCP research sources are insufficient; stop at the draft gate). It delegates research mechanics to `research:using-research`; it does not re-implement search or falsification.

**Harness wiring (the swap):**
- `evals/scripts/check_research.py` (new). Rule contract, no implementation logic at plan time:
  - R1: the `research.md` section headings are present (Topic and Intent, Search/Expand, Falsification/Refine, Scope, Resolved Decisions, Sources).
  - R2: the `*Draft YYYY-MM-DD*` marker is present.
  - Reuse `_checker_utils.has_heading` / `has_draft_marker`, mirroring `check_design.py`.
- `prompts/invocation/research.md` (new): a vague, nothing-gathered topic prompt that asks the operator to run the research phase.
- `assemblies/invocation.yaml` and `assemblies/baseline.yaml`: in `matrix.skill`, replace `feature-test` with `research`.
- `evals/invocation.yaml` and `evals/baseline.yaml`: remove the `feature-test` case, add a `research` case (script `check_research.py`, a judge describing the delegating expand/refine research draft, and a `tokens` ceiling consistent with the neighbors).
- Delete `prompts/invocation/feature-test.md` and `evals/scripts/check_feature_test.py` (its "exactly one executable test" rule moves into `check_design.py` in Step 2).

**Coordinator wiring (additive parts of groups 3 and 4):**
- `developer/skills/ailly/SKILL.md`: replace the stale `developer:brainstorming` / `developer:design-doc` invocations with `developer:research` and `developer:design`; route a vague, new-topic resume point to `developer:research`.
- `developer/skills/using-developer/SKILL.md`: add a `research` routing row and a research draft gate.

**Runnable guarantee:** invocation and baseline assemble at 9 (feature-test out, research in, research skill exists so HC1 holds). Discovery untouched at 8. The `feature-test` skill directory still exists but is no longer in any matrix, so nothing loads a missing body.

---

## Step 2: Merge feature-test into design and retire the feature-test skill

**Enables:** the `design` invocation assertion passes against the new six-section shape and the absorbed one-test rule; the `research-vs-design` and `design-vs-plan` discovery assertions pass. Counts stay 9/9/8.

**Rewrite `developer/skills/design/SKILL.md`** (design group 2):
- Section list becomes the six new names: Purpose, Prior Art, User Journey and Metrics, Specification, Alternatives, Summary ("Problem Statement" becomes "Purpose"; "Metrics" becomes "User Journey and Metrics").
- Absorb the `feature-test` user-story step and its hard gate (write only the test, no implementation). The skill emits one executable feature test in the project test tree (location per `developer:initialize`), and `design.md` records the test path.
- Standardize the output path on the session folder `design.md` (drop the second path the skill names today).
- Keep the `*Draft YYYY-MM-DD*` marker behavior.

**Harness updates:**
- `evals/scripts/check_design.py`: `SECTIONS` becomes the six new names; add the absorbed rule from the deleted `check_feature_test.py`, that the design contains exactly one executable test function (`\bdef\s+test\w*\s*\(` counted over code blocks equals one). Update the module docstring to trace to the new section list.
- `evals/invocation.yaml` and `evals/baseline.yaml`: rewrite the `design` judge prompt to name the six new sections and to require the embedded single feature test as a draft, without the implementation.
- `prompts/invocation/plan.md`: update so the scenario reflects the merged world (a cleared `design.md` that records the test path plus a failing project feature test), rather than a separate cleared `feature-test.md`. This is a fidelity edit implied by group 2; confirm `check_plan.py` and the plan judge still hold against the revised prompt.

**Discovery swap (group 8, feature-test pairs out, design pairs in):**
- `assemblies/discovery.yaml` `matrix.case`: remove `design-vs-feature-test` and `feature-test-vs-plan`; add `research-vs-design` and `design-vs-plan`.
- `evals/discovery.yaml`: remove the two feature-test cases; add `research-vs-design` (a vague idea, nothing gathered, asserts `developer:research` and not `developer:design`) and `design-vs-plan` (a cleared design, asserts `developer:plan` and not `developer:red-green-refactor`).
- Create `prompts/discovery/research-vs-design.md` and `prompts/discovery/design-vs-plan.md`; remove `prompts/discovery/design-vs-feature-test.md` and `prompts/discovery/feature-test-vs-plan.md` from the matrix (count stays 8).

**Delete `developer/skills/feature-test/`** (safe now: HC1 holds because `feature-test` left every matrix in Step 1).

**Coordinator updates:** in `ailly` and `using-developer`, the `design` row notes it now includes the feature test, and the separate feature-test gate is removed from the loop graph and the draft-gate table (folded into design).

**Plan trigger touch-up (group 6):** `developer/skills/plan/SKILL.md` trigger changes from "feature-test draft cleared, reads `feature-test.md`" to "design draft cleared, reads `design.md` plus the project feature test."

**Runnable guarantee:** all three suites assemble at 9/9/8. `disclosure.md` no longer lists `feature-test`; the discovery matrix no longer references it, so the dropped routing target leaves no red case behind.

---

## Step 3: Remove is-clean and git-workflow, elevate Cleanup to the terminal phase

**Enables:** the `cleanup-vs-refactor` discovery assertion passes; the `is-clean-vs-cleanup` assertion is removed; `disclosure.md` no longer advertises `is-clean` or `git-workflow`. Counts stay 9/9/8.

**Delete `developer/skills/is-clean/` and `developer/skills/git-workflow/`** (design group 5). Neither appears in the invocation or baseline matrix, so deletion is harness-safe under HC1.

**Discovery swap:**
- `assemblies/discovery.yaml` `matrix.case`: remove `is-clean-vs-cleanup`; add `cleanup-vs-refactor`.
- `evals/discovery.yaml`: replace the `is-clean-vs-cleanup` case with `cleanup-vs-refactor` (a finish-the-topic prompt asserts `developer:cleanup`; a tidy-while-green prompt asserts `developer:refactor`; the two are not swapped).
- Create `prompts/discovery/cleanup-vs-refactor.md`; the `is-clean-vs-cleanup.md` prompt leaves the matrix (count stays 8).

**Cleanup elevation (parts of groups 3 and 4):**
- `developer/skills/ailly/SKILL.md`: the loop graph edge `rgr -> stop` becomes `rgr -> cleanup -> stop`; route a finish-the-topic resume point to `developer:cleanup`; state that cleanup pauses for human approval before the squash-merge.
- `developer/skills/using-developer/SKILL.md`: repoint the cleanup routing row from `developer:refactor` to `developer:cleanup` as the terminal phase; remove the `is-clean` and `git-workflow` rows.

**Git opinion (group 5 and 6):** in `ailly`, replace the `developer:git-workflow` citation with a plain branch-suggestion instruction, and carry the one wanted rebase-first / force-with-lease opinion as a single inline line.

**Runnable guarantee:** discovery stays at 8; invocation and baseline untouched at 9. `vendor.sh` regenerates `disclosure.md` from the remaining skills automatically (it loops over skill directories, no hardcoded names).

---

## Step 4: Finalize five-phase coordination, add the bugfix reference and quick-loop mode, drive ci.sh green

**Enables:** the `ailly` invocation assertion passes against the new resume table and loop names; the full `developer/e2e/ci.sh` runs green end to end with the hygiene grep passing for the new `research` identifier and the falsification gate holding (`improved > 0`, `regressed == 0`). This is the step that makes the feature test pass.

**Five-phase coordination finalization (groups 3 and 4):**
- `developer/skills/ailly/SKILL.md`: resume table and loop graph fully in the five-phase shape (Research, Design, Plan, Build, Cleanup) with draft gates after research, design, and plan, plus the cleanup merge-approval gate; Build loops red-green-refactor per plan step.
- `developer/skills/using-developer/SKILL.md`: loop graph in five phases; draft-gate table lists research, design, plan, and the cleanup merge-approval gate.

**New content (groups 3 and 7):**
- `developer/references/bugfix.md` (new): observed / expected / unchanged language (Kiro model), consulted by `ailly` and `design` when the task is bug-shaped; the reproduction test fills the slot the merged design feature test fills.
- `ailly`: add a Quick-loop mode section (design User Journey, gates auto-clear, minimal artifacts, churns to a green feature test, documents when it fits and what it trades away) and a short bugfix pointer to `developer/references/bugfix.md`.

**Remaining touch-ups (groups 6 and 8):**
- `developer/skills/cleanup/SKILL.md`: fix the `YYYY-MM-DD-AA` double-A session-folder typo. Do not rename any `docs/` path string (those are governed by the deferred Decision 1 sweep, out of scope here).
- `evals/scripts/check_ailly.py` and the `ailly` judge prompt in `evals/invocation.yaml` / `evals/baseline.yaml`: update assertions tied to the old resume table and loop names; the gate-refusal behavior still holds, now phrased against the merged design draft gate.
- Confirm (no edit expected) that `vendor.sh` prunes nothing by name; verified generic during planning.

**Final verification (the green run):**
- Run `bash developer/e2e/ci.sh` with a live model available (`ANTHROPIC_API_KEY` or `developer/e2e/.env`).
- Confirm: all three suites assemble at 9/9/8; the hygiene grep over `context/AGENTS.md` and `profile.md` passes (no `developer:<skill>` identifier leaks, including `research`); the discovery report lands; the comparison reports `improved > 0` and `regressed == 0`.

**Runnable guarantee:** this step only edits coordinator prose, the bugfix reference, the cleanup typo, and the `ailly` checker; counts are unchanged. On completion the feature test (`ci.sh`) is green.

---

## Notes for the Build phase

- Every changed line traces to a design Specification group: Step 1 to groups 1, 3, 4, 8; Step 2 to groups 2, 6, 8; Step 3 to groups 5, 3, 4, 8; Step 4 to groups 3, 4, 6, 7, 8.
- Deferred and out of scope (design Summary): the `docs/` to `.ailly/` rename (Decision 1) and retiring the `ddd` identifier (Decision 9). Leave all `docs/` path strings untouched.
- Each Build step ends by assembling all three suites to confirm 9/9/8 and no missing-skill load before moving on; the full live `ci.sh` green run belongs to Step 4.
