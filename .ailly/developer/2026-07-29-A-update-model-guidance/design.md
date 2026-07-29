# Design: Current model-selection guidance

## Purpose

Give a maintainer or agent one trustworthy place to choose a model after the
June and July 2026 provider releases. The guidance must remain organized by
task complexity and make scoped evaluation the selection policy. Because that
eval suite is future work, its deliberately dated table is a set of
provider-documented, illustrative candidates rather than evidence that any
candidate has already earned a default.

The update must prevent three contracts from being conflated: a provider may
offer a model, a provider API may assign it a stable or pinned identifier, and
a particular agent harness may expose only a subset through subagent dispatch.
Readers should be able to select a suitable tier without assuming that every
listed name is accepted by their current tool.

Before planning or implementing this design, load `general:writing-skills`.
Before claiming the work complete, load `general:review`.

## Prior Art

`general/skills/dispatching-agents/model-selection.md` already provides the
right organizing principle: match reasoning depth, constraint following,
domain specificity, and generation-versus-evaluation asymmetry to a model that
has cleared task-scoped evaluations. Its dated provider table is intentionally
illustrative rather than the durable contract.

The harness adapters under
`developer/skills/ailly/references/agents/` already distinguish confirmed
model-setting mechanisms from announce-only fallbacks. Code Mode's threshold
reference provides a precedent for a clearly dated cost and context snapshot.
The design extends those patterns rather than introducing another model
registry or an Ailly phase-specific table.

## User Journey and Metrics

**Primary story:** Given a maintainer uses the repository's model-selection
reference after the July 2026 releases, when they choose candidates to
evaluate for a supported harness, then they see a complexity-first,
provider-grounded snapshot covering current Anthropic, OpenAI, Google, and
open-weight/self-hosted options. The guidance says that a candidate becomes a
default only after it clears a task-scoped eval, and warns that provider
availability, API identifiers, and harness dispatch support are separate
contracts.

The journey succeeds when:

- the central table is visibly reviewed on 2026-07-29, labels its entries as
  illustrative candidates, and includes current Anthropic, OpenAI, and Google
  family names;
- the table maps candidate tiers explicitly: Opus 5, GPT-5.6 Sol, and Gemini
  3.5 Flash to sustained/high; Sonnet 5, GPT-5.6 Terra, and Gemini 3.6 Flash to
  balanced; and Haiku 4.5, GPT-5.6 Luna, and Gemini 3.5 Flash-Lite to economy;
- Fable 5 is called out as an exceptional highest-capability/long-horizon
  candidate, not an automatic replacement for every high-tier selection;
- the former open-source category is labeled accurately as open-weight or
  self-hosted; Kimi K2.7 Code appears only as a specialist/high-end candidate
  with evaluation and hardware qualifications, and API-only DeepSeek products
  are not labeled open-weight;
- the surrounding prose preserves eval-first selection and explains stable,
  pinned, and harness-specific identifiers;
- Codex recommends only values confirmed by its active tool schema, while
  Gemini remains explicitly announce-only until its model field is confirmed;
- `DEVELOPMENT.md` prompts periodic review of the dated snapshot;
- Code Mode's July 2026 Claude cost/context snapshot says it was verified
  against provider documentation and includes an implementable Opus 5 row at
  $5 input and $25 output per 1M tokens with a 1M-token context window; and
- the single executable feature test passes with no network access or model
  invocation.

Failure modes are explicit. A newly announced model is not automatically a
default, a provider product name is not automatically a dispatch argument, a
preview or `latest` identifier is not presented as stable, and a large
open-weight coding model is not presented as a universal cheap option.

## Specification

1. Keep `general/skills/dispatching-agents/model-selection.md` as the only
   durable model-selection source of truth. Preserve its complexity dimensions,
   worked phase mapping, eval gate, and explicit-human-intent override.
2. Refresh its dated provider example to a 2026-07-29 snapshot. Describe the
   entries as provider-documented candidates for the future eval suite, not as
   eval-backed defaults. Map the rows explicitly:
   - sustained/high: Anthropic Opus 5, OpenAI GPT-5.6 Sol, and Google Gemini
     3.5 Flash;
   - balanced: Anthropic Sonnet 5, OpenAI GPT-5.6 Terra, and Google Gemini 3.6
     Flash; and
   - economy: Anthropic Haiku 4.5, OpenAI GPT-5.6 Luna, and Google Gemini 3.5
     Flash-Lite.
   Present Fable 5 separately in the Anthropic high cell as an exceptional
   highest-capability/long-horizon option, not an automatic Opus replacement.
3. Rename the open-source column to “Open-weight / self-hosted.” Keep its
   examples illustrative and state in the dated-table section that hardware
   feasibility and scoped evaluations govern their use. Kimi K2.7 Code may
   appear only in the high row as a coding specialist/high-end candidate, not
   as an economy default. State adjacent to the table that API-only DeepSeek
   products are not evidence of an open-weight release; do not place such
   products in the open-weight column.
4. Separate human-facing provider examples from callable identifiers. Explain
   that Anthropic harness aliases are not the same thing as pinned provider API
   IDs, Google stable/preview/latest identifiers have different lifecycle
   guarantees, and each harness's accepted model values are authoritative for
   dispatch.
5. Keep adapter edits narrow. The Codex adapter must direct dispatchers to the
   active tool schema's advertised model values rather than infer support from
   the provider catalog. The Gemini adapter must retain its confirmed
   announce-only behavior. Change another adapter only if the central
   terminology would otherwise contradict it.
6. Add a periodic model-snapshot review nudge to `DEVELOPMENT.md`.
7. Refresh `code-mode-thresholds.md` to identify its pricing/context data as a
   July 2026 snapshot verified against provider documentation. Its table must
   retain the `Input ($/1M)`, `Output ($/1M)`, and `Context` headers and contain
   an `Opus 5` row with `$5`, `$25`, and `1M`, respectively. Preserve the
   threshold decision and existing worked examples.
8. Update only
   `developer/tests/test_subagent_model_mandate.py` as the one executable
   feature test. It must extract the dated Markdown table and check the
   provider columns and row-by-row tier mappings rather than accepting model
   words found anywhere in the document. It must also validate the eval-first
   and portability caveats, the Fable exception, the Kimi hardware/eval
   qualification, the exclusion of API-only DeepSeek products from the
   open-weight column, maintenance policy, the exact Opus 5 Code Mode row, and
   relevant adapter behavior while retaining the prior
   mandate-with-announce contract.
9. Do not change benchmark model pins, runtime integrations, Ailly phase flow,
   or the intentional `haiku-4.5` normalization example.

Automated verification runs:

```sh
python3 developer/tests/test_subagent_model_mandate.py
```

Manual verification reads the rendered provider table and adjacent cautions as
a maintainer on each supported harness, checking that example names cannot
reasonably be mistaken for universally callable IDs.

## Alternatives

### Recommended: centralized snapshot plus narrow contract surfaces

Starting from the existing central reference, refresh the provider snapshot,
then align only the maintenance policy, Code Mode grounding, adapters, and
their existing executable contract. Working backward from a reader making a
portable choice leads to the same boundaries: current examples in one place,
explicit identifier caveats next to them, and harness-specific facts in
adapters. This is reachable without changing runtime behavior and directly
addresses every researched failure mode. Its cost is a modestly broader edit
than changing the table alone.

### Table-only refresh

Starting from the stale rows, replace model names and add a Google column.
Working backward from the desired outcome reveals that readers could still
mistake provider availability for harness support, while Code Mode and the
missing maintenance nudge would remain inconsistent. This is the smallest
diff, but it does not meet the portability or durability requirements.

### Generated model registry

Introduce structured provider metadata and generate prose or tests from it.
Working forward requires a schema, generator ownership, lifecycle rules, and a
new source-of-truth boundary; working backward still requires judgment about
task-scoped evals and harness support that provider metadata cannot supply.
This may become useful if runtime integrations need the same data, but it is
unnecessary machinery for the current documentation-only feature.

## Summary

The design refreshes one central, complexity-first list of candidates and
makes its eval gate and portability limits testable across maintenance policy,
Code Mode grounding, and harness adapters. It does not claim the future eval
suite has already endorsed the illustrative provider mappings, and it
deliberately avoids runtime changes, benchmark pin churn, and a second model
registry.

Quick-loop assumptions: the official-provider findings in `research.md` are
accepted as the factual baseline; current means available as of 2026-07-29;
stable Gemini examples are preferred over preview Pro models; and adapter
values not confirmed by the active harness remain announce-only. No technical
decision is deferred within this scope.

Feature test:
`developer/tests/test_subagent_model_mandate.py`

Initial result:
`T2 review stamp: general/skills/dispatching-agents/model-selection.md is not stamped 'Last reviewed 2026-07-29'`
