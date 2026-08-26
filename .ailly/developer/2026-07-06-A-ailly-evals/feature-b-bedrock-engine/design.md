# Design: Bedrock Engine Implementation

**Feature-step B of the project** `.ailly/developer/2026-07-06-A-ailly-evals/` (`developer/skills/ailly/references/shapes/project/project-cycle.md`).
Closes the Bedrock leg of `domain-driven-design#29`'s "ideal matrix of runners" (14 models, 4 providers).
Repo: `/Users/david.souther/devel/davidsouther/ailly/ailly_two` (branch `main_two`).

**Load before working on this feature-step:** `ailly_two/skills/ailly-skill-eval/SKILL.md` (with `references/method.md`) — the project's method for skill-eval-suite anatomy (discovery/invocation axes, assertion palette, baseline-falsification gate).
`DESIGN.md` at the `ailly_two` repo root is the authoritative schema for `assembly`/`conversation`/`evaluation` YAML.
Neither is load-bearing for this particular feature-step's own content (it touches `src/engine/*`, not the YAML schemas or a skill-eval suite), but both remain in force for the project as a whole per the parent `design.md`.

## Purpose

`open_engine_for_model` (`src/engine/engine.rs:120-140`) is Ailly's provider router: it inspects a conversation's `meta.model` prefix and dispatches to the matching `*_from_env` constructor.
Today it recognizes `"claude-"`, `"gpt-"`, and `"gemini-"` — nothing else, including any Bedrock-shaped id, falls through to `EngineError::ModelNotFound`.
Separately, `bedrock_from_env` (`src/engine/rig_engine.rs:635-642`) already exists as a function signature, gated behind a default-off `bedrock` Cargo feature, but its body unconditionally returns `EngineError::Provider { message: "rig_engine: not yet implemented" }` regardless of input.
Four named models in issue #29's runner matrix (Llama 3.3, Llama 4 Scout, Mistral Large 3, Cohere R+) are Bedrock-hosted; none of them can complete even a routing attempt today, let alone a live call.
This feature-step closes both gaps — the missing router branch and the unimplemented constructor — so a `bedrock:`-addressed model id reaches a real `rig_bedrock::completion::CompletionModel` the same way a `claude-`/`gpt-`/`gemini-` id already reaches its provider today.

This is real implementation work, not a smoke test: the constructor has to actually build an AWS Bedrock client and hand it to `RigEngine`.
It is *not*, however, large surface-area work — the finding this design's Prior Art section below establishes is that `RigEngine<M>`'s generic `complete` implementation (message translation, trace population, error mapping) already works for any `M: rig::completion::CompletionModel`, and `rig_bedrock::completion::CompletionModel` satisfies that bound out of the box.
Feature B is exactly two additions: one constructor body, one router branch.

Live confirmation against real AWS credentials is explicitly **not** this feature-step's job — no AWS credentials are available yet (per project memory, only Anthropic keys are confirmed as of 2026-07-06).
That live round trip is the parent project's Feature C (Bedrock leg), which depends on this one.
This feature-step's job is to close the *local* wiring gap: prove the routing and construction seam works, so Feature C has something to actually call once credentials land.

## Prior Art

**The three existing `*_from_env` constructors share one shape** (`src/engine/rig_engine.rs:554-627`): read one required provider API-key env var via `read_required_key`, which fails fast with `EngineError::Auth` *before* any client is built or network touched; build the provider's Rig client with that key; call `.completion_model(model)`; wrap the result in `RigEngine::new(model, engine_name, model)`.
This eager-key-read-before-client-build ordering is exactly what makes `tests/engine_routing.rs`'s "recognised but keyless" idiom possible — a test can clear an env var and assert a deterministic, offline `Auth` failure.
This is the idiom research flagged to mirror, and I read `tests/engine_routing.rs`, `src/engine/engine.rs`'s own unit tests, and `src/engine/rig_engine.rs`'s `openai_from_env_without_key_fails_with_auth`/`gemini_from_env_without_key_fails_with_auth` tests in full before writing this design.
As detailed below, Bedrock's own credential model breaks the "eager key read" half of this idiom — a finding this design surfaces rather than papers over.

**`RigEngine<M>` is already provider-agnostic.**
`messages_to_rig`, `content_from_rig_choice`, `trace_from_rig`, and `engine_error_from_rig` (`src/engine/rig_engine.rs`) operate entirely on Rig's own `rig::completion::*` types, not on any per-provider type.
`RigEngine<M>`'s `EngineProvider` impl is bounded only by `M: rig::completion::CompletionModel + Clone + Send + Sync + 'static, M::Response: Send` — the same bound every existing provider model already satisfies.
Verified against `rig-bedrock`'s actual source (`crates/rig-bedrock/src/completion.rs` at tag `rig-bedrock-v0.4.6` in `0xPlaygrounds/rig`): `CompletionModel` there is `#[derive(Clone)]`, its `type Response = AwsConverseOutput`, and it implements `rig_core::completion::CompletionModel` with the standard `completion(&self, CompletionRequest) -> Result<CompletionResponse<AwsConverseOutput>, CompletionError>` signature — the identical trait Anthropic/OpenAI/Gemini's models implement.
No adapter-level changes are needed anywhere in `rig_engine.rs` beyond the one new constructor.

**`rig-bedrock`'s client construction is verified, not assumed.**
I read `crates/rig-bedrock/src/client.rs` at tag `rig-bedrock-v0.4.6` directly (the version this repo's `Cargo.lock` already resolves) rather than trusting docs.rs's AI-generated summaries alone.
The load-bearing finding:

```rust
impl ProviderClient for Client {
    type Input = Nothing;
    type Error = rig_core::client::ProviderClientError;
    fn from_env() -> Result<Self, Self::Error> { Ok(Client::new()) }   // always succeeds
    ...
}
impl CompletionClient for Client {
    type CompletionModel = CompletionModel;
    fn completion_model(&self, model: impl Into<String>) -> Self::CompletionModel {
        CompletionModel::new(self.clone(), model)                      // also infallible
    }
}
```

`Client::from_env()` never inspects AWS credentials — it just allocates an empty `OnceCell` (`Client::new()`).
Credential resolution (`aws_config::load_from_env().await`, walking env vars → shared profile → SSO → IMDS role) happens lazily, once, inside `get_inner()`, which is only called from `CompletionModel::completion()` at the moment of a real API call.
This is a materially different shape than Anthropic/OpenAI/Gemini's single-required-env-var-checked-eagerly pattern, and it is why this design's Specification and the feature test diverge from the `gpt-5-turbo`/`gemini-3-pro` "keyless" idiom rather than reproducing it verbatim (see Alternatives).

**`AWS_BEARER_TOKEN_BEDROCK` is already handled, with zero code changes needed, by the exact call `rig-bedrock` already makes.**
Amazon Bedrock API keys — a bearer-token alternative to full IAM/SigV4 credentials, short-term (≤12h, SigV4-derived) or long-term (fixed-expiration, IAM-user-backed) — are a real, documented AWS mechanism ([Bedrock API keys](https://docs.aws.amazon.com/bedrock/latest/userguide/api-keys.html), [Using an API key](https://docs.aws.amazon.com/bedrock/latest/userguide/api-keys-use.html)): "the Amazon Bedrock service recognizes the environment variable `AWS_BEARER_TOKEN_BEDROCK`."
This is a separate Smithy `httpBearerAuth` scheme, not a value the generic SigV4 credential-provider chain interprets on its own — each AWS SDK needed explicit codegen support to recognize it (confirmed by counter-example: the JS v3 SDK lacked it and required a manual workaround, [aws-sdk-js-v3#7204](https://github.com/aws/aws-sdk-js-v3/issues/7204)).
The Rust SDK gained this support via `smithy-rs`'s `EnvironmentTokenProviderDecorator` ([`smithy-rs#4241`](https://github.com/smithy-lang/smithy-rs/pull/4241)), shipped in `aws-sdk-bedrockruntime 1.100.0` (2025-08-05): once that version or later is in play, setting `AWS_BEARER_TOKEN_BEDROCK` makes any client built the standard way (`aws_config::...load()` → `Client::new(&sdk_config)`) automatically prefer the bearer-token `httpBearerAuth` scheme over SigV4 — confirmed by the SDK's own test suite (`sdk/bedrockruntime/tests/environment_token_provider.rs`), including that this preference only loses to an *explicit* in-code `.auth_scheme_preference(...)`/`.token_provider(...)` override, never to an env-set SigV4 credential merely being present too.
Checking `rig-bedrock`'s own `Cargo.lock` at the pinned tag `rig-bedrock-v0.4.6` confirms it resolves `aws-sdk-bedrockruntime 1.124.0`, `aws-config 1.8.13`, `aws-credential-types 1.2.11` — all well past the 1.100.0 threshold — and its `client.rs` calls exactly `aws_config::load_from_env().await` then `aws_sdk_bedrockruntime::Client::new(&config)`, the same "happy path" the AWS changelog documents as sufficient.
**Conclusion: `bedrock_from_env`, as already specified below, already works for and automatically prefers `AWS_BEARER_TOKEN_BEDROCK` over standard AWS credentials whenever it is set — this is a property of the pinned dependency versions and the way `rig-bedrock` already calls them, not something this feature-step needs to implement, test differently, or guard.**
The only action this finding calls for is documentation: `bedrock_from_env`'s doc comment should say so explicitly, since nothing about the function's own code would otherwise tell a reader this works (see Specification item 2).

**Version pin, verified against the real crate history, not just Cargo.lock's current snapshot.**
`Cargo.toml` pins `rig = { version = "0.37", package = "rig-core" }` and `rig-bedrock = { version = "0.4", optional = true }`; `Cargo.lock` resolves `rig-core 0.37.0` + `rig-bedrock 0.4.6` today, confirming the parent research's claim.
I walked `0xPlaygrounds/rig`'s tag history to understand *why* this is stable right now and exactly where it stops being stable: `rig-bedrock-v0.4.7` is the last release before that crate's versioning unifies with `rig-core`'s own version number (`rig-bedrock-v0.4.7`'s manifest requires `rig-core = "0.38.0"`, incompatible with this repo's `rig = "0.37"` requirement).
A caret requirement (`^0.4`, i.e. `>=0.4.0, <0.5.0`) can never resolve to a post-unification `rig-bedrock` version like `0.38.1`, because `0.38.1` falls outside `<0.5.0`.
Two consequences worth being precise about, since the parent research's "a future `cargo update` could silently break this" framing slightly overstates the immediate risk:

- A bare `cargo update` run today, with `Cargo.toml` unedited, cannot regress: Cargo's resolver will keep landing on `rig-bedrock 0.4.6` (the highest `0.4.x` release still compatible with `rig-core "0.37"`) because `0.4.7` is infeasible against the existing `rig` requirement.
- The actual risk window opens the next time someone edits `Cargo.toml` to bump `rig`'s version requirement past `0.37` for an unrelated reason (e.g., chasing an OpenAI Responses API fix, per the parent research's own flagged rough edge).
  If that bump lands without a matching look at `rig-bedrock`'s compatible range, Cargo's resolver will fail *loudly* at build time — not silently — because no `rig-bedrock` version simultaneously satisfies both a bumped `rig-core` requirement above `0.38.0` and the un-bumped `rig-bedrock = "0.4"` cap.
  This is a loud, immediate build failure, not a latent behavioral bug; see Alternatives for why a source comment at the point of risk is this feature-step's chosen guard.

**`domain-driven-design#29`'s exact Bedrock list**, read directly from the issue comment: Llama 3.3, Llama 4 Scout, Mistral Large 3, Cohere R+.
Cross-referencing `rig-bedrock`'s exported model-id constants (`crates/rig-bedrock/src/completion.rs`), three of the four have exact matches: `meta.llama3-3-70b-instruct-v1:0`, `meta.llama4-scout-17b-instruct-v1:0`, `cohere.command-r-plus-v1:0`.
"Mistral Large 3" has no exact constant in the `0.4.6` list (the newest exported Mistral constant is `mistral.mistral-large-2407-v1:0`); since the router does no format validation on the string after `"bedrock:"` (see Specification), pinning the exact current AWS model id for "Mistral Large 3" is not blocked on this feature-step — it is explicitly Feature D's (runner matrix) job, once that model's real Bedrock id or inference-profile ARN is confirmed.

## User Journey and Metrics

**Journey:** A developer writes or edits a conversation/assembly with `model: bedrock:meta.llama3-3-70b-instruct-v1:0` (or any other Bedrock model id or inference-profile ARN prefixed with `bedrock:`) and runs `ailly run` against it.
Today, `open_engine_for_model` returns `EngineError::ModelNotFound` immediately — the run cannot even attempt a call.
After this feature-step, the same id resolves through the router to a real `RigEngine<rig_bedrock::completion::CompletionModel>`, and `ailly run` proceeds exactly as it does for any other provider: it calls `.complete()`, which authenticates via whichever mechanism is present — preferring a Bedrock API key (`AWS_BEARER_TOKEN_BEDROCK`) automatically when set, falling back to the standard SigV4 credential chain (env vars, shared profile, SSO, IMDS role) otherwise, per Prior Art — and either fills the blank assistant turn or surfaces a live engine error (`Auth`, `Timeout`, `Provider`, etc.) through the same `RunCmdError::Engine` path every other provider already uses.
Confirming the *live* half of that journey (a real credential of either kind, a real filled response) is Feature C's job, not this one's.

**Metrics that determine whether this feature-step is done:**

- `open_engine_for_model` resolves every `"bedrock:"`-prefixed id to `Ok(_)`, never `Err(ModelNotFound)` — verified offline, without AWS credentials, by the feature test.
- An id that is *not* `"bedrock:"`-prefixed (including a bare Bedrock-shaped AWS model id with no Ailly prefix) is unaffected: still `Err(ModelNotFound)`, exactly as before this feature-step.
  The change is additive to the router, not a loosening of existing dispatch.
- `bedrock_from_env` no longer returns the hardcoded `"not yet implemented"` stub for any input.
- The `bedrock` Cargo feature builds and (per the parent design's explicit instruction, not re-litigated here) is turned on by default, so a plain `cargo build`/`cargo test` includes Bedrock support without an extra flag — see Specification for how this coexists with the project's existing `mise run test`/`check`/`lint` tasks, which already pass `--all-features` today regardless.
- `bedrock_from_env` works for and automatically prefers `AWS_BEARER_TOKEN_BEDROCK` over standard AWS credentials when both are present — a property already true of the pinned `rig-bedrock`/AWS-SDK versions and the plain `aws_config::load_from_env()` call this feature-step's constructor uses (see Prior Art), verified live during Feature C rather than by this feature-step's offline test (constructing the engine never touches either credential mechanism; the preference only actually fires inside the AWS SDK at the first real API call).

**Failure mode carried forward, not fixed here:** because AWS credential resolution is deferred to the first live call (see Prior Art), a misconfigured or missing-credentials environment will not be caught at construction time the way a missing `ANTHROPIC_API_KEY` is.
It will surface only when `ailly run` actually attempts a completion, as whatever `EngineError` `engine_error_from_rig` classifies the resulting AWS SDK error into (most likely `Auth` for a 403-shaped rejection, `Provider` for anything else, or `Timeout` if credential resolution itself hangs against an unreachable IMDS endpoint).
This is a genuine, if minor, user-experience gap relative to the other three providers (a typo'd Bedrock model id or a completely absent AWS credential chain both look identical until the live call), named here so Feature C's live-confirmation pass knows to watch for it and so it is not mistaken for an oversight later.

## Specification

1. **`Cargo.toml`.**
   Add `bedrock` to a new `default = ["bedrock"]` array under `[features]`, matching the parent design's explicit "turn the feature on by default once implemented" instruction.
   Keep `rig-bedrock` itself as a named, still-independently-toggleable optional dependency (not folded into the unconditional `[dependencies]` block) — a consumer building with `--no-default-features` still gets a smaller dependency graph without the AWS SDK.
   Add a short comment directly on the `[dependencies.rig-bedrock]` stanza and on the `rig` (`rig-core`) line stating the version-pin coupling from Prior Art, so the next person bumping `rig`'s requirement sees the warning at the exact edit point, before hitting a resolver failure.

2. **`bedrock_from_env` (`src/engine/rig_engine.rs`).**
   Replace the hardcoded body with the same three-step shape the other three constructors use, minus the eager key check (there is no single required env var to check — see Prior Art and Alternatives):
   - `rig_bedrock::client::Client::from_env()` (via the `ProviderClient` trait, already imported as `rig::client::CompletionClient` today — add `ProviderClient` to that same `use` line) to build the client.
     Map its `Err` arm (a `rig_core::client::ProviderClientError`; unreachable in practice today per Prior Art's `Ok(Client::new())` finding, but still required for type correctness) to `EngineError::Provider`.
   - `client.completion_model(model)` (via `CompletionClient`, infallible) to get the `rig_bedrock::completion::CompletionModel`.
   - `RigEngine::new(completion_model, "bedrock", model)`, matching the `engine_name` convention (`"anthropic"`, `"openai"`, `"gemini"`) that already flows into the `gen_ai.system` trace attribute.
   No change to the function's public signature (`pub fn bedrock_from_env(model: &str) -> Result<RigEngine<rig_bedrock::completion::CompletionModel>, EngineError>`) is required.
   Update the doc comment to state plainly that the constructor supports and automatically prefers `AWS_BEARER_TOKEN_BEDROCK` (an Amazon Bedrock API key) over the standard SigV4 credential chain when both are present, per Prior Art — this is already true of the exact call the constructor makes, but is invisible from reading the code alone, so the doc comment is the only place this fact can live for a future reader.

3. **Router branch (`open_engine_for_model`, `src/engine/engine.rs`).**
   Insert an `id.strip_prefix("bedrock:")` check before the final `ModelNotFound` fallthrough, calling `bedrock_from_env` with the stripped remainder passed straight through — no validation of its shape (raw AWS model id or inference-profile ARN are both accepted verbatim, per the parent research's decision).
   Gate the branch's *body* on `#[cfg(feature = "bedrock")]` (the crate dependency itself is only in the graph when the feature is on); when the feature is explicitly disabled (`--no-default-features`), a `"bedrock:"`-prefixed id falls through to today's `ModelNotFound`, preserving current behavior for that build configuration rather than panicking or failing to compile.
   Extend the function's existing per-branch doc-comment bullets (it currently documents `"claude-"`/`"gpt-"`/`"gemini-"` each resolving via their key-checked constructor) with a bullet for `"bedrock:"` that explicitly calls out the asymmetry: unlike the other three, a recognized-but-credential-less Bedrock id resolves to `Ok`, not `Err(Auth)`, because credential resolution is deferred to the first live call.

4. **No other file changes.** `messages_to_rig`, `content_from_rig_choice`, `trace_from_rig`, `engine_error_from_rig`, and the `RigEngine<M>` blanket `EngineProvider` impl are already generic over any Rig `CompletionModel` and require no Bedrock-specific branches, per the Prior Art finding that `rig_bedrock::completion::CompletionModel` already satisfies the same trait bound the other three providers do.

5. **Explicitly out of scope for this feature-step:** pinning the exact AWS model id/ARN for "Mistral Large 3" (Feature D); any live call against real AWS credentials (Feature C's Bedrock leg); any change to `RunCmdError`, the CLI surface, or a CI workflow — no CI workflow currently runs bare `cargo test`/`cargo check` for the whole crate (only `e2e/insurance-claim` and `e2e/patterns-eval` have GitHub Actions, both scoped to their own `ci.sh`), so there is no existing credential-skip harness this feature-step needs to extend; that pattern becomes relevant once Feature C or D adds a Bedrock-specific live-run script.

## Alternatives

**Eagerly probe AWS credentials in `bedrock_from_env`, mirroring `read_required_key`.**
Considered and rejected.
AWS's credential chain has multiple legitimate sources beyond a single env var — a shared profile file, SSO, an EC2/ECS instance role via IMDS.
A simple "is `AWS_ACCESS_KEY_ID` set" check would report a false `EngineError::Auth` for any profile-, SSO-, or role-based setup that is actually fully configured, which is strictly worse than deferring the check to the point rig-bedrock's own `Client::from_env()` already defers it to (the first live call).
This is the one place this feature-step's shape has to diverge from the other three `*_from_env` constructors, and the divergence is deliberate, not an oversight this design failed to notice.

**Feature-gate the router branch vs. always compile it with an internal runtime fallback.**
Chose a `#[cfg(feature = "bedrock")]`-gated branch over an always-compiled branch with an internal "feature not compiled" runtime error, because the AWS SDK dependency itself is only present in the build graph when the feature is enabled — an always-compiled branch would require `rig-bedrock` to be an unconditional dependency, defeating the point of keeping it an (now default-on, but still independently toggleable) feature at all.

**Guarding the version-pin fragility.**
Three options, per the parent research's own framing: (a) a dedicated CI check or `mise` task asserting the resolved `rig-core`/`rig-bedrock` version pair; (b) a source comment at the point of risk; (c) explicitly deferring with no guard at all.
This design chooses (b): Cargo's own resolver already fails loudly — a hard build error, not a silent behavior change — the moment someone bumps `rig`'s requirement past what the pinned `rig-bedrock = "0.4"` can satisfy (see Prior Art's precise account of when and why).
A comment at the exact edit point (the `Cargo.toml` `rig` and `rig-bedrock` stanzas) puts the "why" in front of the next person making that edit; a CI check placed elsewhere would not materially improve on a coupling Cargo's resolver already enforces mechanically, for the cost of new CI machinery.
A follow-up `cargo tree`-based drift check is named in Summary as a `TASKS.md`-worthy nice-to-have, not required here.

**Off-the-shelf.**
None — reconfirmed, not re-litigated.
This is Ailly-specific integration work into an already-chosen, already-locked dependency (`rig-bedrock`); no third-party tool substitutes for writing the constructor and the router branch.

## Summary

**Resolved by user feedback on this draft, verified rather than assumed:** the design must ensure Bedrock auth "works for and prefers `AWS_BEARER_TOKEN_BEDROCK`."
Researched against the real AWS SDK source, changelog, and `rig-bedrock`'s own pinned dependency versions (Prior Art): this is already true, automatically, of the plain `aws_config::load_from_env()` call `rig-bedrock`'s `Client::from_env()` already makes, given the pinned `aws-sdk-bedrockruntime 1.124.0` (bearer-token support landed at `1.100.0`).
No constructor logic, precedence check, or extra code is needed — only the doc-comment update in Specification item 2, so this fact is discoverable by a future reader rather than an invisible property of a transitive dependency's version.

**Deferred to `TASKS.md` at this project's cleanup (not decided here):**

- Pinning the exact AWS model id or inference-profile ARN for "Mistral Large 3" (and confirming the other three named Bedrock models' ids against whatever region/account the matrix ultimately runs in) — Feature D's job.
- A `cargo tree`/CI drift check asserting the `rig-core`/`rig-bedrock` version pair stays mutually compatible, as a belt-and-suspenders addition to the source-comment guard this feature-step adds.
  Not required for Feature B to be done.
- Whether a Bedrock-specific live-run script (mirroring `e2e/insurance-claim/ci.sh`'s graceful-skip-without-credentials pattern) is needed — relevant once Feature C's or D's live confirmation work exists; nothing in Feature B's own scope calls a live Bedrock endpoint, so there is nothing yet to skip gracefully.

**Not deferred — already resolved and carried forward from the parent `research.md`/`design.md`** (repeated here so this doc is self-contained at feature-step altitude): the Ailly-side `"bedrock:"` prefix scheme, passing the remainder straight through unvalidated; turning the `bedrock` Cargo feature on by default as part of this feature-step; treating this as real implementation work rather than a smoke test.

### Open Artifact Decisions

**Resolved by the long-loop reviewer (2026-07-06):**

**1. `Cargo.toml` `[features]` shape — default-on feature vs. unconditional dependency.**
**Decided: keep `bedrock` a named, independently-toggleable Cargo feature (`default = ["bedrock"]`, `rig-bedrock` remains `optional = true`), not an unconditional dependency.**
This is the design's own recommended default, and it is the conservative choice: it costs nothing today (the feature is on by default either way) and preserves a real `--no-default-features` escape hatch — a consumer who wants a smaller dependency graph without the AWS SDK still has one.
Folding it into an unconditional dependency is irreversible in practice (removing a hard dependency later is a breaking change for anyone who came to depend on its absence), where keeping it a toggleable feature is not; the reversible option is the conservative one.

**2.**
**Router behavior for `--no-default-features` builds.**
**Decided: a `"bedrock:"`-prefixed id falls through to `ModelNotFound` when the feature is disabled, identical to today's pre-feature behavior.**
This is the design's own recommended default and matches the existing `#[cfg(feature = "bedrock")]` gate already on `bedrock_from_env` — the alternative (a distinct "feature not compiled" error) would require a new `EngineError` variant or a runtime string threaded through a build configuration the router otherwise has no reason to know about, for no behavioral gain over the error the caller already handles (`ModelNotFound`).
Least-surprising, and it is exactly what the router already does for every other unrecognized prefix.

**3.**
**Version-pin fragility guard.**
**Decided: a source comment only, at the `Cargo.toml` `rig` and `rig-bedrock` stanzas; no CI or `mise` check in this pass.**
This is the design's own recommended default.
Cargo's resolver already fails loudly (a hard build error, not a silent regression) the moment someone bumps `rig` past what the pinned `rig-bedrock = "0.4"` can satisfy (Prior Art walks the exact tag history establishing this).
A comment at the edit point gives the next person the "why" at zero marginal machinery cost; a CI/`mise` drift check would duplicate a guarantee the resolver already provides mechanically.
Recorded as a deferred nice-to-have in Summary, not required for this feature-step to be done.

**4.**
**Exact `#[cfg(feature = "bedrock")]` placement inside `open_engine_for_model`.**
**Decided: a single `#[cfg(feature = "bedrock")]`-gated `if let Some(remainder) = id.strip_prefix("bedrock:")` block, placed immediately before the function's final `ModelNotFound` fallthrough — not two `cfg`-gated function variants.**
One gated block mirrors the shape every other provider branch in the function already uses (an `if id.starts_with(prefix) { ... return ...; }` guard ahead of the fallthrough) and needs no duplicate function signature or doc-comment set the way two cfg'd variants of `open_engine_for_model` itself would.
This placement decision belongs to the Plan phase's API-surface breakdown per the design's own note below, and is recorded in `plan.md` Step 0 rather than re-litigated here.

## Feature Test

**Path:** `/Users/david.souther/devel/davidsouther/ailly/ailly_two/tests/engine_routing_bedrock.rs`

**User story (Given/When/Then):** Given a conversation whose `meta.model` is `bedrock:meta.llama3-3-70b-instruct-v1:0` (one of issue #29's four named Bedrock models, addressed through the Ailly-side prefix), when `ailly run` asks `open_engine_for_model` for the engine that serves it, then the router resolves it to a real engine — not the pre-feature `ModelNotFound` dead end — without requiring any AWS credentials to be present, because construction (unlike Anthropic/OpenAI/Gemini's eager key check) never touches the AWS credential chain; that only happens on the first live call, which this test does not make.

The one test function asserts, in order: (1) the named model resolves to `Ok`; (2) an inference-profile ARN passed after the `bedrock:` prefix also resolves to `Ok` with no format validation; (3) the same raw id *without* the `bedrock:` prefix still resolves to `Err(ModelNotFound)`, proving true prefix dispatch rather than a substring match and that the feature does not loosen existing routing; (4) gated on `#[cfg(feature = "bedrock")]` (so the test still compiles and still meaningfully fails without that feature), a direct call to `bedrock_from_env` no longer returns the hardcoded `"not yet implemented"` stub.

**Confirmed RED for the right reason.** `cargo check --test engine_routing_bedrock --all-features` compiles cleanly (no typos, no wrong API usage). `cargo test --test engine_routing_bedrock --all-features` and, separately, `cargo test --test engine_routing_bedrock` (no extra flags — the `#[cfg(feature = "bedrock")]`-gated fourth assertion is compiled out, but the first three still run) both fail at the very first assertion:

```text
panicked at tests/engine_routing_bedrock.rs:54:54:
bedrock: prefix must route to a real engine, not ModelNotFound (the pre-feature dead end);
got ModelNotFound for ModelId("bedrock:meta.llama3-3-70b-instruct-v1:0")
```

This is exactly the missing-router-branch failure this feature-step exists to fix, not a typo or a misused API.
Because the `bedrock` Cargo feature is not yet a default feature (Specification item 1, not yet implemented), verifying the full four-assertion test today requires `--all-features` (or `--features bedrock`), matching the project's own `mise run test`/`check`/`lint` tasks, which already pass `--all-features` unconditionally; once this feature-step's Plan/Build phase makes `bedrock` a default feature, that flag stops being necessary for this test specifically, though the project's `mise` tasks will still pass it for everything else.

**Next steps.**
This is the draft gate: do not continue into `developer:plan` or any implementation skill in this session, even if asked.
Review this `design.md` and the feature test at the path above — pay special attention to the **Open Artifact Decisions** subsection under Summary, since none of those four choices are prescribed by an existing convention or the cleared parent `research.md`/`design.md`.
Make any edits you find appropriate, then remove the `*Draft 2026-07-06*` marker above and start a new session running `developer:ailly` (or `developer:plan` directly) to move into this feature-step's plan phase.
