# Project Design: Ailly Evals — Production-Ready Eval Harness

**Phase:** Implement

**Load before working on any feature-step in this project:** `ailly_two/skills/ailly-skill-eval/SKILL.md` (with `references/method.md`) — the project's own method for skill-eval-suite anatomy, the discovery/invocation axis split, the assertion palette, and the baseline-falsification gate.
It is not registered with Claude Code's `Skill` tool (it lives under `ailly_two/skills/`, not a plugin path); load it by reading the file directly.
`DESIGN.md` at the `ailly_two` repo root is the authoritative schema for `assembly`/`conversation`/`evaluation` YAML — consult it rather than restating it here.

## Purpose

`ailly_two`'s eval harness (assemble → run → eval → report over YAML assemblies, conversations, and evaluation suites) is solid-beta: the architecture already matches the field's converged shape, and its `judge` assertion already exceeds several published best practices.
It is not yet the thing the user needs it to be: a way to change an Ailly skill or add a model with confidence, cheaply, across every provider the team actually uses.
Today, iterating on one skill means paying for the entire suite (`ailly/issues/197`); Bedrock is a routing dead end (`bedrock_from_env` always errors); nothing has confirmed OpenAI or Gemini complete a real round trip; the "ideal matrix of runners" from `domain-driven-design#29` (14 models, 4 providers) exists only as a comment; the `judge` assertion's verdicts are unvalidated against a human; and `report`'s two-run comparison can't tell a real regression from noise.

This project closes each of those gaps.
None alone makes the eval story "production ready" — fast iteration without multi-provider coverage still leaves Bedrock untested; a full matrix without judge calibration still leaves the pass/fail signal unverified — so they ship as one project with one Closing Bell, not as independent patches.

## Prior Art

- **Superpowers' Drill/Gauntlet** drives live coding-agent terminal sessions through a (scenario × agent × credential × OS) matrix, layering an LLM verifier over deterministic checks, sandboxed per agent.
  The matrix-axis and deterministic-plus-judge ideas are already present in `ailly_two`; the terminal-sandboxing concern doesn't transfer because `ailly_two` evals score replayable conversation files against a model API, not a live session.
  The one practice worth adopting outright: a two-speed posture — a fast, small always-run suite, and a separate slow, wide matrix run before declaring victory — rather than trying to make the full 14-model matrix itself fast.
- **`ailly_two`'s own suites are the working precedent**, not a green field: `e2e/patterns-eval/` (`assemblies/{baseline,discovery,invocation}.yaml`, `evals/{baseline,discovery,invocation}.yaml`) already runs the discovery/invocation/baseline-falsification method this project's new suites should follow; `e2e/insurance-claim/` (`assemblies/claim-handler.yaml`, `evals/regression.yaml`) already mixes tool-call, text, and token assertions against a single application.
  Both already have CI (`.github/workflows/e2e-patterns-eval.yml`, `e2e-insurance-claim.yml`) that shells out to `ci.sh`, which itself checks for `ANTHROPIC_API_KEY` (env or project `.env`) and either skips gracefully (`insurance-claim`, exit 0 after the assemble-only path) or hard-fails (`patterns-eval`, which has no assemble-only success path).
  Feature-step C's OpenAI/Gemini/Bedrock credential checks mirror the `insurance-claim` skip pattern.
- **Published frameworks** (promptfoo, OpenAI Evals, DeepEval, Braintrust, LangSmith, Inspect AI) converge on the same four-stage architecture `ailly_two` already has; Inspect AI's Task/Dataset/Solver/Scorer model is the closest analogue.
  None of them implement statistically rigorous run comparison (paired-difference testing, standard-error-of-the-mean) out of the box — Feature-step F is where this project can exceed the field, not just match it.
  None publish a formal "production ready" maturity bar for eval harnesses; the closest is Anthropic's eval-driven-development guidance (small human-labeled samples are fine early, calibrate a judge to >90% agreement before trusting it for release decisions, treat evals as one release-decision input among several).
  Full citations: `docs/research/2026-07-06-A-ailly-evals/public.md`.
- **rig-core / rig-bedrock dependency posture** (full findings: `docs/research/2026-07-06-A-ailly-evals/dependencies.md`): the locked `rig-core 0.37.0` + `rig-bedrock 0.4.6` pair already ships tool calling, streaming, prompt caching, and three Claude-on-Bedrock bugs fixed one version prior.
  Bedrock's gap is entirely local (`bedrock_from_env` unimplemented, feature off by default, no router branch) — Feature-step B is real implementation work, not a smoke test.

## User Journey and Metrics

**Primary journey — the developer this project serves:** they edit a skill's `SKILL.md`, or add a new model to the matrix, and need to know within minutes, not a full-suite runtime, whether they broke discovery or invocation for that skill, on every provider that matters, with a pass/fail signal they can trust.

**Journey today (each broken link maps to a feature-step below):**

1. Edit a skill → must run the *entire* suite to get any signal (Feature A closes this).
2. Want to check the change on a Bedrock-hosted model → `bedrock_from_env` errors unconditionally (Feature B).
3. Want to trust that OpenAI/Gemini actually round-trip, not just that the code compiles → never confirmed live (Feature C).
4. Want to know the change is safe across issue #29's full named model set → no runnable matrix exists (Feature D).
5. Get a `judge` verdict on a subjective case → no evidence the verdict agrees with a human's judgment (Feature E).
6. Compare two runs → only bucket counts, no way to tell signal from noise (Feature F, stretch).
7. Trust that `ailly-skill-eval`'s documented baseline-falsification gate does what it claims → unverified against real suite runs (Feature G).

**Metrics that determine whether the finished project operates within acceptable constraints:**

- A single-skill edit's discovery+invocation feedback loop runs in a small, bounded subset of full-suite time (exact target set in Feature A's own design; directionally: filtered run ≪ full run).
- 14/14 models named in `domain-driven-design#29`, across all 4 providers, each complete one live, successful round trip through `ailly_two`'s CLI.
- The `judge` assertion's verdicts agree with a human labeler's verdicts at ≥90% on a held-out calibration set.
- `report`'s two-run comparison surfaces a statistical significance signal (not just bucket counts) on at least one real historical comparison.
- CI for every provider skips gracefully (not a hard failure) when that provider's credentials are absent, matching the existing `insurance-claim` pattern.
- `ailly-skill-eval`'s documented baseline-falsification gate is confirmed to actually execute and pass today for `patterns-eval` (or its documentation is corrected to match reality).

## Specification

Seven feature-steps.
Each gets its own session folder, `design.md`, feature test, plan, and build/cleanup cycle when work on it starts (per `developer/references/project-cycle.md`, "Plan Steps Are Features") — this document scopes and sequences them; it does not design their internals.

**Feature A — CLI filtering.**
Closes `ailly/issues/197`.
Add a selector to `assemble`/`run`/`eval` so a single skill's affected discovery + invocation cases can be scoped without processing the whole suite.
`assemble` is included even though it's cheap on its own (no model calls) because filtering it lets a developer skip writing conversation files for cases they don't care about, keeping `run`/`eval`'s input scoped without a separate directory-juggling step.
Current gap: `EvalCmdArgs` (`src/cli/eval.rs:33-41`) takes only `suite` + `--over <path>`; there is no `--case`/`--tag`/`--only`.
Selection today only happens by pointing `--over` at a narrower directory.
*No dependencies — start immediately.*

**Feature B — Bedrock engine implementation.**
`open_engine_for_model` (`src/engine/engine.rs:120-140`) has no branch reaching `bedrock_from_env`; `bedrock_from_env` (`src/engine/rig_engine.rs:635-642`, behind a default-off Cargo feature) always returns `EngineError::Provider { message: "rig_engine: not yet implemented" }`.
Implement it against `rig_bedrock::completion::CompletionModel`, add an Ailly-side `"bedrock:"` prefix branch (decided in research: keeps the router's simple prefix-dispatch shape; no clash with `"claude-"` since none of issue #29's Bedrock models are Anthropic's), and turn the feature on by default once implemented. rig-bedrock's `0.4.x` line caps at a `rig-core 0.38.0` requirement incompatible with the current `0.37` pin, but Cargo backtracks to a compatible resolution today, so nothing is broken yet.
Carry forward the risk that a future `cargo update` could silently break that resolution as a note for this feature-step's own design.
*No dependencies — start immediately, parallel with Feature A (disjoint files: `cli/*` vs `engine/*`, no shared contract needed).*

**Feature C — Multi-provider live confirmation.**
Confirm each engine completes a real round trip.
Anthropic: already done.
OpenAI/Gemini: code exists: (`openai_from_env`, `gemini_from_env`, `src/engine/rig_engine.rs:588,613`); confirmation is blocked only on the user's pending credentials, not on code — watch the flagged rough edges.
For OpenAI, watch tool-calling-under-streaming and system-prompt placement, since `messages_to_rig` puts `Role::System` at the head of chat history and the Responses API is mid-churn on exactly that.
For Gemini, watch `Trace.tokens` usage telemetry.
Bedrock: *depends on Feature B.*
*OpenAI/Gemini legs: no code dependency, run whenever credentials land, in parallel with any other feature-step.*
*Bedrock leg: Depends on Feature B.*

**Feature D — Runner matrix.**
Stand up the full `domain-driven-design#29` structure (most likely `assembly` `matrix:` entries per the existing pattern, scoped per provider) with all 14 named models live-confirmed — not a representative subset (decided in research).
*Non-Bedrock rows (10 models, 3 providers): Depends on Feature A (for iteration speed) and Feature C's OpenAI/Gemini legs (for the actual live confirmation Feature D's rows report)* — building and iterating on a 14-entry matrix without filtering means paying full-suite cost on every adjustment, and a matrix row isn't actually live-confirmed until Feature C's corresponding leg has run.
*Bedrock rows (4 models): Depends on Feature B and Feature C's Bedrock leg.*

**Feature E — Judge calibration.**
Measure `ailly_two`'s `judge` assertion's verdict-agreement rate against a human-labeled example set, targeting the ≥90% bar this project's research found.
Operates against existing suites and a new labeled set; touches neither the CLI nor engine routing.
*No dependencies — start immediately, parallel with Features A/B.*

**Feature F — `report` statistical-rigor upgrade (stretch).**
Add paired-difference testing and standard-error-of-the-mean reporting to `compute_comparison` (`src/knowledge/report.rs:61-131`), which today only produces bucket counts (`ComparisonTotals`, lines 29-36).
Also reframe `check_tool_call_order`'s (`src/knowledge/assertions.rs:1302-1324`) rigid subsequence match as an order-insensitive `tool_call_collection` alternative, reusing its `extract_tool_uses`/`tool_use_name` helpers as a multiset comparison — cheap, low-risk cleanup, do opportunistically within this feature-step.
*No hard dependency — can start immediately and develop against existing `patterns-eval`/`insurance-claim` report data; sequence its final validation pass after Feature D lands, to sanity-check the statistics against a real multi-model comparison (soft ordering, not a gate).*

**Feature G — Verify `ailly-skill-eval`'s claims.**
Before any new suite in this project leans on the discovery/invocation/baseline method, confirm it against real behavior: does `patterns-eval`'s baseline-falsification gate (`improved > 0 && regressed == 0`) actually execute and pass today?
Does the documented assertion palette behave as described?
*No dependencies — cheapest step; do first or in the same window as Features A/B, since its outcome affects confidence in every other suite this project builds or extends.*

**Sequencing summary (two-track parallelism — see Alternatives for why over a linear order):**

| Track | Steps | Shape |
|---|---|---|
| Provider capability | A, C(OpenAI/Gemini legs) → D non-Bedrock rows; B → C(Bedrock leg) → D Bedrock rows | A and B start together, disjoint files, no shared contract |
| Quality & rigor | G (recommended first — cheap, no hard dependency) alongside E, F in parallel from day one | Runs independently of the provider track; F's final validation pass follows D |

Both tracks feed the Closing Bell once D reaches 14/14 and E, F, G are complete.

**Release flagging:** Per `developer/references/project-cycle.md`'s default, a project gates behind one release flag until its Closing Bell passes.
**Proposed deviation, flagged for review:** no dedicated flag for this project.
Every feature-step is an additive, opt-in CLI/CI capability with no passive users — nobody is affected by `eval --case` existing until they type it, and Bedrock stays behind its own (already-default-off) Cargo feature until Feature B turns it on deliberately.
There is no live surface a half-built matrix could leak into.
If reviewers disagree, the fallback is a single `evals-production-ready` tracking issue gating the Closing Bell rather than a runtime flag, since there's no runtime behavior to toggle.

## Alternatives

**Sequencing shape.**
Considered three:

1. *Fully linear* (A→B→C→D→E→F→G): safest, no parallel-integration risk, but serializes independent work (E/F/G share no files or contracts with A/B/D) for no reason — slowest wall-clock path.
2. *Two-track parallelism* (recommended, specified above): matches the dependency edges research.md already established (A and C's OpenAI/Gemini legs block D's non-Bedrock rows; B blocks C/D's Bedrock legs) while freeing the quality track to run the whole time.
   Lowest wall-clock cost without inventing false parallelism.
3. *Fully unstructured* (no upfront sequencing beyond the hard blockers): maximizes flexibility, but project-cycle.md requires stating each step's relationship explicitly "so a reader can tell, at a glance, what can start now" — this option under-specifies that on purpose, trading clarity for a small increment of flexibility over option 2.
   Rejected.

**Off-the-shelf vs. build:** No — reconfirmed from research. `ailly_two`'s architecture already matches the field's converged shape; adopting promptfoo/DeepEval/Inspect AI wholesale would mean throwing away an already-solid, already-tailored assertion palette and `judge` design to gain nothing this project's actual gaps (CLI filtering, Bedrock wiring, live confirmation, a runner matrix, judge calibration, report statistics) need from a third party.

**Bedrock model-identifier routing:** Confirmed in research — an Ailly-side `"bedrock:"` prefix, not raw AWS vendor prefixes or mandatory inference-profile ARNs, keeping the router's existing simple-prefix-dispatch shape.

**`tool_call_order` fate:** Rather than removing it, add `tool_call_collection` alongside it (Feature F) — Anthropic's guidance against rigid ordering applies to *most* cases, but genuine sequencing requirements (e.g., a lookup that must precede a write) still exist and deserve the strict assertion.
Reframe as "prefer the collection variant by default," not "delete the order variant."

## Summary

**Deferred to `TASKS.md` at this project's cleanup (not decided here):**

- Superpowers-style workflow-compliance testing of the `developer:*` skill loop itself (as opposed to `ailly_two`'s model-response evals) — explicitly out of scope per research.md; named here again so a future reader doesn't assume it was silently folded in.
- Whether the release-flagging deviation (no dedicated flag) holds up once Feature B (Bedrock) actually lands — revisit if Bedrock support turns out to have a partial/flaky rollout window worth gating.
- Exact numeric target for Feature A's iteration-time metric (this doc states it directionally; Feature A's own design should set and test a concrete bound).

**Not deferred — already resolved and carried forward from research.md** (repeated here so this doc is self-contained at project altitude): CLI filtering is Feature A, first, inside this project (not a standalone pre-project patch); all 14 named models must be live-confirmed, not a representative subset; judge calibration and `report`'s statistical upgrade are both in scope (the latter as a stretch step); the Bedrock routing scheme is the Ailly-side `"bedrock:"` prefix.

**Next steps.**
This is the draft gate: do not continue into `developer:plan` or any implementation skill in this session, even if asked.
Review this `design.md` and `closing-bell.md`, make any edits, then remove the `*Draft 2026-07-06*` marker above and start a new session running `developer:ailly` (or `developer:plan` directly) to move into the project plan phase.

**Closing Bell:** `.ailly/developer/2026-07-06-A-ailly-evals/closing-bell.md`
