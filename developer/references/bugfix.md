# Bugfix Shape

When the research refine pass sizes a topic as a bug, smaller than a feature or a project, the five-phase lifecycle still runs unchanged. Only the design content and the role of the feature test differ. This reference provides the vocabulary for bugfixes instead of features. `developer:ailly` and `developer:design` consult it when the task is bug-shaped.

## The Three Statements

A bug is specified by three statements, not a problem-and-solution narrative.

- **Observed.** What the system does today, stated as a fact a reader can reproduce. Include the trigger, the inputs, and the wrong result. Avoid speculation about cause; describe the symptom.
- **Expected.** What the system should do instead, stated as the single corrected behavior. This is the acceptance criterion the reproduction test asserts.
- **Unchanged.** What must stay exactly as it is. The behaviors, interfaces, and outputs the fix must not disturb. This is the regression boundary that keeps the fix narrow.

Write all three before proposing a change. A fix that cannot name its Unchanged set is a fix that does not know its own blast radius.

## The Reproduction Test

The bug's feature test is a failing **reproduction** test. It fills the exact slot the design's feature test fills in the feature flow: one executable test, placed in the project test tree, linked from `design.md`, written behind the same hard gate (write only the test, no fix).

- It encodes the **Observed** behavior as a failing assertion: run the trigger, assert the **Expected** result, and watch it fail because the bug is present.
- It must fail for the right reason (the bug), not a typo or a missing import.
- It stays red until the fix lands, then turns green. It is the proof the bug is fixed and the guard against its return.

A bugfix never qualifies for skipping the reproduction test. Without it, the fix is a rubber stamp and the regression is free to come back.

## Design Content for a Bug

The design doc keeps its six sections, read through the bug lens:

- **Purpose** states the bug as Observed and Expected.
- **Prior Art** notes prior occurrences, related fixes, or the commit that introduced the regression (use `research:archaeology` to find it).
- **User Journey and Metrics** describes the user path that hits the bug and how you will know it is fixed (the reproduction test passing, plus any monitoring).
- **Specification** is the fix, scoped against the Unchanged set, with the root cause named. Contains the Observed, Expected, and Unchanged portions.
- **Alternatives** weighs targeted fix versus broader refactor; prefer the smallest change that makes the reproduction test pass without breaking the Unchanged set.
- **Summary** records anything deferred.

## Defense in Depth

After the reproduction test is green, consider whether the bug can be made structurally impossible rather than only patched: trace backward from the symptom to the original trigger and fix at the source, then add validation at each layer the bad data passed through. A single patch is "fixed"; source plus layered guards is "cannot recur."
