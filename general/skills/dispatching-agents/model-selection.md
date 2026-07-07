# Subagent model selection

## Selection principle

Match the model to task complexity, not the requesting phase. Use stronger models for complex reasoning, strict rules, special knowledge, or when output is harder to create than to check. Use cheaper, faster models for simple tasks: rote work, orchestration, or narrow scope. Make sure cheaper models pass tests for their work.

Express this as a bare alias, never a dated pinned version: `opus`, `sonnet`, or `haiku` for Anthropic, and the equivalent bare-alias tier for any other provider. A bare alias should point to a provider's own "recommended" or "latest" pointer, not a specific dated release. Aliases track a provider's own current recommendation over time. A pinned version stays frozen the day you write it and goes stale the moment the provider ships a new generation. The dated table below represents the one deliberate, clearly stamped exception to this rule. See Frontier-model caution.

## Complexity dimensions

Classify a task along these axes before choosing a model. A task rarely sits at one extreme on every axis; weigh whichever axis dominates the work.

- **Reasoning depth:** How many inferential steps or multi-step planning does a correct answer require? Shallow: a lookup, a mechanical rewrite, a single-pass transformation. Deep: a design tradeoff, a root-cause diagnosis, a multi-file refactor plan.
- **Constraint- or rule-following:** How many simultaneous constraints must the output satisfy, and how costly is silently dropping one? Loose: prose with a few stylistic preferences. Strict: a spec with many named, interacting invariants, or a security- or correctness-critical contract.
- **Domain specificity:** How much specialized, narrow domain knowledge does the task assume before the model can begin reasoning? General: everyday code or writing. Specific: an unusual API, a niche protocol, a regulatory or legal domain, or a codebase's own idiosyncratic conventions.
- **Generation-vs-evaluation asymmetry:** Is it much harder to produce the output than to check it? High asymmetry means generation is the hard part, so spend more capability there. Low asymmetry means checking is roughly as hard as producing, so a cheaper model works if backed by a strong evaluator or test suite.

## Principle → provider example

<!-- Last reviewed 2026-07-03. Illustrative only. Re-verify against each provider's current every few months.
-->

| Complexity profile | Anthropic | OpenAI | Open Source | Ailly Phases |
| --- | --- | --- | --- | --- |
| High reasoning depth / strict constraints / high generation-evaluation asymmetry | `opus` | `gpt-5.1` (high-reasoning tier) | DeepSeek-R1-class or Llama-4-Maverick-class model | Design |
| Moderate reasoning depth, domain-specific but not judgment-heavy | `sonnet` | `gpt-5.1` (standard tier) | Llama-4-class mid-size model | Plan, Implement |
| Low reasoning depth, rote or narrowly scoped, orchestration over a settled task list | `haiku` | `gpt-5.1-mini` | Llama-4-Scout-class or Qwen3-class small model | Research, Cleanup |

**Worked mapping example (not the organizing key):** ailly's five phases illustrate how the principle applies, not a separate table to memorize. Research and design lean toward the high-reasoning-depth row (open-ended exploration, judgment about tradeoffs). Plan sits in the moderate row (structured but still judgment-heavy). Build (red-green-refactor) and cleanup vary step-by-step: implementing a novel algorithm is high-reasoning-depth; running a lint fix or a mechanical rename is low-reasoning-depth. Classify each dispatch by its own complexity profile rather than by which phase issued it.

## Frontier-model caution

"Newest available" or "highest-benchmarked" is not, by itself, sufficient justification for recommending a model for a complexity dimension. A model earns a dimension's recommendation once it clears a strict eval suite scoped to that dimension. Reasoning-depth tasks get evaluated against reasoning-depth benchmarks. Constraint-following tasks get evaluated against constraint-adherence checks. We document the eval suite here as future work, though this guidance does not build it. Until it exists, prefer a provider's own documented default alias over chasing whichever model is newest or scores highest on a general leaderboard.

**Override:** this is a default, not an absolute. Explicit human intent waives it for that request only. A project setting, a user setting, or a developer's own phrasing can explicitly ask for a frontier or newest model. Phrases like "use frontier" or "with the latest models" override the eval-gating default for that one dispatch. This targeted escape hatch ties to stated intent, not a general loosening of the default for unstated cases.
