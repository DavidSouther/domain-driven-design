# Subagent Model Selection

## Selection Principle

Match the model to the task's complexity profile, not to which phase or skill happens to be dispatching. Work with high reasoning depth, heavy constraint- or rule-following, deep domain specificity, or a pronounced generation-vs-evaluation asymmetry (the task is far harder to produce correctly than to check) favors the strongest available reasoner for that provider. Work that is low-complexity, rote, orchestration over an already-settled task list, or narrowly scoped favors a cheaper, faster model — provided that cheaper model clears an eval suite scoped to the work it is being asked to do.

Express the recommendation using the most portable identifier the active
harness actually accepts. Prefer a harness-level family alias such as `opus`,
`sonnet`, or `haiku` when the harness documents one, but do not assume every
provider offers a uniformly evergreen bare alias. A provider's display name,
its API identifier, and a harness dispatch value are separate contracts. Use
a pinned provider API ID when reproducibility requires it, and treat `latest`
or preview IDs according to that provider's lifecycle guarantees. The dated
table below is a deliberately human-facing exception: it names candidate
families for evaluation, not universally callable identifiers.

## Complexity Dimensions

Classify a task along these axes before choosing a model. A task rarely sits at one extreme on every axis; weigh whichever axis dominates the work.

- **Reasoning depth** — how many inferential steps, or how much multi-step planning, does producing a correct answer require? Shallow: a lookup, a mechanical rewrite, a single-pass transformation. Deep: a design tradeoff, a root-cause diagnosis, a multi-file refactor plan.
- **Constraint- or rule-following** — how many simultaneous constraints must the output satisfy, and how costly is silently dropping one? Loose: prose with a few stylistic preferences. Strict: a spec with many named, interacting invariants, or a security- or correctness-critical contract.
- **Domain specificity** — how much specialized, narrow domain knowledge does the task assume before the model can even begin reasoning about it? General: everyday code or writing. Specific: an unusual API, a niche protocol, a regulatory or legal domain, a codebase's own idiosyncratic conventions.
- **Generation-vs-evaluation asymmetry** — is it much harder to produce the output than to check it once produced? High asymmetry (generation is the hard part) favors spending more capability on generation; low asymmetry (checking is roughly as hard as producing) is a signal that a cheaper model can do the work if a strong evaluator or test suite backs it up.

## Principle → Provider Example

<!-- Last reviewed 2026-07-29. -->

These provider-documented mappings are illustrative candidates for the eval
suite that remains future work. They have not earned defaults merely by
appearing here.

| Complexity profile | Anthropic | OpenAI | Google | Open-weight / self-hosted | Ailly Phases |
| --- | --- | --- | --- | --- | --- |
| high — sustained reasoning / strict constraints / high generation-evaluation asymmetry | Opus 5; Fable 5 only as an exceptional highest-capability, long-horizon option | GPT-5.6 Sol | Gemini 3.5 Flash for sustained work | Kimi K2.7 Code as a coding specialist, subject to scoped eval results and substantial hardware feasibility | Design |
| balanced — moderate reasoning depth, domain-specific but not judgment-heavy | Sonnet 5 | GPT-5.6 Terra | Gemini 3.6 Flash | A current mid-size model that clears the scoped eval and fits available hardware | Plan, Implement |
| economy — low reasoning depth, rote or narrowly scoped | Haiku 4.5 | GPT-5.6 Luna | Gemini 3.5 Flash-Lite | A current small model that clears the scoped eval and fits available hardware | Research, Cleanup |

Fable 5 is not automatic as a replacement for Opus 5 in the high tier; evaluate
its exceptional capability, cost, and long-horizon behavior against the
specific task. Likewise, Kimi K2.7 Code is a high-end specialist rather than a
universal cheap default. API-only DeepSeek products are not open-weight
releases and therefore do not belong in the open-weight / self-hosted column.

Provider availability does not establish API-ID stability or harness
dispatchability. Anthropic harness aliases such as `opus` are distinct from
pinned provider API IDs. Google stable, preview, and `latest` identifiers have
different lifecycle guarantees. For every provider, the active harness's tool
schema is authoritative for accepted dispatch values; if a listed family is
not accepted there, announce the recommendation but do not pass the display
name as a model argument.

**Worked mapping example (not the organizing key):** Ailly's five phases illustrate how the principle applies, not a separate table to memorize. Research and design lean toward the high-reasoning-depth row (open-ended exploration, judgment about tradeoffs). Plan sits in the moderate row (structured but still judgment-heavy). Build (red-green-refactor) and cleanup vary step-by-step: implementing a novel algorithm is high-reasoning-depth; running a lint fix or a mechanical rename is low-reasoning-depth. Classify each dispatch by its own complexity profile rather than by which phase issued it.

## Frontier-Model Caution

"Newest available" or "highest-benchmarked" is not, by itself, sufficient justification for recommending a model for a complexity dimension. A model earns a dimension's recommendation once it clears a strict eval suite scoped to that dimension — reasoning-depth tasks evaluated against reasoning-depth benchmarks, constraint-following tasks evaluated against constraint-adherence checks, and so on. That eval suite is named here as future work; it is not built by this guidance. Until it exists, prefer a provider's own documented default alias over chasing whichever model is newest or scores highest on a general leaderboard.

**Override:** this is a default, not an absolute. Explicit human intent waives it for that request only — a project setting, a user setting, or a developer's own phrasing that explicitly asks for a frontier or newest model ("use frontier," "with the latest models") overrides the eval-gating default for that one dispatch. This is a targeted escape hatch tied to stated intent, not a general loosening of the default for unstated cases.
