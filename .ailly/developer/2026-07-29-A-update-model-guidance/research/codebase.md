# Codebase: repository model-guidance surfaces

## Findings

The repository has one active source of truth for subagent model choice:
`general/skills/dispatching-agents/model-selection.md`. It organizes selection
by complexity dimensions and contains the deliberately dated provider example
table. The previous Ailly-only `model-per-phase.md` table is absent from this
checkout; Ailly now points to the general reference.

The complete task-relevant surface is:

1. `general/skills/dispatching-agents/model-selection.md` — primary selection
   principle, alias policy, dated provider examples, and frontier-model caution.
2. `developer/tests/test_subagent_model_mandate.py` — contract test for the
   primary guidance. It embeds the previous review date and stale-model names.
   At the current commit it fails T4 because `DEVELOPMENT.md` has no maintenance
   nudge.
3. `DEVELOPMENT.md` — intended home for periodic-review policy, currently
   missing the text the contract test requires.
4. `developer/skills/ailly/references/shapes/code-mode-thresholds.md` — dated
   Claude price/context grounding used to decide direct-LLM versus scripting.
   It already includes Fable 5 and Sonnet 5 but omits Opus 5.
5. `developer/skills/ailly/references/agents/claude.md` — declares the
   dispatchable Claude aliases (`sonnet | opus | haiku | fable`).
6. `developer/skills/ailly/references/agents/codex.md` — declares that Codex
   accepts a per-agent model field, but does not state which current model
   identifiers are dispatchable.
7. `developer/skills/ailly/references/agents/gemini.md` and
   `developer/skills/ailly/references/agents/copilot.md` — announce-only
   fallbacks because their subagent calls have no confirmed model-selection
   field.
8. `developer/skills/ailly/SKILL.md`,
   `general/skills/using-general/SKILL.md`, and
   `general/skills/dispatching-agents/SKILL.md` — generic routing and mandate
   language. They should be audited after the central update but contain no
   dated model recommendation.
9. `developer/skills/ailly/references/shapes/code-mode.md`,
   `developer/e2e/evals/scripts/check_code_mode.py`, and the two code-mode eval
   YAML files — intentionally use the stale-looking `haiku-4.5` as user input
   in a worked normalization example whose required output is the bare alias
   `haiku`. They are guidance-adjacent but should not be updated merely because
   a newer model exists.

The many `model: claude-sonnet-4-6` entries under `*/e2e/assemblies/` are eval
runner configuration pins, not user-facing model-selection guidance. Updating
them would change benchmark comparability and is outside this task.

Search expansion covered exact model names and likely synonyms: `model
selection`, `recommended model`, `provider`, `alias`, `tier`, `effort`,
`thinking`, `context window`, `pricing`, and the current/stale provider family
names. A counterexample search did not find another durable recommendation
surface outside the files above.

## Sources

- [1] `general/skills/dispatching-agents/model-selection.md` [aad14cd]
- [2] `developer/tests/test_subagent_model_mandate.py` [aad14cd]
- [3] `DEVELOPMENT.md` [aad14cd]
- [4] `developer/skills/ailly/references/shapes/code-mode-thresholds.md` [aad14cd]
- [5] `developer/skills/ailly/references/agents/claude.md` [aad14cd]
- [6] `developer/skills/ailly/references/agents/codex.md` [aad14cd]
- [7] `developer/skills/ailly/references/agents/gemini.md` [aad14cd]
- [8] `developer/skills/ailly/references/agents/copilot.md` [aad14cd]
- [9] `developer/skills/ailly/SKILL.md` [aad14cd]
- [10] `general/skills/using-general/SKILL.md` [aad14cd]
- [11] `general/skills/dispatching-agents/SKILL.md` [aad14cd]
- [12] `developer/skills/ailly/references/shapes/code-mode.md` [aad14cd]
- [13] `developer/e2e/evals/scripts/check_code_mode.py` [aad14cd]
- [14] `developer/e2e/evals/code-mode.yaml` [aad14cd]
- [15] `developer/e2e/evals/code-mode-baseline.yaml` [aad14cd]

