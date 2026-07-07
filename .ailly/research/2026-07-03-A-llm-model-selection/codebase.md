# LLM Model Selection in Domain-Driven Design Codebase

Research findings on model selection patterns, guidance, and configuration in Claude Code and Ailly.

## Summary

The domain-driven-design repository implements a comprehensive phase-based model selection system for the Ailly developer lifecycle. Models are recommended per development phase based on cost/capability tradeoffs, with provider-specific mappings (Anthropic, OpenAI, Open Source).

## Key Findings

### 1. Phase-Based Model Selection Framework

**Source:** `/developer/skills/ailly/references/checks/model-per-phase.md`

The repository defines a structured phase-by-provider table that maps each development phase to recommended model tiers:

| Phase | Anthropic | OpenAI | Open Source |
|-------|-----------|--------|------------|
| Research | Haiku 4.5 (thinking) | o4-mini | Qwen3-30B-A3B |
| Design | Opus 4.8 (max effort) | o3 | DeepSeek-R1 671B |
| Planning | Sonnet 4.6 (high effort) | GPT-4.1 | Llama 3.3 70B |
| Implementation | Sonnet 4.6 (high effort, 1M context) | GPT-4.1 | Llama 4 Scout |
| Cleanup | Haiku 4.5 | o4-mini | Qwen3-4B |

**Rationale:** "Each phase of the Ailly developer loop has a different cost and capability profile. Research gathers and filters broadly. Design synthesizes and judges. Planning and implementation follow structure over long context. Cleanup tidies. The strongest reasoner is wasted on cleanup, and the cheapest model is a liability for design."

### 2. Model Effort Qualifiers

**Source:** `/developer/skills/ailly/references/checks/model-per-phase.md`

Additional UI-level controls accompany model recommendations, not as part of the model name but as instructions for the developer:

- `thinking` - Extended reasoning capability (Research phase on Anthropic)
- `max effort` - Maximum reasoning effort (Design phase on Anthropic)
- `high effort` - Elevated reasoning effort (Planning and Implementation phases)
- `1M context` - Extended context window (Implementation phase)

These qualifiers are set by the developer in their UI and represent additional capability controls beyond model selection.

### 3. Provider Detection and Fallback

**Source:** `/developer/skills/ailly/references/checks/model-per-phase.md`

The system detects the active model provider from the runtime environment:

- Model names like Opus, Sonnet, Haiku, or `claude-*` identities map to **Anthropic**
- Model names like o3, o4-mini, or `gpt-*` identities map to **OpenAI**
- Model names like Qwen, DeepSeek, or Llama map to **Open Source**

If no identity is present or unrecognized, the system falls back to **Anthropic**.

### 4. Phase-Entry Model Checking

**Source:** `/developer/skills/ailly/references/checks/model-per-phase.md` and `/developer/skills/ailly/SKILL.md`

The Ailly coordinator performs an active model check when entering each phase:

1. Detects the running model from environment context
2. Maps it to the recommended model for the current phase
3. **Compares the two** and reports differences explicitly (not generically)
4. **Never gates** the loop on this check - it continues on the current model regardless

Example announce line: "you are on Opus 4.8; research recommends Haiku 4.5 (thinking)"

This is a **check, not a gate** - flagging a mismatch never stalls the loop.

### 5. Model Switching Protocol

**Source:** `/developer/skills/ailly/references/checks/model-per-phase.md`

Two mechanisms for switching models:

1. **Direct switching (preferred):** If the harness exposes a way to change the active model, the skill does so automatically on phase entry
2. **Fallback switch protocol:** 
   - Announce the recommended model and any mismatch
   - Invite developer to switch with `/model` command
   - Press `s` in picker for session-only switch (preserves saved default)
   - Phase continues on current model if no switch occurs

### 6. Integration with Phase References

**Source:** `/developer/skills/ailly/references/phases/research.md` and `/developer/skills/ailly/references/phases/design.md`

Each phase reference explicitly names the model recommendation at startup:

**Research phase announce line:**
> "Name the recommended model for research from the Phase by Provider table in developer/skills/ailly/references/checks/model-per-phase.md, matched to the active provider, with its effort or thinking qualifier verbatim. If you're not already on it, I'll switch when the harness allows; otherwise switch with `/model` (press `s` for session-only) as the fallback. I'll continue on the current model either way."

**Design phase announce line:**
> "Name the recommended model for design from the Phase by Provider table in developer/skills/ailly/references/checks/model-per-phase.md, matched to the active provider, with its effort qualifier verbatim. If you're not already on it, I'll switch when the harness allows; otherwise switch with `/model` (press `s` for session-only) as the fallback. I'll continue on the current model either way."

### 7. Skill-Level Integration

**Source:** `/developer/skills/ailly/SKILL.md`

Model checking is listed as a mandatory phase-entry check:

> "Model check. Detect the running model and compare it to the model recommended for the phase. On a mismatch, say so explicitly and invite a `/model` switch; continue on the current model either way. This is a check, not a gate — the loop never stalls. Consult `developer/skills/ailly/references/checks/model-per-phase.md` for the phase×provider table, the detection rules, and the switch protocol."

This check is paired with a **tool-readiness check** (see `references/checks/tool-failure.md`).

### 8. Harness Compatibility

**Source:** `/developer/skills/ailly/references/agents/claude.md`

Phase isolation in Claude Code uses `Task` (subagent dispatch) to run each phase in isolation, reading only that phase's reference file. Model switching integrates with Claude Code's native model-selection UI.

Other harnesses (Codex, Copilot, Gemini) have their own agent-specific references at:
- `references/agents/codex.md`
- `references/agents/copilot.md`
- `references/agents/gemini.md`

### 9. No Mandatory Model Configuration in Plugin Metadata

**Source:** `.claude-plugin/plugin.json` files

Plugin definitions do not hardcode model requirements. The model selection is determined at runtime by:
1. Phase entry (which phase is running)
2. Active provider (detected from running model)
3. Developer's UI/harness capabilities

This design allows the same skill to work across multiple providers without modification.

## Design Rationale

The model-selection system embodies these principles:

1. **Cost-Capability Alignment:** Each phase gets the minimum model complexity needed for that phase's work, not uniform overkill
2. **Developer Choice:** Recommendations are advisory, not mandatory gates - developers can override and work on any model
3. **Transparency:** Mismatches are named explicitly so developers see the gap and can decide
4. **Provider Neutrality:** The same recommendation framework works across Anthropic, OpenAI, and open-source models
5. **Effort Qualification:** Beyond model tier, additional UI controls (thinking, effort, context) tune reasoning intensity

## References

1. `/developer/skills/ailly/references/checks/model-per-phase.md` - Complete phase×provider table, detection rules, switch protocol
2. `/developer/skills/ailly/SKILL.md` (lines 1-260) - Coordinator bootstrap and phase routing, model check integration
3. `/developer/skills/ailly/references/phases/research.md` (lines 1-12) - Research phase announce line with model recommendation
4. `/developer/skills/ailly/references/phases/design.md` (lines 1-16) - Design phase announce line with model recommendation
5. `/developer/skills/ailly/references/checks/tool-failure.md` - Companion to model check for phase-entry validation
6. `/developer/skills/ailly/references/agents/claude.md` - Claude Code specific phase isolation and model switching
7. `README.md` (lines 79-88) - Developer skill package overview
8. `/developer/.claude-plugin/plugin.json` - Plugin manifest (no hardcoded models)

## Patterns for Implementation

### For Skill Authors
When writing a skill that may run across multiple providers:
1. Do not hardcode model names in skill references
2. If model capability is critical, check the phase (via coordinator context) to determine whether recommendation applies
3. Let the phase-entry check handle model detection and announce lines
4. Reference `model-per-phase.md` rather than reimplementing model selection logic

### For Phase-Specific Guidance
Each phase that needs explicit model guidance should:
1. Include announce line at start that names the Phase by Provider table and current provider
2. Offer `/model` switch as fallback to direct harness switching
3. Use `s` (session-only) flag to preserve user's default
4. Never gate the phase on model availability

### For Tool/API Integration
When integrating model-specific tools or APIs:
1. Detect provider from running model identity
2. Map to the provider column in phase×provider table
3. Route to provider-specific tool if needed
4. Gracefully degrade if provider capability unavailable

