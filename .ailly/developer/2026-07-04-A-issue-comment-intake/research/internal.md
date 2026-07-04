# Internal (GitHub) Findings — the evidence trail for issue #37

Source: `DavidSouther/domain-driven-design` GitHub, fetched via `gh` CLI.

## Issue #37 — the topic itself

Title: "Ailly task intake only reads issue body, not comments — misses scope-changing
follow-ups." Zero comments (`gh issue view 37 --json comments` → `{"comments":[]}`), confirmed.
The issue is self-demonstrating: its own subject is "intake reads body, not comments," and it
has no comment thread to miss. The scope-shaping guidance therefore comes from the issue body
plus the coordinator's assignment note, not from a #37 comment.

## Issue #29 — the concrete instance of the failure

`gh issue view 29 --json title,body,comments`:

- **Body**: "Soft-block Fable 5 for Ailly coordinator and phase-runner roles until back to
  Sonnet 4.6/Opus 4.8 quality." Suggests a mechanism in `model-per-phase.md`: add a soft-block
  list to the phase-entry model check. Reads as a small prose-guardrail change.
- **Comment** (DavidSouther, OWNER, 2026-07-03T22:12:07Z, posted after the body, before the
  overnight session ran): *"This means a much bigger task of actually getting e2e baselines for
  all models today"* — then lists ~16 models across 4 providers:
  - Anthropic: Haiku 4.5, Sonnet 4.6, Sonnet 5, Opus 4.8, Fable
  - OpenAI: GPT-5.5, GPT-5.4, GPT-5.4-mini
  - Google: Gemini 3.5 Flash, Gemini 3.1 Pro (Preview), Gemini 3.1 Flash-Lite, Gemini 2.5 Pro
  - Bedrock: Llama 3.3, Llama 4 Scout, Mistral Large 3, Cohere R+

The comment reframes the task from "write a guardrail" to "run an e2e benchmarking effort to
substantiate the guardrail empirically." The overnight quickloop never fetched it (used
`gh issue list --json number,title,body,labels`), so neither the coordinator nor the #29
research runner saw it.

## PR #34 — the under-scoped result

`gh pr view 34`: state CLOSED, title "Soft-block Fable 5 in the model-selection guidance."
Touched paths:

- `.ailly/developer/2026-07-03-A-fable-5-softblock/{research,design,plan}.md` (session artifacts)
- `developer/skills/ailly/SKILL.md`
- `general/skills/dispatching-agents/model-selection.md`
- `developer/tests/test_fable5_softblock.py`

The soft-block prose landed in `model-selection.md` and `SKILL.md` (not `model-per-phase.md`,
which had already been removed from the repo). PR #34 contains **no e2e model runs and no
per-model benchmark data**. It satisfied the issue body's literal request and did not touch
the comment's actual ask. This is the exact drift issue #37 was filed to prevent: the
follow-up comment carried the real current scope, and the pipeline discarded it.

## Bearing on the fix

The `research:internal` GitHub fetch capability (`gh issue view <n> --json body,comments`, or
the MCP equivalent) already returns comments — issue #37's own "Suggested fix" names this
command. The failure was procedural, not a missing capability: the orchestration hand-rolled a
`--json ...,body,...` list query instead of routing through the full-thread fetch. The fix is
to make "fetch body + comments" the mandated read whenever a tracker item is selected or scoped.

**Sources**

[Internal] GitHub issue DavidSouther/domain-driven-design#37, body and empty comment thread. `gh issue view 37`. Accessed 2026-07-04.
[Internal] GitHub issue DavidSouther/domain-driven-design#29, body and comment by DavidSouther 2026-07-03T22:12:07Z. `gh issue view 29 --json title,body,comments`. Accessed 2026-07-04.
[Internal] GitHub pull request DavidSouther/domain-driven-design#34 (CLOSED), file list. `gh pr view 34 --json files,title,state`. Accessed 2026-07-04.
