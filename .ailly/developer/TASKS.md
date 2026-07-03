# Tasks

- Extend the answer-leak hygiene gate to also grep the `design-artifacts` pair's prompt (`developer/e2e/prompts/invocation/design-artifacts.md`) for "open artifact" wording. Today the hygiene gate only scans `AGENTS.md` and `profile.md`; the prompt sharing both arms is the fragile invariant for the `design-artifacts` eval pair and isn't covered. See `.ailly/developer/2026-07-02-D-design-artifact-decisions/plan.md` Risks and Notes.
- Fix the plan phase reference: it points at `.ailly/prompts/plan-use-patterns.md`, which does not exist in this repo. The patterns beat currently has to be run by consulting `patterns:using-patterns` directly. Recurring note, also seen in session 2026-07-02-C.
