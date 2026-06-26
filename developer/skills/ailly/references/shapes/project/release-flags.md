# Release Flags

A project lands features over time. A release flag, also called a release toggle or feature flag, keeps the in-progress work from reaching users until the project is done. It decouples deployment from release. Code is deployed continuously behind the flag and exposed to users only when the flag is turned on. This reference holds the practice that `developer/skills/ailly/references/shapes/project/project-cycle.md` summarizes.

## One Project Flag by Default

Gate the unified whole behind a single project-level release flag. Deploying a feature-step is not the same as exposing it. Each step ships dark behind the project flag, so the mainline stays releasable at every step and the project avoids a long-lived branch.

Usually the project flag is enough. Give an individual feature-step its own flag only when it independently changes what users see and must be controlled on its own. Every extra flag is extra debt, so do not add one per step by reflex.

## Parallel Steps Stay Independent

Flags let parallel feature-steps land in any order without exposing a partial experience. They make the parallel marking in the plan safe at runtime, not only in the build.

## Running the Closing Bell Behind the Flag

Run the Closing Bell against a build with the release flag enabled for the participant while production keeps it off. The study evaluates the flagged-on experience before the wider rollout.

## Turning On and Retiring

When the Closing Bell passes, turn the release flag on for users. Prefer a progressive rollout, a percentage or a canary, over a single global flip, so a problem surfaces on a small audience first.

A flag is debt the moment it outlives its purpose. A flag that is fully rolled out and will not be rolled back is dead conditional logic. During cleanup, retire the flag: remove the dead conditional paths, or record removal in `TASKS.md` if the rollout is still being watched.
