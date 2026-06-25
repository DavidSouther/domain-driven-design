# Project Plan: Skill Progressive Disclosure for the Ailly Skillset

<!-- Long-loop reviewer (2026-06-25): plan is fully derived from the reviewed design;
no new open decisions at this gate. Draft marker cleared; run proceeds to build,
Feature A first. -->

**Closing Bell:** `.ailly/developer/2026-06-25-A-progressive-disclosure/closing-bell.md`
**Design:** `.ailly/developer/2026-06-25-A-progressive-disclosure/design.md`

A project plan. Each feature below is its own feature loop (its own design, feature
test, plan, build, cleanup) per `developer/references/project-cycle.md`. The project
plan enumerates the features, marks their dependency relationships, and ties each to
the Closing Bell tasks it advances. Detailed per-feature steps are produced when each
feature's own loop runs; the per-feature outlines here are scoping aids, not the final
feature plans.

## Step 0: Shared contract (settle before parallel work)

The one contract all three features must agree on first, the project-altitude
equivalent of a feature plan's Step 0:

- **Always-on token-share measurement.** Every feature reports the same metric the
  same way: count Level-1 `description:` frontmatter tokens per plugin, before and
  after, using the same assembly path `vendor.py` uses to build `disclosure.md`. The
  baseline is ~4,545 tokens across ~66 concurrent choices; the project target is
  ~25-30 concurrent choices. Each feature shows a net drop in its plugin's always-on
  description share. Record before/after counts in each feature's cleanup.
- **Capability-invisibility guard (common to all).** No capability loses its Level-1
  discoverability without the surviving body carrying keyword-rich routing prose for
  it. This is verified per feature by its `e2e` discovery suite.
- **Measurement instrument unchanged.** `vendor.py` assembly, the three-suite e2e
  shape (discovery / baseline / invocation), and the `ci.sh` falsification gate
  (`improved>0, regressed==0`) keep their structure. Features change the strings the
  assertions match, never the gate logic.

## Features

- [ ] **Feature A: Patterns (pilot)** (no dependencies, can start now)
- [ ] **Feature B: Voices** Parallel with: Feature C; shared contract: Step 0 token-share measurement
- [ ] **Feature C: Project loop** Parallel with: Feature B; shared contract: Step 0 token-share measurement, unchanged `vendor.py` + three-suite e2e shape

Ordering: A runs first and alone as the thesis-falsification pilot. If A fails to
hold-or-improve patterns routing on real eval data, stop. B and C run concurrently
(different sessions, no shared files) only after A validates.

### Feature A: Patterns (pilot)

Collapses 19 pattern leaf skills into one `using-patterns` skill with
`references/patterns/<name>.md` per pattern, adds the dedicated "find applicable
patterns" plan step, and re-expresses the patterns discovery gate.

Advances Closing Bell tasks 1, 2, 3, 6 (newtype, domain-objects, typed errors,
find-patterns) and the patterns half of task 8 (navigability).

Outline (the feature's own loop refines this into 3-7 steps):

1. Move each leaf skill body into `patterns/skills/using-patterns/references/patterns/<name>.md`
   (and its per-language reference triplets under `references/patterns/<name>/`),
   preserving content. Delete the 19 leaf skill frontmatter so only `using-patterns`
   carries a Level-1 description.
2. Rewrite the `using-patterns` body into the single routing surface: a routing table
   stating each pattern's discriminator in prose (the newtype-vs-domain-objects and
   configuring-vs-emitting discriminators explicitly), each row pointing at its
   `references/patterns/<name>.md`. Keep the body under the 500-line guidance; the
   leaf depth lives in references.
3. Re-express the discovery gate per the design: each `patterns:<name>` assertion
   becomes a bare-name assertion plus a `references/patterns/<name>.md` path
   assertion (positive and negative forms); reframe the discovery prompts to "which
   pattern applies, and where is its guidance?"; widen CUJ 0 grep to the
   reference-path form only (reviewer decision 2).
4. Add `.ailly/prompts/plan-use-patterns.md` and wire the dedicated pattern-search
   beat into the plan flow with phase-varying prescriptiveness.
5. Re-vendor `disclosure.md`, run `patterns/e2e/ci.sh`: confirm
   `newtype-vs-evs-order-line` and `errors-library-failure` flip green,
   `newtype-mixed-ids` stays green, suite holds-or-improves, and the always-on
   patterns description share drops (~1,492 tokens / 19 choices to one description).

Feature test (the feature-altitude gate): `patterns/e2e/ci.sh` green with the two
known-red cases flipped and no regression.

### Feature B: Voices

Moves the four character voices out of the skill mechanism, activating them outside
the LLM loop (default: Claude Code output-style, reviewer decision 1).

Advances Closing Bell task 7 (voice on output) and the voices half of task 8.

Outline:

1. Choose the activation mechanism (default output-style; fall back to hook/wrapper
   only on a concrete limitation). Author the voice content in that channel.
2. Remove `using-characters` and the four `voice-*` skills from the always-on Level-1
   view (retire the skills; the voice text becomes harness configuration).
3. Re-express the `characters/e2e` gate (recorded broken in `TASKS.md`): assert the
   project metrics directly: the four voice descriptions no longer appear in the
   always-on Level-1 count, and a styled-output check confirms the voice still colors
   output when activated outside the loop.
4. Measure: ~282 tokens and ~5 choices leave the always-on view.

Feature test: voice still colors output via the harness channel, and the four voice
descriptions are absent from the Level-1 count.

### Feature C: Project loop

Consolidates the developer coordinator plus five phases (`ailly` takes the phase as an
argument, loads one `references/phases/<phase>.md`, preserves subagent isolation) and
defers the five `research:configuring-*` descriptions.

Advances Closing Bell task 5 (run a developer design phase) and the developer half of
task 8.

Outline:

1. Move each phase skill body into `developer/skills/ailly/references/phases/<phase>.md`,
   preserving content. The coordinator selects the phase reference by argument and
   hands it to an isolated subagent (coordinator to phase reference to phase subagent
   reading one reference).
2. Retire the five phase skill frontmatter from the always-on view (per design;
   direct routing unused). Keep quick-loop/long-loop per-phase subagent spawning,
   now pointing each subagent at its one phase reference.
3. **Acceptance criterion (reviewer decision 4):** the phase-entry checks,
   model-per-phase, tool-failure, and program-management references stay reachable
   from the consolidated coordinator. Verify each is still pointed to after
   consolidation; do not orphan them.
4. Defer the five `research:configuring-*` descriptions out of the always-on view;
   keep research source leaves intact (not collapsed).
5. Run `developer/e2e/ci.sh` and `research/e2e/ci.sh`: the coordinator routes a phase
   argument to the right phase reference; research discovery holds after the
   `configuring-*` deferral; always-on developer + research description share drops.

Feature test: `developer/e2e` discovery routes phase arguments correctly with
isolation preserved; `research/e2e` holds; the four reconciled references remain
reachable.

## Notes on harness reality

The `ailly` binary and a model key were not available during this run (the same
deferral every prior `e2e` task in `TASKS.md` records). Where a feature's gate needs a
live `ci.sh` run, the build produces the structural changes and a unit-verified
checker, and the live run is recorded as a TASKS follow-up to execute once the binary
and a key are present, exactly as the model-per-phase, program-management, and
long-loop e2e work were handled.
