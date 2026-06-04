# Available developer skills

These are the skills you can invoke. Each line is one skill's identifier and the `description:` from its frontmatter — the same routing surface a coding agent presents. Select the one whose description fits the situation.

- `developer:ailly` — Use when starting or resuming software development tasks.
- `developer:cleanup` — Used when finished with an Ailly development topic to tidy up the workspace.
- `developer:design` — Use when starting any creative work — building features, components, or modifying system behavior. Explores alternatives and produces a formal design document before implementation.
- `developer:feature-test` — Use when a design doc has been reviewed and cleared — writes a single executable test encoding a user story before any implementation begins.
- `developer:git-workflow` — Use when performing source code tasks that change the working tree.
- `developer:initialize` — Use when starting a new project or setting up a language environment — validates and scaffolds project layout, tooling, and development hooks.
- `developer:is-clean` — Use when validating that a project is in a clean state for development.
- `developer:plan` — Use when a feature test has been reviewed and cleared and is currently failing — breaks passing it into 3-7 incremental plan steps.
- `developer:red-green-refactor` — Use when implementing a plan step — type-first TDD cycle with a thinking trigger for stuck moments and an explicit abort condition.
- `developer:refactor` — Use only when code is currently green (passing static checks and unit tests) to improve the codebase before finalizing a development task.
- `developer:thinking` — Use when facing a compiler error, failing test, invalid lint, or other "red" response during coding implementation.
- `developer:using-developer` — Bootstrap skill to describe developer tasks. Directs which developer skill to invoke for design, feature testing, planning, implementation, or project setup.
- `developer:visual-design` — Use when design exploration needs visual treatment — UI mockups, wireframes, layout comparisons, architecture diagrams, or side-by-side visual options. Launches an interactive browser-based visual companion.
