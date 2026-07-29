# Implementation Plan: Current model-selection guidance

**Feature test:** `developer/tests/test_subagent_model_mandate.py`
**User story:** A maintainer choosing model candidates after the July 2026 releases sees one current, complexity-first, provider-grounded snapshot whose eval gate, identifier caveats, maintenance policy, cost grounding, and harness limits are explicit and executable.

## Libraries & Skills

Before every red-green-refactor step, load `general:writing-skills`. Before claiming the completed change is ready, load `general:review`.

## Pattern Selection

Apply `arrange-act-assert` when restructuring or extending the executable contract: arrange the relevant Markdown text, act once by extracting the bounded section or table, and assert one focused contract. No new domain objects, primitive wrappers, or lifecycle states are introduced, so `domain-objects`, `newtype`, and `type-states` do not apply.

## Steps

- [x] Step 0: Fix the documentation contract surface
- [x] Step 1: Refresh the central provider snapshot and portability guidance
- [x] Step 2: Add maintenance and Code Mode grounding
- [ ] Step 3: Align harness adapter behavior
- [ ] Step 4: Verify the integrated model-guidance contract

## Step 0: Fix the documentation contract surface

Public documentation schemas and the feature test's executable signature:

```text
ProviderSnapshot(
  reviewed_on: YYYY-MM-DD,
  columns: [Complexity profile, Anthropic, OpenAI, Google,
            Open-weight / self-hosted, Ailly Phases],
  rows: [high, balanced, economy],
)

CandidateCell(
  display_name: provider-documented model family,
  qualifications: zero or more scope, hardware, or exceptional-use cautions,
)

HarnessDispatchContract =
  ConfirmedModelField(accepted_values := active tool schema)
  | AnnounceOnly(reason := no confirmed model-selection field)

CostSnapshot(
  verified_month: YYYY-MM,
  columns: [Model, Input ($/1M), Output ($/1M), Context],
)

developer.tests.test_subagent_model_mandate.main() -> int
```

```text
ProviderSnapshotHeaders =
  [Complexity profile, Anthropic, OpenAI, Google,
   Open-weight / self-hosted, Ailly Phases]

ProviderSnapshotRows = [high, balanced, economy]
```

**Enables**

The bounded `ProviderSnapshot` schema consumed by the existing T2–T5 assertions.

**Tests**

Happy path: the existing feature-test parser returns the six exact `ProviderSnapshotHeaders` cells and the three `ProviderSnapshotRows` tier rows from a conforming bounded table.

- An absent or malformed bounded table fails the contract.
- Missing, extra, or reordered headers fail the contract.
- Unknown or duplicate tier rows fail the contract.

**Implementation Outline**

```text
ProviderSnapshot = DocumentationSchema
CandidateCell = DocumentationSchema
HarnessDispatchContract = DocumentationSchema
CostSnapshot = DocumentationSchema
main() -> int
```

## Step 1: Refresh the central provider snapshot and portability guidance

**Enables:** T2 through T5: the `2026-07-29` review stamp, exact ordered equality for all six provider-table headers, exact high/balanced/economy mappings, Fable and Kimi qualifications, DeepSeek exclusion, eval-first candidate status, and separation of provider availability, API identifiers, and harness dispatchability.

First update `developer/tests/test_subagent_model_mandate.py` so its bounded-table assertion compares the original header cells, in order, for exact equality with `Complexity profile`, `Anthropic`, `OpenAI`, `Google`, `Open-weight / self-hosted`, and `Ailly Phases`. Then update `general/skills/dispatching-agents/model-selection.md` while preserving complexity dimensions, the worked phase example, explicit-human-intent override, and future scoped-eval gate. Replace the stale table with the designed Anthropic, OpenAI, Google, and open-weight/self-hosted candidate mappings. Keep aliases as a harness-level preference while correcting the current overgeneralization that every provider offers a uniformly evergreen bare alias.

**Tests**

Happy path: run the feature test and observe T2–T5 pass before the unchanged T6 maintenance assertion becomes the first failure.

- Fable 5 is exceptional/highest-capability/long-horizon and not automatic.
- Kimi K2.7 Code appears only in the high open-weight cell with hardware and eval qualifications; it is absent from every non-high open-weight cell.
- API-only DeepSeek products appear in a caveat, never in the open-weight column.
- Preview, `latest`, pinned API IDs, and harness aliases are not conflated.
- Any reordered, missing, extra, or differently cased provider-table header fails the exact six-cell comparison.

**Implementation Outline**

```text
preserve the complexity-first selection principle
update the feature test to assert exact ordered equality against all six original header cells
stamp the provider example as reviewed 2026-07-29
replace and expand the bounded Markdown table row by row
assert Kimi K2.7 Code is absent from every non-high open-weight cell
label mappings illustrative and pending future-work evals
add adjacent Fable, open-weight, identifier-lifecycle, and harness caveats
retain the human override and worked Ailly phase mapping
```

## Step 2: Add maintenance and Code Mode grounding

**Enables:** T6 and T7: a bounded periodic-review policy in `DEVELOPMENT.md` and the exact provider-documented July 2026 Opus 5 pricing/context row.

Add one concise maintenance paragraph to `DEVELOPMENT.md` tying periodic review to the dated model-selection example table. Refresh only the cost-grounding snapshot in `developer/skills/ailly/references/shapes/code-mode-thresholds.md`; preserve its threshold decision, cost arithmetic, and worked examples.

**Tests**

Happy path: run the feature test and observe T6–T7 pass, with adapter behavior becoming the next unsatisfied assertion if Step 3 is still pending.

- A generic “review models” statement without the dated example/snapshot table does not satisfy the maintenance contract.
- The cost header remains exactly `Model`, `Input ($/1M)`, `Output ($/1M)`, `Context`.
- The `Opus 5` row is exactly `$5`, `$25`, `1M`.
- T7 locates the cost table header case-insensitively, then compares the original header cells and the `Opus 5` row cells with exact casing and values.
- The existing Fable, Sonnet, and Haiku grounding and Code Mode decision remain internally consistent.

**Implementation Outline**

```text
add one periodic dated-snapshot review paragraph under repository maintenance guidance
change the Code Mode heading text to a July 2026 provider-doc-verified snapshot
replace the older Opus family row with the exact Opus 5 row
update T7 to find the header case-insensitively while preserving exact comparisons against the original cells
recheck dependent cost examples without changing the threshold rule
```

## Step 3: Align harness adapter behavior

**Enables:** T8 while preserving T9–T11: Codex uses only model values advertised by the active dispatch tool schema, Gemini is inspected and remains unchanged unless an actual contradiction or test failure is found, and the existing unconditional mandate-with-announce contract still covers phase and within-phase dispatches.

Edit `developer/skills/ailly/references/agents/codex.md` so its guidance is governed by the active dispatch tool schema; do not infer Codex support from the provider catalog. Inspect `developer/skills/ailly/references/agents/gemini.md` and leave it unchanged unless the central guidance creates an actual contradiction or the feature test demonstrates a failure. Leave `claude.md` unchanged unless the new central identifier terminology would otherwise contradict its confirmed `Task` values.

**Tests**

Happy path: run the feature test and observe T8–T11 pass together.

- A provider-announced OpenAI model absent from the active Codex tool schema is not recommended as a dispatch value.
- Gemini does not claim a model-setting field that has not been confirmed.
- The adapters still announce the recommendation even when they cannot set it.
- Phase-level and qualifying within-phase dispatch remain covered unconditionally.

**Implementation Outline**

```text
replace Codex's static provider-derived model-field claim with active-schema authority
retain direct setting only for values that schema advertises
inspect Gemini's explicit no-confirmed-field and announce-only fallback; edit only for a demonstrated contradiction or test failure
compare Claude wording to the central contract and edit only on contradiction
preserve coordinator mandate-with-announce text and scope
```

## Step 4: Verify the integrated model-guidance contract

**Enables:** The full user journey and the feature test's final `PASS: subagent model mandate contract holds` assertion.

Review the complete diff as one documentation contract. Confirm no benchmark/eval runner pins, runtime integrations, Ailly phase flow, or intentional `haiku-4.5` normalization example changed. Use `general:review` before declaring completion.

**Tests**

Happy path:

```sh
python3 developer/tests/test_subagent_model_mandate.py
```

The command exits `0` and prints the expected PASS line.

- Rendered Markdown table columns and rows remain readable.
- Candidate display names cannot reasonably be mistaken for universally callable IDs.
- The feature test runs without network access or a model invocation.
- Repository checks remain runnable with no unrelated file changes.

**Implementation Outline**

```text
run the single executable feature test
inspect its output and the complete scoped diff
manually read the central table and adjacent cautions
confirm every in-scope file maps to a design assertion
confirm every out-of-scope surface is untouched
load general:review and address findings before handoff
```
