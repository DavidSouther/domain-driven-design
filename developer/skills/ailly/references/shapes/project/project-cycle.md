# Project shape

When a topic needs several features that deliver value only as a unified whole, the five-phase lifecycle scales up into a project loop.
Three things change.
Each plan step is a dedicated development cycle.
The exit criterion is a "Closing Bell" usability study rather than one executable feature test.
The documents are long-lived.
Mark them completed rather than deleted, and replicate them to the organization's document repository once accepted.
The research refine pass sizes a topic as a project when it fits, and the `developer:` skills consult this reference when the task is project shaped.

## Feature loop vs project loop

| Aspect | Feature loop | Project loop |
|---|---|---|
| Scope | One module, class, or service | Several features delivering a unified whole |
| Design artifact | One `design.md` | One project design doc with phases |
| Finished criterion | One executable feature test | A Closing Bell usability study |
| Plan step | A red-green-refactor increment | A full feature with a development cycle |
| Step count | 3 to 7 increments | A bounded set of features (split if it grows past a handful) |
| Release flag | None | A release gate for the whole project |
| Timeframe | Hours to days | Days to Weeks |
| Cleanup | Pull salient details out & delete the session folder | Mark documents completed & keep them for posterity |

Do not inflate a single feature into a project.
If the work is one user-visible capability reachable in one design-plan-build pass, run the feature loop.
Only promote to a project when the deliverable is several features that must ship together.

## Long-lived documentation

Projects run over long timeframes, so keep the intervening documents.
Author and edit them locally in `.ailly/developer/YYYY-MM-DD-A-<topic>/` as usual.
When you complete a document and the user accepts it, replicate it to your organization's primary document repository.
Use Notion, Google Drive, SharePoint, or whatever system your organization uses.
A document reaches accepted status once the user clears its draft and approves its section.
The local copy stays your working copy.
The repository copy is the canonical record.
Reconcile the local copy from the repository at the user's request.

- Detect the destination from the organization's configured document repository.
  If it is unknown, ask before replicating.
- The main project design doc is the page that carries the Review, Implement, and Completed phases (see Project Design Doc below) in the repository.
- Research, plans, maps, per-feature designs, and the Closing Bell become supporting sub-pages under the main design doc.
- Replication tracks status.
  As the main doc moves Review to Implement to Completed, update the repository copy to match.
- After other reviewers comment on the published docs, the user may make edits and refinements there.
  When doing work for a project, periodically check for comments and divergence, and offer to reconcile the changes.

## The closing bell

The project's exit criterion is the Closing Bell, a summative usability study that stands in for the feature test.
Write it once, at the start, as a qualitative statement of what the finished project should let a user do.
Run it once, near the end, to judge whether the project delivered it.
Unlike a feature test, it does not run continuously from red to green.
Writing it first fixes the definition of done before you design the features.

See `developer/skills/ailly/references/shapes/project/closing-bell.md` for who runs it, the participant profile, the task scenarios, and the acceptance criteria.

## Project design doc

A project has one umbrella design doc.
It is long-lived and moves through three explicit phases.

| Phase | Meaning |
|---|---|
| **Review** | You draft and refine the doc, the plan, and the Closing Bell. This is the draft-gate period, the project-altitude equivalent of the `*Draft*` marker. |
| **Implement** | You approve the plan and build its feature-steps behind the project's release flag (see Release Flagging). The doc is the living reference for the whole project, updated as feature-steps land. |
| **Completed** | The Closing Bell study passed and the project delivered. Status becomes `completed: YYYY-MM-DD`. |

The doc keeps the six design sections, read at project altitude:

- **Purpose** of the project and why its features deliver value only together.
- **Prior Art** of existing systems, components, and prior projects to learn from.
- **User Journey and Metrics** for the end-to-end journey across all features, with the Closing Bell as the measure of done.
- **Specification** of the set of features, their boundaries, and how they compose.
  Name sequential and parallel relationships here (see below).
- **Alternatives** weighing build against off-the-shelf at project scale, and alternative decompositions.
- **Summary** recording deferred decisions, parked to `TASKS.md`.

Record the Closing Bell's location in the project design doc, the way a feature design records its feature test path.

## Release flagging

A project lands its features over time, so the half-built whole must not reach users before the Closing Bell passes.
Gate it behind a single project-level release flag.
Deploy continuously, but release to users only when the project completes.
In most cases, that one flag is enough.
A feature-step earns its own only when it changes what users see on its own.

See `developer/skills/ailly/references/shapes/project/release-flags.md` for how this decouples deploy from release and how to run the Closing Bell behind the flag.
That reference also describes when a step needs its own flag and how to enable and retire it.

## Plan steps are features

In the feature loop each plan step is a red-green-refactor increment.
In the project loop each plan step is itself a feature.
Each step has its own design-to-cleanup cycle: its own session folder, its own `design.md`, its own feature test, its own plan of several steps, and its own build & cleanup.
The project plan enumerates these feature-steps, names, and scopes each, and ties each to the part of the Closing Bell it advances.

A project plan may list more entries than a feature plan's 3 to 7, but keep it bounded: if the features grow past a handful, ask whether this is two projects.

## Sequential and parallel steps

State each feature-step's dependency relationship explicitly.
A reader must be able to tell, at a glance, what can start now and what must wait.

- **Sequential.**
  The step depends on an earlier step's output or interface.
  Mark it `Depends on: <step>` and say why the dependency exists.
- **Parallel.**
  The step shares no dependency with its siblings and your team can build it concurrently in different sessions.
  Mark it `Parallel with: <steps>` and name any shared interface the parallel steps must agree on first.

Before parallel work begins, settle the shared interfaces and contracts the parallel features depend on.
This is the project-altitude equivalent of the feature plan's Step 0.
Parallel features that have agreed on their boundaries integrate; parallel features that have not collide.

```markdown
# Project Plan: <project name>

**Closing Bell:** `<path>`
**Features:**
- [ ] Feature A: <name>            (no dependencies, can start now)
- [ ] Feature B: <name>            Depends on: Feature A
- [ ] Feature C: <name>            Parallel with: Feature D; shared contract: <name>
- [ ] Feature D: <name>            Parallel with: Feature C; shared contract: <name>
```

## Cleanup for a project

Project cleanup does not delete documents.
Where a feature cleanup removes the session folder, a project cleanup updates document status to `completed: YYYY-MM-DD` and keeps the record.

- Flip the main design doc's phase to Completed and stamp the date.
- Evaluate each supporting sub-page for long-term usefulness.
  Keep the durable records: the design, the Closing Bell and its results, and the decisions.
  Archive or clean up the ephemeral scaffolding, such as scratch maps and superseded plan drafts, according to whether the decisions seem like they'll be useful to review in the future.
- Extract deferred decisions from the design doc into `TASKS.md`, with `TASK-NOTES` where a step needs context, as in a feature cleanup.
- Retire the release flag once the rollout is complete and stable: remove the dead conditional paths, or record flag removal in `TASKS.md` if you're still monitoring the rollout.
  Stale flags are technical debt.
- The final review passes and the human-approval gate before the squash-merge or PR still apply, now at project altitude.
