# ailly-evals: patterns-eval model matrix report

**Date:** 2026-07-08 **Scope:** live `patterns-eval` discovery + invocation-vs-baseline falsification sweep across every currently-credentialed Anthropic and OpenAI model named in `domain-driven-design#29`'s runner matrix (`e2e/runner-matrix/assemblies/live-confirmation.yaml`).
Google and Bedrock rows are excluded — no `GEMINI_API_KEY` / AWS credentials in `ailly_two/.env` as of this run.

## Result table

Emoji = discovery pass/fail (does the model pick the right `patterns:*` skill from its `description:` alone).
Percentage = the invocation arm's pass-rate delta vs. the no-skill baseline arm, computed from `ailly report`'s per-assertion `Improved`/`Regressed`/`Unchanged` classification (3 assertions per skill: `script`, `judge`, `tokens`), regardless of the discovery outcome — invocation always force-loads the skill.

| Resource | Haiku 4.5 | Sonnet 4.6 | Sonnet 5 | Opus 4.8 | Fable | GPT-5.5 | GPT-5.4 | GPT-5.4-mini |
|---|---|---|---|---|---|---|---|---|
| patterns:newtype | ❌ 0% | ❌ 0% | ✅ 0% | ❌ 0% | ❌ +33% | ❌ +33% | ❌ 0% | ❌ +33% |
| patterns:configuring-logging | ❌ 0% | ❌ 0% | ❌ 0% | ❌ 0% | ❌ +33% | ✅ 0% | ✅ 0% | ✅ 0% |
| patterns:emitting-logs | ❌ 0% | ❌ +33% | ❌ +33% | ❌ -33% | ❌ 0% | ❌ +33% | ✅ +33% | ✅ +33% |

Model routing was verified correct for every cell: each eval report's `model` field echoes the exact requested id (no cross-provider misroute).

## Caveats before trusting these numbers

1. **None of the per-model paired-difference tests reach significance** (α = 0.05; n = 9 paired assertions per model). p-values range 0.17–1.0.
   Treat every percentage as directional signal from a single run, not a proven effect — this suite was never sized for statistical power per model, only for fast regression detection on one pinned model.
2. **Two of the three skills' judges have a known calibration problem**, found independently on 2026-07-07 during this same project's judge-calibration work: `newtype`'s judge is too lenient and `emitting-logs`'/`configuring-logging`'s are too harsh against real human ground truth (42% overall agreement, meets_bar = false).
   A 0% invocation delta or a discovery fail on those skills may partly reflect judge miscalibration, not only model behavior.
   `patterns:newtype`'s and `patterns:emitting-logs`' discovery/invocation cells are the ones most likely affected.
3. **Discovery is deliberately hard by design** — `newtype-vs-evs-order-line` and the `configuring-logging`/`emitting-logs` paired cases exist specifically to probe the two hardest discrimination boundaries in the routing table (per `e2e/patterns-eval/README.md`).
   A ❌ here is expected friction, not necessarily a regression.
4. **Small sample per cell** — one prompt per discovery case, one per invocation/baseline case.
   A single unlucky completion flips a whole cell.

## A real bug found and fixed en route

`ailly_two`'s `RigEngine::complete` (`src/engine/rig_engine.rs`) hardcoded `max_tokens: None` on every outgoing Anthropic request.
Rig's Anthropic provider only supplies a default `max_tokens` for model names in its own built-in table; a model name it doesn't recognize (e.g. `claude-fable-5`) hits a hard `` `max_tokens` must be set for Anthropic `` error instead.
Worse, `ailly run`'s directory-target loop aborts the *entire* batch on the first such per-file engine error, so this silently zeroed out every row after the first alphabetically-sorted failure.

Fixed by setting an explicit `DEFAULT_MAX_TOKENS = 16384` (headroom above the largest existing eval token-budget assertion, 14000) on the outgoing request, extracted into a small pure `build_rig_request` helper with a unit test pinning the value.
Verified via `cargo test --lib` (268 passed) plus every other integration test binary (all green — one unrelated, pre-existing, already-broken **uncommitted** stray file, `tests/eval_static_document.rs`, was excluded; it doesn't compile against the current `EvalCmdArgs` struct and predates this session), and via a live re-run of `e2e/runner-matrix`'s confirmation suite (all 8 target models round-tripped afterward).
Not yet committed — left for the user to review alongside this report before deciding whether it lands on `main_two` directly or through its own feature-step.

## Live confirmation (pre-flight smoke test)

Before spending the full patterns-eval budget, ran `e2e/runner-matrix`'s existing live-confirmation suite (1 short call per model) to catch bad model ids or auth issues cheaply:

- 7/8 clean pass.
- `anthropic-opus-4-8` failed only the exact-marker-text assertion (its reply didn't echo the literal string `AILLY-RUNNER-MATRIX-LIVE`) — a real completion came back, this is prompt-following variance, not a routing or auth failure.
- Also found (unrelated, not fixed): `e2e/runner-matrix/ci.sh`'s `run_provider` is missing the `|| true` guard that `e2e/patterns-eval/ci.sh` already has on its `eval` step — a single failing assertion in one provider's leg aborts the whole script under `set -e` and silently skips every provider queued after it.
  Worth the same one-line fix patterns-eval already carries.

## Where the raw data lives

Per-model conversations and eval reports were merged into `e2e/patterns-eval/runs/` and `e2e/patterns-eval/evals/reports/` (both gitignored, consistent with existing historical run data there) — timestamps `2026-07-08T21-3*`.
Each model's comparison report (`<baseline-id>-vs-<invocation-id>.md`) has the full per-assertion drill-down; each discovery run's `<id>-report.md` has the per-case pass/fail table.

## Not run

Google (Gemini) and Bedrock rows: still blocked on `GEMINI_API_KEY` / AWS credentials, unchanged from prior status.
The runner-matrix and patterns-eval structures both already support adding them the moment credentials land — no code changes needed, only re-running this same sweep with the additional provider legs.
