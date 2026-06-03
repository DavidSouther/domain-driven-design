# Next Tasks

## Follow-ups: `research/e2e/` (built 2026-06-03)

The invocation cross-section now covers all ten non-bootstrap research skills. Remaining enhancements (not blockers):

- If/when Ailly's `run` gains live tool execution, add Strategy-C fixture conversations that simulate the typed Not-Available MCP response for the transport-backed skills (papers / books / internal), and reinstate per-case credential gating in `ci.sh`. Until then a single text completion makes credentials irrelevant; those skills are scored on convention (see the build-reconciliation note in the design doc).
> **Implementation note from `general/e2e/` (2026-06-03).** Ailly's project-rooted VFS clamps `..` at the project root, so the blueprint's live `../skills/...` prefix paths do **not** resolve. Reuse `general/e2e/evals/scripts/vendor.sh`: copy the skills under `<plugin>/e2e/context/` (git-ignored, refreshed each `ci.sh` run) and point the assembly prefix there. Also: use `tokens metric: output` (not `total`, which is arm-asymmetric), and add a "no tools, write inline" clause to invocation prompts that ask for files (the model otherwise emits hallucinated `write_file` tool-call JSON under `e2e/AGENTS.md`). See `2026-05-29-D-general-e2e/results.md`.

