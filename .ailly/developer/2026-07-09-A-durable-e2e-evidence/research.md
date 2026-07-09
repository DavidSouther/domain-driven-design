## Topic and Intent

Verbatim seed material:

```markdown
# Durable E2E Evidence System

Recommended session slug: `durable-e2e-evidence`

Start a new developer session from this note. The prior local fix idea was too narrow:
copying files opportunistically after a run does not model the real user journey. The
runner needs to treat eval execution as an evidence-producing workflow with immutable
run archives, replayable reports, and traceability from every summary cell back to raw
inputs and outputs.

## Problem

The all-plugin e2e runner currently uses each plugin's `runs/` and `evals/reports/`
directories as if they were durable storage. They are not. They are plugin-local
scratch directories ignored by Git and safe for the harness to clean. A previous
multi-model run lost raw data because later model/plugin executions cleaned or
overwrote those scratch outputs, while the rendered table was only an untracked derived
file.

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

Introduce an explicit `EvalRunArchive` abstraction. Suggested default root:
`e2e/artifacts/<run-id>/`, with manifest.json, events.jsonl, rendered/, and
plugins/<plugin>/models/<model-slug>/{inputs,runs,reports,commands}/.

## Reporter Contract

The HTML report is a derived artifact, reproducible from a run archive. `--archive
<path-or-run-id>` selects an archive root; `--from-existing --archive ...` renders from
the archive without running assemble/run/eval/report commands. Plugin-local scratch may
be cleaned only after its contents are copied into the archive.

## Acceptance Criteria

- Running multiple models for one plugin preserves all models' raw reports after the run.
- Running all plugins across all models preserves all raw reports after the run.
- Regenerating the table from the archive does not run live eval commands, and still
  works after deleting plugin-local `runs/` and `evals/reports/`.
- A failed run leaves a readable partial archive with failure commands and stderr.
- Unit tests reproduce the prior data-loss failure: two sequential model runs for one
  plugin must both remain loadable from durable storage after scratch cleanup.
- Unit tests cover archive-aware `--from-existing` rendering.

## Suggested First Test

Create a unit test that builds a fake project with report JSON for model A, simulates
scratch cleanup, then writes report JSON for model B. The durable archive must still
allow `--from-existing` to render both model A and model B. This test should fail under
the old scratch-directory approach.
```

Goal: promote the all-plugin e2e runner from scratch-directory reporting to a durable evidence workflow: one immutable run archive per live execution, command-level traceability, archived inputs/outputs before cleanup, and report regeneration from the archive without rerunning evals.

## Search/Expand

Current code confirms the problem shape.
`clean_project_outputs()` deletes each plugin's `runs/` and `evals/reports/` directories before live execution; `run_model_project()` then reads the latest run directory and report JSON back from those same scratch locations; `--from-existing` uses `existing_models()` and `load_existing_project_matrix()` over `project.path / "evals" / "reports"` rather than a durable archive.
The rendered `e2e/table.md` is an HTML figure derived from that scratch state.

Prior-art pattern: CI systems treat build/test output as artifacts to upload and later download, separate from the working directory; GitHub Actions' artifact docs explicitly frame build and test output as files useful for deployments, debugging failed tests, crashes, and coverage, and show an upload-before-consume flow.
Python's `subprocess.run()` already returns a `CompletedProcess` with args, return code, stdout, and stderr when captured, which maps directly to the requested command evidence.
The runner already invokes subprocesses through one wrapper, `run_command()`, so command capture can be centralized instead of scattered.

The deleted `.ailly/developer/TASKS.md` looks related as a durability warning but not confirmed as the exact e2e scratch-cleanup bug.
It is tracked in both `HEAD` and `main`, and the current deletion is local/uncommitted (`git diff -- .ailly/developer/TASKS.md` shows a deleted tracked file).
History shows intentional cleanup commits deleted or restored it: `0c0f546 Clean out .ailly folder for merge` deleted it, `60d625d revert` restored it, and later commits updated it as durable deferred-work state.
Best-supported inference: this worktree currently contains a local deletion of a tracked source-of-truth file, possibly from cleanup/branch operations, but the evidence does not prove it came from the all-plugin runner.
It is still a concrete example of why durable session/task artifacts and disposable scratch outputs must be clearly separated.

## Libraries & Skills

Before doing any work in this feature, load these skills via the active harness's skill-loading mechanism: `developer:ailly`, `research:codebase` for current runner/test structure, `research:archaeology` only if further history is needed, and `patterns:using-patterns arrange-act-assert` for the focused reproduction tests.
No published agentic skill was found for Python stdlib `subprocess`, `pathlib`, `json`, `shutil`, `html`, or `unittest`; that absence is a finding.

Python stdlib is the main implementation surface:

- `subprocess`: current `run_command()` already uses `subprocess.run(..., text=True, capture_output=True)`.
  Official docs confirm `run()` waits for completion and returns `CompletedProcess`; with `capture_output=True`, stdout and stderr are captured.
  This supports a `CommandRecord`/archive command log without changing every caller.
- `pathlib`: current code uses `Path` throughout.
  Official docs support concrete paths, globbing, reading/writing, and path composition, which are enough for a small archive abstraction.
- `json`: current reports are loaded with `json.loads(path.read_text(...))`.
  The manifest can stay stdlib JSON; events can be newline-delimited JSON written as one JSON object per line with `json.dumps`.
- `shutil`: current cleanup uses `shutil.rmtree`; archive capture can use stdlib copy functions plus careful destination handling.
- `html`: current `format_report()` uses `html.escape` and no external templating.
  Keep the renderer dependency-free unless design finds the generated HTML unmaintainable.
- `unittest`: existing `e2e/test_all_plugin_e2e_runner.py` imports runner code directly and uses `unittest.TestCase`; continue that style for narrow tests.
  `pytest` was checked because the prompt mentioned it, but this surface does not currently use pytest.
  If pytest enters later, its `tmp_path` fixture is the closest recipe for fake-project archive tests.

No separate HTML templating framework is in use.
No local `SKILL.md`, MCP server, or shipped `skills/` directory exists for these stdlib modules.

## Falsification/Refine

Size: one feature, not a multi-feature project.
The archive spans live execution, partial failure, and report replay, but it is bounded to `e2e/run_all_plugin_e2e.py` and its unit tests.

Bugfix vs feature: the first red test should reproduce the prior data-loss failure as a bug, but the durable archive abstraction and CLI contract are feature work.
Treat design as a small feature with a bug-reproduction feature test at the center.

Off-the-shelf check: CI artifacts and pytest-html solve adjacent artifact publishing and HTML report problems, but they do not know this runner's plugin/model/suite graph, ailly run ids, baseline comparisons, generated prompt/context inputs, or "every summary cell links back to raw evidence" contract.
The smallest honest version is a local archive abstraction and manifest, not adopting a full reporter framework.

Smallest version that meets intent:

- Add `--archive` and archive-backed `--from-existing` rendering.
- Create one run archive root before live model/plugin work starts.
- Capture command records, run directories, report JSON, comparison JSON, and static input files per plugin/model/suite before any later cleanup.
- Make `format_report()` data come from an archive-derived matrix, while preserving the current HTML shape.
- Add tests for sequential model scratch cleanup and archive-only rendering without live commands.

## Scope

In scope for Design:

- `EvalRunArchive` or equivalent in `e2e/run_all_plugin_e2e.py`.
- Manifest schema for plugins, models, suites, run ids, report paths, comparison paths, command paths, failures, and completion state.
- Archive filesystem layout under `e2e/artifacts/<run-id>/` or an explicit `--archive` path.
- Archive capture after each assemble/run/eval/report step.
- Archive-backed `--from-existing --archive ...` rendering after plugin-local scratch deletion.
- Focused unit tests in `e2e/test_all_plugin_e2e_runner.py` using fake project/report data.

Out of scope for Design:

- Rewriting the e2e runner into multiple modules unless required for the archive abstraction.
- Replacing the current HTML table design or introducing a templating dependency.
- Changing ailly's underlying assemble/run/eval/report behavior.
- Restoring or editing `.ailly/developer/TASKS.md`.
- Publishing archives to remote storage or CI artifact upload; local archive durability is enough for this feature.

## Resolved Decisions

Resolved:

- The durable source of truth must be outside plugin-local `runs/` and `evals/reports/`.
- `--from-existing` must read a selected archive, not scan mutable plugin scratch directories.
- Command capture belongs at the existing `run_command()` boundary.
- Tests should stay in the current import-and-`unittest` style unless a later implementation reason justifies pytest.
- The `.ailly/developer/TASKS.md` deletion should be noted as a local tracked-file deletion and durability caution, but not repaired in this session and not treated as confirmed evidence of the e2e runner bug.

Open for the human/design phase:

- Exact run-id format: timestamp, UUID, or a readable hybrid.
- Whether `manifest.json` is updated atomically after every unit or rebuilt from events at the end.
- Whether command stdout/stderr live inline in JSON records or as separate files indexed by manifest.
- Whether archived inputs include every file under `context/` or only files referenced by assemblies/evals for the selected suites.
- Whether `--archive <run-id>` searches only `e2e/artifacts/` or also accepts absolute/relative paths with the same flag.

## Sources

[1] `e2e/run_all_plugin_e2e.py` [aad14cd].
[2] `e2e/test_all_plugin_e2e_runner.py` [aad14cd, untracked].
[3] `e2e/table.md` [aad14cd, untracked].
[4] `.ailly/developer/TASKS.md` git history: `git log --all --name-status --oneline -- .ailly/developer/TASKS.md`; commits `0c0f546`, `60d625d`, `515c836`, `3ac4e10`.
[5] Python Software Foundation, "`subprocess` -- Subprocess management," Python 3.14.6 documentation. <https://docs.python.org/3/library/subprocess.html>
[6] Python Software Foundation, "`pathlib` -- Object-oriented filesystem paths," Python 3.14.6 documentation. <https://docs.python.org/3/library/pathlib.html>
[7] Python Software Foundation, "`json` -- JSON encoder and decoder," Python 3.14.6 documentation. <https://docs.python.org/3/library/json.html>
[8] Python Software Foundation, "`shutil` -- High-level file operations," Python 3.14.6 documentation. <https://docs.python.org/3/library/shutil.html>
[9] Python Software Foundation, "`unittest` -- Unit testing framework," Python 3.14.6 documentation. <https://docs.python.org/3/library/unittest.html>
[10] GitHub Docs, "Store and share data with workflow artifacts." <https://docs.github.com/en/actions/tutorials/store-and-share-data>
[11] pytest, "Get Started." <https://docs.pytest.org/en/stable/getting-started.html>
[12] pytest, "How to use temporary directories and files in tests." <https://docs.pytest.org/en/stable/how-to/tmp_path.html>
[13] pytest-html, "User Guide." <https://pytest-html.readthedocs.io/en/latest/user_guide.html>
