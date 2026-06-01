# Next Tasks

Each task is one `developer:ailly` session resuming at `developer:feature-test` against the blueprint in `2026-05-29-A-skill-evals/design.md`. The seed prompt for each plugin lives in the corresponding section of that design.

- Implement `characters/e2e/` — invocation + baseline, voice-jefri / voice-jacki / voice-rupert / voice-david. Judge-only.
- Implement `developer/e2e/` — full triple, design / feature-test / plan / red-green-refactor. Fixture authoring required.
- Implement `domain/e2e/` — full triple, glossary (with gate behaviour) / ubiquitous-language / domain-model / contracts-and-invariants.
- Implement `general/e2e/` — full triple, writing-skills / writing-paired-skills / writing-pattern-skills / review.
- Implement `patterns/e2e/` — full triple, reuse 3 from `ailly_two/e2e/patterns-eval` (live-paths assemblies) and add aggregate / parse-dont-validate / repository.
- Implement `research/e2e/` — full triple with tool-availability gating in `ci.sh`. papers / books / codebase / archaeology / configuring-papers / configuring-books.
