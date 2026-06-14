# Closing Bell

The Closing Bell is the exit criterion of a project loop. It is a summative usability study that first defines what the finished project should deliver to a user, and later confirms it delivered. It plays the role a feature test plays in a feature loop, but it is not code and does not run continuously.

`developer/references/project-cycle.md` summarizes the Closing Bell; this reference holds the full structure. `developer:design` consults it when the bell is written, and the final evaluation before cleanup consults it when the study is run.

## Written Once, Run Once

The Closing Bell is authored once, at the start of the project, before the features are designed. Nothing is built yet, so it cannot pass or fail. It is a statement of intent. It describes, in qualitative terms, what the finished project should let a competent user do.

Near completion, it is scheduled and run once. A real participant attempts the tasks, and an evaluator judges against the recorded criteria whether the project delivered what it intended.

This is the difference from a feature test. A feature test is red until the code turns it green, then stays in the suite as a regression guard. The Closing Bell is written once and followed once. Its discipline is fixing the definition of done up front, not gating every build.

## Who Writes It and Who Passes It

Write only the study at the start, not the features. The agent drafts the Closing Bell, helps script the scenarios, and records the outcome. The agent does not pass it on the user's behalf. A passing Closing Bell is evidence from a human study, not from automated checks.

## What the Closing Bell Records

A Closing Bell is a usability test plan. It records:

- **Participant profile.** Who the user is. The user is assumed to be competent with the surrounding system, but not trained on the new feature. The document should state the prior knowledge the participant is assumed to have and the knowledge they must not have.
- **Setup and materials.** The starting state, what is provided, and what is deliberately withheld. No prior training, outside walkthrough, or author over the shoulder. If the feature includes documentation, that documentation is part of the deliverable and is available to the participant.
- **Task scenarios.** Realistic goals stated in the user's language, not in product steps. State the outcome the user wants, not which controls to operate. Out-of-box, first-use framing.
- **Acceptance criteria per task.** Predefined before the study runs and derived from the qualitative outcome the Closing Bell describes. Each task names what correct completion means, plus the thresholds that count as a pass: task completion, a ceiling on time on task, a ceiling on errors, and a floor on reported ease or satisfaction.
- **Critical versus secondary tasks.** Critical tasks must pass for the project to land. Secondary tasks inform the result without blocking it.

## Adjacent Practice

Draw on summative usability testing, human-factors validation, benchmark studies, task success rate, time on task, error rate, and single-question ease or satisfaction scales. The Closing Bell borrows their discipline of fixing objective, task-based acceptance criteria before the study runs.
