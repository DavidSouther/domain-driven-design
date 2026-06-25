# Research: Skill Progressive Disclosure for the Ailly Skillset

<!-- Long-loop reviewer (2026-06-25): read cold; the `## Resolved Decisions`
section already records all five open items decided with the human on 2026-06-25.
No undecided/blocking items remained at this gate, so the draft marker is cleared
and the run proceeds to project-altitude design. -->

## Topic and Intent

The Ailly skillset (66 skills across `developer`, `patterns`, `research`, `domain`,
`general`, `characters`) is "growing beyond what's practical to put in the context window."
The user wants to narrow how skills and agents load. The proposed shape:

- **developer** → one skill `ailly` carrying the coordinator groundwork, progressively
  disclosing parts of `using-developer` to choose which chunks to include as reference
  material. Each of the five phases gets one `references/phases/[phase].md`; Ailly attends
  the model to loading **only one** at a time, plus extras as needed (thinking, PM).
- **patterns** → one skill `using-patterns` that Ailly includes, activating during
  design/plan/review with phase-varying prescriptiveness, and plan gains a dedicated
  "look for applicable patterns" step (`.ailly/prompts/plan-use-patterns.md`).
- **research** → same collapse, "though it's been working pretty well as is."
- **general** and **characters** → "probably need to evolve into Skills + Agents."

Asked explicitly: find the **common problem** while **critiquing the specific proposal**.

## Search/Expand (general lens)

Full findings: [research/sota-progressive-disclosure.md](research/sota-progressive-disclosure.md).

The common problem is well-described in current SOTA (Anthropic Agent Skills docs, Tool
Search Tool, context-engineering writing). Every exposed capability carries an **always-on
description**; N capabilities = O(N) always-on cost with two heads — **token cost** and
**selection accuracy** ("Claude's ability to pick the right tool degrades significantly past
30-50 tools" [3]; "context rot" [4]). The canonical fix is **progressive disclosure / just-
in-time context**: load only what the current task needs.

The single most important fact for this proposal: **Agent Skills already do three-level
progressive disclosure.** Only Level 1 (`name` + `description`) is always-on. The SKILL.md
**body loads on trigger** (Level 2) and **references load on demand** (Level 3), costing zero
tokens until read [1][6]. So skill *bodies* are not the problem — they are already lazy. The
only always-on cost is the description layer.

Tools have a native `defer_loading` (Tool Search Tool) that keeps descriptions out of the
prompt and retrieves them on search [3]. **Skills have no such knob** — there is no native
way to make a skill description phase-conditional. The author's only levers are: write the
description (Level 1, always on) or demote the capability into a body/reference (Level 2/3,
on demand, but no independent harness routing).

The dominant documented failure mode of any consolidation is **capability invisibility**:
discoverability lives entirely in Level-1 text, so a vaguer router description means the
model stops knowing a capability exists [3][6][10].

## Falsification/Refine (specific lens)

Full inventory: [research/current-skill-inventory.md](research/current-skill-inventory.md).

**Two complementary motivations, both real (confirmed with user).** Measured always-on
description load is **~4,545 tokens across 66 skills**. On a large model that is ~2.3% of a
200k window — minor. **But on small models the budget is tight and this crosses >3%, which
is material** — and the *same* move fixes both: cutting the **66 concurrent choices** below
the 30-50 routing-accuracy ceiling [3] also cuts the always-on token share. So this is **not**
a misdiagnosis — token share and routing accuracy are two faces of the same O(N) problem and
the fix complements both. The success metric is **both**: routing accuracy on the per-plugin
`e2e` discovery evals (the binding correctness gate) **and** a measurable drop in always-on
description tokens (the small-model budget gate). Every consolidation step is gated on the
discovery evals improving-or-holding *and* the token share going down.

**Critique of the specific proposal, point by point:**

1. **Don't consolidate uniformly — the plugins differ in kind.**
   - **patterns is the strongest candidate.** 19 leaves, the largest description block
     (~1,492 tok), *all* design/plan-scoped, and used together during a single planning
     beat. Collapsing to one `using-patterns` whose body discriminates the patterns in prose
     is a *better* routing surface than 19 competing descriptions. Direct evidence: the
     `newtype-vs-domain-objects` e2e case is **red today** precisely because 19 descriptions
     can't express the "carries behavior vs not" discriminator; one body can. This is a
     built-in falsification test — flip it green without regressing `newtype-mixed-ids`.
   - **research should NOT be collapsed (the user already senses this).** Its 8 source leaves
     are genuinely distinct question-types the harness routes well, and `configuring-*` are
     already setup-only. You only ever want *one* source at a time, never all 14 — so
     collapsing loses native direct routing and gains little. "Tighten" research by deferring
     the 5 `configuring-*` (a smaller move), not by collapsing the source leaves.
   - **developer phases**: collapsing to `references/phases/[phase].md` is reasonable for the
     description budget, **but must preserve subagent isolation.** Quick-loop/long-loop
     already spawn a subagent per phase. The correct shape is *coordinator skill → phase
     reference → phase subagent that reads one reference*, not the coordinator reading all
     phases inline. Also note the harness can no longer route a user's `/developer:design`
     directly to a phase skill once phases are references; weigh that ergonomic loss.

2. **Guard the #1 failure mode.** Whatever you hide at Level 1 (19 pattern names, 5 phase
   names), the surviving bootstrap description must carry keyword-rich routing prose or the
   model won't know the capability exists [3][6]. This is exactly what the discovery evals
   measure — make them the gate.

3. **General/Characters: the instinct ("Skills + Agents") is right but under-specified — it's
   a mechanism-mismatch problem.** The skill mechanism is doing four jobs; only two fit:
   - **Characters voices** are always-on, every-turn *style* (282 tok). That is a poor fit
     for the skill mechanism (built for triggered capabilities). Better as a Claude Code
     **output-style / always-on snippet**, or an **agent** only when a styled artifact is
     produced — not five always-on skill descriptions.
   - **general:review, thinking, dispatching** are triggered, isolated, artifact-producing →
     **agents/subagents**. **writing-\*** are meta, rarely co-active with coding → fine as a
     small bootstrap. So "evolve into Skills + Agents" resolves to: voices → output-style;
     procedures → agents; routing → bootstrap.

4. **Don't over-engineer against a gap that may close.** The hand-rolled "bootstrap + phase
   references" is a workaround for the *absence* of native skill-deferral. Tools already got
   `defer_loading`; skills may follow. Design the consolidation so it's cheap to undo if a
   native skill-deferral lands — i.e. keep leaf content modular (one file per pattern/phase),
   not fused into one monolith body.

5. **At-use cost is a real trade, acceptable here.** Consolidation trades always-on savings
   for a larger body when the skill *is* used. For patterns/phases that's neutral (you wanted
   those options visible during that beat, and leaf shapes stay in on-demand references). For
   research it's a loss — another reason to leave research's source leaves alone.

**Sizing.** This is a **Project**, not a single feature (see
[developer/references/project-cycle.md]). It touches 5 plugins; each plugin's consolidation
is an independently shippable, independently valuable feature with its own e2e evals to keep
green. The proposal itself enumerates ~4 sub-efforts. Recommend running it as a project with
sequential features, **piloting on patterns first** because it is highest-value, has a
built-in falsification (the red routing case), and directly retires an open TASKS.md item.

**Off-the-shelf?** The native Agent Skills three-level disclosure *is* the off-the-shelf
mechanism for Level 1→2→3; there is no off-the-shelf "skill router/deferral" beyond it. The
`vendor.py`/`disclosure.md` evals are the repo's own bespoke tooling. No external tool
replaces this work.

**Smallest version that still meets the intent.** Pilot = collapse `patterns` 19 → one
`using-patterns` with `references/patterns/<name>.md` per pattern, add the dedicated "find
applicable patterns" plan step, and prove routing accuracy on the existing `patterns/e2e`
discovery evals (target: `newtype-vs-domain-objects` flips green, `newtype-mixed-ids` stays
green, overall ≥ prior). If validated, roll the same shape to developer phases; defer
research `configuring-*`; convert characters to an output-style. If *not* validated, the
thesis (consolidation improves routing) is refuted cheaply before touching four more plugins.

## Scope

Run as a **Project** with three features (decision 3):

- **Feature A — Patterns (pilot).** Collapse `patterns` 19 → one `using-patterns` with
  `references/patterns/<name>.md` per pattern; add the dedicated "find applicable patterns"
  plan step. Gate on `patterns/e2e` discovery evals (`newtype-vs-domain-objects` flips green,
  `newtype-mixed-ids` holds) **and** a measured drop in always-on tokens. Falsification gate
  for the whole thesis.
- **Feature B — Voices.** Move the four character voices out of the skill mechanism entirely;
  activate them **outside the LLM loop** (output-style / hook / wrapper). Removes ~282
  always-on tokens and 5 concurrent choices.
- **Feature C — Project loop.** Consolidate the developer coordinator + phases: `ailly` takes
  the phase as an argument (`/ailly design …`) and loads one `references/phases/<phase>.md`,
  **preserving subagent isolation** (coordinator → phase reference → phase subagent). Defer
  research `configuring-*`; keep research source leaves intact.

**Common success metric across all three:** discovery-eval routing accuracy improves-or-holds
**and** always-on description token share drops (both gates; decision 1).

**Out:**
- Collapsing research's source leaves (rejected by this research).
- Designing for easy reversal against a hypothetical native skill-`defer_loading` (decision 5).
- Domain plugin restructuring (already conditionally loaded; no pressure).
- Invokable phase-skill shells (direct routing unused; decision 4).

## Resolved Decisions

**Answered by research:**
- The always-on cost is **only** Level-1 description; bodies/references are already lazy.
- Real binding constraint is **routing accuracy at 66 concurrent choices**, not tokens
  (~4,545 tok is minor).
- patterns = best consolidation candidate; research source leaves = leave alone; phases =
  consolidate but keep subagent isolation; characters = mechanism mismatch → output-style.
- Smallest version = patterns-first pilot gated on the existing discovery evals, with a
  known-red case (`newtype-vs-domain-objects`) as the built-in falsification.
- Sizing = Project, sequential features.

**Resolved with the human (2026-06-25):**
1. **Metric = both, complementary.** Routing accuracy *and* always-on token share both
   matter; on small models the description block crosses >3% and is material. The single
   consolidation move improves both, so they reinforce rather than compete. Both gates apply.
2. **Character activation happens OUTSIDE the LLM loop.** Voices are not a skill the model
   loads at all — activation is harness-level (output-style / hook / wrapper), decided and
   applied outside the model's reasoning loop. Confirms voices → output-style, not skills,
   not agents-in-loop.
3. **Run as a Project with three features: Patterns, Voices, and the Project loop**
   (developer coordinator + phase-reference consolidation). Patterns is the pilot.
4. **Direct routing is not used** — entry is `/ailly design ...`, `/ailly build ...`. Losing
   harness-native `/developer:design` is fine; the `ailly` skill takes the phase as an
   argument and loads the matching phase reference. No invokable phase shells needed.
5. **Commit to the bootstrap direction regardless.** Do not spend design effort keeping it
   easily reversible for a hypothetical native skill-`defer_loading`; this is the better
   architecture on its own merits.

## Sources

[1] Anthropic, "Equipping agents for the real world with Agent Skills," Anthropic Engineering.
[2] Anthropic, "Code execution with MCP: building more efficient AI agents," Nov 2025.
[3] Anthropic, "Tool search tool," Claude Developer Platform Docs.
[4] Anthropic, "Effective context engineering for AI agents," Anthropic Engineering.
[5] Anthropic, "Introducing advanced tool use," Anthropic Engineering (accuracy figures via secondary; verify before quoting).
[6] Anthropic, "Skill authoring best practices," Claude Developer Platform Docs.
[7] SwirlAI, "Agent Skills: Progressive Disclosure as a System Design Pattern" (secondary).
[8] J. Nielsen, "Progressive Disclosure," Nielsen Norman Group, 2006.
[9] Anthropic, "How we built our multi-agent research system," Jun 2025.
[10] MindStudio, "Progressive Disclosure in AI Agents" (secondary; failure taxonomy).
[11] EclipseSource, "MCP and Context Overload," Jan 2026 (secondary).

*Internal artifacts:* [research/sota-progressive-disclosure.md](research/sota-progressive-disclosure.md),
[research/current-skill-inventory.md](research/current-skill-inventory.md).
