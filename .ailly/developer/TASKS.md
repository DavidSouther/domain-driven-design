# Next Tasks

## Follow-ups: skill progressive disclosure (`2026-06-25-A-progressive-disclosure`)

Project run (long loop) on branch `progressive_disclosure`. Three features built and
committed; concurrent Level-1 skill choices dropped ~66 to ~34 (patterns 19 to 1,
characters 5 to 0, developer 14 to 9, research 14 to 9). Documents are long-lived
(`design.md`, `closing-bell.md`, `report.md`, `plan.md`, `research.md`); design phase is
Implement. **The project is halted at the human merge gate and the Closing Bell.** Open:

- **Live e2e validation: DONE 2026-06-25 (routing GO).** Ran all suites against Anthropic
  with `/Users/david.souther/bin/ailly`. Discovery routing green everywhere: patterns
  16/16 (`newtype-vs-evs-order-line` and `errors-library-failure` flipped green,
  `newtype-mixed-ids` held); developer 9/9 + phase-arg routing improved=7+4/regressed=0;
  research comparison improved=15/regressed=0; domain glossary-gate ENFORCED, improved=8/
  regressed=0; characters structural PASS. Full results in the session `report.md`. Two
  diagnosed follow-ups remain (below), neither a progressive-disclosure routing regression.
- **[follow-up] patterns invocation `regressed=3` is sampling noise; confirm with one
  re-run before merge if desired.** ci.sh tripped on three invocation-arm code-correctness
  (`script`) checks (`aggregate`, `newtype`, `visibility`), single live code samples that
  passed baseline and failed invocation. The three relocated references are byte-identical
  to their `main` originals in teaching and code (only unloaded language links and footer
  pointers changed), so the model got identical guidance in both arms; the trip is
  arm-asymmetric single-sample nondeterminism, not a content regression. A single
  `AILLY=/Users/david.souther/bin/ailly bash patterns/e2e/ci.sh` re-run should show the
  regressing set move or vanish. Optional hardening: sample N>1 for the invocation
  `script` checks so the gate is not flaky.
- **[follow-up] developer long-loop e2e wiring bug (pre-existing, not from this project).**
  First live run of the long-loop arm errors: matrix-less `long-loop.yaml` assembles to
  `default.yaml`, which the eval case `name: long-loop` cannot match
  ("no conversation found for case name long-loop"); comparison then fails on improved=0.
  The long-loop assembly/eval/prompt/checker are untouched by progressive disclosure (only
  whitespace in developer/e2e/ci.sh). Fix depends on ailly's matrix-less conversation
  naming: either give the assembly a single-item matrix so the output is `long-loop.yaml`,
  or point the eval/case at the `default` name ailly emits. Supersedes the older
  "Confirm the long-loop eval live" item below.
- **[follow-up] two single-assertion discovery nits** (reported, not gated): research
  `configuring-books-trigger` named the correct `references/configuring/books.md` but also
  leaked the per-query `research:books` identifier (`text_not_contains` fail); domain
  `glossary-vs-ubiquitous-language` named glossary correctly but also mentioned
  `ubiquitous-language`. Both are negatives on otherwise-correct routes; loosen to the
  path-form negative (as Feature A did for patterns) if they prove persistent.
- **Run the Closing Bell** (`.ailly/developer/2026-06-25-A-progressive-disclosure/closing-bell.md`):
  a human usability study, run once. Critical tasks 1-6 must pass before the project lands.
- **Replicate the long-lived docs to the org repository on acceptance** (project-cycle
  Long-Lived Documentation): once a doc's section is approved, copy `design.md` (main
  page) with `closing-bell.md`/`report.md`/`plan.md`/`research.md` as sub-pages to the
  configured doc repo. Destination not configured here; ask before replicating.
- **General plugin is the recognized next consolidation project** (design Summary): a
  mechanism mismatch (review/thinking/dispatching to agents; writing-* to a bootstrap).
  Out of scope here; run as its own project.
- **Stale illustrative `patterns:<leaf>` identifiers in the general plugin**
  (`general/skills/writing-pattern-skills/SKILL.md`, `general/skills/writing-paired-skills/SKILL.md`,
  `general/e2e/evals/scripts/check_writing_pattern_skills.py`) teach the `plugin:skill`
  cross-reference form using now-retired example names. Refresh to a still-valid example
  when the general consolidation project runs (touching them now risks general/e2e).
- **Research configuring invocation coverage was dropped, not relocated.** Feature C
  removed the two `configuring-*` invocation/baseline cases (now 8 source leaves) rather
  than mix load paths in one matrix; `research/e2e/evals/scripts/check_configuring_books.py`
  and `check_configuring_papers.py` are now unreferenced. Either restore invocation-level
  coverage via a `configuring` arm loading `references/configuring/<name>.md` (the phase-
  style split the developer suite got), or delete the two scripts. Discovery still gates
  setup-routing.
- **Smaller parked items.** Token-trim the deliberately keyword-rich `using-patterns`
  description once discoverability is also carried by the always-loaded body; decide if
  `plan-use-patterns.md` needs its own eval case (currently rides the patterns suite);
  historical cached judge artifacts under `developer/e2e/evals/judges/2026-06-12...`
  carry pre-consolidation strings and regenerate on the next live run.

## Follow-ups: progressive disclosure round 2 (developer + domain deep consolidation)

Deeper consolidation on `progressive_disclosure` (commits `d242f2e` domain, `2b496cb`
developer). developer/skills/ is now { ailly, clean-comments-review }; domain/skills/ is
now { using-domain }. Total concurrent Level-1 choices ~66 -> ~20. Open:

- **Re-run developer/e2e and domain/e2e live (supersedes the round-1 runs for these two).**
  Both suites were re-expressed again this round (developer split ability cases into
  invocation/baseline-abilities, 1+5+3=9; domain collapsed to 5 ability references). The
  earlier live validation ran against the prior structure. Re-run
  `AILLY_BIN=/Users/david.souther/bin/ailly bash developer/e2e/ci.sh` and
  `AILLY=/Users/david.souther/bin/ailly bash domain/e2e/ci.sh` and confirm discovery
  holds and `improved>0, regressed==0`. (pytest was unavailable here, so
  `developer/tests/` was verified by `bash -n`/structure only; run `pytest developer/tests/`
  too once available.)
- **Minor cosmetic staleness (non-blocking).** `developer/skills/ailly/references/refactor.md`
  says "Drive the names from `domain:glossary`" (now the glossary ability under
  `domain:using-domain`); the domain `e2e/evals/scripts/check_*.py` docstrings still name
  `domain:<ability>` invocation cases. Refresh wording opportunistically; neither breaks
  routing. The research/e2e `context/skills/domain/SKILL.md` fixture references
  `domain:glossary` but is a vendored research-suite snapshot, out of scope.

## Follow-ups: phase-entry guardrails (`2026-06-24-A-phase-guardrails`)

Implemented and green (`developer/tests/test_phase_guardrails.py` G1–G7 pass; `test_model_per_phase.py` stays green). Ran the two complementary prompts (`.ailly/prompts/fail-if-no-tools.md`, `.ailly/prompts/force-model-per-phase.md`) together as one phase-boundary escalation discipline: new `developer/references/tool-failure.md`, a strengthened "Phase-entry check" (active current-vs-recommended comparison, mismatch flagged, no-gate preserved) in `developer/references/model-per-phase.md`, a unifying `## Phase-Entry Checks` section in `developer/skills/ailly/SKILL.md` pointing at both, and a harness-first/announce-fallback chain wired into the four phase-skill announce lines ("I'll switch when the harness allows; otherwise `/model` as the fallback"). The announce lines are **provider-parametric**: they defer to the Phase by Provider table and select the model for the active provider rather than hardcoding the Anthropic model, so the verbatim model names + qualifiers live in the reference table (the source of truth) and `test_model_per_phase.py` now asserts them there (R4) plus provider-neutrality of the announce lines (R5, no hardcoded model). Deferred:

- **Behavior-level e2e coverage.** Same deferral as the model-per-phase work: no invocation-harness case asserts the coordinator actually performs the model comparison or the tool-failure escalation at runtime. The feature test is a static contract check over the source files only.
- **`ruff` not on PATH at build time.** Could not lint/format the new `test_phase_guardrails.py` (mirrors the existing test's style). Run `ruff check --fix && ruff format` over it once ruff is available — folds into the existing "Cleanup hygiene" ruff item below.

## Follow-ups: program-management skills (`developer:configuring-program-management` / `using-program-management`)

Merged to `main` via PR (built on `issue_tracking`, feature `943fd6f` + refactor `d004979`). All five plan steps verified **offline** (vendor.py regenerates `disclosure.md` with both skills; routing rows in `using-developer`; integration edits in `ailly`/`cleanup`). Open:

- **Confirm the feature test live.** The discovery routing case `program-management-config-vs-use` (`developer/e2e/evals/discovery.yaml`) was never run against a model — no `ailly` binary on PATH and `ANTHROPIC_API_KEY` unset at build time. Run `AILLY_BIN=<binary> bash developer/e2e/ci.sh` (or scope to the discovery suite) with a key/`.env` present, and confirm both skills route correctly (config→`configuring-program-management`, session→`using-program-management`, not swapped, not `initialize`/`ailly`). Until then the feature test is structurally green only.
- **Deferred from design (not blockers):** invocation-suite coverage for the new pair; per-tracker `references/` split if the practice body grows; widening Note→Doc promotion beyond Project shape; auto per-phase status transitions / subtask-per-plan-step; a standalone `developer:authorization` concern; the `AGENTS.md`/`README.md` one-line pointer to the `DEVELOPMENT.md` contract.

## Follow-ups: per-phase model selection (`2026-06-15-B-model-per-phase`)

Implemented and green (`developer/tests/test_model_per_phase.py` passes): a new `developer/references/model-per-phase.md` reference plus a one-line announce extension in the four primary phase skills (research, design, plan, red-green-refactor). Deferred decisions from the design:

- **Behavior-level e2e coverage.** Whether to later add a case in the e2e invocation harness asserting the model actually emits the recommendation on phase entry. Deferred because the harness is out of scope here, pins a single model, and is nondeterministic. The current feature test is a static contract check over the source files only.
- **Announce lines for `developer:refactor` and `developer:cleanup`.** Whether the two support phases warrant their own announce-line edits later. For now they inherit the active model and appear in the reference table only for completeness (Cleanup row present; refactor not in scope).

## `research` to use `.ailly`

Research is still putting files in `docs/research`.

## Follow-ups: `research/e2e/`

The invocation cross-section now covers all ten non-bootstrap research skills. Remaining enhancements (not blockers):

- If/when Ailly's `run` gains live tool execution, add Strategy-C fixture conversations that simulate the typed Not-Available MCP response for the transport-backed skills (papers / books / internal), and reinstate per-case credential gating in `ci.sh`. Until then a single text completion makes credentials irrelevant; those skills are scored on convention (see the build-reconciliation note in the design doc).
> **Implementation note from `general/e2e/` (2026-06-03).** Ailly's project-rooted VFS clamps `..` at the project root, so the blueprint's live `../skills/...` prefix paths do **not** resolve. Reuse `general/e2e/evals/scripts/vendor.sh`: copy the skills under `<plugin>/e2e/context/` (git-ignored, refreshed each `ci.sh` run) and point the assembly prefix there. Also: use `tokens metric: output` (not `total`, which is arm-asymmetric), and add a "no tools, write inline" clause to invocation prompts that ask for files (the model otherwise emits hallucinated `write_file` tool-call JSON under `e2e/AGENTS.md`). See `2026-05-29-D-general-e2e/results.md`.

## Follow-ups: `domain/e2e/`

`domain/e2e/` is implemented and green (two end-to-end `ci.sh` runs: improved 6–7, regressed 0, routine routing ≥0.85). The following surfaced during it and apply repo-wide:

- **Blueprint correction: live `../../` and `../skills/` prefix paths do not work.** The installed `ailly` jails the project VFS at `-p` and clamps `..` at the root, so cross-root prefix paths resolve *inside* the project and 404. Per-plugin harnesses must reach the shared `e2e/AGENTS.md` and the live `skills/` dir through in-jail symlinks (`<plugin>/e2e/AGENTS.md` → `../../e2e/AGENTS.md`, `<plugin>/e2e/skills` → `../skills`) referenced as `./...`. Update the blueprint (`2026-05-29-A-skill-evals/design.md`) and the per-plugin designs accordingly.
- **`characters/e2e/` is broken — never produced a run.** Its assemblies use the unsupported `../../e2e/AGENTS.md` / `../skills/...` paths. Re-do with the symlink approach above; verify `ci.sh` reaches a run + comparison report. One `developer:ailly` session.
- **Skill bug (out of harness scope): `ddd:` vs `domain:` prefix mismatch.** Skill bodies and the `using-domain` routing table use `ddd:<skill>`; the plugin manifest namespace is `domain:<skill>`. The domain discovery evals accept both prefixes to stay faithful. Decide whether to reconcile the skill bodies to `domain:` (a skill edit, deliberately not done here).
- **Skill finding (out of harness scope): the glossary gate is not enforced at the discovery surface.** A modelling-shaped, term-introducing prompt routes to `domain-model`, not `glossary` first, because `using-domain`'s table only sends "ambiguous/synonymous" terms to `glossary`. `domain/e2e` reports this as `glossary-gate finding: NOT ENFORCED`. Decide whether to strengthen `using-domain`'s routing row for new-term introduction.
- **Blueprint deferreds still open:** per-repo CI workflow (GitHub Actions matrix over each `ci.sh`); model-version sweep once baselines are stable.

## Findings / follow-ups

## Follow-ups: `patterns/e2e/`
- **`newtype` vs `domain-objects` routing discrimination gap.** The `newtype-vs-evs-order-line` discovery case stays red after the 2026-06-03 stale-name fix (`patterns:domain-objects` is now in the table). The model routes the prompt to `patterns:newtype` because it says "wrap the underlying tuple in a new type," even though `OrderLine` carries behavior (price math) and should route to `patterns:domain-objects`. The routing table in `patterns/skills/using-patterns/SKILL.md` does not discriminate "a single primitive carrying no behavior" (newtype) from "an object that carries behavior/calculations" (domain-objects). A fix would sharpen both row descriptions, but risks overfitting the eval and could regress `newtype-mixed-ids` — left for deliberate handling. Verified by discovery run `2026-06-04T03-30-19Z-db948e` (claude-sonnet-4-6): 34/36 assertions pass; this case is the only failure. Distinct from the (now-fixed) stale-name bug.

## Follow-ups: `research:configuring-*`

The `research:configuring-*` family is now complete: `configuring-internal`, `configuring-codebase`, and `configuring-public` were authored 2026-06-07 (session `docs/developer/2026-06-07-B-configuring-research/`), pairing with `internal`/`codebase`/`public` the way `configuring-books`/`configuring-papers` pair with `books`/`papers`. Open items:

- **Add `research/e2e/` discovery cases for the three new bootstrap-vs-per-use pairs.** Deferred from the authoring session because the harness scores frontmatter that did not exist until the bodies were written. Needs three cases on the `paired-*-trigger` shape the existing `configuring-books`↔`books` / `configuring-papers`↔`papers` cases use: "set up our Slack/Confluence access" → `configuring-internal` (not `internal`); "get language servers working for this repo" → `configuring-codebase` (not `codebase`); "set our web-scraping etiquette and blocked domains" → `configuring-public` (not `public`). After adding, re-vendor `research/e2e/context/skills/` (it copies skills verbatim) and run `ci.sh`.
- **Decide on the `internal` routing-description framing.** During the session a subagent rewrote `research:internal`'s frontmatter `description` to lead with "private/authenticated" rather than "internal organizational," and edited the `using-research` row to "private documents (Email, Slack, …)". Both were reverted to keep routing and the e2e assertions stable. If the authenticated-source framing is wanted in the routing surface, make it deliberately (mind the e2e discovery assertions and the avoid-em-dash/hyphen preference) — `configuring-internal`'s own description already carries the "authenticated sources" framing.
- **`lsp-*.md` reconciliation done, not the practice e2e.** `lsp-python.md` / `lsp-rust.md` / `lsp-typescript.md` were footnoted to drop `completions`/`diagnostics` (not on the current `LSP` tool surface), and `codebase/SKILL.md`'s Search Strategy was aligned to the real operation names. No eval covers this; verify against the live `LSP` tool surface if it changes.

## Follow-ups: `patterns/*-feature-flags` — permission category and ACL/RBAC

The `permission` category in `configuring-feature-flags/references/categories.md` and the quick-reference row in `using-feature-flags/SKILL.md` treat entitlements as long-lived flags. This is the right model when no formal authorization system exists, but many projects have a dedicated ACL or RBAC layer (e.g., Casbin, Open Policy Agent, AWS IAM, OIDC scopes). When one is present, a `permission.` flag is at best a thin read-through of that system and at worst a parallel, inconsistent copy.

Review and revise `patterns/skills/configuring-feature-flags/references/categories.md` (the `permission` section and the "Choosing a Category" heuristics) and `patterns/skills/using-feature-flags/SKILL.md` (the category table, Common Mistakes, and Composes With) to:

- Note that `permission` flags are appropriate only when no dedicated authorization system exists.
- When a project has a rigorous ACL/RBAC layer, call out that entitlement decisions belong there; a flag that reads through it is still an `ops` flag (a kill switch over the capability), not a `permission` flag.
- Add a "Composes With" or "See Also" entry for `patterns:domain-objects` or a future `patterns:authorization` pattern (to be authored separately).

One `developer:ailly` session. Likely quick-loop shape.

### Cleanup hygiene (small, independent)

Ruff findings that predate the refactor, in files it never touched (do not bundle them into the refactor history): `developer/e2e/evals/scripts/check_plan.py` has an unused `n = len(matches)` (F841); `check_cleanup.py`, `check_initialize.py`, and `check_refactor.py` are not `ruff format` clean. One pass of `ruff check --fix` plus `ruff format` over `developer/e2e/evals/scripts/` clears all four.

## Follow-ups: long-loop mode

The long-loop coordination mode was authored 2026-06-17 (source prompt `.ailly/prompts/dynamic-workflow.md`): a `## Long-loop Mode` section in `developer/skills/ailly/SKILL.md` plus `developer/references/long-loop.md`. The `developer/e2e/` feature-test case for it was added 2026-06-24 (the `long-loop` / `long-loop-baseline` assembly pair, `evals/scripts/check_long_loop.py` asserting L1-L4, and the second falsification comparison in `ci.sh`). One residual is deferred:

- **Confirm the long-loop eval live (needs the `ailly` binary + a model key).** The case is authored and the structural checker is unit-verified against synthetic good/baseline turns, but the live run (`developer/e2e/ci.sh`) was not executed here because the `ailly` binary is not installed and no model key was available. Run `bash developer/e2e/ci.sh` once both are present and confirm the long-loop comparison reports `improved>0, regressed==0`. Same deferral as the program-management discovery-eval follow-up. The dry-run trace at `.ailly/developer/TASK-NOTES-long-loop-e2e.md` (assertions A1-A7) is the spec the checker encodes.

## Follow-ups: modular review composer (`general:review`)

Merged to `main` via PR #13 (`d278792`). `general:review` is now a composer: compose applicable reviewers (base four-criterion reviewer always present, specialists discovered by `description`) → dispatch in parallel → converge (verify/dedup/severity-rank) → fix → re-evaluate. Added `domain:domain-review` as a composable specialist and registered it in `using-domain`. Deferred from design (`.ailly/developer/2026-06-15-A-reviewers/design.md`):

- **Dynamic-workflow dispatch path is unexercised.** The skill specifies static `Agent` dispatch below six reviewers and a dynamic workflow at or above. Only three composable reviewers exist today (base, `developer:clean-comments-review`, `domain:domain-review`), so the dynamic path is never reached and the feature test does not cover it. Revisit when a sixth specialist lands.
- **Eval coverage for the composer reframing.** The existing `general/e2e` invocation `review` case (`check_review.py` R1–R4 + judge) is structural and framing-neutral; it does not assert the composed-set structure (a second distinct lens, the convergence stage). Decide in a separate session whether to update the discovery/baseline evals or add a dynamic-dispatch eval case. Harness changes were out of scope for the authoring session.
