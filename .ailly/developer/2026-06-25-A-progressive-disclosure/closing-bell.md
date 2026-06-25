# Closing Bell: Skill Progressive Disclosure for the Ailly Skillset

<!-- Long-loop reviewer (2026-06-25): draft marker cleared so the project may proceed
to the plan phase. The reviewer clears the document gate only; it never runs or passes
the usability study itself (a never-auto-clear invariant). The study is run once, by a
human, near completion. -->

The exit criterion for the Skill Progressive Disclosure project. Written now, before
the features are built, to fix the definition of done. Run once near completion: a real
participant attempts the scenarios and an evaluator judges against the criteria below.
A passing Closing Bell is evidence from a human study, not from the e2e suites (those
gate the individual features). The agent drafts and scripts this study and records the
outcome; it does not pass it on the operator's behalf.

## Participant Profile

A competent Ailly operator and skill author who already uses the current skillset
fluently across the `developer`, `patterns`, `research`, and `characters` plugins.

**Assumed prior knowledge:** how to run an Ailly session, how to describe a design
problem in their own words, what design patterns are in general terms, and the
existence of the developer phase flow and character voices.

**Knowledge they must NOT have:** anything about this restructuring. They are not told
that the 19 pattern skills were collapsed into one, that voices moved out of the skill
mechanism, or that the phases became references. They must approach the consolidated
surface as if it were the only surface that ever existed. Do not recruit anyone who
participated in the design, plan, or build of this project.

## Setup and Materials

- A checkout with the project merged (all three features landed behind the merge gate).
- A live model and the `ailly` CLI on PATH, configured as the operator normally works.
- The skillset's own documentation (SKILL bodies, references, routing tables) is part
  of the deliverable and is available to the participant in session.
- Deliberately withheld: no prior training, no walkthrough, no design or plan documents,
  no author over the shoulder. The participant works first-use from their own intent.
- The evaluator observes silently, records task completion, time on task, errors
  (wrong route, capability reported missing, dead end), and a single post-task ease
  rating (1-5).

## Task Scenarios

Stated in the operator's language as outcomes, not product steps. The participant
chooses how to act.

1. **(Critical) Wrap a primitive ID.** "You have a `UserId` and an `OrderId` that are
   both plain strings, and the compiler keeps letting you pass one where the other is
   expected. Get the right guidance for fixing this." Correct outcome: routes to the
   *newtype* pattern guidance, not the value-object guidance.

2. **(Critical) An object that carries behavior.** "You have an `OrderLine` that does
   price math (unit price times quantity, discounts, line totals). The team is debating
   whether to wrap it. Get the right guidance." Correct outcome: routes to the
   *domain-objects* (entity / value-object) guidance, not newtype. This is the
   discrimination the consolidation had to sharpen.

3. **(Critical) A library that fails several ways.** "You are designing a library
   function that can fail three different ways, and the caller must react differently
   to each. Get guidance on how to signal those failures." Correct outcome: routes to
   the *errors typed vs untyped* guidance, not parse-don't-validate.

4. **(Critical) Stand up logging for a new service.** "You are standing up logging for
   a brand-new service from scratch. Get the guidance for setting up the pipeline." Then:
   "Now you are adding a single log line inside an already-running handler." Correct
   outcome: the first routes to the *configuring-logging* guidance, the second to the
   *emitting-logs* guidance; the two are not confused.

5. **(Critical) Run a developer design phase.** "You are starting creative work on a new
   feature and want to run the design phase of the developer workflow." Correct outcome:
   the design phase runs through the consolidated coordinator (entered by argument), the
   right phase guidance loads, and the phase work happens in its isolated context.

6. **(Critical) Find applicable patterns while planning.** "You are planning the
   implementation of a feature and want to make sure you are not missing any design
   patterns that apply." Correct outcome: the plan flow runs a dedicated pattern-search
   beat and surfaces the applicable patterns with appropriate prescriptiveness.

7. **(Secondary) Put a character voice on output.** "You want your session's output
   written in one of the character voices." Correct outcome: the participant can get the
   voice applied to output through the harness, and reports the path to doing so was no
   harder than before. (Activation is outside the model's loop; the participant should
   not have to make the model 'pick' a voice.)

8. **(Secondary) Navigability self-report.** After tasks 1-7, the participant answers:
   "Compared with how you expected the skillset to behave, was anything you wanted to do
   missing or harder to find?" Correct outcome: no capability reported as gone or
   invisible; overall navigation reported no harder than expected.

## Acceptance Criteria Per Task

Predefined thresholds. Critical tasks must all pass for the project to land; secondary
tasks inform the result without blocking it.

| Task | Completion | Time on task ceiling | Error ceiling | Ease floor |
|---|---|---|---|---|
| 1 newtype (critical) | Routes to newtype guidance, not value-object | 3 min | 0 wrong routes | 4/5 |
| 2 domain-objects (critical) | Routes to value-object/entity guidance, not newtype | 3 min | 0 wrong routes | 4/5 |
| 3 typed errors (critical) | Routes to errors typed-vs-untyped guidance | 3 min | 0 wrong routes | 4/5 |
| 4 logging split (critical) | Config and emit routed separately, not confused | 5 min | 0 confusions | 4/5 |
| 5 design phase (critical) | Design phase runs via coordinator, isolated | 5 min | 0 wrong phase | 4/5 |
| 6 find patterns (critical) | Dedicated pattern-search beat surfaces applicable patterns | 5 min | 0 missed-beat | 4/5 |
| 7 voice (secondary) | Voice applied to output via harness | 5 min | 1 | 3/5 |
| 8 navigability (secondary) | Nothing reported missing or harder | n/a | n/a | 4/5 |

## What Counts as a Pass

The project lands when **all critical tasks (1-6) pass** their completion and error
thresholds, meeting two project-level conditions the criteria operationalize:

1. **Routing correctness held or improved for the consolidated plugins.** The operator
   reaches the right guidance for patterns (1-3, 6) and the developer phase loop (5)
   from the consolidated surface, including the two discriminations the consolidation
   had to sharpen (newtype vs domain-objects, configuring vs emitting logs).
2. **No capability became invisible.** Nothing the operator wanted to do (including
   applying a character voice, task 7) is gone or unreachable from the consolidated
   surface (task 8 confirms).

Secondary tasks (7-8) inform the result and surface friction but do not block landing.
A failure on a critical task sends the relevant feature back for revision before the
merge gate opens.
