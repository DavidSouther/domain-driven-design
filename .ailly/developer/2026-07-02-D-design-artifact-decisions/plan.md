# Implementation Plan: Surface Novel Artifact Choices as Open Artifact Decisions

**Feature test:** `developer/e2e/evals/scripts/check_design_artifacts.py` (exists, frozen), driven end to end through the `design-artifacts` / `design-artifacts-baseline` suite pair and gated by `developer/e2e/ci.sh` `report_comparison` (improved>0, regressed==0).
**User story:** Given a settled design task requiring an invented artifact (a machine-readable disposition record whose name and format nothing prescribes), when the design phase writes the draft, then the draft carries an **Open Artifact Decisions** section surfacing that artifact, and the draft-gate message points the human at it.
**Run:** `bash developer/e2e/ci.sh` (needs a live model); targeted RED/GREEN check per step via `ailly -p developer/e2e assemble/run/eval/report` on just the pair.
**Target files:** `developer/skills/ailly/references/phases/design.md` (the only skill-reference edit) plus new harness files under `developer/e2e/` (one prompt, two assemblies, two evals) and `developer/e2e/ci.sh` call sites.
**Libraries & Skills:** none (carried forward from research and design — no external libraries or framework skills; no skill-load directive for the build phase).
**Map:** `maps/suite-pair-path.md` (forward-backward path; fixes the build order harness-first, reference-edit-last, so RED is demonstrated end to end before the edit flips it GREEN).

**Steps:**
- [x] Step 0: API surface area (edit sites and file slots)
- [x] Step 1: The planted-artifact prompt
- [x] Step 2: The assembly pair
- [x] Step 3: The eval pair
- [ ] Step 4: ci.sh wiring and the end-to-end RED
- [ ] Step 5: The design.md reference edits — GREEN

## Step 0: API surface area

This is a documentation-plus-harness feature; there is no runtime code. The "API surface" is (a) the four edit sites in `developer/skills/ailly/references/phases/design.md` fixed by the cleared design and (b) the file set of the suite pair, whose paths the design's Open Artifact Decisions section settled. The checker `developer/e2e/evals/scripts/check_design_artifacts.py` already exists in the working tree (R1–R3 mirrored from `check_design.py`, R4 the load-bearing new rule) and is treated as frozen; no step edits it.

**Correction applied during build:** `check_design_artifacts.py` was not actually present in the working tree at the start of this step, contrary to the text above; it was authored in this step per design.md's "The Feature Test" specification (R1–R3 mirrored from `check_design.py`, R4 added reading the assistant turn from stdin and asserting an "Open Artifact Decisions" heading via `_checker_utils.has_heading`) and is now frozen for later steps.

**Patterns beat (`patterns:using-patterns`):** consulted; no catalog code pattern applies — the deliverables are reference prose, YAML suite definitions, and one shell wiring change, with no primitives to wrap, boundaries to parse, or failure signalling to type. Two analogues orient the work without being applied as code patterns: **arrange-act-assert** is the suite shape itself (prefix arranges the loaded bodies, `run` acts, `eval` asserts), and **triangulate** is the falsification gate's logic (the baseline arm forces the reference to be the real cause of the behavior, not the prompt).

File and edit-site stubs (slots only; final wording is re-derived during build):

```text
developer/e2e/prompts/invocation/design-artifacts.md      <- Step 1 (new)
developer/e2e/assemblies/design-artifacts.yaml            <- Step 2 (new)
developer/e2e/assemblies/design-artifacts-baseline.yaml   <- Step 2 (new)
developer/e2e/evals/design-artifacts.yaml                 <- Step 3 (new)
developer/e2e/evals/design-artifacts-baseline.yaml        <- Step 3 (new)
developer/e2e/ci.sh                                       <- Step 4 (edit: expected_count,
                                                             globals, set/get_run_dir,
                                                             assemble/run/eval calls,
                                                             report_comparison)
developer/skills/ailly/references/phases/design.md        <- Step 5 (edit, four slots):
  S1 Checklist: new step between current 5 (write draft) and 6 (write feature
     test); renumber 6-8 to 7-9
  S2 "Design Docs" section list: add Open Artifact Decisions as a named,
     optional section (empty or omitted when no novel artifacts exist)
  S3 "Writing the design" (The Process): trigger definition (not prescribed by
     skill template / project convention / cleared research.md) and the
     **<artifact>:** ... Proposed: ... entry format
  S4 "After the Design" user-review-gate message: one added line pointing the
     human at the Open Artifact Decisions section
```

Invariants every step preserves: the six-section design-doc core is unchanged (the new section is additional and optional, so `check_design.py` R1 and the existing `invocation-phases` design case keep passing); the long-loop recording format, the other phase references, and the checker file are untouched; the ci.sh hygiene targets (`context/AGENTS.md`, `profile.md`) are not edited, so the answer-leak gates stay meaningful.

**Enables:** nothing directly; the pair does not exist yet. It fixes where each of steps 1–5 lands.

## Step 1: The planted-artifact prompt

**Enables:** the shared user turn both arms consume; prerequisite for every checker rule to be measured at all. R1–R3 pass on both arms only if this prompt demands a well-formed design; R4's falsification signal exists only if this prompt does not leak the answer.

Write `developer/e2e/prompts/invocation/design-artifacts.md` in the same self-contained, "produce the finished design now" style as `prompts/invocation/design.md`: requirements settled, research treated as cleared, six named sections, exactly one embedded executable feature test with its path noted, whole reply marked draft, no tool calls, no clarifying questions, no stopping for approval. The task it describes must require an invented artifact: a machine-readable disposition-record file whose filename and format no skill template, project convention, or prior research prescribes (the design's planted scenario). Two hard constraints on wording: it must state that nothing prescribes the record's name or format (so the artifact is genuinely novel, not derived), and it must never name "Open Artifact Decisions," "open decisions," or any surface-this-choice instruction — the baseline arm reads the identical prompt, and a leak makes improved==0 or vacuous.

**Tests**

Happy path: the answer-leak check on the new prompt.

```bash
grep -ci "open artifact" developer/e2e/prompts/invocation/design-artifacts.md
# expect: 0 (grep exits 1); the prompt plants the scenario without naming the section
```

- Edge: prompt must not instruct the model to "flag," "surface," or "leave open" the artifact choice in any phrasing — that is the behavior under test, not part of the stimulus.
- Edge: prompt must still force R1–R3 compliance (six sections, draft marker, exactly one `def test...`) or the baseline arm fails R1 first and R4 is never the differentiator.
- Edge: the planted artifact must not coincide with a real project convention (avoid names like `package.json`); the disposition-record framing from the design keeps it convention-free.

**Implementation Outline**

```text
prompts/invocation/design-artifacts.md:
  paragraph 1 = the tool/feature scenario + the disposition-record requirement
                ("a machine-readable record of ... ; no existing convention or
                 prior research fixes its filename or format")
  paragraph 2 = the standing instructions block, copied in substance from
                design.md prompt: settled requirements, six sections, one
                pytest feature test + its path, draft marker, inline reply,
                no tools, no questions, no approval stops
```

## Step 2: The assembly pair

**Enables:** `ailly assemble design-artifacts` / `... design-artifacts-baseline` each producing exactly one conversation file — the arrange half of the feature test.

Write `developer/e2e/assemblies/design-artifacts.yaml` and `design-artifacts-baseline.yaml`, mirroring the `long-loop` pair mechanically (single conversation, no matrix — the design records why the `invocation-phases` matrix cannot carry a second design prompt). The invocation arm's prefix loads `context/AGENTS.md`, `profile.md`, then `kind: external` bodies `../skills/ailly/SKILL.md` and `../skills/ailly/references/phases/design.md`, all `cache: true`; the baseline arm drops both external bodies and keeps AGENTS.md + profile.md, so the only difference between arms is the loaded coordinator + phase reference. Both use `model: claude-sonnet-4-6` and the conversation `user: prompts/invocation/design-artifacts.md`, `assistant:` blank. Carry a header comment in each file stating why this is a dedicated pair (mirrors the long-loop.yaml comment discipline).

**Tests**

Happy path: assemble the pair and count conversation files.

```bash
ailly -p developer/e2e assemble design-artifacts-baseline
ailly -p developer/e2e assemble design-artifacts
ls developer/e2e/runs/*-design-artifacts/*.yaml | wc -l           # expect 1
ls developer/e2e/runs/*-design-artifacts-baseline/*.yaml | wc -l  # expect 1
```

- Edge: if `ailly` is unavailable in the build environment, fall back to YAML-parse validation plus field-by-field diff against `long-loop.yaml` / `long-loop-baseline.yaml`; record that assemble verification is deferred to Step 4's ci.sh run.
- Edge: the baseline arm must keep the identical prompt path — a divergent prompt breaks attribution of the behavior gap to the reference.
- Edge: the external path is `../skills/ailly/references/phases/design.md` (relative to the e2e project dir), matching the `invocation-phases.yaml` path family exactly.

**Implementation Outline**

```text
assemblies/design-artifacts.yaml          = long-loop.yaml with the second external
                                            swapped to references/phases/design.md
                                            and prompt swapped to design-artifacts.md
assemblies/design-artifacts-baseline.yaml = long-loop-baseline.yaml with the prompt
                                            swapped to design-artifacts.md
```

**Correction applied during build:** the `ailly` CLI was unavailable in this build environment, so the Edge case fallback was used — YAML-parse validation of both new files plus a field-by-field diff against `long-loop.yaml`/`long-loop-baseline.yaml` confirmed only the intended swaps (external path and prompt path); live `ailly assemble` verification is deferred to Step 4's ci.sh run.

## Step 3: The eval pair

**Enables:** `ailly eval` scoring both arms with the frozen checker — the assert half of the feature test; after this step the checker is actually executed against model output.

Write `developer/e2e/evals/design-artifacts.yaml` and `design-artifacts-baseline.yaml`, mirroring the long-loop eval pair: one case per file, the **same case name on both sides** (the comparison matches same-named cases), and **identical assertion lists** in both files. Assertions: (1) the script assertion `{ type: script, runtime: python, script: { path: evals/scripts/check_design_artifacts.py } }` — the load-bearing one; (2) a judge assertion describing a well-formed six-section design draft with one embedded feature test that additionally surfaces the planted disposition-record artifact in an Open Artifact Decisions section (proposed choice plus alternatives) instead of settling its name and format silently in prose; (3) the token budget `{ type: tokens, metric: output, op: "<", value: 7000 }`, matching the existing design case budget (a design doc plus one extra section; the 6000 long-loop budget is too tight).

**Tests**

Happy path: eval the assembled runs and confirm a report lands per arm.

```bash
ailly -p developer/e2e eval design-artifacts --over developer/e2e/runs/<id-design-artifacts>/ || true
# expect: evals/reports/<id>.json exists; script assertion recorded (pass or fail, not errored)
```

- Edge: the case name must be identical in both files (propose `design-artifacts`); a mismatch silently yields an empty comparison and a vacuous gate.
- Edge: the script path is project-relative (`evals/scripts/...`) exactly as the nine existing suites write it, so `_checker_utils` imports resolve the same way.
- Edge: "errored" vs "failed" — if the eval report shows the script assertion errored (stderr written, bad path), the checker was not exercised; fix wiring before reading pass/fail.
- Edge: judge prompt is identical on both arms (long-loop precedent) so the judge differentiates on behavior, not on wording drift between files.

**Implementation Outline**

```text
evals/design-artifacts.yaml (and -baseline, identical but for `name:`):
  name: design-artifacts[-baseline]
  cases:
    - name: design-artifacts
      assertions:
        - script  -> evals/scripts/check_design_artifacts.py
        - judge   -> six-section draft, one feature test, AND an Open Artifact
                     Decisions section surfacing the planted record file with a
                     proposal and alternatives; not settled silently in prose
        - tokens  -> output < 7000
```

## Step 4: ci.sh wiring and the end-to-end RED

**Enables:** the full feature-test loop runs end to end and fails for the right reason — the invocation arm (reference not yet edited) fails R4, so `report_comparison` prints improved==0 and the gate FAILs. This is the demonstrated RED that Step 5 flips.

Edit `developer/e2e/ci.sh`: add `design-artifacts` and `design-artifacts-baseline` (expected count 1 each) to `expected_count`; add the two run-dir globals and their `set_run_dir`/`get_run_dir` cases; append `assemble_suite`, `run_suite`, and `eval_suite` calls for both; append `report_comparison "${design_artifacts_baseline_run_dir}" "${design_artifacts_run_dir}" design-artifacts-baseline design-artifacts`. Placement is load-bearing: assemble `design-artifacts-baseline` **after** the plain `baseline` suite (the suffix-anchored `runs/*-baseline/` glob would otherwise pick up the `*-design-artifacts-baseline` dir — same reason long-loop-baseline assembles late); simplest correct placement is after the long-loop pair at the end of each CUJ block. Update the header comment's suite inventory. No change to the hygiene gate: the new prompt is not a baseline-prefix file, and neither hygiene target is edited.

**Tests**

Happy path: syntax first, then the live RED.

```bash
bash -n developer/e2e/ci.sh   # expect: exit 0
bash developer/e2e/ci.sh      # with credentials; expect: FAIL at the design-artifacts
                              # comparison with improved=0 — both arms fail R4;
                              # all pre-existing suites still pass their gates
```

- Edge: the targeted RED can be run cheaper than full ci.sh (assemble/run/eval/report on just the pair with `AILLY_BIN`); record whichever was used.
- Edge: confirm the failure reason is R4 on **both** arms (read the pair's eval reports), not R1/R2/R3 — a baseline R1 failure means the Step 1 prompt under-constrains form and must be fixed before proceeding.
- Edge: `expected_count`'s `*)` fallback exits on unknown suites — both new names must be added or assemble aborts.
- Edge: this step intentionally leaves `ci.sh` RED at the new gate only; every other suite and gate must still pass (that is this step's "runnable state").

**Implementation Outline**

```text
ci.sh:
  expected_count: design-artifacts) echo 1 ;; design-artifacts-baseline) echo 1 ;;
  globals + set_run_dir/get_run_dir: design_artifacts_run_dir, design_artifacts_baseline_run_dir
  after long-loop lines in each block:
    assemble_suite design-artifacts-baseline ; assemble_suite design-artifacts
    run_suite      design-artifacts-baseline ; run_suite      design-artifacts
    eval_suite     design-artifacts-baseline ; eval_suite     design-artifacts
  after the long-loop comparison:
    report_comparison $baseline_dir $invocation_dir design-artifacts-baseline design-artifacts
```

## Step 5: The design.md reference edits — GREEN

**Enables:** checker R4 on the invocation arm, and with it the full feature test: `report_comparison` for the pair prints improved>0 (the invocation arm passes R4 where the baseline cannot) and regressed==0.

Make the four edits to `developer/skills/ailly/references/phases/design.md` fixed by the cleared design (slots S1–S4 from Step 0). S1: a new checklist step between "Write the design doc draft" and "Write the feature test" — identify concrete artifact choices (filenames, locations, schemas, formats) not prescribed by a skill template, project convention, or the cleared `research.md`, and record each in an **Open Artifact Decisions** section of the draft; renumber the later steps. The before-the-test position is load-bearing: the feature test binds to artifacts. S2: add the section to the Design Docs list, marked optional (empty or omitted when no novel artifacts exist) so the six-section core is unchanged. S3: in "Writing the design," define the trigger by the three not-derived-from conditions and give the entry format (`**<artifact name/path>:** <choice and options>. Proposed: <recommendation>.`). S4: append the one review-focus line to the user-review-gate message ("Pay special attention to any **Open Artifact Decisions** section — ... Confirm they fit your intent before clearing the draft."). Wording follows `general/skills/writing-skills/SKILL.md` conventions (imperative verbs, trigger conditions, no process restatement); re-derive exact sentences during build.

**Tests**

Happy path: the full gate goes GREEN.

```bash
bash developer/e2e/ci.sh
# expect: design-artifacts comparison improved>0, regressed==0;
#         baseline-phases vs invocation-phases unchanged (design case still passes)
```

- Edge: regression on the existing `invocation-phases` design case — the edited reference is loaded there too; the jq-lite prompt plants no novel artifact, so a correct edit produces no (or an empty) section and `check_design.py` R1–R3 plus its judge still pass. Confirm from that pair's comparison, not by assumption.
- Edge: the trigger definition must keep derived artifacts out (a test path following framework convention, a manifest already in use) — over-flagging inflates the section and risks the judge on the existing design case.
- Edge: checklist renumbering — steps 6–8 become 7–9 and any in-body references to those step numbers must be swept.
- Edge: the Process Flow dot graph sits between the draft and test nodes; the design's Specification names only the four edits, so leave the graph untouched unless the inserted step makes it actively wrong — if a node is added, it is a consistency edit, not new scope. Note the choice in the build log.
- Edge: S4 edits the quoted gate message only; the surrounding "After the Design" flow (wait, revise, decline implementation) is untouched.

**Implementation Outline**

```text
phases/design.md:
  Checklist: insert step 6 "Surface open artifact decisions" (trigger: not
    prescribed by skill template / project convention / cleared research.md;
    action: record each in an Open Artifact Decisions section); renumber 6-8 -> 7-9
  Design Docs list: "- **Open Artifact Decisions** ... (optional; omit or leave
    empty when every artifact is derived)"
  Writing the design: trigger paragraph + entry format block
  After the Design gate message: + one "Pay special attention to ..." line
```

## Risks and Notes

- **Live-model dependency:** RED (Step 4) and GREEN (Step 5) verification both need credentials; ci.sh has no assemble-only success path by design. Budget one targeted pair run per verification rather than full ci.sh where possible.
- **Answer-leak is the fragile invariant:** the prompt (Step 1) is shared by both arms and is not covered by the existing hygiene grep (which only scans AGENTS.md and profile.md). Any phrasing that names the section or the surfacing behavior quietly destroys the falsification claim. Consider (deferred, out of scope) extending the hygiene gate to grep the pair's prompt for "open artifact."
- **Nondeterministic gate:** improved>0 rides one model sample per arm. If the baseline model spontaneously writes an artifact-decision heading, the gate flakes; the mitigation is the R4 failure message and the judge wording anchored to the exact heading, which unskilled output is unlikely to produce verbatim (the long-loop pair accepts the same risk).
- **Regression surface of the reference edit:** `phases/design.md` is loaded by the `invocation-phases` design case; Step 5's edge checks make that pair's continued pass an explicit verification, not an assumption.
- **Missing beat prompt:** the plan phase reference points at `.ailly/prompts/plan-use-patterns.md`, which does not exist in this repo; the patterns beat was run by consulting `patterns:using-patterns` directly (outcome in Step 0). Same note as the prior session (2026-07-02-C); worth a deferred fix.
- **Checker is frozen:** `check_design_artifacts.py` already exists and no plan step modifies it; if build discovers a checker defect, that is a design-level change and goes back through the gate, not a silent edit.
