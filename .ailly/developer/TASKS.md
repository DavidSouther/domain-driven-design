# Next Tasks

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

### Cleanup hygiene (small, independent)

Ruff findings that predate the refactor, in files it never touched (do not bundle them into the refactor history): `developer/e2e/evals/scripts/check_plan.py` has an unused `n = len(matches)` (F841); `check_cleanup.py`, `check_initialize.py`, and `check_refactor.py` are not `ruff format` clean. One pass of `ruff check --fix` plus `ruff format` over `developer/e2e/evals/scripts/` clears all four.
