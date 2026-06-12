# Design: Developer Plugin Structural Refactor (Research, Design, Plan, Build, Cleanup)

**Scope (structural-first, per user 2026-06-12).** This design covers the developer-plugin **structural** changes on the **current `docs/` paths**. Two cross-plugin items from `research.md` are deferred to a follow-up sweep and are out of scope here:

- **Decision 1**, the `docs/` to `.ailly/` rename across developer, research, domain, and general.
- **Decision 9**, retiring the `ddd` identifier (folder and skill prefix) and the prose convention ("Domain-Driven Design" on first mention per file, "DDD" after).

Both are recorded in the Summary as the next design/plan cycle. This design reads `research.md` (Research phase, cleared) as its input and turns its remaining seven decisions into reviewable structural changes. The design uses the **new** six section names it defines (Purpose, Prior Art, User Journey and Metrics, Specification, Alternatives, Summary) rather than the current skill's headings, dogfooding the target.

## Purpose

The developer plugin should teach the five-phase lifecycle: **Research, Design, Plan, Build, Cleanup**, each separated by a human-review draft gate, with red-green-refactor as the Build loop.

Today the plugin does not match that shape:

- There is **no Research phase**. Idea-gathering is folded into `design`, so a vague prompt with nothing gathered yet has no home. Users can and do push their own research due to its high utility, but this pushes that directly into Ailly's core loop.
- **Design and the feature test are two gates.** The human reviews the design, clears it, then reviews the feature test separately, even though the test is most coherent read alongside the design that motivates it.
- `ailly` invokes **`developer:brainstorming`** and **`developer:design-doc`**, neither of which exists. The skill is `design`. The resume table and loop graph still describe the three-loop model.
- Two skills earn little: **`is-clean`** (a status report a current model produces without a loaded skill) and **`git-workflow`** (whose only non-default content is a few rebase opinions).
- **Cleanup is an afterthought.** It is named only in `ailly`'s "Next Task" aside, `using-developer` points its cleanup row at `refactor` rather than `cleanup`, and it is absent from the loop graph (which ends at `rgr -> stop`). It deserves to be a dedicated terminal phase.

This refactor adds the Research phase as a delegating coordinator, merges the feature test into Design behind one gate, removes the dead weight, adds a bugfix reference and a quick-loop mode, elevates Cleanup to a named terminal phase, and re-coordinates `ailly` and a slimmed `using-developer` onto the five-phase shape. The developer e2e harness moves with the skills so the change is provably routed and output-shaped.

## Prior Art

From `research.md`'s external scan (full citations there):

- **`obra/superpowers`** [1] is the closest overall match: markdown skills, a brainstorming sign-off gate, inner-loop TDD that deletes pre-test code. It folds research into brainstorming and keeps TDD inner-loop only. It validates the skills mechanism and the design-plus-gate merge.
- **Gated phase pipelines.** Spec Kit [2], Kiro [3] (with a first-class **Bugfix Spec** of observed/expected/unchanged behavior, the model for Decision 7), BMAD-METHOD [4] (a scale-adaptive **Quick Flow**, the model for Decision 8), Agent OS [5].
- **The acceptance-test outer loop.** "Obey the Testing Goat" [8] (functional-test outer loop) and GOOS [9] (walking skeleton). Direct lineage for "the feature test stays red until the feature is done."
- **The expand-then-falsify research beat.** POPPER [15] (agentic falsification). The most novel part relative to public prior art; no off-the-shelf tool unifies expand and falsify into one gated phase.

Internal prior art the new work stands on:

- **`research:using-research`** already encodes the expand (Jeopardy! search) and falsify (oppositional) method the new `developer:research` will **delegate** to, writing per-skill findings under `docs/research/YYYY-MM-DD-A-<topic>/`.
- **`general:writing-paired-skills`** frames the wiring-vs-practice split. `developer:research` is a phase/practice skill; it cites the `research:configuring-*` wiring contract rather than re-teaching source setup.
- **`developer/references/forward_backward.md`** is the planning method `design` and `plan` already use; it survives unchanged.

## User Journey and Metrics

**Primary journey.** An operator runs `developer:ailly` for a new topic. `ailly` creates the session folder and routes by resume point:

1. **Research** (new `developer:research`). Opens or continues the session, drives `research:using-research` with a **dual-lens** brief (software-engineering practice generally, plus this exact task and codebase): an **expand** pass for supporting complaints and complementary work, and a **refine** pass that asks "is this a bug not a feature," "can an off-the-shelf tool do it," and "what is the smallest version." Writes `research.md` marked draft, stops at the gate.
2. **Design** (merged `design` + `feature-test`). Reads the cleared `research.md`. Produces `design.md` (Purpose, Prior Art, User Journey and Metrics, Specification, Alternatives, Summary) **plus** one executable feature test placed in the project test tree (location per `developer:initialize`), with `design.md` recording the test path. Keeps the feature-test hard gate: write only the test, no implementation. One draft gate covers both.
3. **Plan** (kept). Reads the cleared `design.md` and the failing feature test. Breaks the path into 3 to 7 steps, step 0 modifies type definitions. Marks the plan draft, stops at the gate.
4. **Build** (kept `red-green-refactor`). `ailly` loops red-green-refactor per plan step until the feature test is green. Each step commits.
5. **Cleanup** (kept `cleanup`). A dedicated terminal phase, not an afterthought. Runs the final `developer:refactor` and review pass, applies formatters and lint fixers, extracts the design's deferred decisions into `docs/developer/TASKS.md` (with TASK-NOTES where needed), then **pauses for human approval before** the squash-merge or PR. The feature test stays green throughout.

**Quick-loop mode.** For a small, unambiguous task, the same five phases run compressed: gates auto-clear, artifacts are minimal, the loop churns to a green feature test. `ailly` documents when the mode fits (no ambiguity, small surface) and what it trades away (the human review beats). Not a separate skill.

**Bugfix shape.** When the refine pass reclassifies the task as a bug, `ailly` and the design skill consult `developer/references/bugfix.md` (observed / expected / unchanged). The same five phases run; the design content uses that vocabulary and the feature test is a failing **reproduction** test. Not a separate skill.

**Metrics (how we know it works).** The feature test for this refactor is the developer e2e harness:

- `developer/e2e/ci.sh` runs green with the recomputed suite counts and the falsification gate holding (`improved > 0`, `regressed == 0`).
- The `developer:<skill>` hygiene grep over `context/AGENTS.md` and `profile.md` still passes (no skill identifier leaks to the baseline arm), including the new `research` identifier.
- Discovery routing: a vague-idea prompt routes to `research`; a cleared design routes to `plan`; a finish-the-topic prompt routes to `cleanup` (not `refactor`); the removed pairs no longer appear.
- No skill body references a removed or renamed skill (`brainstorming`, `design-doc`, `is-clean`, `git-workflow`, `feature-test` as a separate phase).

## Specification

Changes grouped by artifact. Each group is a candidate plan step.

### 1. New skill `developer:research`

A thin **delegating coordinator**, not a re-implementation of research mechanics. It owns the artifact and the gate; `research:using-research` owns the search and falsification internals (Jeopardy! expand, oppositional falsify). Frontmatter `description` routes vague, nothing-gathered-yet prompts here (and away from `design`).

**Dual lens (Decision 2, user 2026-06-12).** `research:using-research` is a *general* research skill. `developer:research` frames every delegation with two lenses at once: software-engineering practice **generally** (what established engineering and prior art say about this class of problem) and **this specific task** (the user's exact intent and codebase). The expand brief leans on the general lens; the refine brief leans on the specific lens.

Behavior:

1. Open or continue the session folder (`docs/developer/YYYY-MM-DD-A-<topic>/`).
2. Drive `research:using-research` with an explicit **expand** brief, leaning on the general lens to find supporting complaints and complementary work: feature requests, user complaints, adjacent internal libraries and docs, public projects doing the same thing, and field research. A deep topic may spin off several ancillary supporting docs.
3. Drive a **refine** brief, leaning on the specific lens to narrow the task as far as it will go: is this a bug fix rather than a feature, can an off-the-shelf tool do it, should we be collaborating with another team to work on it, what is the smallest version that still meets the intent? This list is not exhaustive nor necessary; the skill should select appropriate refinements based on the expand findings.
4. Write `research.md` (Topic and Intent, Search/Expand, Falsification/Refine, Scope, Resolved Decisions, Sources) marked `*Draft YYYY-MM-DD*`, then review it for clarity, consistency, and conciseness and collaborate with the user on the questions research did not resolve. Per-skill findings land under `docs/research/YYYY-MM-DD-A-<topic>/<skill>.md` with IEEE-style Sources, the existing `research:using-research` Research Notes Convention.
5. Cite the `research:configuring-*` wiring contract for source setup rather than re-teaching it. If MCP research sources are insufficient (unavailable or returning less than expected), raise a warning and suggest troubleshooting the connectors or refining the task.
6. Stop at the draft gate.

The structure of `research.md` produced by this very session is the template.

### 2. Merge `design` + `feature-test` into `design`

- Keep the skill name `design` (deferred-name note in Summary).
- New section list: **Purpose, Prior Art, User Journey and Metrics, Specification, Alternatives, Summary** ("Problem Statement" becomes "Purpose"; "Metrics" becomes "User Journey and Metrics").
- The skill emits **one executable feature test** in the project test tree, with `design.md` recording its path. It absorbs `feature-test`'s user-story step and its **hard gate** (write only the test, no implementation).
- Standardize the output path on `docs/developer/YYYY-MM-DD-A-<topic>/design.md` (today the skill names two different paths; pick the session-folder one).
- Delete the `feature-test` skill directory after the merge.

### 3. `ailly` re-coordination

- Replace the stale `developer:brainstorming` / `developer:design-doc` invocations with `developer:research` and `developer:design`.
- Resume table and loop graph move to the five-phase shape (Research, Design, Plan, Build, Cleanup) with draft gates after **research**, **design**, and **plan** (the feature-test gate is gone, folded into design). Build loops red-green-refactor per plan step; the loop graph's `rgr -> stop` edge becomes `rgr -> cleanup -> stop`.
- **Formalize Cleanup as the fifth phase.** Route to `developer:cleanup` once the feature test is green; it pauses for human approval before the squash-merge. Today cleanup is only a "Next Task" aside.
- Add a **Quick-loop mode** section (Decision 8).
- Add a short "if the task is a bugfix" pointer to `developer/references/bugfix.md` (Decision 7).
- Replace the `developer:git-workflow` citation with a plain branch-suggestion instruction; optionally keep one line of the rebase-first / force-with-lease opinion inline (Decision 6).

### 4. Slim `using-developer` to the five-phase shape (Option A)

Keep the skill as the developer plugin's self-sufficient routing surface (`general:using-general` may not be installed). Update the loop graph to five phases (Research, Design, Plan, Build, Cleanup); the routing table (`research` added; `feature-test`, `is-clean`, and `git-workflow` rows removed; the `design` row notes it now includes the feature test; the cleanup row repointed from `developer:refactor` to `developer:cleanup` as the terminal phase); and the draft-gate table (research, design, plan, plus the cleanup merge-approval gate).

### 5. Remove `is-clean` and `git-workflow`

Delete both skill directories. Remove the `is-clean-vs-cleanup` discovery pair. Move any genuinely wanted git opinion into one line in `ailly` (see group 3).

### 6. Trigger and pointer touch-ups on kept skills

- `plan`: trigger changes from "feature-test draft cleared / reads `feature-test.md`" to "design draft cleared / reads `design.md` plus the project feature test."
- `red-green-refactor`, `cleanup`, `initialize`: behavior unchanged. One narrow edit lands now regardless: fix `cleanup`'s `YYYY-MM-DD-AA-<topic>` double-A typo. The `docs/` path strings on these skills are governed by the deferred sweep (Decision 1), not this design, so the planner must not rename them here.

### 7. `developer/references/bugfix.md`

New reference in observed / expected / unchanged language (Kiro model), consulted by `ailly` and `design` when the task is bug-shaped. The reproduction test fills the same slot the merged design's feature test fills.

### 8. Developer e2e harness (`developer/e2e/`)

- **`check_design.py`**: `SECTIONS` becomes the new six names; absorb `check_feature_test.py`'s "exactly one executable test" rule.
- **Remove** `check_feature_test.py` and the `feature-test` invocation/baseline prompts; **add** `check_research.py` and `research` invocation/baseline prompts. Net invocation and baseline count stays **9**.
- **Discovery pairs**: remove `design-vs-feature-test`, `feature-test-vs-plan`, and `is-clean-vs-cleanup`; add `research-vs-design` (vague idea, nothing gathered, routes to `research`), `design-vs-plan` (cleared design routes to `plan`), and `cleanup-vs-refactor` (finish-the-topic routes to `cleanup`; tidy-while-green routes to `refactor`). **Discovery count stays 8** (remove 3, add 3); the new `cleanup-vs-refactor` pair restores the routing coverage the deleted `is-clean-vs-cleanup` pair gave `cleanup`. The bugfix reclassification is deliberately **not** a discovery case: a bug-shaped and a feature-shaped prompt both route research then design, so they do not discriminate at the routing surface. The bugfix path is exercised by `developer/references/bugfix.md` and the `design` invocation check instead.
- **`ci.sh`**: `expected_count(discovery)` **stays 8** (three pairs out, three in); invocation and baseline stay 9. The `developer:<skill>` hygiene grep keeps working and must pass for the new `research` identifier.
- **`check_ailly.py`**: update any assertions tied to the old resume table / loop names.
- Confirm `vendor.sh` copies skill bodies generically (no hardcoded `is-clean` / `git-workflow` / `feature-test` names to prune).

## Alternatives

- **Off-the-shelf tool instead of building this.** Rejected in `research.md`: no public artifact combines gated phases, composable markdown skills, a held-red acceptance test as the outer loop, and an expand-then-falsify research phase. The pieces are proven and cited; the assembly is not available, so building as skills is justified.
- **Drop `using-developer`, route via `ailly` + `general:using-general` (Option B).** Rejected. `general` may not be installed, so the developer plugin needs its own routing surface. Accept the redundancy when `general` is present.
- **Keep `is-clean` / `git-workflow`.** Rejected. Current models cover their intent without a loaded skill; the only non-default content (rebase opinions) folds into one `ailly` line.
- **One combined design and plan, or sweep-first.** Rejected in favor of **structural-first**: design the developer-plugin structural changes on `docs/` paths now, then a separate sweep renames `docs/` to `.ailly/` and retires `ddd`. Keeps this design's blast radius developer-only and lands a green developer e2e before the wide mechanical rename.
- **Separate skills for bugfix and quick-loop.** Rejected. A reference document and an `ailly` mode keep the five-phase framework single; only the design content and the test's role differ.

## Summary

The developer plugin moves to Research, Design, Plan, Build, Cleanup with draft gates after research, design, and plan and a human approval before the cleanup merge. New `developer:research` delegates to `research:using-research`; `design` absorbs the feature test behind one gate; Cleanup is elevated from an afterthought to a named terminal phase; `is-clean` and `git-workflow` are deleted; a bugfix reference and a quick-loop mode are added; `ailly` and a slimmed `using-developer` re-coordinate; the developer e2e harness moves with the skills and stays green.

**Feature test for this refactor (next phase writes it):** `developer/e2e/ci.sh` green with recomputed suite counts and the falsification gate holding. Place per existing harness conventions; `design.md`'s test path slot is `developer/e2e/ci.sh`.

**Deferred to the follow-up sweep (its own design/plan cycle):**

- **Decision 1**, `docs/` to `.ailly/` across developer, research, domain, and general skill bodies, references, the README, and all three e2e harnesses (artifact paths only, never `docs` inside URLs or prose).
- **Decision 9**, retire the `ddd` identifier: `docs/ddd/` to `.ailly/domain/`, skill prefix `ddd:` to `domain:`, fix `ddd:using-ddd` to `domain:using-domain`, tighten `domain/e2e` patterns to `domain:` only. Prose convention: write "Domain-Driven Design" on first mention per file, "DDD" thereafter.

**Other deferred decisions:** the merged skill keeps the name `design` (revisit only if a clearer name surfaces). The discovery count is committed at 8 (see Specification group 8).

## Sources

Inherits `research.md`'s sources. Citation numbers above index that document's reference list. Files read for this design (this repo, HEAD, 2026-06-12): `developer/skills/{ailly,design,feature-test,plan,using-developer,cleanup}/SKILL.md`, `research/skills/using-research/SKILL.md`, `developer/e2e/ci.sh`, `developer/e2e/evals/scripts/check_design.py`, `developer/e2e/` file tree.
