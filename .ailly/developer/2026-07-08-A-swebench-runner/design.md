# SWE-bench Runner with Claude Code Long-Loop

Design for a small standalone Python CLI that, for each SWE-bench instance,
drives Claude Code headlessly through `developer:ailly` long-loop mode to produce
a patch, and writes those patches as official-format `predictions.jsonl`.

**Load-skill directive (carried forward from `research.md`, honor in plan/build):**
Before writing harness logic that constructs the Claude Code prompt, load
`developer:ailly` via the harness's skill-loading mechanism so the prompt uses
the coordinator's real long-loop trigger phrasing rather than a guessed string.

## Purpose

We want a real SWE-bench pass-rate number for "Claude Code driven through
`developer:ailly` long-loop." That requires a harness that, given one or more
SWE-bench task instances (repo, `base_commit`, `problem_statement`), autonomously
checks out each repo at its base commit, runs Claude Code headlessly against the
issue, captures the resulting code change as a patch, and emits predictions in the
exact format the official SWE-bench evaluation harness consumes. This design
covers that harness plumbing. It deliberately stops short of running the Docker
grader.

## Prior Art

- **`.github/scripts/release.py` + `.github/scripts/tests/test_release_feature.py`**
  in this repo: a real application tool with a `main(argv)` entrypoint whose
  feature test builds a live git fixture in a temp dir and asserts on the tool's
  file output. This is the exact shape, layout (`<tool>/`, `<tool>/pyproject.toml`,
  `<tool>/tests/`), and test framework (`unittest`) the runner follows.
- **Official SWE-bench predictions contract**: each JSONL line carries
  `instance_id`, `model_name_or_path`, `model_patch` (a plain unified diff applied
  with `git apply`). The official `swebench.harness.run_evaluation` reads exactly
  this file — our output seam.
- **Claude Code headless mode** (from `research.md`): `claude -p "<prompt>"
  --output-format json` runs one non-interactive pass and prints a JSON envelope
  containing `session_id`, `total_cost_usd`, and `result`.

## User Journey and Metrics

**Primary journey (plumbing — what the feature test proves).** An engineer has a
local `instances.jsonl` (a SWE-bench slice, or a hand-written fixture) and runs:

```
python3 -m swebench_runner run \
  --instances instances.jsonl \
  --out predictions.jsonl \
  --model-name claude-ailly-longloop
```

For each instance the runner clones the repo, checks out `base_commit` into an
isolated working directory, invokes `claude -p <prompt>` inside that checkout,
captures the working-tree diff as `model_patch`, and appends one official record
to `predictions.jsonl`. It also appends `instance_id` / `session_id` /
`total_cost_usd` to a metadata sidecar so spend per instance is tracked. When the
run finishes, `predictions.jsonl` holds one valid record per instance.

**Real end-to-end mode is the same command.** The *only* differences between the
feature test and a real SWE-bench run are (a) which `claude` is first on `PATH`
(the real CLI vs. a fake script) and (b) whether `--repo-base` points at GitHub
(default `https://github.com/{repo}.git`) or a local fixture directory. There is
no separate code path: the injection seam (`PATH` + `--repo-base`) is what makes
the plumbing testable offline while the real run exercises identical logic. The
real run is invoked manually because it spends real Anthropic API budget and
clones multi-repo GitHub sources; it is not a CI target.

**Metrics.** (1) Every instance yields exactly one well-formed predictions record
(`model_patch` is a non-empty diff or an explicit empty string on failure, never a
crash). (2) `total_cost_usd` is captured per instance. (3) Downstream: the emitted
`predictions.jsonl` is accepted as-is by the official grader (validated manually,
out of feature-test scope).

**Failure modes.** Clone/checkout failure, `claude` non-zero exit, unparseable
JSON on stdout, or an empty diff. Each is recorded as a failed instance (empty
`model_patch` plus an error note in the sidecar) and the batch continues to the
next instance rather than aborting the whole run.

## Specification

A small package `swebench_runner/` at the repo root (a standalone tool, not a
plugin), mirroring the `.github/scripts/` layout:

- `swebench_runner/runner.py` — `main(argv) -> int` with an argparse `run`
  subcommand (and a reserved, unimplemented `grade` subcommand for the deferred
  Docker stretch).
- `swebench_runner/pyproject.toml` — `requires-python >=3.12`, ruff dev dep,
  matching `.github/scripts/pyproject.toml`. No runtime third-party deps: instances
  come from a local JSONL file, so no `datasets`/HuggingFace dependency and no
  network in the tool itself.
- `swebench_runner/tests/` — the one feature test (below).

Per-instance algorithm inside `run`:

1. **Read instances.** Parse `--instances` JSONL; each record needs `instance_id`,
   `repo`, `base_commit`, `problem_statement`. Batch semantics: iterate the list
   sequentially (single instance is a batch of one). No parallelism.
2. **Isolated checkout.** Resolve `--repo-base` template (`{repo}` substituted) to
   a clone source; `git clone <source> <workdir>/<instance_id>`; then
   `git -C <checkout> checkout <base_commit>`.
3. **Invoke Claude Code.** `subprocess.run(["claude", "-p", <prompt>,
   "--output-format", "json", "--permission-mode", "acceptEdits", "--max-turns",
   <N>], cwd=<checkout>, ...)`. Subprocess (not an SDK) is the mechanism: it is the
   standard scriptable interface, needs no extra dependency, lets us set `cwd` to
   the checkout, and lets the feature test inject a fake `claude` via `PATH`.
   **Do not pass `--bare`** — long-loop mode needs skill auto-discovery to load
   `developer:ailly`, which `--bare` suppresses.
4. **The prompt** frames the SWE-bench task for long-loop mode and embeds only the
   `problem_statement` (see "Prompt" below).
5. **Capture the patch.** After `claude` returns, `git -C <checkout> add -A` then
   `git -C <checkout> diff --cached` → `model_patch`. Capturing from the working
   tree (not from Claude's stdout prose) is robust to however Claude phrases its
   result.
6. **Capture session metadata.** Parse `claude`'s stdout JSON for `session_id` and
   `total_cost_usd`.
7. **Write outputs.** Append `{"instance_id", "model_name_or_path", "model_patch"}`
   to `--out`; append `{"instance_id", "session_id", "total_cost_usd"}` (plus any
   error note) to the metadata sidecar.

**Prompt.** A fixed template that (a) declares long-loop mode explicitly, (b) tells
Claude to run autonomously with no draft-gate stops, (c) embeds the issue text, and
(d) sets the done-condition to leaving the fix in the working tree:

```
Run a developer:ailly long loop to completion, autonomously, with no draft-gate
stops, to resolve the following GitHub issue in the repository checked out in the
current working directory. Do not commit; leave the changes in the working tree.

Issue:
<problem_statement>
```

Only the `problem_statement` is included. The gold `patch` and the `FAIL_TO_PASS`
/ `PASS_TO_PASS` test names are withheld: leaking the target test names would
contaminate the benchmark and inflate the pass rate. Tradeoff: withholding makes
the task harder for the model but yields a valid, uncontaminated number, which is
the entire point of the exercise.

## Alternatives

- **Fetch instances from HuggingFace in-process** (via `datasets`). Rejected for
  the MVP: it adds a heavyweight dependency and network to the tool and its test.
  A local `instances.jsonl` keeps the tool dependency-free and the feature test
  hermetic; the user materializes the slice with a one-line `datasets`/`curl`
  script outside the tool.
- **Claude Agent SDK / a Python SDK** instead of subprocess. Rejected: `research.md`
  found the CLI subprocess is the standard, scriptable mechanism and no separate
  SDK is required; subprocess also gives the clean `PATH`/`cwd` injection seam the
  feature test relies on.
- **Include Docker grading in the feature test.** Rejected (see Summary): the
  official grader needs a Docker daemon and pulls multi-GB per-instance images —
  too heavy and slow for a quick-loop CI test, and orthogonal to the plumbing the
  test exists to prove.
- **A live one-shot `claude` invocation in the feature test.** Rejected: it would
  spend real API budget on every CI run for a quick loop whose whole risk surface
  is local plumbing (checkout, subprocess wiring, diff capture, JSONL writing).
  A fake `claude` on `PATH` proves that surface deterministically; the real
  invocation is the separate, manually-run mode of the same `main()`.

## Summary

A dependency-free `swebench_runner/` package with a `run` subcommand batches over a
local `instances.jsonl`; for each instance it clones + checks out `base_commit`,
invokes `claude -p ... --output-format json` (real long-loop mode) inside the
checkout, captures the working-tree diff as `model_patch`, and writes one
official-format record to `predictions.jsonl` plus a session-metadata sidecar. The
feature test proves this plumbing offline with a fake `claude` on `PATH` and a
local git fixture; the identical command run against GitHub with the real `claude`
is the manually-invoked benchmark run.

**Deferred decisions:**
- **Docker grading is a follow-up**, exposed as a reserved `grade` subcommand that
  will later shell out to `swebench.harness.run_evaluation` over the emitted
  `predictions.jsonl`. Kept out of the feature test per `research.md`.
- **Test-file filtering** in `model_patch` (SWE-bench applies `test_patch`
  separately) — the MVP submits the full working-tree diff; refining to exclude
  test files is a later pass.
- **Retries, caching, parallelism** — explicitly out of scope.

### Open Artifact Decisions

**`swebench_runner/` package location:** a new top-level directory at the repo root
vs. nesting under an existing plugin or `.github/scripts/`.
Proposed: repo-root `swebench_runner/`, mirroring the `.github/scripts/` layout, to
signal it is a standalone tool and not one of the skill plugins.

**Instances input format/flag:** how tasks are fed in.
Proposed: `--instances <path.jsonl>`, one SWE-bench instance record per line
(`instance_id`, `repo`, `base_commit`, `problem_statement`).

**Session-metadata sidecar:** where `session_id` / `total_cost_usd` land, since the
official predictions record has no field for them.
Proposed: a parallel `run_metadata.jsonl` (one record per instance), overridable
via `--metadata-out`, written alongside `--out`.

**Clone-source injection flag:** the seam that makes the test offline.
Proposed: `--repo-base <template>` with `{repo}` substitution, default
`https://github.com/{repo}.git`; the feature test points it at a local directory.

(The predictions output path and 3-field schema are prescribed by the SWE-bench
convention, so `--out predictions.jsonl` with `instance_id` / `model_name_or_path`
/ `model_patch` is derived, not an open choice.)

## Feature Test

Path: `swebench_runner/tests/test_predictions_plumbing.py`

**User story.** Given a local instances file and a fake `claude` on `PATH` that
edits the checkout and prints a JSON envelope, When I run the `run` subcommand,
Then `predictions.jsonl` contains exactly one official-format record per instance
whose `model_patch` is the unified diff of the edit, and the metadata sidecar
captures that instance's `session_id` and `total_cost_usd` — all with no network
and no live Anthropic API call.

This test proves the harness plumbing (checkout at `base_commit`, subprocess
invocation, working-tree diff capture, official JSONL writing, metadata capture).
It stays red until `swebench_runner/runner.py` exists.
