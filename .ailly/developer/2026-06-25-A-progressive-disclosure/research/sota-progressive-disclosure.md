# SOTA: Progressive Disclosure & Context Economy in Agent Skill Systems

*General lens. Compiled 2026-06-25.*

## The common problem (two heads, one move)

Every skill/tool a harness exposes carries a description that is **always resident**
in context. With N capabilities you pay an O(N) always-on cost before the user types
anything. That cost has two heads:

1. **Token cost** — O(N) always-on tokens compete with system prompt, history, request.
   A typical multi-server MCP setup burns ~55k tokens of tool definitions before any
   work [3]; a code-execution-on-demand workflow cut 150k→2k tokens, 98.7% [2].
2. **Selection accuracy** — signal-to-noise collapses as N grows. "Claude's ability to
   correctly pick the right tool degrades significantly once you exceed 30-50 available
   tools" [3]. Anthropic frames the root as **context rot**: "as token counts increase,
   accuracy decreases" [4].

Both heads are solved by the same move: **stop loading everything upfront.**

## The canonical solution

### Three-level progressive disclosure (Agent Skills) — THE load-bearing fact
Anthropic's official model loads a skill in three tiers [1][6]:
- **Level 1 — metadata, ALWAYS loaded.** Only `name` + `description` are pre-loaded into
  the system prompt: "just enough information for Claude to know when each skill should be
  used without loading all of it into context" [1].
- **Level 2 — SKILL.md body, loaded ON TRIGGER.** Read into context only if Claude judges
  the skill relevant [1].
- **Level 3+ — references/scripts, loaded ON DEMAND.** "Reference files don't consume
  context tokens until actually read"; scripts run via bash, "only the script's output
  consumes tokens" [6]. Bundleable context is "effectively unbounded" [1].

**Implication for any consolidation argument:** the only always-on cost is Level 1
(name+description). Skill *bodies* are already lazy. So "skills are too big for the context
window" is only true of the *description* layer; bodies and references already cost nothing
until used.

### Retrieval / deferred loading (tools)
The Tool Search Tool with `defer_loading: true` keeps deferred tools out of the system
prompt; Claude searches a catalog and the API expands the 3-5 best matches inline [3].
Reduces tool-definition load >85%. Limits: max 10k tools, keep 3-5 most-used non-deferred,
use when >10 tools or >10k tokens of defs [3]. **No equivalent `defer_loading` exists for
Skills today** — skill descriptions are always Level-1. (Claude Code auto-defers *MCP tool*
descriptions past ~10% of budget — tools, not skills [secondary 5].)

### Subagent / context isolation
Subagents get their own context windows, explore, and return a condensed summary [9].
Tradeoff: handoff fidelity + high aggregate token use ("token usage explains 80% of the
variance" in research-task performance) [9].

### Unifying principle
All three are **just-in-time context**: keep lightweight identifiers, load the body at
runtime [4]. Lineage = Nielsen's progressive disclosure: show the few most-important options
first, the rest on request, improving learnability and error rate [8].

## Concrete guidance & numbers
| Item | Guidance | Src |
|---|---|---|
| `name` | ≤64 chars, lowercase/hyphens, no "anthropic"/"claude" | [6] |
| `description` | ≤1024 chars; state what it does AND when to use; third person | [6] |
| Scale | description chosen "from potentially 100+ available Skills" | [6] |
| SKILL.md body | keep <500 lines for optimal performance; split past that | [6] |
| references | keep one level deep; add a TOC for files >100 lines | [6] |
| metadata cost | ~100 tokens/skill always-on (community estimate, not primary) | [7] |
| tool search | >85% def-load reduction; max 10k tools; 3-5 non-deferred | [3] |

## Failure modes / limits (guard rails for the critique)
1. **Capability-invisibility — the #1 risk.** Discoverability lives entirely in Level-1.
   Weak/vague description ⇒ the model never learns the capability exists. Docs make
   description quality load-bearing and recommend padding with "common keywords" [3][6].
   Consolidation that produces a vaguer router description *loses routing accuracy*.
2. **Wrong-skill / blended-instruction.** Collapsing many workflows into one large body
   makes the model "blend instructions inappropriately" across workflows [secondary 10].
3. **Over/under-fetch** without clear trigger logic [secondary 10].
4. **Latency.** Deferral converts upfront tokens into sequential round-trips (search→expand→call) [3].
5. **Nested-reference truncation.** References >1 level deep get partial-read (`head -100`) [6].
6. **Subagent coordination cost** [4][9].

**Net:** literature supports thin Level-1 metadata, <500-line bodies, one-level references,
retrieval/isolation for the long tail. The single point of failure is **degrading Level-1
description quality during consolidation.**

## Sources (IEEE)
[1] Anthropic, "Equipping agents for the real world with Agent Skills," Eng. blog.
[2] Anthropic, "Code execution with MCP," Eng. blog, Nov 2025.
[3] Anthropic, "Tool search tool," Claude Developer Platform Docs.
[4] Anthropic, "Effective context engineering for AI agents," Eng. blog.
[5] Anthropic, "Introducing advanced tool use," Eng. blog (figures via secondary; verify).
[6] Anthropic, "Skill authoring best practices," Claude Developer Platform Docs.
[7] SwirlAI, "Agent Skills: Progressive Disclosure as a System Design Pattern" (secondary).
[8] J. Nielsen, "Progressive Disclosure," NN/g, 2006.
[9] Anthropic, "How we built our multi-agent research system," Eng. blog, Jun 2025.
[10] MindStudio, "Progressive Disclosure in AI Agents" (secondary; failure taxonomy).
[11] EclipseSource, "MCP and Context Overload," Jan 2026 (secondary).
