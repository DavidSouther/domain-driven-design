# Research: Ailly Evals — from solid beta to production-ready

## Topic and Intent

"Get evals freaking solid for Ailly" — take `ailly_two`'s existing eval harness (assemble/run/eval/report over YAML assemblies, conversations, and evaluation suites) from its current solid-beta state to "a verifiably correct approach we can call production ready."
In the user's own framing, this spans: drawing on a competitor's (Superpowers) eval-harness design for inspiration; treating the existing `e2e/` suites as a good start rather than a green field; unblocking fast local iteration (`ailly/issues/197`, filterable test runs); confirming Rig actually drives `ailly_two` against Bedrock and OpenAI/GPT, not just Anthropic; and building toward the "ideal matrix of runners" named in `domain-driven-design#29`'s comment (14 named models across Anthropic, OpenAI, Google, and Bedrock).
Explicitly and firmly out of scope for this topic: the follow-on work refining Ailly's own language — the outstanding Vale style-guide effort and Fable-5 prompt-engineering technique adoption.
Do not begin that work from this session.

## Search/Expand

### What already exists (grounding, not aspiration)

`ailly_two` is further along than "a good start" suggests:

- **CLI**: `assemble` expands a YAML assembly's `matrix:` into one conversation file per parameter binding; `run` fills blank assistant turns by calling a live model; `eval <suite> --over <run-dir>` scores filled conversations against a suite; `report` renders a single-run summary or a two-run improved/regressed/unchanged diff.
  Neither `run` nor `assemble` nor `eval` currently accepts any filter — each takes exactly one target/suite and processes everything under it, confirming `ailly/issues/197` ("Allow filtering to specific tests... running the entire test loop is way too expensive for single skills") describes a real, present gap, not a hypothetical one.
- **Assertion palette** (`src/knowledge/assertions.rs`, ~2,570 lines): `must_call_tool`, `must_not_call_tool`, `tool_call_count`, `tool_call_order`, `text_contains`/`text_not_contains`, `text_matches`, `text_semantic_match`, `json_path`, a token-budget assertion keyed by cache breakpoint, `script`/`program` subprocess checkers, and `judge` (LLM-as-judge).
  This already covers the deterministic-plus-judge layering Superpowers' Drill harness is praised for.
- **The `judge` assertion is already more sophisticated than the "good start" framing implies.**
  It sends a fixed system prompt requiring step-by-step reasoning before a final verdict line (`GRADE: P|F|I` — pass/fail/ **inconclusive**, not a forced binary), and resolves the verdict via a regex that greedily matches the *last* `GRADE:` occurrence — a deliberate prompt-injection mitigation the code's own comment attributes to Inspect AI.
  This already matches or exceeds several practices the expand pass found published (binary-leaning verdict with mandatory chain-of-thought critique per Hamel Husain; an explicit "cannot decide" out per Anthropic's guidance against a judge hallucinating false confidence).
  See `docs/research/2026-07-06-A-ailly-evals/dependencies.md` §"Judge assertion" note and `public.md` §3.
- **Existing e2e suites already do discovery/invocation/baseline structure.**
  `e2e/patterns-eval` sweeps a paired-skill discovery axis and a structural-invocation axis, then falsifies both against a no-skill baseline arm (`improved`/`regressed`/`unchanged_pass`/`unchanged_fail` buckets, gated on `improved > 0 && regressed == 0`).
  `e2e/insurance-claim` covers a single-prompt application with a `regression.yaml` suite mixing tool-call, text, and token-budget assertions.
  Both already have CI wiring (`ci.sh`, GitHub Actions workflows) that skip the live-model half gracefully when `ANTHROPIC_API_KEY` is absent, so the pattern this project needs for OpenAI/Gemini/Bedrock (skip-with-notice rather than fail on missing credentials) already has a working precedent to extend, not invent.
- **A skill for this already exists and is unindexed by the current session.**
  `ailly_two/skills/ailly-skill-eval/SKILL.md` documents exactly the discovery/invocation/baseline method the `patterns-eval` suite exemplifies, generalized to any skillset.
  See Libraries & Skills below — this must be loaded, not reinvented, by downstream phases.

### Competitor inspiration (Superpowers' Drill/Gauntlet)

Superpowers' harness drives real coding-agent CLI sessions (via tmux) and layers an LLM verifier over deterministic post-checks, run as a (scenario × agent × credential × OS) matrix, sandboxed per agent, in Docker for full runs.
The most directly transferable ideas — matrix axes, deterministic-plus-judge layering, sandboxed/skip-gracefully CI — are **already present** in `ailly_two`'s design.
The parts that don't transfer directly: Superpowers tests *workflow compliance* of a coding agent operating a real terminal session (did the right skill trigger, did it stop to ask, did it try to game the reviewer), whereas `ailly_two`'s evals test *model response quality* against a fixed, replayable conversation file — there is no live terminal session or tmux-style sandboxing concern here, because there's no session to sandbox.
Where Superpowers is genuinely a step ahead: full-matrix runs are explicitly slow (3–30+ min per scenario) and they've made peace with that by keeping a separate, lighter internal loop before shipping a change — worth adopting the same two-speed posture (a fast, small always-run suite; a slow, wide matrix run before declaring victory) rather than trying to make the full 14-model matrix fast.

### Public prior art on eval-harness maturity (full findings: `docs/research/2026-07-06-A-ailly-evals/public.md`)

- **Architecture**: every framework surveyed (promptfoo, OpenAI Evals, DeepEval, Braintrust, LangSmith, Inspect AI) converges on the same four stages `ailly_two` already has.
  Inspect AI's Task/Dataset/Solver/Scorer model is architecturally the closest published analogue.
- **Nondeterminism is structural, not a tooling gap.**
  Even at temperature 0, production LLM serving is not bitwise-reproducible (batch-invariance failures in inference kernels — Thinking Machines Lab measured 80 distinct completions from 1000 identical calls).
  This means tolerance/variance handling belongs in the design of `report`, not as an afterthought.
- **No commodity framework does statistically rigorous run comparison.**
  Anthropic's own research guidance (paired-difference testing, standard-error-of-the-mean reporting, clustered SEs) is not implemented by promptfoo, DeepEval, Braintrust, or LangSmith out of the box — this is a concrete opportunity for `report` to exceed the field rather than merely match it, but it is optional polish, not a gate.
- **LLM-judge best practice**: prefer deterministic assertions first, judge only where code can't reach (already Ailly's shape); calibrate the judge against one principal domain expert's labels with a >90% agreement target *before* trusting it for release decisions — this calibration step has not been done for Ailly's `judge` assertion and is a real gap, distinct from the assertion's already-solid mechanical design.
- **Anthropic explicitly warns against rigid tool-call-order assertions** as "too rigid... overly brittle" — direct, actionable feedback on when to reach for `ailly_two`'s existing `tool_call_order` assertion versus the order-insensitive alternatives.
  Reframe as `tool_call_collection`, to allow for general tool call requirements without being dogmatic on their ordering.
- **No formal "production ready" maturity model exists for eval harnesses.**
  The closest published bar is Anthropic's "eval-driven development" practice: start with 20–50 real-failure-derived tasks (small samples are fine — effect sizes are large early on), track pass@k and pass^k, and treat evals as one of several release-decision inputs (alongside monitoring, A/B tests, manual transcript review) rather than the sole gate. "0% pass@100 usually signals a broken task, not an incapable agent" — a suite isn't trustworthy until someone has read enough transcripts to rule out grader bugs.
- **Multi-provider abstraction pitfalls** are real and specific: OpenAI returns tool-call arguments as a JSON string while Anthropic/Gemini return parsed objects; JSON-schema strictness differs (Gemini rejects bare `items: {}`); temperature/reasoning constraints conflict across providers (Anthropic requires `temperature=1` under extended thinking; OpenAI's o3/GPT-5 reject `temperature` outright); only Anthropic requires explicit cache-breakpoint markers; and Bedrock's Converse API is a *third* schema on top of native Anthropic, with ARN-based model IDs and event-stream framing. `rig-core` is already `ailly_two`'s normalization layer for exactly this — the question is whether it's actually wired for all four families (see below), not whether to build a new one.

### Dependency deep-dive: rig-core / rig-bedrock (full findings: `docs/research/2026-07-06-A-ailly-evals/dependencies.md`)

This is the single most decision-relevant finding from this research pass:

**`bedrock_from_env` is a local wiring gap, not an upstream immaturity problem.**
`ailly_two`'s `Cargo.lock` already resolves `rig-core 0.37.0` + `rig-bedrock 0.4.6` — a version pair that ships tool calling (a parallel-tool-call-drop bug fixed one version earlier, in 0.4.5), streaming, prompt caching, OpenTelemetry tracing, structured output, and three Claude-on-Bedrock reasoning/caching bugs found *and fixed* in 0.4.5, one version before the one already locked.
Only one open Bedrock-tagged issue exists upstream (a bearer-token auth feature request, not a blocker).
The actual gaps are entirely local: `bedrock_from_env` unconditionally returns `EngineError::Provider { message: "rig_engine: not yet implemented" }`, the `bedrock` Cargo feature is off by default, and `open_engine_for_model`'s prefix router (`"claude-"`, `"gpt-"`, `"gemini-"`) has no branch that would ever reach `bedrock_from_env` even if it worked.
**This means "confirm Rig works for Bedrock" (item 4 in the task) is really "implement Bedrock support," not "run a smoke test."**

Two real but narrower risks, both worth carrying into design/plan:

1. **Version-pin fragility.**
   rig-bedrock unified its versioning with rig-core starting at `0.38.1`; its old `0.4.x` line stopped at `0.4.7`, which itself requires `rig-core 0.38.0` (incompatible with `ailly_two`'s `rig "0.37"` pin).
   Cargo currently backtracks to the compatible `0.4.6`, but this is a narrow, silent window — a future `cargo update` bumping one crate without the other could break resolution with no warning until the build fails.
2. **OpenAI Responses API is the most actively-churned integration surface** in `rig-core` right now (an in-flight breaking change moves system instructions to a new top-level field, exactly the code path `ailly_two`'s `messages_to_rig` touches by placing `Role::System` messages at the head of chat history) — worth stress-testing tool-calling-under-streaming and system-prompt delivery specifically during OpenAI live-key confirmation.
   Gemini's rough edge is usage/telemetry counters, worth checking `Trace.tokens` values specifically during Gemini confirmation.

## Libraries & Skills

**Before doing any work in this feature, load these skills via the Skill tool:**

- **`ailly-skill-eval`** (`ailly_two/skills/ailly-skill-eval/SKILL.md`, with `references/method.md` for the long-form rationale) — the project's own, already-written method for building/regression-testing a skill-eval suite: project anatomy (`context/skills/`, `assemblies/`, `prompts/`, `evals/`, `runs/`), the discovery/invocation axis split, the assertion palette per axis, and the baseline-arm falsification gate (`improved > 0 && regressed == 0`).
  Any new eval suite this project adds (e.g. for the runner matrix) should follow this method rather than inventing a new project shape.
  This is the Astrolabe-shaped finding this research pass exists to catch: it would have been easy to miss a skill living under `ailly_two/skills/` rather than a `.claude/skills/` or plugin path.
- No published third-party agentic skill exists for `rig-core`, `rig-bedrock`, promptfoo, DeepEval, or Inspect AI — none of the public-research sources surfaced a shipped `SKILL.md`/MCP server for any of them.
  Design/plan should consult their official docs directly (cited in `docs/research/2026-07-06-A-ailly-evals/public.md` and `dependencies.md`) rather than expect a skill to load.
- **`ailly-skill-eval` is unverified.**
  This research pass found the skill and read its description of the discovery/invocation/baseline method, but did not check that description against what the existing suites actually do at runtime (e.g., does the baseline-arm falsification gate the skill describes actually execute and pass today, for both `patterns-eval` and any other suite that claims to use it?
  Does every assertion the skill's palette lists actually behave as documented?).
  Treat the skill's own text as a claim, not a verified fact, until a feature-step in this project spot-checks it against real suite runs.
  See Scope.
- `DESIGN.md` (repo root of `ailly_two`) is the authoritative schema reference for `conversation`, `assembly`, and `evaluation` YAML — the `ailly-skill-eval` skill explicitly defers to it rather than restating it, and design/plan should do the same.

## Falsification/Refine

**Size: project, not a single feature.**
Per `developer/references/project-cycle.md`, this qualifies as project-shaped: several features that only deliver value as a unified whole toward the stated goal ("production ready"), no one of which alone would let the user call the eval story solid.
Candidate feature-steps surfaced by this research (final naming/sequencing is the Design phase's job, not fixed here):

1. **CLI filtering** (closes `ailly/issues/197`) — scope `assemble`/`run`/`eval` to specific conversation(s)/case(s).
   No dependencies; explicitly called out by the user as wanted "right away" because every other feature-step's iteration speed depends on it.
   **Decided: Feature A, first, no deps, inside this project's plan** (not pulled out as a standalone pre-project patch).
2. **Bedrock engine implementation** — a real `bedrock_from_env` built on `rig_bedrock::completion::CompletionModel`, plus a routing branch in `open_engine_for_model`.
   **Decided: Bedrock models are addressed by an Ailly-side `"bedrock:"` prefix** (e.g. `bedrock:meta.llama3-3-70b-instruct-v1:0`), keeping the router's simple prefix-dispatch pattern and passing the remainder straight through to `rig-bedrock` as a raw AWS model ID or inference-profile ARN.
   No clash with the existing `"claude-"` branch: none of issue #29's named Bedrock models (Llama 3.3, Llama 4 Scout, Mistral Large 3, Cohere R+) are Anthropic.
3. **Multi-provider live confirmation** — once keys exist, confirm `anthropic_from_env` (already done), `openai_from_env`, `gemini_from_env`, and (post feature-step 2) `bedrock_from_env` each complete a real round trip.
   Depends on feature-step 2 for the Bedrock leg; the OpenAI/Gemini legs are blocked only on the user's pending credentials, not on code.
4. **Runner matrix** — build the `domain-driven-design#29` "ideal matrix of runners" as an actual runnable structure (most likely `assembly` `matrix:` entries following the existing pattern, scoped per provider).
   **Decided: all 14 named models must be live-confirmed for this feature-step to be done** — not a representative subset.
   Depends on feature-step 2 for the Bedrock leg; can start for Anthropic/OpenAI/Gemini once step 1 lands.
5. **Judge calibration** — measure `ailly_two`'s `judge` assertion's verdict-agreement rate against a human-labeled set of examples, per the >90%-agreement-before-trusting-it bar this research found.
   **Decided: in scope as a feature-step of this project**, not spun out as a separate follow-on.
6. **`report` statistical-rigor upgrade** — paired-difference testing and standard-error-of-the-mean reporting on two-run comparisons, per Anthropic's published guidance.
   **Decided: in scope as a stretch feature-step** of this project.
7. **Verify `ailly-skill-eval`'s claims** against actual suite behavior (see Libraries & Skills and Scope) — a small, cheap feature-step or a check folded into feature-step 4's matrix-building work.

**Off-the-shelf check**: no, adopting promptfoo/DeepEval/Inspect AI wholesale is not proposed or warranted — `ailly_two`'s own architecture already matches their converged shape, its assertion/judge design already matches or exceeds several of their documented best practices, and the actual gaps found (CLI filtering, Bedrock wiring, live multi-provider confirmation, a runner matrix) are Ailly-specific integration work no off-the-shelf tool does for a bespoke Rust CLI with its own YAML schemas.

**Smallest version that still meets the stated intent — superseded by explicit user decision.**
This research's first pass proposed a smaller slice (one model per provider, judge calibration and `report` statistics deferred to `TASKS.md`), reasoning from the public research's own bar that "production ready" is an evidenced practice rather than an exhaustive matrix.
The user reviewed that framing and explicitly chose the larger scope instead: full 14-model coverage, judge calibration, and `report` statistics are all in this project (see Resolved Decisions).
This project is accordingly larger than research's initial recommendation — expect a project plan with roughly 6–7 feature-steps rather than 3–4, and size the timeframe (Design phase should estimate) accordingly.

## Scope

**In scope for this project:**

- `ailly/issues/197` CLI filtering, as Feature A.
- Real Bedrock engine implementation (constructor + router branch on an Ailly-side `"bedrock:"` prefix), independent of whether AWS credentials are available yet to test it live.
- Live confirmation of OpenAI and Gemini engines against real keys once the user supplies them (code is already written; this is verification, per `dependencies.md`'s flagged rough edges to watch: OpenAI tool-calling-under-streaming and system-prompt delivery, Gemini token/usage telemetry).
- Standing up the full runner-matrix structure keyed to `domain-driven-design#29`'s named models, with all 14 models live-confirmed across all 4 providers — not a representative subset.
- A judge-calibration pass: human-labeled examples, measured agreement rate against `ailly_two`'s `judge` assertion, against the >90% bar this research found.
- `report`'s statistical-rigor upgrade: paired-difference testing and standard-error-of-the-mean reporting on two-run comparisons.
- Applying the concrete, low-cost feedback surfaced by this research to existing/new suites where it's cheap to do now: preferring order-insensitive tool assertions over `tool_call_order` except where sequencing is a genuine correctness requirement.
- **Verifying `ailly-skill-eval`'s claims against actual behavior** before design/plan treat it as authoritative: confirm the baseline-arm falsification gate it describes actually runs and passes today (at minimum for `patterns-eval`), and spot-check that the assertion palette it lists behaves as documented.
  The user flagged this skill's trustworthiness as unconfirmed rather than assumed — this project should settle that, not defer it further.

**Out of scope for this project** (confirmed explicitly by the user; do not start even if it seems related):

- Vale style-guide voice work.
- Fable-5 prompt-engineering technique adoption (`platform.claude.com` prompting-Fable-5 guidance).

**Deferred, not decided as in/out — flagged for the Design phase or `TASKS.md`:**

- Superpowers-style workflow-compliance testing of the `developer:*` skill loop itself (as opposed to `ailly_two`'s model-response evals) — the user's framing throughout is about `ailly_two` the tool, not about testing whether Claude Code sessions running Ailly's own skills follow the intended workflow discipline.
  Named here so it isn't silently assumed in or out later.

## Resolved Decisions

**Resolved by this research:**

- This is project-shaped work (seven feature-steps that only add up to "production ready" together), not a single feature or a bug fix.
- "Confirm Rig works for Bedrock" is not a smoke test — it requires real implementation work (`bedrock_from_env` + router branch); the upstream crate is not the blocker.
- The existing `judge` assertion design (CoT-then-verdict, ternary P/F/I, prompt-injection-resistant greedy-last-line parsing) already reflects current best practice; the real, still-open gap is calibration evidence, not assertion redesign.
- No off-the-shelf harness replaces this work; `ailly_two`'s own architecture is already the right shape per the field's converged practice.
- Superpowers-style live-session/tmux sandboxing does not transfer directly, because `ailly_two` evals score replayable conversation files against a model API, not a live terminal session — there is no session to sandbox.
- `ailly-skill-eval`'s described method is a claim to verify, not a fact to build on — the user asked that this project confirm it against real suite behavior rather than trust its own documentation.

**Resolved with the user, 2026-07-06:**

1. **Feature-step sequencing**: CLI filtering (issue #197) is Feature A inside this project's plan — not pulled out as a standalone pre-project patch.
2. **Runner-matrix coverage target**: all 14 models named in issue #29 must be live-confirmed across all 4 providers for this project's Closing Bell — not a representative subset.
3. **Judge calibration**: in scope as a feature-step of this project, not spun out as a separate follow-on.
4. **`report`'s statistical-rigor upgrade** (paired-difference + SEM): in scope as a stretch feature-step of this project.
5. **Bedrock model-identifier routing scheme**: an Ailly-side `"bedrock:"` prefix (e.g. `bedrock:meta.llama3-3-70b-instruct-v1:0`), keeping the router's existing simple prefix-dispatch pattern rather than keying off raw AWS vendor prefixes or requiring inference-profile ARNs.

No open questions remain from this research pass.
The project is larger than research's own initial "smallest version" recommendation (see Falsification/Refine) — that tradeoff was surfaced and the user chose full scope deliberately.

## Sources

- [`.ailly/prompts/superpowers_evals`](../../prompts/superpowers_evals) — internal notes on Superpowers' Drill/Gauntlet harness.
- `ailly/issues/197` — "[ailly_two] Allow filtering to specific tests," github.com/DavidSouther/ailly/issues/197.
- `domain-driven-design#29` comment — github.com/DavidSouther/domain-driven-design/issues/29#issuecomment-4879596890, the "ideal matrix of runners" (14 models, 4 providers).
- Local source read directly: `ailly_two/Cargo.toml`, `Cargo.lock`, `src/engine/engine.rs`, `src/engine/rig_engine.rs`, `src/knowledge/assertions.rs`, `README.md`, `DESIGN.md`, `e2e/insurance-claim/**`, `e2e/patterns-eval/README.md`, `skills/ailly-skill-eval/SKILL.md`, `.github/workflows/e2e-*.yml`.
- Full IEEE-style source lists with per-claim citations: [`docs/research/2026-07-06-A-ailly-evals/public.md`](../../../docs/research/2026-07-06-A-ailly-evals/public.md) (eval-framework prior art, nondeterminism, judge reliability, production-readiness bar, multi-provider pitfalls) and [`docs/research/2026-07-06-A-ailly-evals/dependencies.md`](../../../docs/research/2026-07-06-A-ailly-evals/dependencies.md) (rig-core/rig-bedrock maturity, OpenAI/Gemini rough edges).
