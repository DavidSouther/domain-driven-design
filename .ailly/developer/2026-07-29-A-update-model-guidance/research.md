# Research: update model guidance

## Topic and Intent

Review the repository's model-selection guidance after a concentrated set of
model releases in the past month, then update it to reflect models that are
actually available now. The user asked for a quick loop, so the research must
be narrow enough to drive an implementation immediately while preserving the
repository's eval-first model-selection principle.

## Search/Expand

The repository no longer uses the older Ailly phase-by-provider table. Its
active source of truth is the complexity-oriented table in
`general/skills/dispatching-agents/model-selection.md`, last reviewed July 3.
The surrounding surface includes its contract test, a missing maintenance
nudge in `DEVELOPMENT.md`, Claude cost/context grounding for Code Mode, and
harness adapters that determine which central recommendations can actually be
set on a subagent dispatch.

Official provider research verified several material releases:

- OpenAI GPT-5.6 Sol, Terra, and Luna became available July 9 across Codex and
  the API, replacing the table's GPT-5.1-era examples [1].
- Anthropic's current stack is Fable 5, Opus 5, Sonnet 5, and Haiku 4.5;
  Sonnet 5 launched June 30, Fable 5 was restored July 1, and Opus 5 is now the
  complex-agentic-coding tier [2]-[4].
- Google made Gemini 3.6 Flash and Gemini 3.5 Flash-Lite generally available
  July 21, while the current table has no Google column despite a supported
  Gemini harness [5], [6].
- Current open/self-hosted examples include the coding-specialized Kimi K2.7
  Code, while DeepSeek V4's official evidence is API availability rather than
  an open-weight release [7], [8].

The primary design pressure is not simply inserting newer names. Provider
availability, API identifiers, harness aliases, stability stage, per-harness
dispatch support, cost, and refusal behavior differ. The update must make
those distinctions explicit.

## Libraries & Skills

Before doing any work in this feature, load these skills via the active harness's skill-loading mechanism: `general:writing-skills` for editing and testing skill guidance, and `general:review` before claiming the change complete.

No external programming library or framework is introduced by this task, and
no provider publishes an agentic skill that is needed to edit this
repository's Markdown guidance. Provider documentation is reference material,
not a runtime dependency. The current-codebase and public-research skills were
used during research; their findings are in `research/codebase.md` and
`research/public.md`.

## Falsification/Refine

This is a single documentation-and-contract feature, not a multi-feature
project and not a bugfix. The smallest version that meets the intent is:

1. Refresh the dated provider-example table and review stamp with the currently
   available Anthropic and OpenAI families.
2. Add Google as a first-class provider because the repository supports a
   Gemini harness.
3. Rename and qualify the open-model column so API-only products are not
   mislabeled as open source.
4. Clarify that provider availability does not guarantee the active harness
   can set that model, and that provider API IDs are not uniformly evergreen
   aliases.
5. Update the contract test and add the already-required periodic-review nudge.
6. Refresh Code Mode's Claude pricing/context snapshot where Opus 5 is missing.

The opposing hypothesis—that every newest model should directly replace an
old entry—was refuted. Fable 5 has higher cost and refusal/fallback behavior;
Anthropic's dateless API IDs are pinned; Gemini lifecycle stages differ; the
active Codex subagent tool does not expose every GPT-5.6 tier; and a 1.1T
open-weight coding model is not a credible cheap default [1], [3], [6], [8].
The existing eval-first caution remains valid and should be retained.

## Scope

In scope for the next phase:

- `general/skills/dispatching-agents/model-selection.md`
- `developer/tests/test_subagent_model_mandate.py`
- `DEVELOPMENT.md`
- `developer/skills/ailly/references/shapes/code-mode-thresholds.md`
- Narrow adapter clarification in
  `developer/skills/ailly/references/agents/{claude,codex,gemini}.md` only if
  the central terminology otherwise leaves their dispatch behavior ambiguous
- Focused tests proving the review stamp, provider coverage, current examples,
  and maintenance policy

Out of scope:

- Changing benchmark/eval runner `model:` pins under `*/e2e/assemblies/`
- Reintroducing a phase-specific Ailly model table
- Changing phase flow, delegation policy, or the eval-first principle
- Updating the intentional `haiku-4.5` user-input normalization example in Code
  Mode
- Adding runtime provider integrations or benchmarking every newly released
  model

## Resolved Decisions

- Use official provider documentation as the authority for current names,
  availability, lifecycle, pricing, and provider-recommended task tiers.
- Keep complexity dimensions as the organizing principle; phase names remain
  examples only.
- Treat Fable as an exceptional highest-capability/long-horizon option, not an
  automatic replacement for Opus on every high-complexity task.
- Use GPT-5.6 Sol/Terra/Luna as the current OpenAI family, but document that a
  harness may expose only a subset.
- Add a Google column using stable Gemini 3.5/3.6 models rather than a preview
  Pro model.
- Preserve alias-first dispatch guidance while distinguishing harness aliases
  from pinned provider API IDs.
- Rename "Open Source" to "Open-weight / self-hosted" and keep its
  recommendations illustrative and hardware/eval-qualified.

Unresolved implementation risk: the exact bare values accepted by every
non-Claude harness cannot be proved from provider docs alone. The implementation
should only mandate values confirmed by that harness's tool schema and use
announce-only guidance otherwise.

## Sources

- [1] OpenAI, "GPT-5.6: Frontier intelligence that scales with your ambition," Jul. 9, 2026. [Online]. Available: https://openai.com/index/gpt-5-6/. Accessed: Jul. 29, 2026.
- [2] Anthropic, "Claude Platform documentation," Jul. 2026. [Online]. Available: https://platform.claude.com/docs/en/home. Accessed: Jul. 29, 2026.
- [3] Anthropic, "Choosing the right model," Jul. 2026. [Online]. Available: https://platform.claude.com/docs/en/about-claude/models/choosing-a-model. Accessed: Jul. 29, 2026.
- [4] Anthropic, "Redeploying Fable 5," Jun. 30, 2026. [Online]. Available: https://www.anthropic.com/news/redeploying-fable-5. Accessed: Jul. 29, 2026.
- [5] Google, "Gemini API release notes," Jul. 21, 2026. [Online]. Available: https://ai.google.dev/gemini-api/docs/changelog. Accessed: Jul. 29, 2026.
- [6] Google, "Gemini API models," Jul. 21, 2026. [Online]. Available: https://ai.google.dev/gemini-api/docs/models. Accessed: Jul. 29, 2026.
- [7] DeepSeek, "Change Log," Apr. 24, 2026. [Online]. Available: https://api-docs.deepseek.com/updates/. Accessed: Jul. 29, 2026.
- [8] Moonshot AI, "Kimi-K2.7-Code model card," Jun. 2026. [Online]. Available: https://huggingface.co/moonshotai/Kimi-K2.7-Code. Accessed: Jul. 29, 2026.
