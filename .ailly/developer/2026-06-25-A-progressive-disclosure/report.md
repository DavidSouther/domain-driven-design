# End-of-Run Report: Skill Progressive Disclosure

*Long-loop project run, 2026-06-25. Branch `progressive_disclosure`.*

The long loop ran the full five-phase lifecycle at project altitude, crossing each
draft gate with a research-and-decide reviewer, and halted at the two never-auto-clear
gates: the human merge gate and the Closing Bell. This report follows the project-loop
retention rule (persisted alongside the design and the Closing Bell).

## Where it stopped

At the **human merge gate**, with all three features built and committed on
`progressive_disclosure`. The **Closing Bell** has not been run (a human study, run
once near completion; the agent never passes it). Both are awaiting the human.

## What was decided (per gate)

- **Research gate.** No open items: `research.md`'s Resolved Decisions already recorded
  all five decisions settled with the human on 2026-06-25. Marker cleared.
- **Design gate.** Four build-blocking items resolved by the reviewer (recorded in
  `design.md`, "Resolved by the long-loop reviewer"): (1) voice activation defaults to a
  Claude Code output-style; (2) the widened CUJ 0 grep forbids only the reference-path
  form, not bare names; (3) `plan-use-patterns` rides the existing patterns suite; (4)
  Feature C must keep the phase-guardrail/model/tool/program-management references
  reachable (promoted to a build acceptance criterion).
- **Plan gate.** No new open items (derived from the reviewed design). Marker cleared.
- **Feature A build review.** Corrected one falsification-fragility: `newtype-mixed-ids`
  kept a bare-name negative (`domain-objects`) that would false-fail a well-reasoned
  answer; switched to the path-form negative, consistent with the build's own rationale.
  Fixed the dangling `domain:domain-review` pointer the collapse introduced.
- **Feature C build review.** Fixed README's stale phase-skill table and a `triangulate`
  cross-ref to the argument-entered form. Reviewer-decision-4 references confirmed
  reachable.

## What was done (per feature)

| Feature | Change | Always-on Level-1 |
|---|---|---|
| A Patterns (pilot) | 18 leaf skills folded into one `using-patterns` router; per-pattern references; discovery gate re-expressed (name + reference-path); plan-use-patterns beat added | 19 choices / ~1,492 tok to 1 / ~284 tok |
| B Voices | 4 voices to Claude Code output-styles, activated outside the LLM loop; characters is output-style-only; e2e replaced by a metric check | 5 choices / ~282 tok to 0 |
| C Project loop | 5 developer phases to `references/phases/<phase>.md`, argument-entered with isolation; 5 research `configuring-*` deferred to references; both e2e gates re-expressed | developer -5 choices; research -5 choices |

Total concurrent Level-1 choices: ~66 to ~34 (patterns -18, characters -5, developer -5,
research -5). General and domain left untouched (out of scope). The ~25-30 target is
approached; the residual is the intentionally-kept research source leaves, developer
auxiliaries, and the out-of-scope general/domain plugins.

Commits: `c123329` (research+design+Closing Bell), `533be47` (Feature A), `df82471`
(Feature B), `0a2107a` (Feature C).

## The validation gate is deferred (the one thing the human must close first)

The design makes Feature A a falsification gate: the live `patterns/e2e/ci.sh` must show
`newtype-vs-evs-order-line` and `errors-library-failure` flipped green,
`newtype-mixed-ids` held, and `improved>0, regressed==0`. **No live run was possible in
this environment** (no `ailly` binary, no model key, the standing repo deferral). All
gates are structurally verified only. Before merging, run the four re-expressed suites
(see TASKS.md). If Feature A does not hold-or-improve patterns routing on real eval data,
the thesis is refuted and the consolidation should be reconsidered before merge.

## Status

Project design doc phase: **Implement** (features landed, behind the merge gate).
Becomes **Completed** only after the Closing Bell passes and the branch merges to `main`.
