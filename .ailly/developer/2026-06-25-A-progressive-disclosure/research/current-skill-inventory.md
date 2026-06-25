# Current Ailly Skill Inventory

*Specific lens. Measured 2026-06-25 against working-repo source.*

## Always-on Level-1 load by plugin
| Plugin | Skills | ~Description tokens | Notes |
|---|---|---|---|
| **patterns** | 19 | ~1,492 | Largest. Most didactic; each leaf teaches a when/when-not decision. All design/plan-scoped. |
| **research** | 14 | ~1,260 | 5 `configuring-*` are setup-only; 8 source leaves are genuinely distinct question-types. |
| **developer** | 14 | ~834 | Coordinator (`ailly`) + 5 phases + auxiliary (thinking, refactor, cleanup, initialize, viz, PM pair, clean-comments). |
| **domain** | 7 | ~330 | `using-domain` already says "Not loaded during implementation." |
| **general** | 7 | ~347 | conversation, review, dispatching, 3× writing-*, using-general. |
| **characters** | 5 | ~282 | 4 voice overlays + using-characters. Pure always-on style. |
| **TOTAL** | **66** | **~4,545** | |

**Two readings of the number.** 4,545 tokens is ~2.3% of a 200k window / ~0.45% of 1M —
minor as *tokens*. But 66 concurrently-visible choices is well past the **30-50 routing
threshold** [3]; the harness shows them all at once. The binding constraint is **routing
accuracy, not token count.**

## What's already progressive
- **developer:ailly** coordinator routes to phase skills; references/ (bugfix, long-loop,
  project-cycle, model-per-phase, tool-failure, forward_backward, …) load on demand. Quick-
  loop / long-loop spawn **subagents per phase** for context isolation.
- **research configuring-*** are setup-only by convention (never inside a session).
- **domain** is conditionally loaded by instruction ("not during implementation").
- **vendor.py / vendor.sh** assemble `disclosure.md` from frontmatter for the e2e discovery
  evals — i.e. there is already a routing-accuracy test harness per plugin.

## Mechanism mismatch (the taxonomy)
The skill mechanism is being used for four different jobs; only two fit well:
| Current use | Example | Better mechanism |
|---|---|---|
| Always-on, every-turn style | characters voice-* (282 tok) | output-style / always-on snippet, NOT a skill |
| Triggered, isolated, produces artifact | thinking, review, research phases | agent/subagent |
| Triggered capability w/ reference depth | patterns, research sources | skill + references (native fit) |
| Routing / coordination | using-* bootstraps, ailly | bootstrap skill (native fit) |

## Known routing defect that doubles as a falsification target
`patterns/e2e` `newtype-vs-domain-objects` case is **red**: 19 competing always-on
descriptions can't discriminate "primitive carrying no behavior" (newtype) from "object
carrying behavior" (domain-objects). A single `using-patterns` body could state the
discriminator in prose once. If consolidation flips this case green without regressing
`newtype-mixed-ids`, the thesis is validated on real data. (TASKS.md follow-up.)

## Consolidation potential (concurrent-choice count, the metric that matters)
Rough post-consolidation concurrent count: developer ~14→~3, patterns 19→1, research
14→~9 (keep distinct source leaves, defer configuring-*), characters 5→0-1, general 7→~3,
domain unchanged ~7. **~66 → ~25-30, under the 30-50 threshold.**

## At-use cost caveat
Consolidation trades always-on savings for at-use body size. For **patterns** this is
neutral-to-good (one dedicated "find patterns" plan step wants all options visible; leaf
shapes stay in references loaded as needed). For **research** it is *bad*: you only ever
want ONE source skill at a time, never all 14 — collapsing loses native direct routing and
gains little. This is why research "works well as-is."
