# Durable E2E Evidence System

Recommended session slug: `durable-e2e-evidence`

Start a new developer session from this note.
The prior local fix idea was too narrow: copying files opportunistically after a run does not model the real user journey.
The runner needs to treat eval execution as an evidence-producing workflow with immutable run archives, replayable reports, and traceability from every summary cell back to raw inputs and outputs.

## Problem

The all-plugin e2e runner currently uses each plugin's `runs/` and `evals/reports/` directories as if they were durable storage.
They are not.
They are plugin-local scratch directories ignored by Git and safe for the harness to clean.
A previous multi-model run lost raw data because later model/plugin executions cleaned or overwrote those scratch outputs, while the rendered table was only an untracked derived file.

The durable source of truth must be separate from plugin scratch output.

## User Journey

1. The user starts a live eval run with selected plugins and model families or exact
   models.
2. The runner creates one immutable top-level run id before any plugin/model work starts.
3. For every plugin and model, the runner assembles, runs, evaluates, and compares the
   relevant suites.
4. Each subprocess command is recorded with command arguments, working directory,
   timestamps, return code, stdout, and stderr.
5. After each suite step, generated artifacts are captured into the run archive before
   any later cleanup can remove plugin scratch files.
6. The run archive stores the static input definitions used for the run: assemblies,
   eval configs, prompts, generated disclosure/profile/context files where relevant,
   and the effective model for each suite.
7. The runner writes a manifest that indexes plugins, models, suites, run ids, report
   paths, comparison paths, failures, and completion state.
8. The report renderer reads the manifest/archive, not mutable scratch directories.
9. The user can regenerate `table.md` or HTML from archived evidence without rerunning
   evals.
10. If the process fails midway, the archive remains useful: completed plugin/model/suite
    units are marked complete, failed units have command logs, and missing units are
    explicit.

## Archive Model

Introduce an explicit `EvalRunArchive` abstraction.
Suggested default root:

`e2e/artifacts/<run-id>/`

Suggested shape:

```text
e2e/artifacts/<run-id>/
  manifest.json
  events.jsonl
  rendered/
    table.html
    table.md
  plugins/
    <plugin>/
      models/
        <model-slug>/
          inputs/
            assemblies/
            evals/
            prompts/
            context/
          runs/
          reports/
          commands/
```

`events.jsonl` should be append-only and record lifecycle events:

- `run_started`
- `plugin_model_started`
- `command_started`
- `command_finished`
- `suite_assembled`
- `suite_ran`
- `suite_evaluated`
- `comparison_reported`
- `artifact_archived`
- `plugin_model_completed`
- `plugin_model_failed`
- `run_completed`

`manifest.json` should be the renderer's primary index, containing at least:

- archive schema version
- run id
- start/end timestamps
- requested plugins
- requested models and expanded models
- per-plugin/per-model status
- suite names
- report JSON paths
- comparison JSON paths
- run YAML paths
- command log paths
- rendered report paths

## Reporter Contract

The HTML report is a derived artifact.
It should be reproducible from a run archive.

Required CLI behavior:

- Live execution writes a new archive by default.
- `--archive <path-or-run-id>` selects an archive root for reading or writing.
- `--from-existing --archive <path-or-run-id>` renders from the archive without running
  assemble/run/eval/report commands.
- If `--from-existing` is used without `--archive`, choose the latest complete archive
  or fail clearly if none exists.
- Plugin-local scratch directories may be cleaned only after their contents have been
  copied into the archive.

Each report cell should be traceable.
The renderer should either include links or enough data attributes to identify:

- discovery report JSON used by the discovery cell
- invocation comparison JSON used by the invocation cell
- baseline run YAML
- invocation run YAML
- command log for the relevant suite/comparison

## Acceptance Criteria

- Running multiple models for one plugin preserves all models' raw reports after the run.
- Running all plugins across all models preserves all raw reports after the run.
- Regenerating the table from the archive does not run live eval commands.
- Regenerating the table from the archive after deleting plugin-local `runs/` and
  `evals/reports/` still works.
- A failed run leaves a readable partial archive with failure commands and stderr.
- The manifest can explain why a table cell is unknown, failed, or missing.
- Unit tests reproduce the prior data-loss failure: two sequential model runs for one
  plugin must both remain loadable from durable storage after scratch cleanup.
- Unit tests cover archive-aware `--from-existing` rendering.

## Implementation Notes

Keep plugin-local `runs/` and `evals/reports/` as scratch.
Do not make them the source of truth.

Prefer a small archive class with methods such as:

- `start_run(...)`
- `record_command(...)`
- `archive_project_state(plugin, model, suites, run_dirs)`
- `archive_reports(plugin, model)`
- `record_plugin_model_status(...)`
- `write_manifest()`
- `load_manifest(...)`

The current code already has useful pieces:

- model family expansion
- resource inventory
- comparison outcome categorization
- HTML report formatting
- project discovery

The next session should preserve those pieces while redesigning storage around the
archive.

## Suggested First Test

Create a unit test that builds a fake project with report JSON for model A, simulates
scratch cleanup, then writes report JSON for model B. The durable archive must still
allow `--from-existing` to render both model A and model B. This test should fail under
the old scratch-directory approach.
