# Full-Suite E2E Dashboard

This dashboard reviews archived full-suite plugin e2e runs. A full-suite run
executes the model-driven e2e harness across the plugin suites, captures the run
inputs, reports, command streams, and session transcripts into `e2e/artifacts/`,
then renders the archived evidence into either a static HTML table or an
interactive drilldown app.

The dashboard is for tactical review: find the resource/model cells that need
attention, open the cell, compare the baseline and invocation sessions, and read
the evaluator evidence that produced the status icons.

## Archive Model

Archives live under:

```sh
e2e/artifacts/<archive-id>/
```

Each archive has a `manifest.json` with:

- the archive run id, status, creation time, and `source_snapshot`
- plugin records keyed by plugin name
- model records keyed by model name, with a stable model slug for filesystem paths
- suite records for `discovery`, `baseline`, `invocation`, and split suites such
  as `baseline-phases` / `invocation-phases`
- captured report paths, comparison report paths, run directories, inputs, and
  command stdout/stderr paths

The dashboard groups archives by `source_snapshot`. A dashboard view should
compare archives that ran against the same source snapshot; mixing source
snapshots makes the table misleading because resource rows and evaluator content
may have changed between runs.

## Running A Full Suite

From the worktree or repo root:

```sh
python3 e2e/run_all_plugin_e2e.py \
  --model anthropic \
  --model openai \
  --archive "$(date -u +%Y%m%dT%H%M%SZ)-manual" \
  --report ./e2e-dashboard.html
```

Useful options:

- `--model anthropic`, `--model openai`, or `--model <exact-model>` chooses
  model families or specific models.
- `--plugin <name>` limits execution to one plugin. Repeat for multiple plugins.
- `--archive <id-or-path>` writes live captured evidence to that archive.
- `--report <path>` writes the static HTML report.
- `--skip-static` skips root static e2e checks.
- `--fail-fast` stops at the first suite failure.

To render from already captured evidence without running models:

```sh
python3 e2e/run_all_plugin_e2e.py \
  --from-existing \
  --archive e2e/artifacts/<archive-id> \
  --report /tmp/e2e-dashboard.html \
  --skip-static
```

`--archive` may be a bare archive id under `e2e/artifacts/`, a single archive
path, or an archive root directory. When rendering an archive directory,
`--source-snapshot <snapshot>` selects a specific source snapshot group.

## Starting The Drilldown App

The web app serves the same archive data through a tactical dashboard with a
detail pane:

```sh
python3 e2e/serve_e2e_dashboard.py \
  --archive e2e/artifacts/<archive-id> \
  --host 127.0.0.1 \
  --port 8765
```

Then open:

```text
http://127.0.0.1:8765/
```

Useful options:

- `--archive <id-or-path-or-root>` selects the archive source.
- `--plugin <name>` limits rows to one plugin. Repeat for multiple plugins.
- `--model <name-or-family>` limits columns. Repeat for multiple models.
- `--host` and `--port` control the local HTTP bind address.

The app exposes JSON endpoints:

- `/api/state` returns grouped dashboard state.
- `/api/cell?resource=<resource>&model=<model>&kind=<discovery|invocation>`
  returns the detail payload for one table cell.
- `/artifact/<archive-relative-path>` serves an archived file preview.

## Dashboard Table

The main table is a horizontally scrolling `<figure>` with sticky model headers
and a sticky resource column. Text does not wrap at any viewport size. Each
model has two subcolumns:

- `Discover` - whether discovery found the resource.
- `Invoke` - the fixed evaluator-slot summary for the invocation comparison.

Discovery icons:

| Icon | Meaning |
| --- | --- |
| `✅` | discovery passed |
| `⛔️` | discovery failed |
| `⁇` | no discovery evidence |

Invocation cells always represent three evaluator slots in this order:

1. check: script or static checker
2. judge
3. tokens

If a known slot has no evaluator evidence, it renders as `⁇`. Unknown evaluator
types also render as `⁇`; no evaluator type should be forced into the wrong
rubric.

Check icons:

| Icon | Meaning |
| --- | --- |
| `✅` | invocation checker passed |
| `⛔️` | invocation checker failed |
| `⚠️` | checker errored or malformed |
| `⁇` | no checker evidence |

Judge icons:

| | Ailly good | Bad |
| --- | --- | --- |
| Model good | `🗡️` unneeded skill | `👎` regression |
| Bad | `🥇` win | `💥` noise |

Token icons:

| Icon | Meaning |
| --- | --- |
| `💵` | invocation passed the token budget, so the skill saved budget |
| `🔥` | invocation failed the token budget, so it burned budget |
| `⚠️` | token check errored or malformed |
| `⁇` | no token evidence |

The judge quadrant applies only to judge assertions. Script/static checks are
straight invocation pass/fail. Token checks are money/burn markers.

## Detail Pane

Click a table cell to open its detail pane. The pane has four tabs:

- `Reports` shows the selected case rows and raw assertion records from the
  archived report.
- `Session` shows archived and recovered transcripts, command records, session
  files, prompts, and context inputs.
- `Evaluators` shows per-assertion evaluator results, their icons, and the
  archived evaluator/checker files.
- `Summary` shows compact counts for the selected evidence.

Invocation-cell drilldown is comparison-aware. The `Session` tab resolves both
comparison arms:

- `baseline` from `report.arm_a.run_id`, falling back to the matching baseline
  suite record in the manifest when older reports lack explicit arm ids.
- `invocation` from `report.arm_b.run_id`, falling back to the selected
  invocation suite record.

Transcripts and session files are grouped by arm, so a reviewer can inspect the
baseline answer and invocation answer for the same case without switching cells.

## Transcript Recovery

Archives should capture run directories after `ailly run` writes assistant
responses. Earlier archive data may contain YAML transcript files with assistant
markers but empty assistant bodies. The web app detects that shape and looks for
the matching checkout run under:

```text
<plugin>/e2e/runs/<run-id>/<case>.yaml
```

When checkout recovery finds non-empty assistant content, the transcript is
served with `source: "checkout"` while preserving the archived path. This keeps
old archives reviewable without pretending the archived copy itself had the
response body.

## Evaluator Detail

The `Evaluators` tab flattens report assertions into review rows with:

- case
- evaluator type
- baseline outcome
- invocation outcome
- change label
- result icon
- reason text when present

Comparison assertions use `arm_a` for baseline and `arm_b` for invocation.
Non-comparison assertions use `outcome` or `status`.

## Files To Commit

Dashboard source changes normally belong in:

- `e2e/run_all_plugin_e2e.py`
- `e2e/serve_e2e_dashboard.py`
- `e2e/test_all_plugin_e2e_runner.py`
- `e2e/test_e2e_dashboard_server.py`
- `DASHBOARD_README.md`

Generated files should usually stay uncommitted:

- `e2e-dashboard.html`
- `e2e/artifacts/`

The generated archive data can be large, local, model-specific, and tied to a
dirty source snapshot. Commit it only when a specific fixture is intentionally
being added.

## Verification

Run the focused dashboard checks:

```sh
python3 -m unittest \
  e2e.test_all_plugin_e2e_runner \
  e2e.test_e2e_archive_durability \
  e2e.test_e2e_dashboard_server
```

Compile the touched Python files without writing pyc files into the repo:

```sh
PYTHONPYCACHEPREFIX=/private/tmp/pycache-ddd-dashboard \
  python3 -m py_compile \
  e2e/run_all_plugin_e2e.py \
  e2e/serve_e2e_dashboard.py \
  e2e/test_all_plugin_e2e_runner.py \
  e2e/test_e2e_archive_durability.py \
  e2e/test_e2e_dashboard_server.py
```

Check whitespace before committing:

```sh
git diff --check
```
