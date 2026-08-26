# Implementation Plan: Durable e2e Evidence Archive

**Feature test:** `e2e/test_e2e_archive_durability.py` **User story:** As an e2e report user, I can render `--from-existing --archive <run>` from durable archived evidence after plugin-local scratch outputs have been cleaned.
**Libraries & Skills:** `developer:ailly`, `research:codebase`, `patterns:using-patterns arrange-act-assert`; use `research:archaeology` only if a later question requires history.
**Steps:**

- [x] Step 0: API surface area
- [x] Step 1: Archive identity, path resolution, and manifest loading
- [x] Step 2: Archive-backed existing report indexing
- [x] Step 3: CLI replay wiring for `--from-existing --archive`
- [x] Step 4: Live-run archive scaffolding and evidence capture hooks

## Step 0: API surface area

Applicable pattern beat:

- `patterns:repository`: `EvalRunArchive` is the narrow file-backed repository for manifest, events, command streams, reports, and run evidence; callers should not know the on-disk schema details.
- `patterns:newtype`: `RunId` and `ModelSlug` are domain-meaningful strings that should not be confused with raw CLI input, model display names, or filesystem paths.
- `patterns:parse-dont-validate`: `--archive` input crosses the CLI boundary and must parse once into an archive path; `manifest.json` crosses a file boundary and should parse into typed records before report rendering.
- `patterns:domain-objects`: command records, suite records, model records, plugin records, and the manifest are value objects that carry the archive contract.
- `patterns:bootstrap-and-service`: `main()` should stay a thin CLI adapter that parses flags and delegates archive replay/capture to functions with testable inputs.
- `patterns:arrange-act-assert`: each build-step test should keep setup, one action, and assertions separated because the archive fixture setup is easy to blur with behavior.

New types and function signatures (stubs only, no bodies):

```python
RunId = NewType("RunId", str)
ModelSlug = NewType("ModelSlug", str)


@dataclasses.dataclass(frozen=True)
class CommandRecord:
    sequence: int
    step: str
    args: tuple[str, ...]
    cwd: str
    started_at: str
    finished_at: str
    returncode: int
    stdout_path: str
    stderr_path: str


@dataclasses.dataclass(frozen=True)
class ArchiveSuiteRecord:
    status: str
    run_id: str | None
    input_paths: tuple[str, ...]
    run_paths: tuple[str, ...]
    report_paths: tuple[str, ...]
    comparison_paths: tuple[str, ...]
    command_records: tuple[CommandRecord, ...]


@dataclasses.dataclass(frozen=True)
class ArchiveModelRecord:
    slug: ModelSlug
    suites: dict[str, ArchiveSuiteRecord]


@dataclasses.dataclass(frozen=True)
class ArchivePluginRecord:
    path: str
    models: dict[str, ArchiveModelRecord]


@dataclasses.dataclass(frozen=True)
class ArchiveManifest:
    schema_version: int
    run_id: RunId
    created_at: str
    status: str
    plugins: dict[str, ArchivePluginRecord]
    models: tuple[str, ...]
    rendered: dict[str, str]
    failures: tuple[dict, ...]


@dataclasses.dataclass(frozen=True)
class ArchiveUnit:
    project: Project
    model: str
    model_slug: ModelSlug
    suite: Suite


class EvalRunArchive:
    root: Path
    manifest: ArchiveManifest

    @classmethod
    def create(cls, repo: Path, run_id: RunId | None = None, created_at: str | None = None) -> "EvalRunArchive": ...
    @classmethod
    def open(cls, root: Path) -> "EvalRunArchive": ...

    def unit_root(self, project: Project, model_slug: ModelSlug) -> Path: ...
    def append_event(self, event_name: str, payload: dict) -> None: ...
    def write_manifest(self, manifest: ArchiveManifest) -> None: ...
    def begin_unit(self, unit: ArchiveUnit) -> None: ...
    def record_command(self, unit: ArchiveUnit, step: str, result: subprocess.CompletedProcess[str]) -> CommandRecord: ...
    def capture_inputs(self, unit: ArchiveUnit) -> tuple[str, ...]: ...
    def capture_run_dir(self, unit: ArchiveUnit, run_dir: Path) -> str: ...
    def capture_report(self, unit: ArchiveUnit, report_path: Path) -> str: ...
    def finish_unit(self, unit: ArchiveUnit, suite_record: ArchiveSuiteRecord) -> None: ...
    def fail_unit(self, unit: ArchiveUnit, reason: str) -> None: ...


def generate_run_id(now_utc: datetime | None = None, uuid_factory: Callable[[], uuid.UUID] = uuid.uuid4) -> RunId: ...
def model_slug(model: str, used_slugs: Iterable[str] = ()) -> ModelSlug: ...
def resolve_archive_path(repo: Path, archive_arg: str) -> Path: ...
def parse_archive_manifest(path: Path) -> ArchiveManifest: ...
def archive_models(manifest: ArchiveManifest, requested_plugins: set[str] | None = None) -> list[str]: ...
def archive_project_matrix(
    archive: EvalRunArchive,
    projects: list[Project],
    models: list[str],
) -> dict[str, dict[str, ResourceCell]]: ...
def run_model_project(
    args: argparse.Namespace,
    project: Project,
    model: str | None,
    archive: EvalRunArchive | None = None,
) -> dict[str, ResourceCell]: ...
```

## Step 1: Archive identity, path resolution, and manifest loading

**Enables:** `runner.main([... "--archive", archive_id, ...])` accepts the flag and can resolve the test's bare archive id to `REPO / "e2e" / "artifacts" / archive_id` instead of failing argparse before assertions run.

Build the archive boundary primitives: run id generation, model slugging, bare-id versus path resolution, and manifest parsing into records.
The feature test will still fail until replay uses the manifest, but `--archive` will no longer be an unrecognized argument and a hand-built manifest can be opened.

**Tests**

Describe the main test for this step.

```python
test "bare archive id resolves under repo artifacts and loads manifest":
  repo <- temp repo with e2e/artifacts/20260709T000000Z-1234abcd/manifest.json
  archive_path <- resolve_archive_path(repo, "20260709T000000Z-1234abcd")
  manifest <- parse_archive_manifest(archive_path / "manifest.json")
  assert archive_path equals repo / "e2e" / "artifacts" / "20260709T000000Z-1234abcd"
  assert manifest.models equals ("model-a", "model-b")
```

- Explicit relative path with a separator resolves from the current working directory.
- Absolute path resolves unchanged.
- Model names with `/`, `:`, or whitespace become stable lowercase slugs.
- Slug collisions append a hash suffix only within the same plugin scope.

**Implementation Outline**

```python
add parser.add_argument("--archive")

function resolve_archive_path(repo, archive_arg):
  if archive_arg has no path separator and is not absolute
    return repo / "e2e" / "artifacts" / archive_arg
  return Path(archive_arg)

function parse_archive_manifest(path):
  read manifest.json
  map nested dicts into ArchiveManifest value objects
  normalize list fields to tuples
```

## Step 2: Archive-backed existing report indexing

**Enables:** the replay path can derive models, suites, resources, discovery cells, and invocation cells from archived `report_paths` and `comparison_paths` instead of plugin-local `evals/reports`.

Build a manifest-backed equivalent of the current existing-report loaders.
It should read only archived report JSON files referenced by complete suite records, preserve the current `ResourceCell` and `format_report()` contract, and reuse `initial_project_cells()`, `case_passes()`, `baseline_for()`, `resource_name()`, and `comparison_invocation_icons()` where practical.

**Tests**

Describe the main test for this step.

```python
test "archive project matrix includes both archived model reports":
  archive <- opened fixture archive whose manifest has model-a and model-b discovery reports
  projects <- discovered fixture project list
  matrix <- archive_project_matrix(archive, projects, ["model-a", "model-b"])
  assert matrix["fixture:skill"]["model-a"].discovery_pass is True
  assert matrix["fixture:skill"]["model-b"].discovery_pass is True
```

- Missing archived report path marks the relevant cell with an error instead of reading scratch.
- A manifest plugin not selected by `--plugin` is ignored by the replay matrix.
- A report whose model field disagrees with the manifest model key does not create a new model column.
- Comparison reports still populate invocation icons when present.

**Implementation Outline**

```python
function archive_models(manifest, requested_plugins):
  walk selected plugin records in manifest order
  collect manifest.models entries that exist under selected plugins
  return unique models

function archive_project_matrix(archive, projects, models):
  index projects by project.name
  for each selected plugin in archive.manifest.plugins:
    project <- matching discovered Project
    suites <- suite_map(project)
    for each model in models:
      cells, discovery_resources <- initial_project_cells(project, suites)
      for each complete suite record for model:
        for report_path in suite.report_paths:
          report <- read archive.root / report_path
          apply the same discovery and comparison cell rules used by scratch replay
      merge cells into project_matrix
  return project_matrix
```

## Step 3: CLI replay wiring for `--from-existing --archive`

**Enables:** the full feature test assertions: `exit_code == 0`, the rendered report contains `>model-a</th>`, `>model-b</th>`, and `>fixture:skill</th>` after plugin-local scratch contains only model B.

Wire `main()` so archive replay bypasses `existing_models()` and `load_existing_project_matrix()` when both `--from-existing` and `--archive` are present.
The report should still flow through `format_report()` and `--report`, with static checks skipped the same way current `--from-existing` replay does.

**Tests**

Describe the main test for this step.

```python
test "from-existing archive renders from archived reports after scratch cleanup":
  repo <- temp fixture from e2e/test_e2e_archive_durability.py
  clean_project_outputs(fixture_project)
  write only model-b scratch report
  exit_code <- main(["--plugin", "fixture", "--from-existing", "--archive", archive_id, "--report", output, "--skip-static"])
  report <- read output
  assert exit_code equals 0
  assert report contains ">model-a</th>"
  assert report contains ">model-b</th>"
  assert report contains ">fixture:skill</th>"
```

- `--archive` without `--from-existing` does not change replay behavior yet; it only prepares live capture for Step 4.
- `--from-existing` without `--archive` keeps the current scratch-backed behavior.
- Empty archive model selection returns the existing "No model-driven plugin e2e projects found." failure shape.
- Coverage validation still runs against discovered selected projects before rendering.

**Implementation Outline**

```python
function main(argv):
  args <- parse_args(argv)
  model_projects, static_projects <- discover_projects(REPO)
  apply --plugin filtering
  collect coverage_errors

  if args.from_existing and args.archive:
    archive <- EvalRunArchive.open(resolve_archive_path(REPO, args.archive))
    model_fallback <- archive_models(archive.manifest, selected plugin names)
    models <- expand_model_args(args.model, model_fallback)
    matrix <- archive_project_matrix(archive, model_projects, models)
  else:
    keep current scratch replay or live-run branches

  report <- format_report(models, matrix, static_results, coverage_errors)
  write args.report when present
  return current error status calculation
```

## Step 4: Live-run archive scaffolding and evidence capture hooks

**Enables:** future live e2e runs create the same durable evidence shape that the replay path now reads, so the feature is not limited to hand-built test archives.

Build the minimal live-run capture path decided by the design: create one archive before cleanup, write `events.jsonl`, maintain `manifest.json` atomically, record command sidecar streams at the `run_command()` boundary, and copy selected run/report/input evidence after each suite unit.
Keep this limited to the storage contract required by archive replay; richer rendered links and remote artifact publication remain deferred.

**Tests**

Describe the main test for this step.

```python
test "live run capture writes manifest, events, command streams, and report paths":
  archive <- EvalRunArchive.create(repo, fixed_run_id)
  unit <- ArchiveUnit(project, "model-a", ModelSlug("model-a"), discovery_suite)
  command_result <- completed process with stdout and stderr
  archive.record_command(unit, "eval", command_result)
  archive.capture_report(unit, project.path / "evals" / "reports" / "run-a.json")
  archive.finish_unit(unit, suite_record)
  reloaded <- EvalRunArchive.open(archive.root)
  assert reloaded.manifest.plugins[project.name].models["model-a"].suites["discovery"].report_paths is not empty
```

- Failed command records still preserve stdout, stderr, return code, and a failed unit event.
- Manifest writes use temp-file replacement so interrupted writes do not corrupt the previous manifest.
- Missing selected input files are recorded as unit failures.
- `--dry-run` does not create archive evidence.

**Implementation Outline**

```python
function run_model_project(args, project, model, archive):
  suites <- suite_map(project)
  with patched_models(project, model):
    for each suite:
      unit <- ArchiveUnit(project, model, model_slug(model), suite)
      archive.begin_unit(unit)
      archive.capture_inputs(unit)
      result <- run_command(... assemble ...)
      archive.record_command(unit, "assemble", result)
      archive.capture_run_dir(unit, run_dir_for(project, suite))
    for each run/eval/report command:
      result <- run_command(...)
      archive.record_command(unit, step_name, result)
      capture produced report or comparison path
      archive.finish_unit(unit, suite_record)

function main live branch:
  if args.archive:
    archive <- EvalRunArchive.create(REPO, RunId(args.archive) if explicit run id is allowed else None)
  else:
    archive <- EvalRunArchive.create(REPO)
  call run_model_project(..., archive)
```
