## Purpose

The all-plugin e2e runner needs a durable evidence source that survives plugin-local cleanup.
Today, `runs/` and `evals/reports/` are treated as both scratch space and report storage, so later model or plugin executions can remove the raw data behind earlier table cells.
This feature introduces an immutable run archive as the source of truth for replayable reports, command evidence, and traceability back to the inputs used for each plugin/model/suite unit.

The work stays one feature: archive evidence during live e2e execution and make `--from-existing --archive <run>` render from that archive without running eval commands or scanning mutable scratch reports.
Future phases should load `developer:ailly`, `research:codebase`, and `patterns:using-patterns arrange-act-assert`; use `research:archaeology` only if a later question requires history.

## Prior Art

CI artifact upload patterns are the closest prior art: build and test outputs are copied out of the working directory before later jobs consume them.
Python's `subprocess.CompletedProcess` is also a useful local model because it already carries the command args, return code, stdout, and stderr that this runner must preserve at the `run_command()` boundary.

These patterns are suggestive, not sufficient.
The runner still needs its own manifest because the evidence is organized by plugin, model, suite, run id, comparison, and rendered summary cell.

## User Journey and Metrics

The user starts a live all-plugin e2e run with selected plugins and models.
Before any plugin work starts, the runner creates one run id under `e2e/artifacts/`; as each plugin/model/suite is assembled, run, evaluated, and reported, the runner records commands and copies generated reports, comparisons, run directories, and selected static inputs into that archive.
The HTML/table renderer then reads the manifest and archived files, so the user can regenerate `table.md` later with `--from-existing --archive <run>` after deleting every plugin-local `runs/` and `evals/reports/` directory.

Acceptable behavior is measured by the research acceptance criteria: sequential model runs for one plugin keep both models' raw reports; all-plugin/all-model runs keep every completed raw report; archive replay does not run live assemble/run/eval/report commands; partial failures leave readable command stderr and explicit failed or missing units; and the feature test reproduces the old data-loss path.

## Specification

Archive roots live at `e2e/artifacts/<run-id>/` by default.
A run id uses a readable hybrid format, `YYYYMMDDTHHMMSSZ-<uuid8>`, generated from the UTC start time and the first eight lowercase hex characters of a UUID4.
The timestamp keeps local archive folders sortable and debuggable; the UUID suffix avoids collisions across reruns in the same second.

Use this filesystem layout:

```text
e2e/artifacts/<run-id>/
  manifest.json
  events.jsonl
  rendered/
  plugins/<plugin>/models/<model-slug>/
    inputs/assemblies/
    inputs/evals/
    inputs/context/
    runs/
    reports/
    commands/
```

`manifest.json` is the replay index and is updated atomically after each completed or failed plugin/model/suite unit by writing a temporary file and replacing it.
`events.jsonl` is append-only audit evidence for troubleshooting and future recovery, but the normal renderer reads the manifest directly rather than rebuilding the manifest from events.
This keeps interrupted archives immediately usable without requiring an event replay engine in the report path.

Command stdout and stderr are separate side files in each unit's `commands/` directory, indexed by command records in the manifest.
The manifest stores command args, cwd, timestamps, return code, and paths such as `commands/003-eval.stdout.txt` and `commands/003-eval.stderr.txt`; it does not inline large streams.
This keeps the manifest readable while preserving exact command evidence.

Archived static inputs include only files referenced by the selected suites' assemblies and evals: the effective assembly YAML after model patching, matching eval YAML, prompt and prefix files referenced by those YAML files, and generated disclosure/profile/context files when those selected suites reference or produce them.
Do not copy the entire `context/` tree by default; the archive should be traceable to the run inputs without silently ballooning with unrelated files.
If a referenced file is missing, the unit should be marked failed with that missing input in the manifest.

`--archive` accepts both bare run ids and explicit paths.
A bare value with no path separator resolves under `e2e/artifacts/<run-id>`; an absolute path or relative path with a separator resolves as a filesystem path from the current working directory.
This supports the common local replay path while still allowing CI or copied artifact directories to be rendered directly.

For live runs, the runner creates the archive before `clean_project_outputs()` and captures each unit's generated artifacts before any later cleanup can remove them.
For replay, `--from-existing --archive <run>` bypasses `existing_models()` and `load_existing_project_matrix()` over plugin-local `evals/reports/`; instead it reads `manifest.json`, derives the model list and project matrix from archived reports and comparisons, and uses archived input metadata to map reports back to resources.
Existing `format_report()` output shape should remain the renderer contract; the data source changes from scratch directories to archive evidence.

The one feature test follows the research suggested first test without changing its intent.
It creates a fake plugin project, writes model A scratch output and archived evidence, deletes plugin-local scratch with `clean_project_outputs()`, writes model B scratch output and archived evidence, then invokes `--from-existing --archive <run>` and asserts the rendered report contains both model columns.
The exact test path is `e2e/test_e2e_archive_durability.py`.

## Alternatives

One alternative is to keep copying report JSON opportunistically after each model run while leaving `--from-existing` scratch-based.
That is too narrow because it preserves a few files but does not give command traceability, static inputs, partial failure state, or a replay contract independent of scratch cleanup.

A second alternative is to rely on CI artifact upload.
CI artifacts are useful for publishing the completed archive, but they do not define the runner's plugin/model/suite index or let local `--from-existing` reconstruct summary cells from raw evidence.

A third alternative is to adopt a reporter such as pytest-html.
This runner is not a pytest execution surface, and the current report semantics are specific to discovery and invocation comparisons.
Keeping the local manifest plus existing `format_report()` preserves the current table while fixing the storage model.

The recommended approach is a small local archive abstraction inside the runner: it centralizes capture at the existing command/report boundaries, keeps the CLI contract explicit, and avoids replacing the report format or e2e execution model.

## Summary

Implement a durable local archive rooted at `e2e/artifacts/<run-id>/`, with an atomically updated manifest, append-only event log, sidecar command streams, selected static inputs, raw run/report evidence, and archive-backed replay.
Defer remote artifact publication, manifest schema migration tooling, and richer HTML links from summary cells into raw evidence; those can build on the archive once the storage contract is green.

### Open Artifact Decisions

**Run id string:** Timestamp-only, UUID-only, or readable hybrid.
Proposed: `YYYYMMDDTHHMMSSZ-<uuid8>`, using UTC time plus the first eight lowercase hex characters of a UUID4.

**`e2e/artifacts/<run-id>/manifest.json`:** The exact top-level schema field names.
Proposed: `schema_version`, `run_id`, `created_at`, `status`, `plugins`, `models`, `rendered`, and `failures`, with plugin/model/suite entries carrying `status`, `run_id`, `input_paths`, `run_paths`, `report_paths`, `comparison_paths`, and `command_records`.

**`e2e/artifacts/<run-id>/events.jsonl`:** Whether event names are free-form or fixed.
Proposed: fixed event names `run_started`, `unit_started`, `command_finished`, `artifact_captured`, `unit_finished`, `unit_failed`, and `run_finished`, one JSON object per line.

**Command stream files:** Inline command output, one combined side file, or separate stdout/stderr side files.
Proposed: separate files named `<sequence>-<step>.stdout.txt` and `<sequence>-<step>.stderr.txt` under each unit's `commands/`, indexed from `command_records`.

**Model slug:** How model names that contain `/`, `:`, or whitespace become paths.
Proposed: lowercase the model name, replace every non-alphanumeric run with `-`, trim leading/trailing `-`, and append `-<hash8>` only on collision within the same plugin.

**`e2e/test_e2e_archive_durability.py`:** New file versus amending the existing runner tests.
Proposed: add a new file with exactly one `unittest.TestCase` method so the archive durability feature test is isolated from the existing runner unit tests.

This session ran in quick-loop mode and stops after design: no `plan.md`, no implementation, and the one feature test is `e2e/test_e2e_archive_durability.py`.
