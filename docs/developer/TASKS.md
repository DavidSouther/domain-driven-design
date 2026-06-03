# Next Tasks

## Follow-ups: `research/e2e/` (built 2026-06-03)

The invocation cross-section now covers all ten non-bootstrap research skills. Remaining enhancements (not blockers):

- If/when Ailly's `run` gains live tool execution, add Strategy-C fixture conversations that simulate the typed Not-Available MCP response for the transport-backed skills (papers / books / internal), and reinstate per-case credential gating in `ci.sh`. Until then a single text completion makes credentials irrelevant; those skills are scored on convention (see the build-reconciliation note in the design doc).
> **Implementation note from `general/e2e/` (2026-06-03).** Ailly's project-rooted VFS clamps `..` at the project root, so the blueprint's live `../skills/...` prefix paths do **not** resolve. Reuse `general/e2e/evals/scripts/vendor.sh`: copy the skills under `<plugin>/e2e/context/` (git-ignored, refreshed each `ci.sh` run) and point the assembly prefix there. Also: use `tokens metric: output` (not `total`, which is arm-asymmetric), and add a "no tools, write inline" clause to invocation prompts that ask for files (the model otherwise emits hallucinated `write_file` tool-call JSON under `e2e/AGENTS.md`). See `2026-05-29-D-general-e2e/results.md`.

## Carried forward from `domain/e2e/` (implemented 2026-06-03)

`domain/e2e/` is implemented and green (two end-to-end `ci.sh` runs: improved 6–7, regressed 0, routine routing ≥0.85). The following surfaced during it and apply repo-wide:

- **Blueprint correction: live `../../` and `../skills/` prefix paths do not work.** The installed `ailly` jails the project VFS at `-p` and clamps `..` at the root, so cross-root prefix paths resolve *inside* the project and 404. Per-plugin harnesses must reach the shared `e2e/AGENTS.md` and the live `skills/` dir through in-jail symlinks (`<plugin>/e2e/AGENTS.md` → `../../e2e/AGENTS.md`, `<plugin>/e2e/skills` → `../skills`) referenced as `./...`. Update the blueprint (`2026-05-29-A-skill-evals/design.md`) and the per-plugin designs accordingly.
- **`characters/e2e/` is broken — never produced a run.** Its assemblies use the unsupported `../../e2e/AGENTS.md` / `../skills/...` paths. Re-do with the symlink approach above; verify `ci.sh` reaches a run + comparison report. One `developer:ailly` session.
- **Skill bug (out of harness scope): `ddd:` vs `domain:` prefix mismatch.** Skill bodies and the `using-domain` routing table use `ddd:<skill>`; the plugin manifest namespace is `domain:<skill>`. The domain discovery evals accept both prefixes to stay faithful. Decide whether to reconcile the skill bodies to `domain:` (a skill edit, deliberately not done here).
- **Skill finding (out of harness scope): the glossary gate is not enforced at the discovery surface.** A modelling-shaped, term-introducing prompt routes to `domain-model`, not `glossary` first, because `using-domain`'s table only sends "ambiguous/synonymous" terms to `glossary`. `domain/e2e` reports this as `glossary-gate finding: NOT ENFORCED`. Decide whether to strengthen `using-domain`'s routing row for new-term introduction.
- **Blueprint deferreds still open:** per-repo CI workflow (GitHub Actions matrix over each `ci.sh`); model-version sweep once baselines are stable.
