# Project Design: Skill Progressive Disclosure for the Ailly Skillset

**Phase:** Review
**Closing Bell:** `.ailly/developer/2026-06-25-A-progressive-disclosure/closing-bell.md`
**Release flag:** the `progressive_disclosure` branch / merge gate (see Release Flagging).

This is a Project, not a single feature. It carries the six design sections at
project altitude per `developer/references/project-cycle.md`, and its exit
criterion is the Closing Bell above, not one executable feature test. Each of the
three features keeps its own per-plugin e2e gate (the feature-test slot at feature
altitude).

## Purpose

The Ailly skillset is 66 skills across six plugins, carrying ~4,545 always-on
Level-1 `description:` tokens. Every exposed skill pays an O(N) always-on cost the
moment a session starts, with two heads that are the same problem seen twice:
token share (material on small models, where the description block crosses >3% of a
tight budget) and routing accuracy (66 concurrent choices is past the documented
30-50 ceiling where selection degrades). Agent Skills already do three-level
disclosure, so skill bodies and references are already lazy; the only always-on
cost is the description layer. The single move that helps both heads is to cut the
number of concurrently-visible Level-1 descriptions while preserving every
capability's discoverability in a surviving body.

The three features deliver value only together because they are one move applied to
the three plugins where the skill mechanism is being mis-used in three different
ways:

- **Patterns** uses 19 always-on descriptions to express a single design-time
  decision (which pattern applies). One body that states the discriminators in prose
  is a better routing surface than 19 competing descriptions.
- **Voices** uses 4 always-on, every-turn style overlays through a mechanism built
  for triggered capabilities. Style belongs outside the model's selection loop.
- **The project loop** uses one coordinator description plus five phase descriptions
  to route a flow that is already entered by argument (`/ailly design ...`), not by
  the harness selecting a phase skill.

Shipped one at a time without the others, the always-on count stays above the
routing ceiling and the small-model budget stays blown; the value is in driving the
whole concurrent-choice count from ~66 to ~25-30, under the threshold. Patterns is
the pilot because it carries the largest description block, has a built-in
falsification (two known-red routing cases the consolidation must flip green), and
retires an open `TASKS.md` item. If consolidation does not improve patterns routing
on real eval data, the thesis is refuted before B and C touch two more plugins.

## Prior Art

- **Native three-level Agent Skills disclosure.** Level 1 (`name` + `description`)
  is always loaded; the SKILL.md body loads on trigger; references load on demand and
  cost zero tokens until read. This is the off-the-shelf mechanism this project
  leans on: consolidation demotes 19 leaf descriptions (Level 1) into one body
  (Level 2) plus per-pattern references (Level 3). No external router is needed or
  exists.
- **Tool Search `defer_loading`.** The Tool Search Tool keeps deferred tool
  descriptions out of the prompt and retrieves them on search, cutting tool-definition
  load by >85%. It applies to tools only; there is no skill-description equivalent
  today. The hand-rolled bootstrap-plus-references shape is the skill-side stand-in
  for that missing knob. Research decision 5 commits to this direction regardless of
  whether a native skill-deferral lands later, so the design does not spend effort on
  reversibility.
- **The repo's own routing-eval harness.** `vendor.py` / `vendor.sh` assemble
  `disclosure.md` from each plugin's frontmatter, and each plugin's `e2e/` runs a
  discovery suite (routing from descriptions), a baseline arm (no skill loaded), and
  an invocation suite, with a falsification gate (`improved>0, regressed==0`). This
  is bespoke repo tooling, not off-the-shelf; it is the measurement instrument every
  feature gates on.
- **Prior consolidation and e2e work (`TASKS.md`).** The per-plugin e2e harnesses
  (`patterns/e2e`, `developer/e2e`, `research/e2e`, `domain/e2e`, `general/e2e`,
  `characters/e2e`) and the paired-skill convention
  (`general:writing-paired-skills`, the `configuring-*` families) are the precedent
  this project extends. `TASKS.md` already records the patterns `newtype` vs
  `domain-objects` discrimination gap as a known follow-up; Feature A retires it.
  `characters/e2e` is recorded as broken (never produced a run); Feature B's removal
  of voices from the skill mechanism resolves that surface rather than repairing it.

## User Journey and Metrics

The end-to-end journey is the **skill author / Ailly operator** working a normal
session. They never see the restructuring; they describe a problem in their own
words and expect the right guidance to surface. The project succeeds when, after
consolidation, that operator's routing stays accurate (or improves) while the
always-on description load drops.

Journey, before and after:

1. The operator opens a session. **Before:** 66 descriptions load, ~4,545 tokens.
   **After:** ~25-30 descriptions load, with the always-on share measurably lower.
2. The operator hits a design pressure ("wrap a primitive ID so it can't be mixed").
   **Before:** the model picks among 19 pattern descriptions. **After:** the model
   loads one `using-patterns` body and names the pattern from its routing prose,
   pointing at `references/patterns/<name>.md`.
3. The operator runs a developer phase (`/ailly design ...`). **Before/After:** the
   coordinator routes to the phase; after, it loads one `references/phases/<phase>.md`
   and spawns a phase subagent that reads only that reference (isolation preserved).
4. The operator wants a character voice on output. **Before:** a voice skill loads
   into the model's selection view. **After:** the voice is applied outside the LLM
   loop and is not a choice the model weighs.

**Metrics (both gates, every feature):**

- **Routing accuracy** — the per-plugin `e2e` discovery suite improves-or-holds, and
  the falsification gate in `ci.sh` (`improved>0, regressed==0`) stays green. This is
  the binding correctness gate.
- **Always-on token share** — count Level-1 `description:` frontmatter tokens per
  plugin before and after, the same way `vendor.py` assembles `disclosure.md` from
  frontmatter. Baseline is ~4,545 tokens / ~66 concurrent choices; the target is
  ~25-30 concurrent choices, each consolidation step showing a net drop in its
  plugin's always-on description share. The patterns block (~1,492 tokens, 19
  choices) collapses to one description; voices remove ~282 tokens and ~5 choices;
  the developer phases collapse from 5 descriptions plus the coordinator toward ~3.

The **measure of done** is the Closing Bell above: a competent operator, untold of
the restructuring, routes to the right guidance for the consolidated plugins, finds
no capability gone invisible, and reports the surface no harder to navigate.

## Specification

Three independently-shippable features, each with its own per-plugin e2e gate. The
common contract every feature honors: **no capability loses its Level-1
discoverability without the surviving body carrying keyword-rich routing prose for
it**, because discoverability lives entirely in Level-1 text and a vaguer router is
the documented #1 failure mode (capability invisibility).

### Feature A — Patterns (pilot)

Collapse the 19 pattern leaf skills into ONE `using-patterns` skill whose body
carries the routing and teaching prose, with one `references/patterns/<name>.md` per
pattern holding the leaf content (overview, when-to-use, core pattern, language
references). The existing per-language reference triplets move under the
corresponding `references/patterns/<name>/` tree. Add a dedicated "find applicable
patterns" plan step at `.ailly/prompts/plan-use-patterns.md` (source prompt already
present) so the plan phase always runs a pattern-search beat with phase-varying
prescriptiveness: encourage during design, prescribe shape during plan, both
directions during review.

Boundary: Feature A changes the patterns plugin only. It does not touch the
`vendor.py` assembly contract, the three-suite e2e shape, or the falsification gate
in `ci.sh`. It changes which identifiers the discovery evals assert (below).

#### The discovery-gate re-expression (the critical design problem)

Today `patterns/e2e/evals/discovery.yaml` asserts plugin-prefixed skill identifiers
as routing targets, e.g. `text_contains "patterns:newtype"`,
`text_not_contains "patterns:domain-objects"`. The discovery prompts ask "Which
`patterns:*` skill applies?". Once the 19 leaves collapse into one
`using-patterns`, those identifiers no longer name real skills: the correct answer
becomes "apply the *newtype* pattern / see the newtype reference", not "invoke
`patterns:newtype`". The gate must keep measuring routing accuracy and keep
falsifying baseline-arm output without weakening `improved>0, regressed==0`.

The harness fact that makes this favorable: the discovery arm already loads ONLY
`using-patterns/SKILL.md` as the system skill (`assemblies/discovery.yaml`). So the
body's routing prose is already the thing under test. Consolidation moves the leaf
descriptions out of the always-on view but leaves the routing surface exactly where
the test already points.

Concrete assertion changes the build will make:

1. **Assert the pattern-name token and the reference path, not the skill
   identifier.** Replace each `patterns:<name>` assertion with two assertions: the
   bare pattern name as a routing token (e.g. `text_contains "newtype"`,
   `text_not_contains "domain-objects"`) AND the reference path the body points at
   (`text_contains "references/patterns/newtype.md"`). The pattern name plus the
   on-disk reference path together name a real artifact after consolidation, where
   `patterns:newtype` no longer does. The body's routing table will emit both, so a
   correct route is unambiguous and a wrong route fails both halves.
2. **Reframe the discovery prompts** from "Which `patterns:*` skill applies?" to
   "Which pattern applies, and where is its guidance?" so the asked question matches
   the post-consolidation answer shape. The prompts already describe the situation in
   the operator's language; only the closing question changes.
3. **Keep the falsification target cases.** `newtype-vs-evs-order-line` and
   `errors-library-failure` are the two known-red cases (a stale routing entry and a
   missing routing row, per the eval-file comments and `TASKS.md`). The consolidated
   body must state the discriminators in prose once: "a single primitive carrying no
   behavior" routes to `newtype`; "an object carrying behavior or calculations"
   (OrderLine with price math) routes to `domain-objects`; a library function failing
   several ways the caller matches on routes to `errors-typed-untyped`. These two
   cases must flip green.
4. **Preserve `newtype-mixed-ids` green.** The body's `newtype` row must still win
   the bare `UserId`/`OrderId` mixing case without dragging in `domain-objects`. This
   is the regression guard the discrimination sharpening must not break.

Why this does not make the checker vacuous: the baseline arm (no `using-patterns`
loaded, only `AGENTS.md` + `profile.md`) cannot emit the pattern-name-plus-reference
pairing the body teaches, so it still fails the `text_contains` half exactly as it
fails the identifier today. CUJ 0's falsification grep is widened from
`patterns:[a-z-]+` to also forbid the bare pattern names and `references/patterns/`
paths leaking into `AGENTS.md` / `profile.md`, so the baseline arm cannot see the
answer through the renamed token. The `improved>0, regressed==0` gate in `ci.sh` is
untouched in logic; only the strings the assertions match on change, and they still
discriminate skilled from un-skilled output. Asserting two tokens (name AND path)
rather than one is strictly harder to satisfy by accident, not easier.

### Feature B — Voices

Move the four `characters` voice overlays OUT of the skill mechanism entirely.
Activation happens OUTSIDE the LLM loop (research decision 2): an output-style,
hook, or wrapper decided at the harness level, not a skill the model loads, not an
in-loop agent. The model never weighs a voice as a selection choice. `using-characters`
and the four `voice-*` skills are removed from the always-on Level-1 view; the voice
text becomes harness configuration applied to output.

Boundary: Feature B changes the characters plugin and the harness activation point
only. Its gate is the `characters/e2e` surface, which `TASKS.md` records as broken
(never produced a run). Rather than repair an in-loop discovery suite for skills
that will no longer be skills, Feature B's e2e gate asserts the two project metrics
directly: the four voice descriptions no longer appear in the always-on Level-1
count (token-share drop), and a styled-output check confirms the voice still colors
output when activated outside the loop (capability not lost). The exact activation
mechanism (output-style vs hook vs wrapper) is a build-phase decision at the harness
level, recorded in the plan; the design fixes only that it is outside the model's
reasoning loop.

### Feature C — Project loop

Consolidate the `developer` coordinator plus the five phases so `ailly` takes the
phase as an argument (`/ailly design ...`) and loads one
`references/phases/<phase>.md`, PRESERVING subagent isolation. The correct shape is
coordinator skill → phase reference → phase subagent that reads one reference, never
the coordinator reading all phases inline. The five phase descriptions leave the
always-on Level-1 view; the phase bodies become references the coordinator selects by
argument and hands to an isolated subagent. Also defer the 5 `research:configuring-*`
descriptions (setup-only by convention) out of the always-on view; keep the research
source leaves intact (decision: research source leaves are not collapsed).

Boundary: Feature C changes the developer coordinator, the five phase skills, and the
research `configuring-*` frontmatter only. It does not collapse research source
leaves, does not add invokable phase-skill shells (direct routing is unused), and does
not change quick-loop/long-loop's existing per-phase subagent spawning beyond pointing
each subagent at its one phase reference. Its gate is the `developer/e2e` discovery
suite (the coordinator still routes a phase argument to the right phase reference) plus
the `research/e2e` discovery suite holding after the `configuring-*` deferral. Shared
contract with the existing harness: the phase-entry checks, model-per-phase, and
tool-failure references stay reachable from the coordinator (see `TASKS.md`
phase-guardrails work); consolidation must not orphan them.

### How the three compose

All three honor the common contract (no lost Level-1 discoverability) and the common
metric (routing holds-or-improves AND always-on share drops). They share the
`vendor.py` / per-plugin `e2e` measurement instrument unchanged in structure. Feature
A is the falsification pilot: it proves the consolidation thesis on the plugin with
the largest description block and a built-in red case, cheaply, before B and C commit.

Dependency structure:

- **Feature A — Patterns (pilot).** No dependencies; can start now. It is the
  thesis-falsification gate for the whole project.
- **Feature B — Voices.** `Parallel with: Feature C`. Independent of A and of C: it
  touches the characters plugin and a harness activation point, sharing no code with
  the others. Shared contract: the always-on token-share measurement method (count
  Level-1 `description:` tokens per plugin) must be agreed before A/B/C so all three
  report the metric the same way.
- **Feature C — Project loop.** `Parallel with: Feature B`. Independent of A and of
  B: it touches the developer coordinator, phase skills, and research `configuring-*`
  frontmatter. Shared contract: the same token-share measurement method, plus the
  unchanged `vendor.py` assembly and three-suite e2e shape every feature gates on.

Ordering rationale: A first, because it falsifies the thesis on the cheapest, highest
-signal surface before B and C touch two more plugins. B and C may run concurrently in
different sessions once A validates, because they share no files and only need the
agreed token-share measurement contract. If A's consolidation fails to hold-or-improve
patterns routing, stop: the thesis is refuted and B/C should not proceed as designed.

### Release flagging for a docs-and-skills project

These are skill and plugin edits, not runtime code, so there is no runtime conditional
to gate. Handle the release-flag concept honestly: the single project-level "flag" is
the **`progressive_disclosure` feature branch and its merge gate**. Deploy continuously
(commit per feature on the branch), but release to operators only when the branch
merges to `main` after the Closing Bell passes. The half-consolidated skillset never
reaches operators because the unmerged branch is not what their plugin cache loads.
Each feature lands as its own commit (or sub-PR into the branch) and is independently
revertable; no feature earns its own runtime flag because none changes operator-visible
behavior on its own before merge. The merge to `main` is the single release event,
gated on the Closing Bell.

## Alternatives

**Build vs off-the-shelf at project scale.** The native three-level Agent Skills
disclosure IS the mechanism; there is no off-the-shelf skill router or skill-side
`defer_loading` to adopt. Tool Search `defer_loading` solves the analogous problem for
tools but does not apply to skills. So the choice is not build-vs-buy; it is how to use
the native mechanism well. The project's only bespoke component is the existing
`vendor.py` / `e2e` measurement harness, already in the repo and reused unchanged.

**Uniform collapse of all six plugins — rejected.** The plugins differ in kind.
Research's 8 source leaves are genuinely distinct question-types the harness routes
well, and you only ever want one source at a time, so collapsing them loses native
direct routing and gains little (at-use cost rises). Domain is already conditionally
loaded ("not during implementation") and under no pressure. General's writing-* are
meta and rarely co-active. A uniform collapse would degrade the surfaces that work to
chase a number, violating the capability-invisibility guard. The project consolidates
only where the mechanism is mis-used: patterns (19 descriptions for one decision),
voices (style through a capability mechanism), and the phase loop (descriptions for an
argument-entered flow).

**Collapsing research source leaves — rejected.** Same reasoning, called out
separately because the original proposal floated it. The research source leaves stay
intact; only the 5 `configuring-*` setup-only descriptions are deferred. This is the
smaller, correct move for research.

**Re-expressing the discovery gate by weakening it — rejected.** An alternative to the
name-plus-path assertion would be to drop the `text_not_contains` half or relax to a
judge-only check. Rejected: dropping the negative assertion lets a body that names
every pattern pass vacuously, and a judge-only gate is harder to keep falsifying
against the baseline arm. Asserting two concrete tokens (name AND reference path) with
both positive and negative forms keeps the gate strictly harder to satisfy by accident
than the current single-identifier assertion.

**Keeping voices as in-loop agents — rejected by research decision 2.** Voices are
every-turn style, not triggered artifact production, so an in-loop agent would
re-introduce a selection choice for the model. Activation outside the loop removes the
choice entirely.

## Summary

The project applies one progressive-disclosure move to the three plugins where the
skill mechanism is mis-used, gated everywhere on routing-holds-or-improves AND
always-on-share-drops, piloted on patterns because it falsifies the thesis cheapest.
The critical resolution is the discovery-gate re-expression: assert the pattern-name
token plus the `references/patterns/<name>.md` path (both positive and negative
forms) instead of the `patterns:<skill>` identifier, reframe the discovery prompts to
ask which pattern applies, widen the CUJ 0 falsification grep to the new tokens, and
keep `improved>0, regressed==0` untouched in logic. A runs first and alone (pilot); B
and C run in parallel after A validates, sharing only the token-share measurement
contract.

Deferred decisions, parked for `TASKS.md` at project cleanup:

- The exact voice-activation mechanism for Feature B (output-style vs hook vs
  wrapper) is a build-phase harness decision; the design fixes only "outside the LLM
  loop."
- Whether the widened CUJ 0 falsification grep over bare pattern names risks
  false-positive matches on prose in `AGENTS.md` / `profile.md` (the names are common
  English-ish tokens like `builder`, `repository`); the build must confirm the grep
  stays clean or scope the forbidden tokens to the reference-path form.
- Whether the `plan-use-patterns.md` step's phase-varying prescriptiveness needs its
  own discovery/invocation eval case, or rides on the existing patterns suite.
- General plugin (review, thinking, dispatching → agents; writing-* → bootstrap) is
  recognized as a mechanism-mismatch but is out of this project's scope; record as a
  candidate follow-up project.
- Whether a native skill-side `defer_loading` (if it lands) would let any of these
  consolidations be expressed more cheaply; decision 5 commits to the bootstrap shape
  regardless, so this is a watch item, not a design obligation.
- Reconciling the `developer:configuring-program-management` / phase-guardrail /
  model-per-phase references so Feature C's coordinator consolidation does not orphan
  them (cross-check against the open `TASKS.md` items before building C).

## Resolved by the long-loop reviewer (2026-06-25)

The design gate was crossed autonomously (long-loop mode). The reviewer read the
design and Closing Bell cold and resolved the open build-blocking items with
conservative defaults. None tripped an escalation trigger (all are reversible
skill/doc edits inside the research's recorded Scope).

**1. Feature B voice-activation mechanism. Decided: a Claude Code output-style is
the default mechanism; a hook/wrapper is the fallback only if an output-style cannot
carry per-voice selection.** Research decision 2 fixes "outside the LLM loop" and the
inventory maps voices to "output-style / always-on snippet, NOT a skill." Output-style
is the harness-native always-on style channel applied outside the model's selection
loop and is fully reversible (it is configuration). The build confirms during Feature B
and falls back only if a concrete limitation surfaces.

**2. Widened CUJ 0 falsification grep. Decided: forbid only the reference-path form
(`references/patterns/<name>`) in addition to the existing `patterns:<name>`
identifier; do NOT add bare pattern names (`builder`, `repository`, ...) to the grep.**
Bare names are common English tokens that would false-positive on legitimate prose in
`AGENTS.md` / `profile.md`. Falsification strength is preserved on the assertion side
instead: the positive discovery assertion requires BOTH the bare pattern name AND the
reference path in the answer, which the baseline arm cannot emit, so the grep need not
carry the brittle bare-name form.

**3. `plan-use-patterns.md` eval coverage. Decided: ride on the existing patterns e2e
suite for the pilot; add a dedicated case only if the pilot shows the pattern-search
beat under-routing.** This is the smallest version that meets the intent and avoids
overfitting evals before there is evidence the beat needs its own guard.

**4. Feature C reference reconciliation. Decided: promote it from a deferred item to an
explicit Feature C build acceptance criterion.** The phase-entry checks, model-per-phase,
tool-failure, and program-management references must stay reachable from the consolidated
coordinator, verified by confirming each reference is still pointed to after the phase
consolidation. Not an escalation; a known build constraint to verify, not defer.

The remaining Summary items (General-plugin follow-up project, native skill
`defer_loading` watch item) are correctly parked, not build-blocking, and need no
reviewer decision.
