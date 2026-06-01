# `developer/e2e/` — Skill Eval Harness for the `developer` Plugin

*DRAFT 2026-05-29*

## Problem Statement

The `developer` plugin ships thirteen skills, four of which are phase-gated and the entire reason the plugin exists: `design`, `feature-test`, `plan`, `red-green-refactor`. None of these have regression coverage. An edit that softens a phase boundary — for instance, blurring `feature-test`'s "single executable test" rule, or moving `plan`'s 3–7 step range into a fuzzier "a few steps" phrasing — would change the artifacts the model produces without changing what the model says it is doing. The same blur problem exists laterally: `feature-test` and `plan` are both middle-loop artifacts; `red-green-refactor` and `thinking` are both invoked when the build is red; `refactor` and `red-green-refactor` both run during the inner loop; `is-clean` and `cleanup` both touch the working-directory state. An edit to any one `description:` frontmatter that drifts toward a neighbour can silently route the model to the wrong skill.

This harness catches both failure modes for the four phase skills, applying the shared blueprint in [`docs/developer/2026-05-29-A-skill-evals/design.md`](../2026-05-29-A-skill-evals/design.md) with no shape divergence.

## Prior Art

- The shared blueprint and its `developer` subsection define the cross-section (`design`, `feature-test`, `plan`, `red-green-refactor`), the six discovery cases (with paired-blur partners), the four invocation cases (fixture-dependent), and the falsification convention. This document does not redebate any of those decisions; it produces the concrete prompt text, fixture content, and check-script skeletons the blueprint defers.
- `ailly_two/e2e/patterns-eval` is the reference harness. Prompts here follow its one-question coding-situation shape ending in `Which developer:* skill applies?`. Check scripts ship as placeholders matching its `check_<skill>.py` convention until the upstream eval-script slice lands.
- Sibling per-plugin design docs (`docs/developer/2026-05-29-B-characters-e2e`, `…-C-patterns-e2e`, `…-D-general-e2e`) are placeholder directories at the time of writing; this is the first per-plugin slice to land.

## Metrics

Inherited from the blueprint. The harness operates within constraints when:

| Metric | Source | Target |
|---|---|---|
| Discovery pass rate | `evals/discovery.yaml` assertions over 6 cases | ≥ 0.9 |
| Invocation pass rate | `evals/invocation.yaml` assertions over 4 cases | ≥ 0.8 |
| Baseline pass rate | `evals/baseline.yaml` (identical assertions, no skill loaded) | as low as the prompt allows |
| **Falsification gap** | invocation − baseline | ≥ 0.5 |

The falsification gap is the headline. The phase-gated cluster gives the harness a strong test for this: an unloaded model has no reason to produce `*Draft YYYY-MM-DD*` markers, the exact six design-doc section headings, the 3–7-step ceiling, or the type-stub-first ordering of red-green-refactor. The structural checks should pass on the invocation arm and fail on the baseline arm. If they pass on both, the prompt has encoded the answer.

## Specification

### Layout

```
developer/e2e/
├── profile.md                              # purpose + Full triple
├── assemblies/
│   ├── discovery.yaml                      # matrix over case (6)
│   ├── invocation.yaml                     # matrix over skill (4)
│   └── baseline.yaml                       # matrix over skill (4), no SKILL.md loaded
├── prompts/
│   ├── discovery/
│   │   ├── design-vs-feature-test.md
│   │   ├── feature-test-vs-plan.md
│   │   ├── plan-vs-rgr.md
│   │   ├── rgr-vs-thinking.md
│   │   ├── refactor-vs-rgr.md
│   │   └── is-clean-vs-cleanup.md
│   └── invocation/
│       ├── design.md
│       ├── feature-test.md
│       ├── plan.md
│       └── red-green-refactor.md
├── fixtures/
│   ├── design.md                           # cleared design for feature-test + plan cases
│   ├── feature-test.md                     # passing feature-test artifact for plan + rgr cases
│   └── plan.md                             # cleared plan for rgr case
├── evals/
│   ├── discovery.yaml
│   ├── invocation.yaml
│   ├── baseline.yaml
│   ├── scripts/
│   │   ├── check_design.py
│   │   ├── check_feature_test.py
│   │   ├── check_plan.py
│   │   └── check_red_green_refactor.py
│   └── reports/
├── runs/
└── ci.sh
```

The `profile.md` is the short per-plugin appendix to the shared `e2e/AGENTS.md`. It states (1) "this directory tests the `developer` skill plugin" and (2) the axis profile (`Full`). It does not name skills under test or paraphrase any skill content.

### Assemblies

The three assemblies follow the blueprint's illustrative shapes verbatim. The prefix loads `../../e2e/AGENTS.md`, `./profile.md`, `../skills/using-developer/SKILL.md`, and (for invocation only) the skill under test. The baseline assembly drops only the two `kind: system` skill entries; `AGENTS.md` and `profile.md` stay. Live `../skills/<name>/SKILL.md` paths — no `context/` tree.

### Discovery prompts (6)

Each prompt is a 1–3-sentence coding situation followed by `Which developer:* skill applies?`. The pair is named in the filename for traceability; the prompt itself never mentions any skill name. The right and wrong answers below are encoded in `evals/discovery.yaml` as a `text_contains` / `text_not_contains` pair.

| Filename | Situation (summary) | Right answer | Paired-blur partner |
|---|---|---|---|
| `design-vs-feature-test.md` | "I have a vague idea for a feature, where do I start?" — premise pulls toward writing a test first, but no problem statement yet exists. | `developer:design` | `developer:feature-test` |
| `feature-test-vs-plan.md` | "The design is approved, the `*Draft*` marker is gone, the file is checked in — what's next?" — both middle-loop artifacts compete. | `developer:feature-test` | `developer:plan` |
| `plan-vs-rgr.md` | "The feature test is failing the way I want — now what?" — premise pulls toward starting an implementation cycle. | `developer:plan` | `developer:red-green-refactor` |
| `rgr-vs-thinking.md` | "I'm in a TDD cycle, the compiler rejected my type, I changed the type, it rejected the new type the same way — what do I do?" | `developer:thinking` | `developer:red-green-refactor` |
| `refactor-vs-rgr.md` | "All tests are green, the diff has some smells I want to clean up before merging — which loop am I in?" | `developer:refactor` | `developer:red-green-refactor` |
| `is-clean-vs-cleanup.md` | "I want to know whether this branch is in a state where I can start fresh work on something new." (a *check*) — paired in the same file with the inverse "I'm done with this topic and want to close it out" (an *action*). | `developer:is-clean` (for the check); the prompt also requires `developer:cleanup` to NOT be the answer to the check half. | `developer:cleanup` |

Concrete prompt bodies are sketched in the **Concrete prompt drafts** section below.

### Invocation prompts (4) and fixture dependencies

Each invocation prompt asks the model to produce one of the four phase-gated artifacts. Three of the four depend on a prior-phase fixture. The fixtures are deliberately authored to **avoid pre-encoding the answer** — see the *Fixture authoring rules* subsection.

| Filename | Task | Fixture(s) referenced |
|---|---|---|
| `design.md` | Produce a design doc for a one-paragraph problem statement embedded in the prompt. | None (this is the outer loop entry). |
| `feature-test.md` | Produce a feature-test artifact (user story + executable test) for a cleared design fixture. | `fixtures/design.md` |
| `plan.md` | Produce a 3–7-step implementation plan that drives a passing feature test from a cleared design + feature-test pair. | `fixtures/design.md`, `fixtures/feature-test.md` |
| `red-green-refactor.md` | Produce the type-first stubs + a single arrange-act-assert test + the implementation for **step 1 only** of a cleared plan. | `fixtures/design.md`, `fixtures/feature-test.md`, `fixtures/plan.md` |

#### Fixture authoring rules

Per the blueprint's wrinkles section:

- A fixture **must be passing** for its phase: the `design.md` fixture must look like a design a human would have cleared; the `feature-test.md` fixture must look like a single executable test a human would have cleared; the `plan.md` fixture must look like a 3–7-step plan a human would have cleared. If the fixtures look like drafts, the model will (correctly) refuse to advance and the invocation case becomes untestable.
- A fixture **must not include the next phase's name or skeleton**. Concretely:
  - `fixtures/design.md` must NOT contain a function signature for the feature test, must NOT name the test, must NOT outline a step list. It states a problem, prior art, metrics, specification, alternatives, summary. It is *exactly* what the design skill's checklist produces.
  - `fixtures/feature-test.md` must NOT contain a step list, must NOT name implementation milestones, must NOT propose type signatures for new domain objects. It contains a user story and an executable test in the project's test framework signature.
  - `fixtures/plan.md` must NOT contain implementation code for any step. It contains 3–7 named steps, each with a one-sentence description and a pointer to which feature-test assertion it enables.
- Fixtures are **reused across the matrix** to keep the dependency tree shallow. The same problem domain runs through all three: a small CLI utility that reads JSON from stdin, filters records by a field predicate, and writes the survivors back to stdout. This domain is small enough to fit in a single design doc, narrow enough that the test signature is forced, and concrete enough that the plan can name 3–4 real steps. (Details below.)

#### Fixture domain: `jq-lite`

A line-buffered JSON filter. The user pipes JSON-Lines into stdin and a predicate expression as a CLI argument; the tool prints records whose evaluation is truthy. Three reasons this domain works:

1. **Forces a single executable test**. End-to-end exercise is "feed stdin, capture stdout, assert on captured lines". One test covers the user story.
2. **Forces a step plan**. Parsing the predicate, evaluating it against a record, and streaming I/O are three obvious stages; if the candidate adds error handling and exit codes, four; if it adds a missing-field policy, five. Stays inside 3–7.
3. **Forces type-first signatures**. The predicate parser and the evaluator have clear interfaces that show up in `red-green-refactor`'s type-first step.

The domain is **not** a CRUD app, not a web service, not a UI. Domains in those classes tempt the model to scaffold structure beyond what the prompt asks. CLI-filter scope keeps the scaffolding pressure low.

### Fixture mechanism — DEFERRED

The blueprint commits to fixtures-as-prefix-files but defers *whether* `ailly` grows a per-case prefix override or the fixture content is inlined into the prompt body. Both options are tracked here:

- **Per-case prefix override.** Each invocation case names additional `kind: file` entries in its prefix. Requires an ailly feature that does not yet exist. Cleaner separation: the prompt body asks the question, the prefix carries the data.
- **Inlined into prompt body.** The fixture file is included verbatim inside the prompt markdown, between fenced code blocks with the path as a header. No ailly change needed; the prompt grows larger.

This harness commits to neither in the design. The invocation prompts below are written so the fixture reference is a path string (e.g., "the cleared design at `fixtures/design.md`"). Whichever mechanism lands, the prompt text changes minimally: either the fixture appears in the prefix and the prompt's path reference resolves to the loaded file, or the prompt is post-processed to inline the file contents before the assistant turn.

**Decision deferred to:** the developer plugin's feature-test session that converts this design into an executable test. That session will read the in-flight ailly capability set and decide which mechanism is reachable now.

### Check scripts (4)

Each script reads the assistant turn from stdin and writes a single-line JSON verdict to stdout. Until the upstream eval-script slice lands, all four are placeholders matching the patterns-eval `check_newtype.py` convention: read stdin, write `{"status": "placeholder", "reason": "eval-script not yet wired"}`, exit 0. Each placeholder file contains a docstring naming the *eventual* rule set drawn from the skill's body. The rule sets:

- `check_design.py` — eventual rules: assistant output contains exactly the six headings (`Problem Statement`, `Prior Art`, `Metrics`, `Specification`, `Alternatives`, `Summary`); contains the `*Draft YYYY-MM-DD*` marker on a line by itself; the writes-to path matches the `docs/developer/YYYY-MM-DD-A-<topic>/design.md` shape.
- `check_feature_test.py` — eventual rules: assistant output contains one `User Story` section (Given/When/Then or narrative) and one executable test; the test contains one `test(...)` / `it(...)` / `def test_...` declaration; the file is marked `*Draft YYYY-MM-DD*`; no second test is present.
- `check_plan.py` — eventual rules: assistant output contains between 3 and 7 numbered steps (`## Step 1`, `## Step 2`, …); each step has an `**Enables:**` line referencing a feature-test assertion; no step contains implementation code (no fenced code blocks with function bodies, only signatures permitted); the `*Draft YYYY-MM-DD*` marker is present.
- `check_red_green_refactor.py` — eventual rules: assistant output contains exactly one `it(...)` / `test(...)` / `def test_...` declaration; the implementation section appears *after* the type-stub section; no `git commit` shell command appears in the body (commit is mentioned but not executed); no thinking-doc invocation appears (no `developer:thinking` mention).

The placeholder docstrings record these rule sets so the slice that wires the real checks reads them as the spec.

### Falsification convention

Per the blueprint: `profile.md` and `e2e/AGENTS.md` are both grepped by `ci.sh` for the `developer:<skill>` pattern; either match fails the run. `profile.md` may use bare common words (`design`, `plan`, `refactor`) — these are unavoidable in a coding-agent prompt and the blueprint explicitly permits them. Both files appear in the baseline prefix; both also appear in the invocation prefix. The two assemblies differ only in the two `kind: system` SKILL.md entries.

### `ci.sh`

Copy from `ailly_two/e2e/patterns-eval/ci.sh`. Three parameters change:

1. `expected_count()`: `discovery=6`, `invocation=4`, `baseline=4`.
2. Suites driven: `discovery`, `baseline`, `invocation` (all three, since profile is Full).
3. `repo_root="$(cd "${project_dir}/../.." && pwd)"` — the e2e directory is two levels under the repo root.

`ailly` is invoked as a CLI from the user's environment (`ailly -p "${project_dir}" assemble <suite>`), matching the blueprint's convention. The `cargo run` invocations in the patterns-eval version are replaced with `ailly` directly.

### Concrete prompt drafts

The drafts below land verbatim in `prompts/discovery/*.md` and `prompts/invocation/*.md`. They are sized to fit the patterns-eval voice — short, situational, no preamble.

#### Discovery prompts

**`prompts/discovery/design-vs-feature-test.md`**

> I have a rough idea for a feature — users should be able to share a draft document with one collaborator and see their cursor live. I haven't written anything yet. Where do I start? Which `developer:*` skill applies?

**`prompts/discovery/feature-test-vs-plan.md`**

> The design doc for the live-cursor feature is checked in, the `*Draft*` marker is gone, the reviewer signed off this morning. No test exists yet and no implementation has started. What's the next step? Which `developer:*` skill applies?

**`prompts/discovery/plan-vs-rgr.md`**

> The feature test for live cursors is in place and failing exactly the way I expect — no implementation, the assertion about a second cursor appearing never runs because the page object can't find a second cursor element. The test name and the design are both cleared. What's the next step? Which `developer:*` skill applies?

**`prompts/discovery/rgr-vs-thinking.md`**

> I'm in the middle of a TDD cycle on the predicate parser. I wrote the type signatures, the type checker rejected my generic bound, I rewrote the bound, and the type checker rejected it again with the same error message. The plan step itself looks fine to me. Which `developer:*` skill applies?

**`prompts/discovery/refactor-vs-rgr.md`**

> All tests are green on the auth-handler change. Looking at the diff, I see three places where I duplicated the bearer-token parsing logic and one method that grew past 60 lines. I want to clean this up before opening the PR. Which `developer:*` skill applies?

**`prompts/discovery/is-clean-vs-cleanup.md`**

> Two related questions about the same branch:
> (a) Before I start work on a new ticket, I want to confirm this branch is in a state I can build on — tests green, no stale draft markers, no uncommitted scratch files.
> (b) Separately: when this branch's feature is fully shipped and the PR is merged, I want to tear down the topic folder and any deferred-task notes.
> Which `developer:*` skill applies to each?

The eval for the paired prompt asserts `developer:is-clean` appears in the answer to (a) and `developer:cleanup` appears in the answer to (b); a single-skill answer fails.

#### Invocation prompts

**`prompts/invocation/design.md`**

> I want a small CLI tool that reads JSON-Lines from stdin, evaluates a predicate expression supplied as a single CLI argument against each record, and writes the records that match to stdout. Records that don't parse as JSON should go to stderr with a one-line warning and the tool continues. The predicate expression is a small subset of jq (field access, comparison operators, `and`/`or`/`not`, parentheses). Produce the design document.

**`prompts/invocation/feature-test.md`**

> A cleared design for a JSON-Lines filter CLI lives at `fixtures/design.md`. The design has been reviewed and the `*Draft*` marker is gone. No feature test has been written yet. Produce the feature test (user story + one executable test) following the project's conventions.

**`prompts/invocation/plan.md`**

> A cleared design and a cleared feature test for a JSON-Lines filter CLI live at `fixtures/design.md` and `fixtures/feature-test.md`. The feature test is currently failing because no implementation exists. Produce the implementation plan.

**`prompts/invocation/red-green-refactor.md`**

> A cleared design, feature test, and plan for a JSON-Lines filter CLI live at `fixtures/design.md`, `fixtures/feature-test.md`, and `fixtures/plan.md`. Execute **only step 1 of the plan** using a red-green-refactor cycle — write the type-first signatures, write one arrange-act-assert test that fails for the right reason, then implement until that single test passes. Do not start step 2.

### Fixture content sketches

The full fixture text is authored in the feature-test session; sketches here name what each file contains so the design is reviewable end-to-end.

**`fixtures/design.md`** (≈ 60 lines, marker absent — i.e., cleared):

```markdown
# jq-lite — JSON-Lines Predicate Filter

## Problem Statement
…paragraph about line-buffered JSON filtering…

## Prior Art
- `jq`: full grammar, separate binary, not embeddable.
- `grep`: line-oriented but no structured matching.

## Metrics
- 1 MB JSONL filtered in < 200 ms with a trivial predicate.
- Malformed lines never abort the stream.

## Specification
- Predicate grammar: field-access, `==`/`!=`/`<`/`>`, `and`/`or`/`not`, parens.
- Stream protocol: read stdin line by line; write matches to stdout; warnings to stderr.
- Exit code: 0 if every line was valid; 1 if any line failed to parse.

## Alternatives
- Embed `jq` itself: too heavy for the predicate-only use case.
- Use a generic expression parser library: pulls in an unbounded grammar.

## Summary
Build a small parser → evaluator → streaming I/O loop. No persistence, no
configuration, no library dependencies beyond stdlib.
```

This fixture is a passing design. It does **not** include a test name, a function signature, or a step list. The four invocation cases that downstream depend on this fixture each get a clean cleared design to work from.

**`fixtures/feature-test.md`** (≈ 40 lines, marker absent):

```markdown
# Feature Test — jq-lite

## User Story
Given a stream of JSON-Lines on stdin and a predicate expression on the
command line, when the user runs jq-lite, then records matching the
predicate appear on stdout in their original order.

## Test
The executable test lives at `tests/feature_test.<ext>` and runs the
binary as a subprocess with stdin piped from a fixture file. It captures
stdout, splits on newlines, and asserts the captured set matches the
expected survivor records.
```

This fixture is a passing feature test artifact. It does **not** propose step names, does **not** propose type signatures for the parser or evaluator, does **not** list assertions beyond the one user-story outcome.

**`fixtures/plan.md`** (≈ 50 lines, marker absent):

```markdown
# Implementation Plan — jq-lite

**Feature test:** `tests/feature_test.<ext>`
**User story:** users filter JSON-Lines streams with a small predicate language.

**Steps:**
- [ ] Step 1: Predicate parser (grammar → AST)
- [ ] Step 2: AST evaluator against a single record
- [ ] Step 3: Streaming I/O loop wiring stdin → evaluator → stdout
- [ ] Step 4: Error-stream policy for malformed lines

## Step 1: Predicate parser
**Enables:** `expect_parses_field_eq_literal`
Build a small recursive-descent parser that turns the predicate string into
an AST. Types only at this stage — no evaluator yet.

## Step 2: AST evaluator
**Enables:** `expect_record_matches_field_eq`
Walk the AST against a parsed JSON value, return a boolean.

## Step 3: Streaming I/O loop
**Enables:** the top-level feature-test assertion that captured stdout
contains the survivor records.
Wire stdin → JSON parse → evaluator → stdout serializer.

## Step 4: Error stream policy
**Enables:** `expect_malformed_line_goes_to_stderr`
Catch parse errors per line; emit a one-line warning to stderr; continue.
```

This fixture is a passing plan (4 steps, within the 3–7 range). It does **not** include implementation code, only step names and one-sentence descriptions. The `red-green-refactor` invocation case implements **only step 1** so the case stays bounded; the script asserts a single arrange-act-assert test and the stub-first ordering.

### Test surface — failure modes the harness catches

| Edit | Caught by |
|---|---|
| `design`'s description loses "before implementation" | `design-vs-feature-test` flips |
| `feature-test`'s description grows toward `plan` | `feature-test-vs-plan` flips |
| `plan`'s description grows toward `red-green-refactor` | `plan-vs-rgr` flips |
| `red-green-refactor` loses the thinking trigger | `rgr-vs-thinking` flips |
| `refactor` loses its post-green precondition | `refactor-vs-rgr` flips |
| `is-clean` or `cleanup` lose the check-vs-action distinction | `is-clean-vs-cleanup` flips |
| `design` loses the six-section structure | `check_design.py` flips (when wired) |
| `feature-test` loses "single executable test" | `check_feature_test.py` flips |
| `plan` softens the 3–7-step range | `check_plan.py` flips |
| `red-green-refactor` softens "type-first" or "one test" | `check_red_green_refactor.py` flips |

## Alternatives

**Reuse one fixture set across the matrix vs. one fixture per case.** Adopted: one shared fixture set (`jq-lite`). Considered and rejected: per-case fixtures (different domain for each invocation case). Per-case fixtures isolate the matrix at the cost of authoring three to four small designs the reviewer must sanity-check independently. The shared fixture lets the reviewer load the `jq-lite` domain into their head once and read all four invocation cases against it.

**Pre-encode the fixture into the prompt body now vs. wait for the per-case prefix override.** Deferred per the blueprint. See the *Fixture mechanism — DEFERRED* section above.

**Test all 13 developer skills now vs. the 4 phase-gated skills.** Adopted: 4. The blueprint commits to the cross-section explicitly. Adding `refactor`, `thinking`, `is-clean`, `cleanup` as invocation cases would double the matrix without adding falsification signal; their discovery surfaces are already covered by the paired-blur cases above.

**Use a real project's design doc as the fixture vs. author a fresh small one.** Adopted: fresh small one (`jq-lite`). Real project design docs in this repo carry context the model can echo back; the harness wants a domain narrow enough that the answers are reproducible across runs and small enough that the fixture itself fits on one page.

**Multi-turn invocation conversations.** Rejected at the blueprint level and not reopened here. The fixtures-as-prefix-files approach keeps every conversation single-shot.

## Summary

Six discovery prompts, four invocation prompts, three fixtures (shared across the matrix), four placeholder check scripts, three assemblies, three eval YAMLs, one `ci.sh`, one `profile.md`. All artifacts land under `developer/e2e/` (created by this design's downstream feature-test session). The doc directory at `docs/developer/2026-05-29-E-developer-e2e/` holds this design and will accept follow-ups (feature-test, plan, etc.) as later phases run.

**Deferred decisions.**

- **Fixture mechanism.** Per-case prefix override vs. inlined-into-prompt-body. Deferred to the developer plugin's feature-test session, which reads the in-flight ailly capability set and chooses.
- **Check-script bodies.** All four scripts ship as placeholders matching the patterns-eval convention; the upstream eval-script slice in ailly is the gating dependency.
- **Model-version sweep strategy.** All three assemblies pin `claude-sonnet-4-6` for now; sweep tooling lands when baseline metrics are stable.
- **Project file extensions in fixtures.** The fixture text uses `<ext>` as a placeholder. The feature-test session picks one project test framework (likely `pytest` or `vitest`) and instantiates the extension throughout; that decision rides with the choice of language for the `jq-lite` reference implementation.
- **Whether the four phase cases also need a paired-skill judge prompt** (in addition to the structural script). The blueprint's invocation YAML carries judge + script + tokens for each case; adopted here without modification.
