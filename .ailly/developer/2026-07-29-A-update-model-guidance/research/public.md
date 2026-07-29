# Public: current model families relevant to subagent guidance

## Findings

This pass used only first-party provider documentation and official model
repositories. Query variants covered release announcements, current model
lists, changelogs, availability/deprecation pages, pricing, aliases/versioning,
and provider model-selection guidance.

### Anthropic

- Anthropic's current four-tier family is Fable 5 (highest capability and
  long-horizon agents), Opus 5 (complex analysis and agentic coding), Sonnet 5
  (balance of intelligence and speed), and Haiku 4.5 (fastest) [1], [2].
- Fable 5 became generally available June 9, was temporarily suspended, and
  was restored globally July 1. It is materially different from an ordinary
  default: it costs $10/$50 per million input/output tokens and may return
  classifier refusals that require fallback handling [3], [4].
- Anthropic recommends starting Opus 5 at `high` effort and stepping up to
  `xhigh` for demanding coding and agentic work; effort tuning may be preferable
  to switching models [2].
- A dateless Claude API ID from generation 4.6 onward is a pinned snapshot, not
  an evergreen alias [5]. The repository's bare `opus`, `sonnet`, `haiku`, and
  `fable` values are therefore harness dispatch aliases and must not be
  described as equivalent to all Anthropic API identifiers.

### OpenAI

- OpenAI released GPT-5.6 generally on July 9 across ChatGPT, Codex, and the
  API. Its durable capability tiers are Sol (flagship), Terra (balanced/lower
  cost), and Luna (fastest/most affordable), priced at $5/$30, $2.50/$15, and
  $1/$6 per million input/output tokens respectively [6].
- Codex supports selecting Sol, Terra, and Luna according to plan
  availability, plus effort controls through `max` and `ultra` [6]. The active
  Codex subagent interface in this session advertises Sol and Terra but not
  Luna, so repository guidance must distinguish provider availability from
  harness dispatchability.
- The dated `gpt-5.1` and `gpt-5.1-mini` examples are obsolete as current
  provider examples. The current family gives a direct high/balanced/economy
  mapping, but exact identifiers should match the harness's accepted values.

### Google

- Google released stable Gemini 3.6 Flash and Gemini 3.5 Flash-Lite on July
  21. Google describes 3.6 Flash as balancing speed and intelligence with
  agentic planning capability, 3.5 Flash as its most intelligent stable Flash
  model for sustained agentic/coding work, and 3.5 Flash-Lite as the fastest,
  most cost-effective 3.5 option [7], [8].
- The repository supports a Gemini harness but the current provider-example
  table omits Google entirely. A Google column is therefore a model-guidance
  gap, even though Gemini's subagent mechanism remains announce-only.
- Google explicitly distinguishes stable IDs, preview IDs, evergreen `latest`
  aliases, and experimental IDs [8]. Durable guidance should favor stable IDs
  unless the user explicitly asks for preview/frontier behavior.

### Open-weight and other providers

- DeepSeek's current API family is V4 Pro and V4 Flash; legacy
  `deepseek-chat`/`deepseek-reasoner` aliases were scheduled for discontinuation
  July 24 [9]. Because the official evidence reviewed is an API release rather
  than an open-weight release, it should not be presented unqualified as an
  "Open Source" recommendation.
- Moonshot's official Kimi K2.7 Code model repository is an open-weight,
  coding-focused, long-horizon agentic model released in June and deployable
  with common local inference engines [10]. It is a credible current example,
  but its 1.1T-parameter footprint makes it unsuitable as a generic moderate or
  cheap self-hosted recommendation.
- The current open/self-hosted column should be renamed to "Open-weight /
  self-hosted" and remain class-based unless the project adds task-specific
  evals and hardware constraints. Provider API products and downloadable model
  weights should not be mixed into one undifferentiated category.

### Falsification

The load-bearing claim "newest models can directly replace every old table
entry" was tested against availability, stability, alias semantics, cost,
refusals, and harness support. It is false:

- Fable 5 has refusal/fallback and cost implications [3].
- Anthropic dateless API IDs are not evergreen aliases [5].
- Gemini preview and latest aliases have different lifecycle guarantees from
  stable IDs [8].
- Codex exposes a narrower subagent-model set than OpenAI's full product family
  in the active harness.
- Kimi K2.7 Code is current but too large and specialized to serve as the cheap
  self-hosted row [10].

The refined update should therefore refresh examples and provider coverage
while keeping the eval-first caution and adding explicit
provider-availability-versus-harness-dispatchability language.

## Sources

- [1] Anthropic, "Claude Platform documentation," Jul. 2026. [Online]. Available: https://platform.claude.com/docs/en/home. Accessed: Jul. 29, 2026.
- [2] Anthropic, "Choosing the right model," Jul. 2026. [Online]. Available: https://platform.claude.com/docs/en/about-claude/models/choosing-a-model. Accessed: Jul. 29, 2026.
- [3] Anthropic, "Introducing Claude Fable 5 and Claude Mythos 5," Jun. 2026. [Online]. Available: https://platform.claude.com/docs/en/about-claude/models/introducing-claude-fable-5-and-claude-mythos-5. Accessed: Jul. 29, 2026.
- [4] Anthropic, "Redeploying Fable 5," Jun. 30, 2026. [Online]. Available: https://www.anthropic.com/news/redeploying-fable-5. Accessed: Jul. 29, 2026.
- [5] Anthropic, "Model IDs and versioning," Jul. 2026. [Online]. Available: https://platform.claude.com/docs/en/about-claude/models/model-ids-and-versions. Accessed: Jul. 29, 2026.
- [6] OpenAI, "GPT-5.6: Frontier intelligence that scales with your ambition," Jul. 9, 2026. [Online]. Available: https://openai.com/index/gpt-5-6/. Accessed: Jul. 29, 2026.
- [7] Google, "Gemini API release notes," Jul. 21, 2026. [Online]. Available: https://ai.google.dev/gemini-api/docs/changelog. Accessed: Jul. 29, 2026.
- [8] Google, "Gemini API models," Jul. 21, 2026. [Online]. Available: https://ai.google.dev/gemini-api/docs/models. Accessed: Jul. 29, 2026.
- [9] DeepSeek, "Change Log," Apr. 24, 2026. [Online]. Available: https://api-docs.deepseek.com/updates/. Accessed: Jul. 29, 2026.
- [10] Moonshot AI, "Kimi-K2.7-Code model card," Jun. 2026. [Online]. Available: https://huggingface.co/moonshotai/Kimi-K2.7-Code. Accessed: Jul. 29, 2026.

