# Next Tasks

Each task is one `developer:ailly` session resuming at `developer:feature-test` against the blueprint in `2026-05-29-A-skill-evals/design.md`. The seed prompt for each plugin lives in the corresponding section of that design.

- Implement `developer/e2e/` — full triple, design / feature-test / plan / red-green-refactor. Fixture authoring required.
- Implement `domain/e2e/` — full triple, glossary (with gate behaviour) / ubiquitous-language / domain-model / contracts-and-invariants.
- Implement `general/e2e/` — full triple, writing-skills / writing-paired-skills / writing-pattern-skills / review.
- Implement `research/e2e/` — full triple with tool-availability gating in `ci.sh`. papers / books / codebase / archaeology / configuring-papers / configuring-books.

<!-- DONE 2026-06-03: `patterns/e2e/` — full triple, 6 invocation + 8 discovery cases.
     Live skills via in-root symlinks (ailly VFS clamps `..`); gate green
     (improved=2, regressed=0); discovery 0.90. See 2026-05-29-C-patterns-e2e/. -->

<!-- DONE 2026-06-03: `characters/e2e/` — invocation + baseline (no discovery;
     voices load by plugin presence, not by description). 4 judge-only cases.
     voice-ailly replaces the non-existent voice-david skill (real skill,
     completes the blueprint's Rupert-vs-Ailly pair). tokens metric=output, not
     total. Live skills via in-root symlinks (base, skills). Gate green
     (improved=1 via voice-ailly, regressed=0; jacki/rupert unchanged_pass,
     jefri unchanged_fail null). See 2026-05-29-B-characters-e2e/. Deferred:
     check_voice_*.py structural scripts; voice-david case once it ships. -->

