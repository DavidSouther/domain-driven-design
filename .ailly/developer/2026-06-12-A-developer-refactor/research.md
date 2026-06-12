# Research: Developer Skills Refactor (Research, Design, Plan, Build)

## Topic and Intent

Refactor the `developer:` plugin so its lifecycle matches a four phase shape: **Research, Design, Plan, Build**, each separated by a human review draft gate, with TDD red-green-refactor as the Build loop. The shape comes from the "Ailly OODA" blog post, but the OODA vocabulary and the "Obey the Testing Goat" framing stay in the blog; the skills use the established vocabulary of TDD and Extreme Programming.

Concretely the user asked for seven changes:

1. Replace `docs/` with `.ailly/` as the top level artifacts folder.
2. Add a focused `developer:research` skill that coordinates `research:using-research` for a topic, with a **search/expand** phase and a **falsification/refine** phase.
3. Merge `developer:design` and `developer:feature-test` into one skill that outputs `design.md` plus the executable feature test, dropping `feature-test.md`.
4. Keep `plan`, `red-green-refactor`, `cleanup`, and `initialize` substantially as they are.
5. Update `developer:ailly` for the new coordination, and judge whether `using-developer` still earns its place.
6. Judge whether `is-clean` and `git-workflow` are still necessary, given current models cover their intent without a loaded skill.
7. Update the e2e harness & project documentation to match.

## Search / Expand Phase

### Source material: the Ailly OODA blog post

The post (fetched from Notion, 2026-06-12) describes the target lifecycle directly. The load-bearing statements for this refactor:

- **Research** = "Observe + Orient." Gather canonical reference material from MCP tools, then apply Jeopardy search to expand context and find an anchor to the user intent, then "look to refute the idea." Produce a research report, review it for clarity/consistency/conciseness, collaborate with the user. Deep research "may have several ancillary supporting docs." If MCP tools are insufficient (ie, internal docs are unavailable or returning less information than might be expected), raise this as a warning and suggest either troubleshooting the connectors or refining the task.
- **Design** = "Orient + Decide." Focus the original prompt into "a specific, verifiable feature description" plus a sized overview. Output is "a design doc, including purpose, prior art, the user journey (and any guiding metrics), a specification, and alternatives considered", and "a feature test that, while it fails at this point, when it passes will show that the feature is appropriately implemented." The post explicitly bundles the feature test into the design output. Ailly asks clarifying questions for ambiguities research did not resolve.
- **Plan** = build a detailed implementation plan; "always look for a step 0 that modifies the type definitions" ("Type-First Test Driven Development"); final review before implementing.
- **Build** = mostly hands off, the agent will write tests, run them, write code, run tests until the code passes, then run checks until the plan is complete. Each step gets a commit. The feature test is green at the end.
- **Cleanup** = remove the questionable-value artifacts, ensure the branch is merged (squash), leave the directory ready for the next task. Ensure that any tasks are recorded, and any design details that are salient to the project long term have been captured in appropriate project documentation.
- The Quickstart already names **`.ailly/prompts`** as the home for long prompts, confirming the `.ailly/` direction.

This matches the requested changes: the design section list and the "feature test is part of design" merge both come straight from the post.

### Current developer plugin inventory (internal)

Fourteen skills today: `ailly`, `using-developer`, `design`, `feature-test`, `plan`, `red-green-refactor`, `thinking`, `refactor`, `cleanup`, `initialize`, `is-clean`, `git-workflow`, `clean-comments-review`, `visual-design`.

The current loop is a **three loop** model (`using-developer`): outer = design; middle = feature-test then plan; inner = red-green-refactor. `ailly` coordinates the session folder and enforces draft gates after design, feature-test, and plan.

Observations and existing drift the refactor should also resolve:

- `docs/` is referenced in **nine** skill bodies (`ailly`, `design`, `plan`, `cleanup`, `thinking`, `feature-test`, `using-developer`, `refactor`, `red-green-refactor`). The swap to `.ailly/` is mechanical but wide.
- `ailly` invokes **`developer:brainstorming`** and **`developer:design-doc`** (Skill Invocations and resume table), neither of which exists as a skill; the skill is `design`. Stale names.
- `design` writes to two different paths: `docs/developer/design/YYYY-MM-DD-A-<topic>.md` (checklist step 7) and `docs/developer/YYYY-MM-DD-A-<topic>/design.md` (After the Design). Inconsistent. Standardize on `design.md`.
- `design`'s six sections today are **Problem Statement, Prior Art, Metrics, Specification, Alternatives, Summary**. The target is **Purpose, Prior Art, User Journey and Metrics, Specification, Alternatives, Summary**. ("Problem Statement" becomes "Purpose"; "Metrics" becomes "User Journey and Metrics.")
- `cleanup` has a `YYYY-MM-DD-AA-<topic>` (double A) path typo.
- No OODA / Testing Goat / aviation language has leaked into any skill body; that framing is descriptive for the blog post's documentation. (obey the testing goat language is in voice-jefri, that's OK).

### Prior art: internal adjacent libraries and conventions

- **`research:using-research`** already encodes exactly the two-phase method the new `developer:research` skill should drive: a **Jeopardy! search** expand pass (3 to 5 query variants per concept) and a **Falsification** oppositional pass (restate the claim as a universal, negate into 3 to 5 falsifiable hypotheses, dispatch a subagent per hypothesis to hunt the counterexample). The new skill should **delegate** to this rather than reimplement it. Its Research Notes Convention writes per-skill findings to `docs/research/YYYY-MM-DD-A-<topic>/<skill>.md` with a `**Sources**` IEEE-style section. When delegating it should focus the expand language to finding supporting complaints & complementary work and the refine language to narrowing the scope of the task as much as possible.
- **`general:writing-paired-skills`** frames the wiring-vs-practice split. The new `developer:research` is a *phase/practice* skill (runs once per topic, produces `research.md`, assumes the research-plugin sources are configured by the `research:configuring-*` wiring skills). It cites that contract; it does not re-teach source setup.
- **`developer/references/forward_backward.md`** is the planning method `design` and `plan` already lean on; it survives the refactor unchanged.
- The **e2e harness** (`developer/e2e/`) is a three arm eval: *discovery* (does each `description:` route the model to the skill), *invocation* (does the skill body shape the output), *baseline* (same prompts, no skill). It is driven by the `ailly` Rust binary over YAML conversation files, vendored from live skill bodies by `vendor.sh`. `ci.sh` hardcodes suite counts (discovery 8, invocation 9, baseline 9) and runs a falsification gate (`improved > 0`, `regressed == 0`).

### Prior art: external (public projects and field research)

No single public artifact combines all four elements of this design (four gated phases, composable markdown skills, an executable acceptance test held red as the outer loop, and an expand-then-falsify research phase). Each cluster below covers a subset, which is the answer to "can an off-the-shelf tool do this": parts are well trodden, the combination is not.

- **Skills-as-markdown, gated phases, inner TDD: `obra/superpowers`** [1] is the closest overall match and the canonical example of the pattern this plugin is built in. Its lifecycle is `brainstorming` (Socratic design, presented in sections for sign-off) then `writing-plans` then `executing-plans` / `subagent-driven-development` then `test-driven-development` (red-green-refactor, deletes code written before tests) then `requesting-code-review` then `finishing-a-development-branch`. It folds research into brainstorming (no distinct Research phase) and its TDD is inner-loop only (no standing acceptance test). It validates both the skills mechanism and the merge of design with its sign-off gate.
- **Spec-driven phase pipelines with gates.** GitHub **Spec Kit** [2] (Spec then Plan then Tasks then Implement, markdown artifacts feeding forward). AWS **Kiro** [3] (Requirements then Design then Tasks, explicit approval gates, and a first-class **Bugfix Spec** type capturing current/expected/unchanged behavior). **BMAD-METHOD** [4] (four phases Analysis, Planning, Solutioning, Implementation, with a PASS/CONCERNS/FAIL readiness gate and a "Quick Flow" that skips planning for small work). **Agent OS** [5] (six commands including a `shape-spec` then `write-spec` split mirroring Research then Design). **Cline/Roo Plan and Act** [6] (the mode switch is the minimal gate). **Tessl** [7] (spec-centric: code is disposable, only the reviewed spec is durable). None maintain an executable acceptance test as the outer loop.
- **The acceptance-test outer loop.** This is the established double-loop / outside-in TDD pattern: "Test-Driven Development with Python" (Obey the Testing Goat) names the functional-test outer loop wrapping the unit-test inner loop [8], and GOOS uses a **walking skeleton**, an end-to-end acceptance test for the thinnest slice established first and grown [9]. This is the direct lineage for "the feature test stays red until the whole feature is done." A community Claude skill already ports GOOS into the skills format [9], precedent for this plugin's approach.
- **Field research on agent loops.** ReAct (reason-act-observe) [10], Reflexion (attempt-reflect-retry, the self-critique outer loop) [11], Self-Refine [12], and Plan-and-Solve / Plan-and-Execute (the planner/executor split that is the ancestor of Plan then Build) [13]. The OODA loop is the closest classical full-cycle analogue but has no built-in human gate; Schneier and Ottenheimer's "Agentic AI's OODA Loop Problem" [14] argues agents run OODA on untrustworthy observations, which is precisely the case for the human review gates this design inserts at each phase.
- **The expand-then-falsify research beat.** This is the most novel part relative to public prior art. The falsify/narrow half has a direct academic analogue in **POPPER** [15], an agentic framework guided by Popper's falsification principle that designs and runs falsification experiments against a hypothesis. The bug-vs-feature reclassification half is encoded as a first-class branch in Kiro's Bugfix Spec [3] and BMAD's investigate / Quick Flow [4]. No public framework unifies expand and falsify into one named, gated research phase, which positions this beat as the design's contribution rather than a port.

Takeaway for the falsification of the refactor itself: the pieces are derivative and proven (cite them in the Design phase to stand on established practice), but the assembly is not available off the shelf, so building it as skills in this plugin is justified.

## Falsification / Refine Phase

Each decision is stress tested with the same questions the new `developer:research` skill is meant to ask: is this a bug fix rather than a feature, can an off the shelf tool do it, and what is the smallest version that still meets the intent.

### Decision 1: `docs/` becomes `.ailly/`

- **For.** `docs/` collides with human authored project documentation; Ailly's session artifacts are explicitly "of questionable value outside the feature cycle" and cleaned up after. A hidden, tool owned `.ailly/` signals "ephemeral tool state," parallels `.git` / `.claude`, and is trivially gitignored or cleaned. The blog already uses `.ailly/prompts`. README line 24 documents an ad hoc `docs/` override, evidence the collision is already felt.
- **Falsify.** Not a feature; a convention rename. No off the shelf substitute (project specific). The rename is wider than the developer plugin: artifact paths live in **developer** (`docs/developer/`), **research** (`docs/research/`, written by every `research:*` skill via `using-research`), and **domain** (`docs/ddd/`) skill bodies, plus `docs/prompts/`. A unified `.ailly/` root is the point, so all move: `.ailly/developer/`, `.ailly/research/`, `.ailly/domain/` (see Decision 9, the `ddd` name is retired), `.ailly/prompts/`. Precision required: some `docs` hits are URLs (for example O'Reilly `integration-docs`) or generic prose, not the artifacts folder, and must not be rewritten.
- **Resolved (user, 2026-06-12).** Convention only. Update all artifact-folder references across all skills (developer, research, domain, general) and the three e2e harnesses and the README. Do **not** migrate existing `docs/` folders; that is a trivial manual move with few consumers.

### Decision 2: add `developer:research`

- **For.** The new first phase has no skill today. It needs a session driver that produces `research.md` behind a draft gate, the way `design` produces `design.md`. The two named phases (expand, then narrow) are the post's "Jeopardy then refute" recast in plain language.
- **Falsify.** Is `research:using-research` alone enough? No: that is a routing bootstrap, not a phase skill with an output artifact and a gate. Reimplement its search/falsify internals? No, that duplicates a maintained skill; **delegate** instead. Smallest version: a thin coordinator that (1) opens/continues the session folder, (2) drives `research:using-research` for the topic with an explicit expand brief (feature requests, user complaints, adjacent internal libraries and docs, public projects doing the same thing, field research) and a refine brief (bug-fix-not-feature, off-the-shelf alternative, scope reduction), (3) writes `research.md` marked draft, (4) stops at the gate.
- **Dual lens when delegating (user, 2026-06-12).** `research:using-research` is a *general* research skill. The `developer:research` coordinator frames every delegation with two lenses at once: software engineering practice **generally** (what established engineering and prior art say about this class of problem) and **this specific task** (the user's exact intent and codebase). The expand brief leans on the general lens to find supporting complaints and complementary work; the refine brief leans on the specific lens to narrow the task's scope as far as it will go.
- **Verdict.** Proceed as a delegating coordinator, not a re-implementation, with the dual-lens framing above.

### Decision 3: merge `design` and `feature-test`

- **For.** The post bundles the feature test into the design output. Merging removes one draft gate (the feature-test gate), so the human reviews design and its acceptance test together, which is where they are most coherent.
- **Falsify.** Does the feature test lose scrutiny by sharing a gate? It is reviewed alongside the design at one gate; acceptable and matches the post. The executable test moves "to the logical place for the project" (the project test tree per `initialize` conventions), and `design.md` references its path; `feature-test.md` is dropped. The merged skill keeps `feature-test`'s hard gate (write only the test, no implementation).
- **Verdict.** Proceed. New design sections = Purpose, Prior Art, User Journey and Metrics, Specification, Alternatives, Summary, plus the feature test artifact.

### Decision 4: keep `plan`, `red-green-refactor`, `cleanup`, `initialize`

- **Falsify "unchanged."** `plan` triggers today on "feature-test draft cleared" and reads `feature-test.md`; after the merge it triggers on "design draft cleared" and reads `design.md` plus the project feature test. `cleanup` and `thinking` and `rgr` carry `docs/` paths. So "unchanged" is true in spirit but each needs a trigger/path touch up. `initialize` and `red-green-refactor` are essentially untouched apart from path strings.
- **Verdict.** Keep; apply path and trigger edits only.

### Decision 5: `ailly` coordination and the value of `using-developer`

- **`ailly`** must change: resume table, loop graph, and Skill Invocations move to the four phase shape with gates after research, design, and plan; stale `brainstorming`/`design-doc` names are replaced; `docs/` becomes `.ailly/`.
- **`using-developer` falsification.** It is the bootstrap router (three-loop map, routing table, draft-gate table). It overlaps `ailly` heavily; both answer "which developer skill now." Its distinct job is the *discovery surface* the e2e measures and the at-a-glance map loaded by `general:using-general`. Today's models route from `description:` fields without it. **Option A:** keep a slimmed `using-developer` updated to the four phase shape (cheap, preserves the discovery eval, gives a map). **Option B:** drop it and let `ailly` plus `general:using-general` route. This is a genuine user decision.
- **Resolved (user, 2026-06-12): Option A.** Update `ailly` and keep a slimmed `using-developer` on the four phase shape. Rationale: `general:using-general` may not be installed, so the developer plugin needs its own routing surface to be self-sufficient. When `general` *is* installed the routing is doubled up, which is acceptable redundancy.

### Decision 6: necessity of `is-clean` and `git-workflow`

- **`is-clean`** is a diagnostic that runs CI commands and prints a status report. No skill body invokes it; only the e2e `is-clean-vs-cleanup` discovery pair and itself reference it. A current model can run `git status` and the CI commands and report cleanliness without a loaded skill. Low marginal value. **Lean remove.**
- **`git-workflow`** encodes an opinionated rebase-first feature-branch flow (`--force-with-lease`, `git rerere`, `checkout --theirs` for conflicts, interactive squash). `ailly` cites it to "suggest moving to that branch." The branch/commit mechanics are model-default knowledge, but the *opinions* (rebase over merge, force-with-lease, rerere) are not defaults a model would invent. **Counter:** loaded rarely; the opinion could live as a short reference or a few lines folded into `ailly`'s branch suggestion. **Lean remove or drastically slim**, keeping only the opinionated bits.
- **Resolved (user, 2026-06-12): remove both.** Delete `is-clean` and `git-workflow`. Remove `ailly`'s citation of `git-workflow` (the branch suggestion stays as a plain instruction in `ailly`). The `is-clean-vs-cleanup` discovery pair is removed from the developer e2e. Any opinionated git behavior that is genuinely wanted (rebase-first, force-with-lease) can be a short line in `ailly` rather than a loaded skill, but is not required.

### Decision 7: bugfix mode and an observed/expected reference (new, user, 2026-06-12)

- **For.** The refine phase explicitly asks "is this a bug fix rather than a feature." When the answer is yes, the work has a different shape than a feature. Kiro's Bugfix Spec [3] captures it cleanly as **observed / expected / unchanged** behavior driving a root-cause then fix then regression-test flow.
- **Shape.** Not a new skill: a **reference document** (for example `developer/references/bugfix.md`) written in observed/expected/unchanged language, that `ailly` (and the merged design skill) consult when the task is bug-shaped. The reproducing test is the regression guarantee; the feature-test merge already produces an executable test, so a bugfix produces a failing reproduction test in the same slot.
- **Verdict.** Add the reference and a short "if the task is a bugfix" pointer in `ailly` and the design skill. Keep the same Research, Design, Plan, Build framework; only the design content (observed/expected/unchanged) and the test's role (reproduction) differ.

### Decision 8: a quick-loop mode, not a BMAD skill (new, user, 2026-06-12)

- **For.** BMAD's scale-adaptive "Quick Flow" [4] and the blog's own "Ailly, complete this using a quick loop" both let a small, well-understood task skip the full gated pipeline. This is the model's own judgment plus the user's escape hatch, not a separate methodology.
- **Shape.** A **mode** of `ailly`, not a skill. The same Research, Design, Plan, Build framework runs compressed: collapse or auto-clear gates, produce minimal artifacts, churn to a green feature test. `ailly` documents when the mode is appropriate (no ambiguity, small surface) and what it trades away (the human review beats).
- **Verdict.** Add a quick-loop mode section to `ailly`. Do not create a BMAD skill.

### Decision 9: retire the `ddd` identifier (new, user, 2026-06-12)

The `.ailly` sweep surfaced that `ddd` is used two stale ways, both of which the user wants thoroughly retired in favor of `domain`:

- **Artifact path `docs/ddd/`** (all five domain skills plus `research:domain`) becomes `.ailly/domain/`, not `.ailly/ddd/`.
- **Skill prefix `ddd:<skill>`** in the domain skill bodies (`ddd:glossary`, `ddd:domain-model`, `ddd:ubiquitous-language`, `ddd:contracts-and-invariants`, `ddd:arrow-of-maturity`) becomes `domain:<skill>`. The plugin manifest namespace is already `domain:`; the `ddd:` prefix is the known mismatch recorded in `TASKS.md`.
- **`ddd:using-ddd`** references a skill that does not exist under that name; it is `domain:using-domain`.
- **e2e:** with `ddd:` gone from the bodies, `domain/e2e` tightens its `(ddd|domain):` patterns and `ci.sh` hygiene grep to `domain:` only, and the `docs/ddd/` strings in its prompts and `check_arrow_of_maturity.py` move to `.ailly/domain/`.
- **Not retired:** the prose acronym "DDD" where it names the methodology Domain-Driven Design (for example "the living DDD glossary"). That is the discipline's name, not the stale identifier. Flagging for the user to confirm; if full prose retirement is wanted, say so and it folds into the same sweep.
- **Verdict.** Retire the `ddd` identifier (folder and skill prefix) across the domain plugin and its e2e as part of the rename sweep.

### Tone

No OODA / Testing-Goat / aviation language is present in skill bodies, so the tone task is preventive: write the new and edited skills in TDD/XP vocabulary (feature test, acceptance test, red-green-refactor, draft gate), not "observe/orient/decide/act," "dogfight," or "obey the goat." "Whimsical" language should be constrained to the voices skills.

## Scope and e2e Impact (feasibility)

Two blast radii. The `.ailly` rename is **cross-plugin**; the structural skill changes are **developer-only**.

**Cross-plugin (`.ailly` rename plus `ddd` retirement).** Artifact-folder strings change in developer, research, domain, and general skill bodies and references, in the README, and in all three e2e harnesses that assert path strings (`developer/e2e`, `research/e2e`, `domain/e2e`): vendored `context/skills/` (re-vendored by each `vendor.sh`), invocation prompts, evals YAML, and the `check_*.py` scripts that match `docs/...` paths (for example `check_cleanup.py`, `check_arrow_of_maturity.py`). Rewrite only artifact paths (`docs/developer` to `.ailly/developer`, `docs/research` to `.ailly/research`, `docs/ddd` to `.ailly/domain`, `docs/prompts` to `.ailly/prompts`), never `docs` inside URLs or generic prose. Per Decision 9 the domain plugin's `ddd:<skill>` prefixes also become `domain:<skill>`, and `domain/e2e` tightens its `(ddd|domain):` patterns and hygiene grep to `domain:` only.

**Developer-only (structural).** The harness is real coupling, not optional. Concrete deltas:

- **`check_design.py`** section list changes to the six new names (Purpose, Prior Art, User Journey and Metrics, Specification, Alternatives, Summary), and it absorbs `check_feature_test.py`'s "exactly one executable test" rule (the merged skill emits the test).
- **`check_feature_test.py`** and the `feature-test` invocation/baseline prompts are removed; a **`check_research.py`** and `research` invocation/baseline prompts are added. Net invocation/baseline count stays 9.
- **Discovery** pairs change: `design-vs-feature-test` and `feature-test-vs-plan` collapse (merge); `is-clean-vs-cleanup` is removed (both skills deleted); add a `research`-routing pair (vague idea, nothing gathered yet, routes to `research` not `design`) and consider a bug-vs-feature routing case for the refine phase. Recompute the discovery count.
- **`ci.sh`** `expected_count()` (discovery 8, invocation 9, baseline 9) updates to the new counts; the `developer:<skill>` hygiene grep keeps working and must still pass for the new `research` skill identifier.
- Remove the `is-clean` and `git-workflow` skill directories and their vendored copies.

Bounded and mechanical once the skill set is settled. The right size for a single plan with a step per artifact group (rename sweep, merge, research skill, removals, ailly, e2e).

## Resolved Decisions (user, 2026-06-12)

All four open questions are answered; the verdicts above are updated to match.

1. **Artifacts:** convention only, no migration. `.ailly/` across all skills (developer, research, domain, general), the README, and the three e2e harnesses. Artifact paths only, not URLs. The domain artifacts root is `.ailly/domain/`; the `ddd` identifier is retired (Decision 9).
2. **`using-developer`:** keep, slimmed to the four phase shape (Option A), because `general` may not be installed.
3. **`is-clean` and `git-workflow`:** remove both.
4. **Feature-test location:** the location the `initialize` skill indicates for the project's test tree, with `design.md` holding the path.

Two additions:

- **Bugfix reference (`developer/references/bugfix.md`):** observed/expected/unchanged language for bug-shaped tasks; consulted by `ailly` and the design skill. Not a skill.
- **Quick-loop mode in `ailly`:** the scale-adaptive compressed loop. Not a BMAD skill.

## Sources

- Ailly OODA, internal blog (Notion), fetched 2026-06-12. Source of the four-phase lifecycle, the design section list, and the "feature test is part of design" merge.
- `developer/skills/*/SKILL.md`, `developer/e2e/**`, `README.md` (this repository, HEAD), read 2026-06-12. Current skill inventory, e2e coupling, and existing drift.
- `research/skills/using-research/SKILL.md` and `research/references/{jeopardy,falsify,citations}.md`. The expand/falsify method `developer:research` delegates to.
- `general/skills/writing-paired-skills/SKILL.md`, `general/skills/writing-skills/SKILL.md`. Authoring and pairing methodology.

External prior art (loose IEEE):

[1] obra, "superpowers," github.com/obra/superpowers; blog.fsck.com/2025/10/09/superpowers/.
[2] GitHub, "Spec Kit," github.github.com/spec-kit/.
[3] AWS, "Kiro Specs," kiro.dev/docs/specs/.
[4] BMAD-METHOD, github.com/bmad-code-org/BMAD-METHOD; docs.bmad-method.org/reference/workflow-map/.
[5] Builder Methods, "Agent OS," github.com/buildermethods/agent-os.
[6] Cline, "Plan and Act," docs.cline.bot/core-workflows/plan-and-act.
[7] Tessl, "Spec-driven development," docs.tessl.io/use/spec-driven-development-with-tessl.
[8] H. Percival, "Test-Driven Development with Python," ch. 24 (outside-in), obeythetestinggoat.com.
[9] S. Freeman and N. Pryce, "Growing Object-Oriented Software, Guided by Tests," growing-object-oriented-software.com; skills port: github.com/marshally/marshally-claude-skills.
[10] S. Yao et al., "ReAct," arXiv:2210.03629.
[11] N. Shinn et al., "Reflexion," arXiv:2303.11366.
[12] A. Madaan et al., "Self-Refine," arXiv:2303.17651.
[13] L. Wang et al., "Plan-and-Solve Prompting," arXiv:2305.04091.
[14] B. Schneier and D. Ottenheimer, "Agentic AI's OODA Loop Problem," 2025, schneier.com.
[15] K. Huang et al., "POPPER: Automated Hypothesis Validation with Agentic Sequential Falsifications," arXiv:2502.09858 (ICML 2025).
