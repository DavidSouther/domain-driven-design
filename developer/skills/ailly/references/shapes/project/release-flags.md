# Release flags

A project lands features over time. A release flag, also called a release toggle or feature flag, keeps the in-progress work from reaching users until you finish the project. It decouples deployment from release. The project deploys code continuously behind the flag and shows it to users only when the project turns the flag on. This reference holds the practice that `developer/skills/ailly/references/shapes/project/project-cycle.md` summarizes.

## One project flag by default

Gate the unified whole behind a single project-level release flag. Deploying a feature-step is not the same as exposing it. Each step ships dark behind the project flag, so the mainline stays releasable at every step and the project avoids a long-lived branch.

In most cases, the project flag is enough. Give an individual feature-step its own flag only when it independently changes what users see and you must control it independently. Every extra flag is extra debt, so do not add one per step by reflex.

## Parallel steps stay independent

Flags let parallel feature-steps land in any order without exposing a partial experience. They make the parallel marking in the plan safe at runtime, not only in the build.

## Running the closing bell behind the flag

Run the Closing Bell against a build with the release flag enabled for the participant while production keeps it off. The study evaluates the flagged-on experience before the wider rollout.

## Turning on and retiring

When the Closing Bell passes, turn the release flag on for users. Prefer a progressive rollout, a percentage or a canary, over a single global flip, so a problem surfaces on a small audience first.

A flag is debt the moment it outlives its purpose. A flag that you fully roll out and do not roll back is dead conditional logic. During cleanup, retire the flag: remove the dead conditional paths, or record removal in `TASKS.md` if you are still watching the rollout.
