# Design: Judge Calibration

**Feature-step:** E, of the `2026-07-06-A-ailly-evals` project.
See the parent [design.md](../design.md), [research.md](../research.md), and [closing-bell.md](../closing-bell.md) for full project context; this document scopes only Feature E.

**Load before working on this feature-step:** `ailly_two/skills/ailly-skill-eval/SKILL.md` (with `references/method.md`) and `ailly_two/DESIGN.md` — the authoritative `assembly`/`conversation`/`evaluation` schemas.
Neither is restated here.

## Purpose

`ailly_two`'s `judge` assertion (`src/knowledge/assertions.rs::check_judge`) is mechanically solid: chain-of-thought before verdict, a ternary `GRADE: P|F|I` that gives the model an honest "cannot decide" out, and a greedy-last-line regex that resists prompt injection from the very candidate response it is grading.
None of that proves the verdicts are *correct*.
As a beta product, every suite that leans on a `judge` assertion — `patterns-eval`'s invocation axis, `insurance-claim`'s `over-limit` case, and every future suite this project's other feature-steps add — has been exercised implicitly by beta users, whose feedback (bug reports, "that grade looked wrong," silent continued use) is real signal that the judge is *probably* not badly broken.
But that signal is informal and unsystematic: nobody has checked the judge's verdicts against a human labeler's ground truth in a structured, repeatable way, so there is no actual agreement-rate number behind the accumulated sense that it's "probably fine" — only the absence of loud complaints.
The parent research names the industry bar explicitly: calibrate an LLM judge to ≥90% agreement with a human labeler before trusting it for release decisions.
This feature-step measures that number for `ailly_two`'s judge and builds the reusable harness to remeasure it whenever the judge prompt or the fleet of judge-backing models changes.

This is a measurement feature, not a new capability: nothing about `run`, `assemble`, the CLI surface, or engine routing changes.
The one genuinely new piece of production code is a small, pure function that reads an already- produced `EvalReport` (unchanged from the existing `evaluate()` orchestrator) alongside a human-authored label set and computes an agreement rate and a bar-crossing flag.

## Prior Art

- **`check_judge` itself** (`src/knowledge/assertions.rs:313-408`), read directly for this design: sends `JUDGE_SYSTEM_PROMPT` (chain-of-thought required, `GRADE: P|F|I`, "last GRADE line is binding") as the system turn, a `RUBRIC:` / `USER QUESTION:` / `CANDIDATE RESPONSE:` block as the user turn (plus an optional `PROGRAM_OUTPUTS:` tail), calls `ctx.engine.complete`, and parses the reply with `grade_regex()` (`(?is).*(GRADE\s*:\s*([PFI]))`, confirmed greedy-last by `parse_judge_reply_greedy_last_grade_wins_over_injected_earlier_one` at `assertions.rs:2107`).
  `P` → `Pass`; `F` → `Fail { reason: <CoT prefix> }`; `I` → `Malformed { reason: "judge inconclusive: …" }`; no `GRADE:` line at all → `Malformed { reason: "judge produced no GRADE line: …" }`; an engine transport error → `Errored`.
  This four-way (five counting `Deferred` when no engine is wired) outcome space is exactly what a calibration harness must fold against a two-way human ground truth.
- **`evaluate()`'s orchestration** (`src/knowledge/eval.rs:263-359`) is the existing, unmodified machinery this feature-step reuses wholesale: it walks suite cases, matches conversations, calls `Assertion::check`/`check_judge`, and folds verdicts into an `EvalReport` (`suite`, `run_id`, `totals`, `per_class`, `cases: Vec<CaseReport>`, each case carrying `name` and `matches: Vec<MatchReport>`, each match carrying `assertions: Vec<AssertionReport>` with `class`/`outcome: String`/`reason: Option<String>`).
  `outcome` is one of the five string labels `outcome_label` produces: `"pass"`, `"fail"`, `"deferred"`, `"malformed"`, `"errored"` (`eval.rs:504-512`).
  A calibration harness that consumes this report needs no new orchestration — it needs a suite shaped as one case per human-labeled example, and a small function that reads the resulting report against a labels file.
- **`NoopEngine`** (`src/engine/engine.rs:193-282`), specifically
  `from_replies`/`from_scripts`, is the existing scriptable test double.
  `tests/eval_judge.rs` already demonstrates the exact pattern this
  feature-step's test reuses: build a suite YAML inline, build `Conversation`
  values by hand, wire `NoopEngine::from_replies([...])` into an
  `EvaluationContext`, call `evaluate()` directly (bypassing
  `cli::eval::run`'s model-routing, which would decline to open an engine for
  `model: noop` per `is_noop_model`/`resolve_judge_engine`,
  `src/cli/eval.rs:208-235`), and assert on the returned `EvalReport`.
- **`report.rs`'s shape** (`src/knowledge/report.rs:1-60`) is the closest
  existing analogue to what this feature-step's new module should look like:
  a pure function (`compute_comparison`) that takes one or two `EvalReport`
  values and produces a small `Serialize`/`Deserialize` domain struct, with
  I/O (writing JSON/markdown to disk) left to the `cli` layer. `calibration.rs`
  follows the same split.
- **`e2e/patterns-eval` and `e2e/insurance-claim`** (read directly, including
  both `ci.sh` scripts) establish the working "Ailly content project" shape —
  `context/`, `evals/`, `runs/`, a `README.md`, an `.env`, and a `ci.sh` that
  hard-fails or skips-with-notice depending on the suite's own tolerance for
  missing credentials — and the precedent of inlining a small Python
  computation directly in `ci.sh` (`report_comparison`'s falsification-gate
  check) rather than adding new `ailly` CLI surface for a one-off computation.
- **`ailly-skill-eval`'s "Project anatomy"** (`skills/ailly-skill-eval/SKILL.md`) describes `context/skills/`, `assemblies/` (discovery + invocation + baseline), and `prompts/` — machinery for regression-testing a *skillset's* discovery/invocation behavior.
  Judge calibration tests something orthogonal: whether a fixed grading prompt agrees with a human on fixed candidate responses.
  There is no skill under test, no discovery axis, and no baseline-arm falsification question ("does removing the skill make the candidate worse" doesn't apply to "does the judge model score this candidate the way a human did").
  Only the generic Ailly-project conventions (`evals/`, `runs/`, `ci.sh`, credential-skip) transfer; the discovery/ invocation/axis method does not.
  See Alternatives.

## User Journey and Metrics

**Primary journey (Closing Bell Task 4):** "One of your suites uses an LLM `judge` assertion to grade a subjective response.
You're not sure whether to trust its pass/fail calls.
Find out how much you should trust it."
The developer runs the judge-calibration suite, reads a report that names an agreement rate and states plainly whether it clears the ≥90% bar, and decides whether to trust the judge for release decisions or to keep a human in the loop.

**Two speeds, same computation, per Superpowers' two-speed posture the parent
research adopted:**

1. **Deterministic, fast, always-run (this feature-step's feature test and
   its downstream unit tests):** a scripted judge (`NoopEngine`) with known
   replies against known human labels, so the *arithmetic* — agreement rate,
   exclusion of environmental errors, the bar comparison — is pinned in CI on
   every commit with no network call and no flakiness.
2. **Live, slow, human-labeled, run manually or in a credential-gated CI job (a later plan step within this same feature-step, not this design's test):** the same computation fed a real `EvalReport` from a real judge-backed model call against `e2e/judge-calibration`'s 20-50 human-labeled examples.
   This is the number the Closing Bell's ≥90% metric is actually about; it is an empirical outcome of live model behavior, not something this design or its test can assert a specific value for.

**Metrics:**

- The harness computes an agreement rate and a boolean bar-crossing flag for
  any `(EvalReport, labels)` pair, matching hand-computed expectations exactly
  — this is what the feature test pins.
- (Downstream, not gated by this design's test) The live run against
  `e2e/judge-calibration`'s human-labeled set reports the actual number; per
  the parent Closing Bell, ≥90% is the target but this feature-step's Closing
  Bell contribution is "the number is measured and visible," not "the number
  is forced above 90%" — a judge that calibrates below the bar is a true,
  useful finding (parallel to `ailly-skill-eval`'s "null result" framing: a
  measurement that comes back unfavorable is not a defect in the harness).

## Specification

### New module: `src/knowledge/calibration.rs`

A pure, synchronous function — no engine, no I/O, no `async` — registered as `pub mod calibration;` in `src/knowledge/mod.rs` alongside `eval`, `report`, `assertions`, `script_runner`.
Mirrors `report.rs`'s split: computation here, persistence (writing a JSON/markdown calibration report to disk) is a `cli`- layer concern for a later plan step, not this module.

```rust
/// Ground truth for one calibration example, authored by a human labeler.
/// Binary by design: a labeler is expected to reach a decision, unlike the
/// judge's own ternary P/F/I (which gives the *judge* an honest "cannot
/// decide" out, not the human ground truth).
pub enum HumanVerdict { Pass, Fail }

/// How one example's judge outcome relates to its human label.
pub enum Agreement {
    Agree,
    Disagree,
    /// Excluded from the rate's denominator: the judge call itself failed
    /// (`Errored`) or never ran (`Deferred`) — an environmental/wiring
    /// problem, not evidence about the judge's grading quality.
    Excluded,
}

/// One example's outcome, folded for reporting.
pub struct ExampleAgreement {
    pub id: String,               // matches the suite case `name:`
    pub human_verdict: HumanVerdict,
    pub judge_outcome: String,    // the report's own "pass"/"fail"/"malformed"/"errored"/"deferred"
    pub reason: Option<String>,   // carried from the report's AssertionReport.reason
    pub agreement: Agreement,
}

/// The ≥90% bar the parent research found as the industry threshold before
/// trusting an LLM judge for release decisions.
pub const JUDGE_CALIBRATION_BAR: f64 = 0.90;

pub struct CalibrationReport {
    pub suite: String,
    pub run_id: String,
    pub total_examples: usize,
    pub excluded: usize,
    pub considered: usize,     // total_examples - excluded
    pub agreements: usize,
    pub agreement_rate: f64,   // agreements / considered; 0.0 when considered == 0
    pub meets_bar: bool,       // considered > 0 && agreement_rate >= JUDGE_CALIBRATION_BAR
    pub examples: Vec<ExampleAgreement>,
}

/// Fold an `EvalReport` produced by a judge-calibration suite (one case per
/// labeled example, each case carrying exactly one `judge` assertion over
/// exactly one matched conversation) against a human-authored label map keyed
/// by case name.
pub fn compute_calibration(
    report: &crate::knowledge::eval::EvalReport,
    labels: &std::collections::BTreeMap<String, HumanVerdict>,
) -> CalibrationReport
```

**Outcome-to-agreement mapping** (the core judgment call this feature-step
makes, stated here for review):

- `"pass"` agrees with `HumanVerdict::Pass`, disagrees with `Fail`.
- `"fail"` agrees with `HumanVerdict::Fail`, disagrees with `Pass`.
- `"malformed"` (covers both the judge's own `I` verdict and a reply with no parseable `GRADE:` line) always **disagrees** — it counts against the rate.
  A judge that cannot commit to a verdict is not "agreeing" with a human who did commit to one; treating `malformed` as excluded would let a judge that hedges constantly report a deceptively high agreement rate on the cases it *did* commit to.
- `"errored"` and `"deferred"` are **excluded** from both numerator and denominator — these are transport/wiring failures (auth, rate limit, no engine configured), not the judge exercising grading judgment.
  Counting them as disagreement would conflate "the model was unreachable" with "the model graded wrong"; counting them as agreement would be worse.
- A case whose report shape doesn't match the one-case/one-match/one-
  assertion expectation (e.g. a suite-authoring mistake) is out of scope for
  this design's single feature test; `plan` should decide whether that's a
  panic, a skip, or a `CalibrationError` — flagged in Summary.

**Bar semantics:** inclusive (`>=`), matching the parent research's own "≥90%" framing and the project design's Task 4 metric wording.
Chosen because the alternative (`>`) has no textual support anywhere in the parent project's artifacts, and an exclusive bar would silently reject a judge sitting exactly at the industry-cited threshold.

### Suite/labels shape for the (downstream) live run

Not built by this design's feature test, but specified here so `plan` has a
concrete target:

- `e2e/judge-calibration/evals/judge-calibration.yaml` — one `Case` per example, `name: <example-id>`, a single `{ type: judge, prompt: <rubric> }` assertion.
  Standard `evaluation` schema, nothing new.
- `e2e/judge-calibration/runs/<run-id>/<example-id>.yaml` — one conversation
  per example, hand-authored (not `ailly run`-generated — the candidate
  response under test is fixed data, drawn from a real prior suite run or
  deliberately constructed as an edge case, per Anthropic's "real-failure-
  derived" guidance the parent research cites), `meta.model` set to whichever
  real model backs the live judge call (e.g. `claude-sonnet-4-6`).
- `e2e/judge-calibration/evals/labels.yaml` — a small, new, project-owned
  sidecar format (**not** one of `DESIGN.md`'s three schemas — deliberately
  kept separate rather than overloading `evaluation.Case` with a field
  `DESIGN.md` doesn't define): `{ <example-id>: pass | fail }`, one entry per
  example, authored by the human labeler.
- `e2e/judge-calibration/ci.sh` — mirrors `insurance-claim`/`patterns-eval`'s credential-skip convention: `ailly eval judge-calibration --over runs/<id>/` (existing, unmodified `eval` CLI) produces the standard `evals/reports/<run-id>.json`; a follow-on step loads that JSON plus `labels.yaml` and reports the calibration numbers.
  Because `compute_calibration` is a plain Rust function with no CLI wrapper (Feature E adds no new `ailly` subcommand — the parent design explicitly scopes this feature-step to touch "neither the CLI nor engine routing"), this step is most likely a small `#[ignore]`d, credential-gated integration test (`cargo test --test judge_calibration_live -- --ignored`) rather than a shell/Python recomputation of the same arithmetic — one implementation of the math, exercised twice (deterministically here, live there), rather than two implementations kept in sync by hand.
  `plan` should confirm this shape.

### Feature test

**Path:** `/Users/david.souther/devel/davidsouther/ailly/ailly_two/tests/judge_calibration.rs`

Fully self-contained (no dependency on the not-yet-authored
`e2e/judge-calibration/` fixtures), mirroring `tests/eval_judge.rs`'s style:
an inline suite YAML, ten hand-built two-turn conversations (`model: noop`),
a `NoopEngine::from_replies` scripted with ten `GRADE:` replies, and an inline
`BTreeMap` of human labels chosen so exactly one of ten disagrees with its
scripted judge reply.

- **Act 1:** call the existing, unmodified `evaluate()` to produce a real
  `EvalReport` (proves the harness sits cleanly downstream of today's
  orchestration, per the parent spec's "touches neither the CLI nor engine
  routing").
- **Act 2:** call the new `compute_calibration(&report, &labels)`.
- **Assert:** `total_examples == 10`, `excluded == 0`, `considered == 10`,
  `agreements == 9`, `agreement_rate == 0.9` (exact — chosen to land exactly
  on the inclusive bar, so the test pins the `>=` boundary decision rather
  than leaving it untested), `meets_bar == true`, and the one deliberately-
  disagreeing example's `ExampleAgreement.agreement == Agreement::Disagree`
  by id.

This is currently **RED**: `ailly_two::knowledge::calibration` does not exist.
`cargo check --test judge_calibration` fails with `unresolved import
`ailly_two::knowledge::calibration`` (confirmed below) — a missing-
implementation failure, not a typo or an existing-API misuse.

## Alternatives

**Full skill-eval anatomy (`context/skills/`, `assemblies/` with a discovery+invocation+baseline sweep) vs. a lighter Ailly-project shape.**
Rejected the full anatomy: it is built around a *skillset* whose `description:` frontmatter and body can independently regress, swept across a case/skill matrix and falsified against a no-skill baseline.
Judge calibration has no skill, no discovery surface, and no meaningful "baseline" arm — there is nothing to remove and re-run to prove the judge "earns its place," because the judge is not optional machinery being evaluated for usefulness, it's a grading function being evaluated for *accuracy*.
Adopting the full anatomy would mean inventing `assemblies/` templates and a `prompts/` matrix for content that is, by construction, fixed human-labeled data with no axis to sweep.
The generic parts of an Ailly content project (`evals/`, `runs/`, `ci.sh`, `.env`, credential-skip) still apply and are specified above.

**New `ailly calibrate` CLI subcommand vs. a plain library function + integration test.**
Rejected the CLI subcommand for this feature-step: the parent design scopes Feature E to touch "neither the CLI nor engine routing," and a new subcommand is exactly the kind of durable, user-facing surface Feature A's own CLI-filtering work is separately, carefully designing — duplicating that effort here for a single-purpose computation would cut across that feature-step's scope.
A plain `pub fn compute_calibration` plus a credential-gated `#[ignore]`d test gives the same live-verification power (run it by hand, or wire it into CI as its own job) without adding a long-lived CLI contract this project doesn't otherwise need.
Revisit if a later project wants judge calibration to be a first-class, repeatable operator command rather than an occasional health check.

**Treating `malformed` as excluded (like `errored`/`deferred`) vs. counted as a disagreement.**
Considered excluding it, reasoning that `I` ("cannot decide") is a legitimate, designed-in judge outcome distinct from a hard failure.
Rejected: excluding every hedge would let a judge that frequently answers `I` on the examples it finds hard report an artificially high agreement rate on the remainder, which is precisely the false confidence the `I` verdict exists to avoid *creating* in a downstream reader — the industry guidance this project cites calibrates against a judge deciding to trust, not against a filtered subset of its most confident calls.

**Recomputing the calibration arithmetic in `ci.sh`'s inline Python (matching the existing `report_comparison` precedent) vs. a Rust integration test.**
Leaning toward the Rust test (see Specification) to avoid two independent implementations of the same agreement/bar math drifting apart, but flagged as an open call for `plan` rather than decided firmly here, since the existing precedent for exactly this kind of one-off report-shape check is Python.

## Summary

**Open Artifact Decisions** (judgment calls made without a live reviewer;
confirm at the draft gate):

1. **Calibration report file format.**
   Not prescribed anywhere upstream.
   Proposed: mirror `report.rs`'s dual JSON+Markdown convention (`evals/calibration/<run-id>.json` + a rendered `.md` summary), for consistency with the existing single-run/comparison report split and to keep the live number CI-parseable.
   A human should confirm this is worth the two-format duplication versus JSON-only.
2. **`labels.yaml`'s exact shape and location.**
   Proposed as a flat `{ id: pass|fail }` map under `evals/`, deliberately not folded into the `evaluation` schema.
   A human should confirm this doesn't collide with any near-term plan to extend `DESIGN.md`'s `Case` shape with an `expected:` field (no such plan is currently recorded).
3. **Live verification's exact mechanism** (a `#[ignore]`d credential-gated
   Rust test vs. a `ci.sh` Python recomputation vs. something else) — see
   Alternatives; leaning Rust, not firmly decided.
4. **Malformed-shaped calibration suites** (a case with zero or multiple
   matches, or more than one assertion) — behavior undefined by this design;
   `plan` should pick panic vs. skip vs. a typed `CalibrationError` and add a
   test for it.
5. **Curating the actual 20-50 labeled examples** for `e2e/judge-calibration/` is real, human-judgment-heavy work (per the parent research's "real- failure-derived" guidance) that this design intentionally defers to a later plan step within this same feature-step, after `compute_calibration` itself is proven correct.
   Where the examples are sourced from (existing `patterns-eval`/`insurance-claim` judge transcripts vs. purpose-written edge cases vs. both) is not decided here.

**Resolved by the long-loop reviewer (2026-07-06)**

**1.**
**Calibration report file format.**
**Decided: mirror `report.rs`'s dual JSON+Markdown convention (`evals/calibration/<run-id>.json` + a rendered `.md` summary), as this design's Specification already proposed.**
Read `src/knowledge/report.rs` directly: `compute_comparison`/`render_single_markdown`/ `render_comparison_markdown` already establish the project's convention of a pure JSON-serializable domain struct plus a separate pure markdown-rendering function, with disk I/O left entirely to the `cli` layer.
A JSON-only report would break that convention for no stated reason and would make the human- readable summary a downstream ad-hoc concern instead of a first-class, testable function; the two-format duplication costs one small pure function (`render_calibration_markdown`), which is cheap relative to consistency with the existing single-run/comparison split.
Conservative default: match established precedent rather than diverge.
Persistence itself (the actual `evals/calibration/<run-id>.json` + `.md` write) remains, as specified, a `cli`-layer concern for a later plan step — this decision fixes the shape of `calibration.rs`'s pure render function, not new I/O in this pass.

**2. `labels.yaml`'s exact shape and location.**
**Decided: a flat `{ id: pass|fail }` map under `evals/` (i.e. `e2e/judge-calibration/evals/labels.yaml`), not folded into the `evaluation` schema, as this design's Specification already proposed.**
Read `DESIGN.md` at the repo root directly: it defines exactly three schemas (`conversation`, `assembly`, `evaluation`) and states `evaluation`'s `Case` shape precisely (`name?`, `when?`, `assertions`) with no `expected:` or ground-truth field anywhere in the grammar, and no in-flight research or design artifact in this project proposes adding one.
Extending `Case` would mean either overloading a schema three other feature-steps already depend on for something (human ground truth) `DESIGN.md`'s current audience — an eval suite author, not a labeler — never needs, or teaching the schema a concept (binary human verdict) that deliberately diverges from the judge's own ternary pass/fail/inconclusive outcome space this same design's "Outcome-to- agreement mapping" section already treats as load-bearing.
A small, separate, project-owned sidecar format keeps that divergence explicit instead of silently smuggling a fourth concept into a three-schema contract.
Conservative default: do not touch a cross-cutting schema three other feature-steps rely on when a narrowly-scoped sidecar file fully satisfies this feature-step's need.

**3.**
**Live verification's exact mechanism.**
**Decided: defer building it in this pass entirely.**
Per this long-loop's explicit instruction, only `compute_calibration`'s pure computation (folding an `EvalReport` plus a labeled set into an agreement rate and bar verdict) is built and tested in this plan/build cycle — that is what `tests/judge_calibration.rs` actually pins, per its own doc comment ("pins the harness's own correctness, not a live judge's actual calibration").
The choice among a `#[ignore]`d credential-gated Rust integration test, a `ci.sh` Python recomputation, or another mechanism remains open for a later plan step within this same feature-step, once `e2e/judge-calibration/`'s labeled examples exist to verify against (see item 5, still deferred).
Deciding the live mechanism now, before there is any labeled data or CLI plumbing to run it against, would be speculative; the pure-computation work this pass does is a strict prerequisite for that later decision either way, so nothing downstream is blocked by leaving it open.

**4.**
**Malformed-shaped calibration suites (zero or multiple matches, or more than one assertion per case).**
**Decided: a typed `CalibrationError` returned from `compute_calibration`, not a silent skip or a panic.**
Read `src/engine/engine.rs`'s `EngineError` and `src/knowledge/script_runner.rs`'s error enum directly: both use `#[derive(thiserror::Error, Debug)]` typed error enums at library-internal boundaries within `ailly_two`'s own crate, reserving stringly-typed/`anyhow`-style errors for actual application boundaries (the CLI).
`compute_calibration` is a `pub fn` in a library module (`src/knowledge/calibration.rs`) consumed by other Rust code (tests today, a CLI wrapper and a live-verification harness later), not a process boundary a human reads output from directly — per `patterns:errors-typed-untyped`'s library-vs-application-boundary distinction, a typed error a caller can match on is the right shape here, matching this crate's own established convention.
A silent skip would hide a suite-authoring mistake (e.g. a case matching zero conversations, silently excluded from both numerator and denominator, quietly inflating apparent coverage); a panic would make a malformed suite crash the whole calibration run instead of surfacing a precise, catchable diagnosis.
`plan.md` adds `CalibrationError` (an `enum` with at least `NoMatch { case: String }`, `MultipleMatches { case: String, count: usize }`, `NoAssertions { case: String }`, `MultipleAssertions { case: String, count: usize }` variants — zero and more-than-one assertions are distinct variants, mirroring how zero/more-than-one matches are already split into `NoMatch`/`MultipleMatches` rather than folded into one count-carrying variant) and a `compute_calibration` signature returning `Result<CalibrationReport, CalibrationError>`, plus a test asserting each malformed shape is rejected with the correct variant.

**5.**
**Curating the actual 20-50 labeled examples.**
**Resolved by the user, 2026-07-06: mine candidate examples from the operator's own real Claude Code and Codex agent-session history, wherever those sessions actually invoked Ailly, via a durable, reusable, checked-in script — not by hand-authoring examples from scratch, and not by treating the mined output itself as ground truth.**
This was the human's own explicit direction, not a reviewer default.
The script lives at `ailly_two/e2e/judge-calibration/evals/scripts/mine_calibration_candidates.py` on branch `feature/e-judge-calibration-labels-miner` (built in an isolated worktree, `.worktrees/e-judge-calibration-labels-miner`, off `main_two`, to avoid colliding with this feature-step's own concurrent build on `feature/e-judge-calibration`).
It walks `~/.claude/projects/**/*.jsonl` (including each session's dedicated `subagents/agent-*.jsonl` sub-invocation transcripts) and `~/.codex/sessions/**/rollout-*.jsonl` — both roots overridable by flag, neither assumed installed — and, per turn, checks a structural Ailly-invocation signal (Claude Code: `attributionSkill`/ `attributionPlugin` or a `<command-name>` tag containing "ailly"; Codex: the clean `event_msg` user-message text against a small set of Ailly-specific patterns) rather than a naive full-text search, which would false-positive on every session's own skill-catalog boilerplate (both tools list a skill literally named "ailly" in every session regardless of use).
It records which model produced each candidate response when the transcript itself recorded one (`message.model` for Claude Code, the matching `turn_context` for Codex), leaving it `null` rather than guessing when it did not.
It never assigns a pass/fail verdict: output lands under `e2e/judge-calibration/mined/` (added to `ailly_two/.gitignore` and never committed — transcripts span personal projects and client/employer codebases alike) as a flat `labels.yaml`-shaped `{ id: TODO }` map per item 2's decided shape, one draft `conversation`-schema YAML per candidate under `mined/conversations/`, and a `candidates.jsonl` carrying full provenance plus, where a transcript's own next human message made an unambiguous approval/complaint (e.g. "that's wrong", "looks good"), a `candidate_label_human_implied` hint kept structurally separate from the blank `label` a human must still confirm.
A real run against the author's own machine mined 663 candidates (602 Claude Code, 61 Codex) across 1,102 scanned session files, with model metadata present for 100% of candidates (both tools record a model id on every relevant turn this script's heuristics matched) and 5 candidates carrying a low-confidence human-implied hint.
This resolves *where the examples come from* and *how the harvesting is repeated* (by this operator again later, or by a different user on a different machine); it does not itself complete item 5's curation — a human still must review a subset of the mined candidates, confirm each one's `pass`/`fail` label, and promote that reviewed subset into the real, checked-in `e2e/judge-calibration/evals/labels.yaml` and `runs/<run-id>/*.yaml`, per item 2's shape — but it changes that remaining work from "author 20-50 examples from nothing" to "review and label a curated slice of 663 real, already-collected candidates."

**Next steps.**
This is the draft gate: do not continue into `developer:plan` or any implementation skill in this session, even if asked.
A human should review this `design.md`, resolve the Open Artifact Decisions above, then remove the `*Draft 2026-07-06*` marker and start a new session running `developer:plan` to move into this feature-step's plan phase.
