# Subagent Model Selection

## Selection Principle

Match the model to the task's complexity profile, not to which phase or skill happens to be dispatching. Work with high reasoning depth, heavy constraint- or rule-following, deep domain specificity, or a pronounced generation-vs-evaluation asymmetry (the task is far harder to produce correctly than to check) favors the strongest available reasoner for that provider. Work that is low-complexity, rote, orchestration over an already-settled task list, or narrowly scoped favors a cheaper, faster model — provided that cheaper model clears an eval suite scoped to the work it is being asked to do.

Express this as a bare alias, never a dated pinned version: `opus`, `sonnet`, or `haiku` for Anthropic, and the equivalent bare-alias tier for any other provider (a provider's own "recommended" or "latest" pointer, not a specific dated release). Aliases track a provider's own current recommendation over time; a pinned version is frozen the day it is written and goes stale the moment the provider ships a new generation. The dated table below is the one deliberate, clearly-stamped exception to this rule — see Frontier-Model Caution.

## Complexity Dimensions

Classify a task along these axes before choosing a model. A task rarely sits at one extreme on every axis; weigh whichever axis dominates the work.

- **Reasoning depth** — how many inferential steps, or how much multi-step planning, does producing a correct answer require? Shallow: a lookup, a mechanical rewrite, a single-pass transformation. Deep: a design tradeoff, a root-cause diagnosis, a multi-file refactor plan.
- **Constraint- or rule-following** — how many simultaneous constraints must the output satisfy, and how costly is silently dropping one? Loose: prose with a few stylistic preferences. Strict: a spec with many named, interacting invariants, or a security- or correctness-critical contract.
- **Domain specificity** — how much specialized, narrow domain knowledge does the task assume before the model can even begin reasoning about it? General: everyday code or writing. Specific: an unusual API, a niche protocol, a regulatory or legal domain, a codebase's own idiosyncratic conventions.
- **Generation-vs-evaluation asymmetry** — is it much harder to produce the output than to check it once produced? High asymmetry (generation is the hard part) favors spending more capability on generation; low asymmetry (checking is roughly as hard as producing) is a signal that a cheaper model can do the work if a strong evaluator or test suite backs it up.

## Principle → Provider Example

<!-- Last reviewed 2026-07-03. Illustrative only. Re-verify against each provider's current every few months.
-->

| Complexity profile | Anthropic | OpenAI | Open Source | Ailly Phases |
| --- | --- | --- | --- | --- |
| High reasoning depth / strict constraints / high generation-evaluation asymmetry | `opus` | `gpt-5.1` (high-reasoning tier) | DeepSeek-R1-class or Llama-4-Maverick-class model | Design |
| Moderate reasoning depth, domain-specific but not judgment-heavy | `sonnet` | `gpt-5.1` (standard tier) | Llama-4-class mid-size model | Plan, Implement |
| Low reasoning depth, rote or narrowly-scoped, orchestration over a settled task list | `haiku` | `gpt-5.1-mini` | Llama-4-Scout-class or Qwen3-class small model | Research, Cleanup |

**Worked mapping example (not the organizing key):** Ailly's five phases illustrate how the principle applies, not a separate table to memorize. Research and design lean toward the high-reasoning-depth row (open-ended exploration, judgment about tradeoffs). Plan sits in the moderate row (structured but still judgment-heavy). Build (red-green-refactor) and cleanup vary step-by-step: implementing a novel algorithm is high-reasoning-depth; running a lint fix or a mechanical rename is low-reasoning-depth. Classify each dispatch by its own complexity profile rather than by which phase issued it.

## Frontier-Model Caution

"Newest available" or "highest-benchmarked" is not, by itself, sufficient justification for recommending a model for a complexity dimension. A model earns a dimension's recommendation once it clears a strict eval suite scoped to that dimension — reasoning-depth tasks evaluated against reasoning-depth benchmarks, constraint-following tasks evaluated against constraint-adherence checks, and so on. That eval suite is named here as future work; it is not built by this guidance. Until it exists, prefer a provider's own documented default alias over chasing whichever model is newest or scores highest on a general leaderboard.

**Override:** this is a default, not an absolute. Explicit human intent waives it for that request only — a project setting, a user setting, or a developer's own phrasing that explicitly asks for a frontier or newest model ("use frontier," "with the latest models") overrides the eval-gating default for that one dispatch. This is a targeted escape hatch tied to stated intent, not a general loosening of the default for unstated cases.
