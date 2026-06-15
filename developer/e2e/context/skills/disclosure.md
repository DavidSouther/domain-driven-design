# Available developer skills

These are the skills you can invoke. Each line is one skill's identifier and the `description:` from its frontmatter — the same routing surface a coding agent presents. Select the one whose description fits the situation.

- `developer:ailly` — Use when starting or resuming software development tasks.
- `developer:clean-comments-review` — Use when reviewing the comments and DocBlocks in code for their audience and longevity, not the code's correctness. Applies when a public DocBlock enumerates current callers or describes how a symbol is used today (detail that rots when usage changes) instead of why the symbol exists, when a comment's audience is unclear (an external-reader DocBlock versus an internal line comment), or when over-documentation should be cut back to intent. Produces a critique document, not edits to the code.
- `developer:cleanup` — Used when finished with an Ailly development topic to tidy up the workspace.
- `developer:design` — Use when starting creative work such as building features, components, or modifying system behavior, and the research is cleared. Explores alternatives, produces a formal design document, and writes the one executable feature test that defines done.
- `developer:initialize` — Use when starting a new project or setting up a language environment — validates and scaffolds project layout, tooling, and development hooks.
- `developer:plan` — Use when the design draft is cleared and its recorded feature test is currently failing. Defines the API surface area and breaks down the design for passing the feature test into 3 to 7 descriptive implementation steps.
- `developer:red-green-refactor` — Use when implementing a plan step — type-first TDD cycle with a thinking trigger for stuck moments and an explicit abort condition.
- `developer:refactor` — Use only when code is currently green (passing static checks and unit tests) to improve the codebase before finalizing a development task.
- `developer:research` — Use when a development topic is vague and nothing has been gathered or researched yet. Drives research:using-research with a dual lens (software-engineering practice generally, plus this exact task and codebase): an expand pass for supporting complaints and complementary work, then a refine pass that sizes the work (a project, a feature, or a bug), asks whether an off-the-shelf tool already does it, and what the smallest version is. Writes research.md as a draft and stops at the gate.
- `developer:thinking` — Use when facing a compiler error, failing test, invalid lint, or other "red" response during coding implementation.
- `developer:using-developer` — Bootstrap skill to describe developer tasks. Directs which developer skill to invoke for design, feature testing, planning, implementation, or project setup.
- `developer:visual-design` — Use when design exploration needs visual treatment — UI mockups, wireframes, layout comparisons, architecture diagrams, or side-by-side visual options. Launches an interactive browser-based visual companion.
