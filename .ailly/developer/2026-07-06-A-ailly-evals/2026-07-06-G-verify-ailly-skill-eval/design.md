# Design: Feature G — Verify `ailly-skill-eval`'s Claims Against Actual Behavior

**Parent project:** `.ailly/developer/2026-07-06-A-ailly-evals/design.md` (Feature G), research at `.ailly/developer/2026-07-06-A-ailly-evals/research.md`, Closing Bell at `.ailly/developer/2026-07-06-A-ailly-evals/closing-bell.md` (Task 6: "Trusting the method itself").

**Repo under design:** `ailly_two` (sibling repo, branch `main_two`).
Load `ailly_two/skills/ailly-skill-eval/SKILL.md` and `references/method.md` before reading this doc — everything below verifies specific claims from those files.
`ailly_two/DESIGN.md` is the schema reference.

## Purpose

The parent project's research flagged `ailly-skill-eval`'s documented discovery/invocation/baseline method as "a claim to verify, not a fact to build on": the skill's own author found and read its description of the method, but never checked that description against what the existing suites actually do at runtime.
Every other feature-step in this project (D's runner matrix, E's judge calibration, and any future skill-eval suite) either extends `e2e/patterns-eval` or builds a new suite on the same method.
If the method's central claim — that a baseline arm proves a skill earns its place, gated on `improved > 0 && regressed == 0` — doesn't actually hold up when exercised for real, every suite built on faith in it inherits an unverified foundation.

This feature-step settles two concrete questions, cheaply, before any of that downstream work leans on the answer:

1. Does the bucket computation behind the falsification gate (`improved`/`regressed`/`unchanged_pass`/`unchanged_fail`, and the gate formula `improved > 0 && regressed == 0`) match what `SKILL.md` and `references/method.md` document, in the code that actually runs?
2. Does the assertion palette the skill documents (`text_contains`/`text_not_contains`, `judge`, `script`/`program`, `tokens`, etc.) actually behave as described when exercised by the real `e2e/patterns-eval` suite?

Because this is a verification task, not new product functionality, "done" does not mean shipping a capability a user asks for — it means converting an untested claim into either a corrected doc or a standing, automatically-checked guarantee, plus an honest, dated record of what a real live run showed.

## Prior Art

### What already exists and is already correct (confirmed by direct code reading and by running existing tests)

- **`compute_comparison`** (`src/knowledge/report.rs:61-131`) already implements the exact four-bucket formula both `SKILL.md` ("Falsification as an optional layer") and `references/method.md` §6 describe: for each assertion paired by `(case_name, conversation, class)` across two runs, `(fail, pass) → Improved`, `(pass, fail) → Regressed`, `(pass, pass) → UnchangedPass`, and the remaining case with both outcomes validated as `pass`/`fail` (i.e. `(fail, fail)`) → `UnchangedFail`.
  Unnamed cases and any non-`pass`/`fail` outcome (`deferred`, `malformed`, `errored`) are excluded from both indexing and pairing — this exclusion is already stated in the function's own doc comment and is exactly the behavior `tests/report_cmd.rs` already exercises and asserts against a hand-built regression fixture (3 improved / 1 regressed / 4 unchanged-pass / 2 unchanged-fail), green today.
- **The assertion palette's executor mechanics are already covered by deterministic, non-live tests**, all confirmed green in this session (run via `cargo test`, `ANTHROPIC_API_KEY` unset):
  - `src/knowledge/assertions.rs` carries an extensive existing unit-test suite (from line ~1400) directly exercising `text_contains`, `text_not_contains`, `text_matches`, `text_equals`, `must_call_tool`, `must_not_call_tool`, `tool_call_count`, `tool_call_order`, `json_path`, `response_field`, `tokens`, and `latency_ms` against synthetic conversations.
  - `tests/eval_judge.rs` (`judge_assertion_with_grade_p_reply_tallies_pass_and_writes_judge_transcript`) drives `Assertion::Judge` end-to-end through a scripted (non-live) engine, confirming the `GRADE:` regex parse and transcript-write behavior `SKILL.md`/`method.md` describe.
  - `tests/eval_script.rs` and `tests/eval_program_outputs.rs` drive `Assertion::Script`/`Assertion::Program` end-to-end through real subprocesses (no model call), confirming the stdout-reason/empty-stderr/exit-code contract `method.md` §4 documents.
  - **`tests/patterns_eval_checkers.rs` runs `e2e/patterns-eval`'s own three shipped checkers** (`check_newtype.py`, `check_configuring_logging.py`, `check_emitting_logs.py`) directly against a conforming and a violating TypeScript sample apiece, confirming each exits 0/prints nothing on conforming input and exits 1/prints a single-line reason on stdout with empty stderr on violating input.
    This is the strongest available evidence for Claim 2 specific to `patterns-eval` (not just the generic palette), and it is green today.
  - `tests/skill_eval_guide.rs` confirms, as literal string matches against the real files on disk, that `references/method.md` states the `improved > 0` / `regressed == 0` gate and names the built falsification arm `baseline.yaml` (the "Fidelity rule" `method.md` §6 states) — green today.

**Conclusion on Claim 1's formula and Claim 2's mechanics: both are already correct, and already covered by fast, deterministic, already-green tests.**
No documentation correction is warranted for the bucket semantics or the assertion executors themselves.

### What is corroborated but stale: the live gate's historical pass

`docs/developer/TASKS.md`'s existing "patterns-eval structural-checker fragility" follow-up (committed 2026-06-01, the same commit, `8cbb524`, that first built the live falsification gate) already records a real finding: on genuine live runs, `improved` ranged 1–3 across runs, the gate survived "largely on the LLM-as-judge assertion," the regex/heuristic `check_*.py` checkers "reliably discriminate only `emitting-logs`," and `newtype` is an intentional null result (both arms pass, contributing nothing to `improved`).
`e2e/patterns-eval/AGENTS.md`'s "Reading the invocation comparison" section (same date) independently restates the same three-skill breakdown.
`references/method.md` §6's own worked example (`improved 2, regressed 0, unchanged pass 5, unchanged fail 2`, 9 total assertions — exactly 3 skills × 3 assertion classes) falls squarely inside that documented 1–3 range and is therefore very likely a real captured run's output, not an invented illustration.
**Two independent primary sources, committed the same day as the gate's first live pass, corroborate `method.md`'s account.**
This triangulation is good evidence the documented method was accurate *as of 2026-06-01*.

That confirmation is now over a month stale, and re-confirming it is harder than it should be:

- **GitHub Actions CI for `e2e/patterns-eval` has had zero successful runs since 2026-06-01** (`gh run list --workflow=e2e-patterns-eval.yml`).
  The most recent run against `main_two` (2026-06-09, commit "fix(eval): per-run report path agreement") failed in 36 seconds with `engine error: engine authentication failed: provider returned 401 Unauthorized` — before `ailly run` ever reached the live half, let alone the comparison/gate step.
  Two later runs (2026-06-16, 2026-06-19, triggered by an unrelated PR) fail identically.
  `gh secret list` shows the repo's `ANTHROPIC_API_KEY` secret was last rotated 2026-06-02T14:50:34Z — the same day CI started failing — strongly suggesting the rotated value is invalid.
  **This is a real, actionable finding this feature-step surfaces but cannot itself fix** (it requires repo-secret-management access, not a code or design change).
- **Exactly one complete local `assemble→run→eval→report` cycle exists on disk** (`e2e/patterns-eval/runs/` and `evals/reports/`, both `.gitignore`d, never committed), timestamped 2026-06-08, and it is **not valid evidence either way**: reading the underlying conversation YAML directly shows the assistant turns were never filled (`role: assistant` with no `content` follows), and the corresponding report records every `script`/`judge` assertion as `fail` with the literal reason `"...: no filled assistant turn"`.
  The resulting comparison shows `improved: 0, regressed: 0` — which sits *outside* the documented 1–3 range and is best read as a broken or interrupted manual test run (`ailly run` was skipped or failed silently before `eval` was invoked against the same directory), not a genuine re-measurement of the skill's effect.
  Roughly 600 further local run directories accumulated between 2026-06-08 and 2026-06-29 with no corresponding report files — consistent with ad-hoc manual CLI exploration of unrelated work, not further `ci.sh` cycles.
- Per project state (see `MEMORY.md`), `ailly_two/.env` and `e2e/patterns-eval/.env` both currently carry a working Anthropic key locally, so a fresh, valid local re-run is possible today even though the CI secret is broken — this is exactly the manual verification step this feature-step recommends for the Build phase (see Specification).

**Net assessment:** the claim "the gate actually executes and passes today" is well-supported historically and not contradicted by any valid current evidence, but it is not *independently re-confirmed* within the last month, and the fragility TASKS.md itself already documents (thin margin, judge-dependent, only one of three skills' script checkers reliably discriminates) means a point-in-time confirmation decays — this is precisely why Feature G's actual deliverable is a fresh, dated live run, not a re-reading of a five-week-old success.

### Sources read directly for this design

`src/knowledge/report.rs`, `src/knowledge/eval.rs`, `src/knowledge/assertions.rs` (structure and existing unit tests), `ailly_two/DESIGN.md`, `skills/ailly-skill-eval/SKILL.md`, `skills/ailly-skill-eval/references/method.md`, `e2e/patterns-eval/{README.md,AGENTS.md,ci.sh,.gitignore}`, `e2e/patterns-eval/evals/reports/*` (the one stale local artifact and its source conversation files), `docs/developer/TASKS.md`, `.github/workflows/e2e-patterns-eval.yml`, `gh run list`/`gh run view --log` for the workflow's history, `gh secret list`; existing tests `tests/{report_cmd,patterns_eval_checkers,eval_judge,eval_script,eval_program_outputs,skill_eval_guide,skill_forge_clean_comments_review}.rs` (read; the first six were also executed in this session and confirmed green without `ANTHROPIC_API_KEY` set — `skill_forge_clean_comments_review.rs` was read only, not executed, since it requires a live model call and this design phase makes no live calls per the parent brief).

## User Journey and Metrics

**Primary journey** (Closing Bell Task 6, "Trusting the method itself"): a developer is about to build a new eval suite for a skillset using `ailly_two`'s documented method.
Before investing in it, they need to find out whether the method's central claim — that a baseline arm proves a skill earns its place — actually holds up in practice today, using only the provided documentation (no author walkthrough).

**What this feature-step changes about that journey:**

- **Today:** the developer can read `SKILL.md`/`method.md`'s prose account and `method.md`'s one worked example, but has no way to check the *formula itself* against the running code without either trusting the docs outright or reading `report.rs` themselves — and no automated test currently pins the gate's two-conjunct boolean decision (`improved > 0 && regressed == 0`) as its own first-class, reusable check.
  The boolean is currently re-derived by hand in three independent places (`e2e/patterns-eval/ci.sh`'s Python heredoc, `tests/skill_forge_clean_comments_review.rs`'s inline assertions, and implicitly by a human reading a comparison report's summary line) — three chances for the derivation to silently drift from the documented formula if `compute_comparison`'s bucket semantics ever change.
- **After this feature-step:** the gate formula is a named, tested Rust function (`ComparisonTotals::passes_falsification_gate`) that any current or future consumer can call instead of re-deriving, and one automated test pins its behavior against the three qualitatively distinct outcomes a real comparison can produce.
  Separately, a Build-phase manual step actually re-runs the live suite once against current code with valid credentials, and records the result in a dated, durable artifact — so the next developer asking Task 6's question finds an answer that says *when* it was last checked, not just what the docs claim.

**Metrics** (from the parent design's Metrics list): *"`ailly-skill-eval`'s documented baseline-falsification gate is confirmed to actually execute and pass today for `patterns-eval` (or its documentation is corrected to match reality)."*
This feature-step operationalizes that as:

1. The four-bucket formula and the two-conjunct gate are pinned by an automated, deterministic test that fails today (RED) because the gate has no first-class implementation, and will pass once it does.
2. A live run of `e2e/patterns-eval/ci.sh` executes against current code with valid credentials at least once during this feature-step's Build phase, and its exact `improved`/`regressed`/`unchanged_pass`/`unchanged_fail` totals and pass/fail verdict are recorded in a dated artifact a future reader can find without re-running it themselves.
3. If that live run's result contradicts the documented account (e.g. `improved` falls to 0, or a regression appears), `SKILL.md`/`method.md`/`AGENTS.md` are corrected to match reality rather than left standing — this feature-step's Closing Bell is not "the gate passed" but "the gate's actual state is now known and documented accurately."

## Specification

**1.**
**Promote the falsification gate to a first-class, tested Rust API.**
Add to `src/knowledge/report.rs`:

```text
impl ComparisonTotals {
    /// The falsification gate documented in `skills/ailly-skill-eval/SKILL.md`
    /// ("Falsification as an optional layer") and `references/method.md` §6:
    /// the skill under test must help on at least one assertion the baseline
    /// arm failed, and must break nothing the baseline arm passed.
    pub fn passes_falsification_gate(&self) -> bool {
        self.improved > 0 && self.regressed == 0
    }
}
```

This is the exact formula independently stated in `SKILL.md`, `references/method.md` §6, `e2e/patterns-eval/AGENTS.md`, and re-derived (inverted, as a failure check) in `ci.sh`'s Python heredoc — confirmed identical by direct reading of all four.
No paraphrase or reinterpretation is introduced; this step's only change is giving the already-correct, already-scattered formula one canonical, reusable, tested home.

**Feature test** (written this session, RED for the right reason): `/Users/david.souther/devel/davidsouther/ailly/ailly_two/tests/falsification_gate.rs`, `falsification_gate_matches_the_documented_improved_and_regressed_formula`.
It builds three synthetic `EvalReport` fixture pairs (no live calls, no filesystem I/O) via `compute_comparison`, covering the three qualitatively distinct results a real comparison can produce:

1. **Clears the gate** — one assertion improves (`fail → pass`), nothing regresses.
   Asserts `passes_falsification_gate() == true`.
2. **Fails on regression** — one assertion improves *and* a different one regresses (`pass → fail`).
   Asserts `passes_falsification_gate() == false`, pinning that `improved > 0` alone is not sufficient — the second conjunct must be enforced.
3. **Fails as vacuous** — nothing changes between arms (mirrors both `method.md`'s explicit "a gate that never fails proves nothing" warning and the shape of the one stale local artifact found during this design's research).
   Asserts `passes_falsification_gate() == false`, pinning that `regressed == 0` alone is not sufficient either.

Confirmed today via `cargo check --test falsification_gate`: the test fails to compile with exactly three `E0599: no method named 'passes_falsification_gate' found for struct 'ComparisonTotals'` errors — no other errors, confirming RED for the right reason (missing implementation only; every type name, field name, and existing function signature the test references — `compute_comparison`, `EvalReport`, `CaseReport`, `MatchReport`, `AssertionReport`, `ReportTotals` — already compiles clean).

**2.**
**Manual/CI verification step for the Build phase (not the automated feature test):** actually run the live suite once against current code with valid credentials, since this — not the gate arithmetic, which is already correct — is what Task 6 and the parent project's Metrics actually need confirmed.

1. Clear stale local debris first: `rm -rf e2e/patterns-eval/runs e2e/patterns-eval/evals/reports e2e/patterns-eval/evals/judges` — roughly 600 accumulated local run directories (2026-06-08 through 2026-06-29) predate this feature-step and are not reliable evidence either way; a clean slate avoids picking up a stale report by accident.
2. Run `bash e2e/patterns-eval/ci.sh` from the `ailly_two` repo root (it resolves its own project root; the local `.env` files already present supply `ANTHROPIC_API_KEY`).
3. Record the discovery suite's single-run pass rate and the baseline-vs-invocation comparison's exact four bucket totals and gate verdict.
4. If the result matches the documented account (an `improved` count in a plausible small range, `regressed == 0`), record a dated confirmation.
   If it does not (e.g. `improved == 0`, or any `regressed > 0`), treat that as a real finding: investigate whether it is a genuine regression in the skills/checkers/prompts, a live-model idiom-variation flake (`TASKS.md`'s fragility note already anticipates this for `newtype`/`configuring-logging`), or a harness bug — and correct `SKILL.md`/`method.md`/`AGENTS.md` if the documented account no longer holds.
5. Separately from this feature-step's own scope (it requires repo-secret-management access this design cannot exercise): flag that the GitHub Actions `ANTHROPIC_API_KEY` secret has returned 401 Unauthorized on every run since 2026-06-02 and needs to be rotated to a valid value before CI's own pass/fail status can serve as an ongoing, automatic re-confirmation of this gate.

Where the live-run result is recorded is an Open Artifact Decision — see Summary.

## Alternatives

**Automated feature test drives the live suite directly (e.g. `#[ignore]`-gated on `ANTHROPIC_API_KEY`).**
Rejected, per the parent brief and mirroring Feature A's sibling design's `noop`-model precedent: a live run is expensive (real API spend) and non-deterministic (the same `TASKS.md` note this design cites documents `improved` varying 1–3 across runs), so a test that sometimes fails for reasons unrelated to the code under test is worse than no automated test at all.
The deterministic fixture test plus an explicit, separately-tracked manual live-run step gets the same evidence without coupling CI-green to model variance.

**Leave the gate exclusively in `ci.sh`'s Python heredoc; treat "verification" as complete once this design's read-through confirms the formula matches by inspection.**
Rejected: inspection alone is a one-time check with no standing guard against future drift — if a later change to `compute_comparison` (e.g. a new `AssertionOutcome` variant, or a change to the `_ => "UnchangedFail"` catch-all) silently altered what counts as `improved`/`regressed`, nothing would catch it, because the gate boolean itself is never independently computed and tested in Rust.
Feature G's purpose is to convert an unverified claim into a standing, falsifiable guarantee, not a one-time confirmation that immediately starts going stale again.

**Add a CLI-level gate check now (e.g. `ailly report <a> <b> --gate`, exit non-zero on failure) to replace `ci.sh`'s Python heredoc outright.**
Considered, deferred: this is real, useful follow-on work (it would let *any* suite's CI script drop its own hand-rolled gate-check in favor of one flag, not just `patterns-eval`'s), but it is CLI-surface scope beyond what "verify the claim" requires, and arguably overlaps Feature F's report-upgrade territory more than Feature G's verification territory.
Recorded as a `TASKS.md` follow-up candidate rather than folded into this feature-step, keeping Feature G "the cheapest step" per the parent design's sequencing rationale.

**Rewrite `SKILL.md`/`references/method.md` now, on the theory that an unverified claim should be presumed wrong until proven right.**
Rejected by the evidence: this design's research found the bucket formula and the assertion-executor mechanics are already correct and already well-tested, and the documented live-run account is corroborated by two independent primary sources (`TASKS.md`, `AGENTS.md`) committed the same day the gate was first built.
Rewriting correct documentation on spec would be worse than the problem it solves.
The live re-run (Specification, step 2) is the right-sized way to check whether five weeks of silence have changed that conclusion, rather than assuming either way.

## Summary

**Confirmed by this design, no correction needed:** `compute_comparison`'s four-bucket formula and the `improved > 0 && regressed == 0` gate exactly match `SKILL.md`/`references/method.md`'s documented account; the assertion palette's executor mechanics (`judge`, `script`, `program`, `text_*`, `tool_*`, `json_path`, `tokens`, `latency_ms`) are already correct and already covered by fast, deterministic, currently-green tests, including a test that runs `patterns-eval`'s own three shipped checker scripts directly.

**Gap this feature-step closes:** the gate's boolean decision has no first-class, tested Rust implementation today — it is re-derived by hand in `ci.sh`'s Python heredoc and inline in `tests/skill_forge_clean_comments_review.rs`. `ComparisonTotals::passes_falsification_gate` closes that, pinned by the one feature test recorded above.

**Gap this feature-step surfaces but does not itself close:**

- The live gate's last independently-confirmed pass is over a month old (2026-06-01); GitHub Actions CI for `e2e/patterns-eval` has had zero successful runs since, blocked by what looks like an invalid `ANTHROPIC_API_KEY` secret (rotated 2026-06-02, 401 Unauthorized on every run since).
  Fixing that secret requires repo-secret-management access this design phase does not exercise.
- The one complete local run on disk (2026-06-08) is contaminated (unfilled conversations) and must not be read as evidence of anything; it should not be mistaken for a valid re-confirmation by a future reader who finds it on disk.

### Open Artifact Decisions (for human review at the draft gate)

1. **Where the Build-phase live-run result gets recorded.**
   Recommended default: a dated note appended to `docs/developer/TASKS.md`'s existing "patterns-eval structural-checker fragility" entry (the repo already uses this " **Done (DATE):** ..." / " **Re-confirmed (DATE):** ..." convention elsewhere in the same file), naming the exact bucket totals and verdict.
   Alternative considered: commit a snapshot of the passing comparison JSON/MD pair to a new, non-`.gitignore`d path — rejected as the default because a static committed artifact ages silently and could be mistaken for a live guarantee weeks later, but could be added in addition if a reviewer wants a machine-readable record alongside the prose note.
   **Concrete collision risk found post-design, worth resolving before Build starts:** `docs/developer/TASKS.md` is *currently* sitting with uncommitted changes from the unrelated, already-in-flight `docs/developer/2026-06-26-A-eval-static-doc` session (three new entries added, per `git diff`).
   Appending this feature-step's note to the same file while that edit is still uncommitted risks a stacked/awkward diff or a lost edit if the two sessions' changes are staged carelessly together.
   Do not append to `TASKS.md` until that other session's edit has landed (committed) — sequence this note after it, or land it in the same commit deliberately rather than by accident.
2. **Whether to fix the GitHub Actions `ANTHROPIC_API_KEY` secret as part of this feature-step's Build phase**, so CI's own pass/fail status becomes the ongoing recurring re-confirmation instead of a one-time manual run.
   This needs someone with repo-secret-management access; flagged here so it isn't lost, not decided.
3. **Whether `passes_falsification_gate` should also be wired into `ci.sh` (replacing its Python heredoc) and into `tests/skill_forge_clean_comments_review.rs`'s inline assertions**, once it exists.
   Recommended: not in this feature-step (both call sites already work correctly today; this would be pure refactoring with no behavior change) — recorded as a `TASKS.md` follow-up instead.
4. **Cadence for re-running the live confirmation going forward** (a one-time check now vs. an ongoing recurring one once CI is fixed).
   No recommendation made; left to whoever picks up decision 2.
5. **Whether to clean up the ~600 stale local run directories under `e2e/patterns-eval/runs`/`evals/reports`** before the Build-phase live run.
   Recommended yes (low-risk, local-disk-only, avoids a future reader mistaking old debris for current evidence the way this design's research initially did) — included as step 1 of the Specification's Build-phase procedure, not a separate decision to make.

**Next steps.**
This is the draft gate: do not continue into `developer:plan` or any implementation skill in this session, even if asked.
Review this `design.md` against the parent project's `design.md` and `closing-bell.md`, make any edits (especially resolving the Open Artifact Decisions above), then remove the `*Draft 2026-07-06*` marker and start a new session running `developer:plan` to move into this feature-step's plan phase.
