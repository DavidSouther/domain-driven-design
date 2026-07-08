# Implementation Plan: SWE-bench Runner Predictions Plumbing

**Feature test:** `swebench_runner/tests/test_predictions_plumbing.py`
**User story:** Given a local instances file and a fake `claude` on `PATH` that edits the checkout and prints a JSON envelope, running the `run` subcommand produces exactly one official-format `predictions.jsonl` record per instance (with a real unified-diff `model_patch`) and a metadata sidecar capturing `session_id` / `total_cost_usd` — no network, no live Anthropic API call.

**Libraries & Skills (carried forward from `design.md`):** Before implementing Step 4 (the code that constructs the Claude Code prompt in `build_prompt`), load `developer:ailly` via the harness's skill-loading mechanism and check the prompt text against `developer/skills/ailly/references/shapes/long-loop.md`'s actual trigger phrasing ("run a long loop", "dynamic workflow", "run \<project\> to completion") rather than relying on the guessed wording already drafted in `design.md`. Confirm or adjust the literal template before writing it into the stub from Step 0.

**Patterns beat (`patterns:using-patterns`, run before fixing Step 0's surface):**
- **domain-objects** — `Instance`, `ClaudeInvocation`, and the two output records (prediction row, metadata row) are Value Objects: no identity beyond their data, immutable, replaced rather than mutated. None of them carry behavior, so no methods beyond construction are needed.
- **parse-dont-validate** — `parse_instances` is the boundary: a raw JSONL line becomes an `Instance` only if the required fields are present. Once parsed, no code downstream re-checks `instance_id`/`repo`/`base_commit`/`problem_statement` presence.
- **errors-typed-untyped** — internally, the per-instance loop needs to *branch* on which failure mode happened (checkout failed vs. `claude` failed vs. empty diff), so `ClaudeInvocation`/the per-instance outcome carries a small typed `error: str | None` (or an explicit tag) the orchestrator matches on — not a bare `bool`. The metadata sidecar itself stays stringly-typed (a human-readable `error` string), per the pattern's application-boundary guidance. This is the design's "Failure modes" section made concrete.
- **newtype** and **repository** were considered and skipped as disproportionate: `instance_id`/`repo` are plain strings used in exactly one small module (no cross-type confusion risk to guard against), and `predictions.jsonl` has no read side or swappable storage technology — a plain append function is sufficient.

The path from the current `ModuleNotFoundError` to the feature test's assertions is directly given by `design.md`'s numbered algorithm (Specification section) and does not require the forward-backward method.

**Steps:**
- [ ] Step 0: API surface area
- [ ] Step 1: Argparse scaffolding and `main(argv)` entry stub
- [ ] Step 2: Instances-JSONL parsing
- [ ] Step 3: Isolated git checkout
- [ ] Step 4: Claude Code subprocess invocation and prompt template
- [ ] Step 5: Patch capture via working-tree diff
- [ ] Step 6: Predictions/metadata writing and end-to-end wiring
- [ ] Step 7: Failure-mode refactor and cleanup

## Step 0: API surface area

New types and function signatures (stubs only, no bodies) in `swebench_runner/runner.py`:

```python
from __future__ import annotations

import argparse
import json
import subprocess
from dataclasses import dataclass
from pathlib import Path

DEFAULT_REPO_BASE = "https://github.com/{repo}.git"
DEFAULT_MAX_TURNS = 40  # not exposed as a required CLI flag; a module constant is enough for MVP


@dataclass(frozen=True)
class Instance:
    instance_id: str
    repo: str
    base_commit: str
    problem_statement: str


@dataclass(frozen=True)
class ClaudeInvocation:
    """Result of one `claude -p ...` subprocess call."""
    returncode: int
    session_id: str | None
    total_cost_usd: float | None
    error: str | None  # None on success; a human-readable note on any failure mode


def parse_instances(path: Path) -> list[Instance]: ...


def checkout_instance(instance: Instance, repo_base: str, workdir: Path) -> Path:
    """Clone `repo_base.format(repo=instance.repo)` into `workdir/instance.instance_id`
    and check out `instance.base_commit`. Returns the checkout path."""
    ...


def build_prompt(problem_statement: str) -> str:
    """The fixed developer:ailly long-loop prompt template from design.md,
    verified against long-loop.md's trigger phrasing (Step 4)."""
    ...


def invoke_claude(checkout: Path, prompt: str, max_turns: int = DEFAULT_MAX_TURNS) -> ClaudeInvocation:
    """Run `claude -p <prompt> --output-format json --permission-mode acceptEdits
    --max-turns <max_turns>` with cwd=checkout. Never raises on a non-zero exit or
    unparseable stdout; both are folded into ClaudeInvocation.error."""
    ...


def capture_patch(checkout: Path) -> str:
    """`git add -A && git diff --cached` in checkout. Empty string, not an error,
    when there is no change."""
    ...


def append_jsonl(path: Path, record: dict) -> None: ...


def run(args: argparse.Namespace) -> int:
    """Orchestrates parse_instances -> checkout_instance -> build_prompt ->
    invoke_claude -> capture_patch -> append_jsonl(predictions) + append_jsonl(metadata)
    for every instance; a per-instance failure is recorded, not raised, and the
    batch continues."""
    ...


def grade(args: argparse.Namespace) -> int:
    """Reserved for the Docker-grading stretch goal. Unimplemented in this feature."""
    ...


def main(argv: list[str] | None = None) -> int: ...
```

Everything above is exercised, directly or indirectly, by `test_predictions_plumbing.py`.

## Step 1: Argparse scaffolding and `main(argv)` entry stub

**Enables:** The test can call `_r.main([...])` at all (today it fails at `import runner as _r` with `ModuleNotFoundError`). This step gets past the import and establishes the CLI contract, though `run()` still does nothing real yet.

Build the `argparse.ArgumentParser` with `run` and `grade` subcommands. `run`'s flags: `--instances` (required), `--repo-base` (default `DEFAULT_REPO_BASE`), `--workdir` (required, per the feature test), `--out` (required), `--metadata-out` (required), `--model-name` (required). `main(argv)` parses and dispatches to `run(args)` or `grade(args)`, catching nothing yet — a stub `run` can simply `return 0` for now so the module is importable and the CLI shape is locked in.

**Tests**

```
test "CLI rejects missing --instances":
  rc <- call main(["run", "--out", "x", "--metadata-out", "y", "--workdir", "w", "--model-name", "m"])
  assert SystemExit raised (argparse error) -- no --instances given

test "CLI accepts full flag set and dispatches without crashing":
  rc <- call main(["run", "--instances", "i.jsonl", "--repo-base", "t", "--workdir", "w",
                    "--out", "o.jsonl", "--metadata-out", "m.jsonl", "--model-name", "n"])
  assert rc == 0  -- stub run() just returns 0 at this point
```

- Edge case: unknown subcommand (`main(["bogus"])`) → argparse error, non-zero/SystemExit, not a crash.
- Edge case: `grade` subcommand is reachable but does not attempt any behavior yet.

**Implementation Outline**

```
def main(argv):
    parser = build_parser()  # top-level parser + run/grade subparsers
    args = parser.parse_args(argv)
    if args.command == "run": return run(args)
    if args.command == "grade": return grade(args)
```

## Step 2: Instances-JSONL parsing

**Enables:** `run()` can turn `--instances` into real `Instance` objects; the feature test's single-line fixture (`fixture__demo-1`) becomes loop-able data. No feature-test assertion passes yet on its own, but it unblocks Step 3.

`parse_instances(path)` reads the file line by line, skips blank lines, `json.loads`-parses each, and constructs an `Instance` from the four required keys, raising a clear, specific error (per parse-dont-validate) naming the line number and the missing/invalid field rather than a bare `KeyError`.

**Tests**

```
test "parses a two-instance fixture":
  path <- write_jsonl([{instance_id: "a", repo: "o/a", base_commit: "abc", problem_statement: "..."},
                        {instance_id: "b", repo: "o/b", base_commit: "def", problem_statement: "..."}])
  instances <- parse_instances(path)
  assert len(instances) == 2
  assert instances[0] == Instance("a", "o/a", "abc", "...")
```

- Edge case: blank/whitespace-only lines between records are skipped.
- Edge case: a line missing `base_commit` raises a specific error naming the line number and field, not a generic `KeyError`/`TypeError`.
- Edge case: malformed JSON on one line raises with the line number in the message.

**Implementation Outline**

```
def parse_instances(path):
    instances = []
    for lineno, line in enumerate(path.read_text().splitlines(), start=1):
        if not line.strip(): continue
        data = json.loads(line)  # on failure, wrap with line number context
        instances.append(Instance(
            instance_id=data["instance_id"], repo=data["repo"],
            base_commit=data["base_commit"], problem_statement=data["problem_statement"],
        ))  # on missing key, wrap with line number + field name context
    return instances
```

## Step 3: Isolated git checkout

**Enables:** The feature test's `--repo-base` injection seam and per-instance isolated working directory. This is the first step touching real subprocesses (`git`) and is where the "clone/checkout failure" failure mode from `design.md` first appears.

`checkout_instance` resolves `repo_base.format(repo=instance.repo)` to a clone source, `git clone <source> <workdir>/<instance_id>`, then `git -C <checkout> checkout <base_commit>`, returning the checkout path. Uses `subprocess.run(..., check=True, capture_output=True)` so failures surface as `CalledProcessError` for the caller (Step 6/7) to catch and translate into a per-instance error note, per the errors-typed-untyped split (raise internally, translate to a string at the `run()` boundary).

**Tests**

```
test "checks out base_commit into an isolated workdir":
  repo <- init_git_fixture_repo(with_file "calc.py")
  base <- head_commit(repo)
  instance <- Instance("x", "fixture/demo", base, "...")
  checkout <- checkout_instance(instance, repo_base=str(repo.parent / "{repo}"), workdir=tmp / "work")
  assert (checkout / "calc.py").exists()
  assert head_commit(checkout) == base
```

- Edge case: cloning a nonexistent `repo_base` path raises `CalledProcessError` (caller's job to catch, not this function's).
- Edge case: checking out a `base_commit` that doesn't exist in the clone raises `CalledProcessError`.
- Edge case: re-running against a `workdir` that already contains a stale checkout for the same `instance_id` (test with two runs) — decide and note whether this step removes/reclones or fails; the feature test only exercises a fresh `workdir`, so a simple "clone must not already exist" precondition is enough for now.

**Implementation Outline**

```
def checkout_instance(instance, repo_base, workdir):
    source = repo_base.format(repo=instance.repo)
    dest = workdir / instance.instance_id
    run(["git", "clone", source, str(dest)], check=True, capture_output=True)
    run(["git", "-C", str(dest), "checkout", instance.base_commit], check=True, capture_output=True)
    return dest
```

## Step 4: Claude Code subprocess invocation and prompt template

**Enables:** The feature test's fake `claude` on `PATH` actually gets invoked and its JSON envelope (`session_id`, `total_cost_usd`) gets captured — the metadata-sidecar assertions in the feature test depend on this step.

Per the carried-forward Libraries & Skills note, load `developer:ailly` and confirm the exact long-loop trigger phrasing before finalizing `build_prompt`'s literal text (design.md's draft: *"Run a developer:ailly long loop to completion, autonomously, with no draft-gate stops, to resolve the following GitHub issue in the repository checked out in the current working directory. Do not commit; leave the changes in the working tree.\n\nIssue:\n\<problem_statement\>"*). `invoke_claude` runs `subprocess.run(["claude", "-p", prompt, "--output-format", "json", "--permission-mode", "acceptEdits", "--max-turns", str(max_turns)], cwd=checkout, capture_output=True, text=True)` — **no `--bare`** — and parses stdout as JSON. Any of {non-zero exit, unparseable stdout JSON} is caught and folded into `ClaudeInvocation.error`, never raised past this function (this is the "`claude` non-zero exit" / "unparseable JSON on stdout" failure modes from `design.md`).

**Tests**

```
test "captures session_id and total_cost_usd from a fake claude":
  put_fake_claude_on_PATH(prints session_id="s1", total_cost_usd=0.5, exits 0)
  result <- invoke_claude(checkout=some_dir, prompt="...", max_turns=5)
  assert result.returncode == 0
  assert result.session_id == "s1"
  assert result.total_cost_usd == 0.5
  assert result.error is None
```

- Edge case: fake `claude` exits non-zero → `ClaudeInvocation(error=<non-empty note mentioning the exit code>)`, no exception raised.
- Edge case: fake `claude` prints non-JSON to stdout → `ClaudeInvocation(error=<note mentioning the parse failure>)`, `session_id`/`total_cost_usd` are `None`.
- Edge case: `claude` not found on `PATH` at all (`FileNotFoundError`) is also folded into `error`, not raised.

**Implementation Outline**

```
def invoke_claude(checkout, prompt, max_turns=DEFAULT_MAX_TURNS):
    try:
        proc = subprocess.run(["claude", "-p", prompt, "--output-format", "json",
                                "--permission-mode", "acceptEdits", "--max-turns", str(max_turns)],
                               cwd=checkout, capture_output=True, text=True)
    except OSError as e:
        return ClaudeInvocation(returncode=-1, session_id=None, total_cost_usd=None, error=str(e))
    if proc.returncode != 0:
        return ClaudeInvocation(proc.returncode, None, None, error=f"claude exited {proc.returncode}: {proc.stderr}")
    try:
        envelope = json.loads(proc.stdout)
    except json.JSONDecodeError as e:
        return ClaudeInvocation(proc.returncode, None, None, error=f"unparseable claude stdout: {e}")
    return ClaudeInvocation(proc.returncode, envelope.get("session_id"), envelope.get("total_cost_usd"), error=None)
```

## Step 5: Patch capture via working-tree diff

**Enables:** The feature test's `model_patch` assertions (`"calc.py"`, `-    return a - b`, `+    return a + b` present in the diff text).

`capture_patch(checkout)` runs `git -C <checkout> add -A` then `git -C <checkout> diff --cached`, returning stdout as the patch string. Per design.md, an empty result (no changes) is a valid, non-error outcome — the "empty-diff handling" failure mode — not exceptional; it just means the batch continues with an empty `model_patch` for that instance.

**Tests**

```
test "captures a unified diff of the working-tree edit":
  checkout <- git_fixture_with("calc.py" containing "return a - b")
  (checkout / "calc.py").write_text(... "return a + b" ...)
  patch <- capture_patch(checkout)
  assert "calc.py" in patch
  assert "-    return a - b" in patch
  assert "+    return a + b" in patch
```

- Edge case: no changes in the working tree → `capture_patch` returns `""`, not an error.
- Edge case: a newly created (untracked) file is included, since `add -A` stages new files before diffing `--cached`.

**Implementation Outline**

```
def capture_patch(checkout):
    run(["git", "-C", str(checkout), "add", "-A"], check=True, capture_output=True)
    result = run(["git", "-C", str(checkout), "diff", "--cached"], check=True, capture_output=True, text=True)
    return result.stdout
```

## Step 6: Predictions/metadata writing and end-to-end wiring

**Enables:** This is the step where `test_produces_official_predictions_record` is expected to go green: `rc == 0`, exactly one line in `predictions.jsonl` with the three official fields, and one line in the metadata sidecar with `instance_id`/`session_id`/`total_cost_usd`.

`append_jsonl(path, record)` appends one `json.dumps(record) + "\n"` line (opened fresh — truncated — at the start of a `run()` call, then appended to per instance, so a rerun doesn't concatenate onto a stale file). `run(args)` becomes the real orchestrator: `parse_instances` → loop → `checkout_instance` → `build_prompt` + `invoke_claude` → `capture_patch` → write `{"instance_id", "model_name_or_path": args.model_name, "model_patch"}` to `--out` and `{"instance_id", "session_id", "total_cost_usd"}` (plus `error` when present) to `--metadata-out`. Returns `0` when the batch completes (even with some per-instance failures — see Step 7).

**Tests**

The feature test itself (`test_predictions_plumbing.py::PredictionsPlumbingTest::test_produces_official_predictions_record`) is the acceptance test for this step — run it directly.

Suggested narrower unit test alongside it:

```
test "append_jsonl truncates once then appends":
  append_jsonl(path, {"a": 1})
  append_jsonl(path, {"a": 2})
  assert path.read_text().splitlines() == ['{"a": 1}', '{"a": 2}']
```

- Edge case: two instances in one `--instances` file produce two lines in `--out`, in the same order as the input (batch semantics from design.md — sequential, no parallelism).
- Edge case: `--out` and `--metadata-out` point at paths whose parent directories already exist (the feature test's `tmp` dir) — no directory-creation logic is required yet.

**Implementation Outline**

```
def run(args):
    instances = parse_instances(Path(args.instances))
    Path(args.out).write_text("")           # truncate/create fresh
    Path(args.metadata_out).write_text("")
    for instance in instances:
        checkout = checkout_instance(instance, args.repo_base, Path(args.workdir))
        prompt = build_prompt(instance.problem_statement)
        invocation = invoke_claude(checkout, prompt)
        patch = capture_patch(checkout)
        append_jsonl(Path(args.out), {
            "instance_id": instance.instance_id,
            "model_name_or_path": args.model_name,
            "model_patch": patch,
        })
        append_jsonl(Path(args.metadata_out), {
            "instance_id": instance.instance_id,
            "session_id": invocation.session_id,
            "total_cost_usd": invocation.total_cost_usd,
        })
    return 0
```

## Step 7: Failure-mode refactor and cleanup

**Enables:** No new feature-test assertion (the feature test is already green after Step 6); this step hardens the batch against the failure modes design.md calls out so a single bad instance can't abort the run, and tidies the module.

Wrap the per-instance body of `run()`'s loop (`checkout_instance` through `capture_patch`) in a boundary that catches `CalledProcessError`/`OSError` from checkout and folds it into the same per-instance metadata record as an `error` string (errors-typed-untyped: typed/raised internally, translated to a stringly-typed sidecar field at this application boundary) with an empty `model_patch`, then `continue`s to the next instance rather than propagating. Confirm `grade` still returns a clear non-zero/"not implemented" result rather than silently no-op'ing. Run `ruff` (per `swebench_runner/pyproject.toml`, matching `.github/scripts/pyproject.toml`'s `select = ["E", "F", "I"]`) and fix any findings. Extract the prompt template string and `DEFAULT_MAX_TURNS`/`DEFAULT_REPO_BASE` constants if not already done in Step 0.

**Tests**

```
test "a checkout failure for one instance still yields a record and the batch continues":
  instances_file <- two instances, first with an invalid base_commit
  rc <- run(args pointing at instances_file)
  assert rc == 0
  lines <- read predictions.jsonl
  assert len(lines) == 2
  assert json.loads(lines[0])["model_patch"] == ""
  meta_lines <- read metadata sidecar
  assert "error" in json.loads(meta_lines[0])
  assert json.loads(lines[1])["instance_id"] == "<second instance>"  -- batch continued
```

- Edge case: `grade` subcommand invoked directly (`main(["grade", ...])`) returns non-zero or prints a clear "not implemented" message; it must not crash with an unrelated `AttributeError`/stub `...` (`NotImplementedError` surfaced deliberately, or a clean early return, is acceptable).
- Edge case: re-run the full feature test after this refactor to confirm it is still green (no regression from the added try/except).

**Implementation Outline**

```
for each instance:
    patch, invocation, error <- "", empty ClaudeInvocation, None
    attempt:
        checkout <- checkout_instance(...); invocation <- invoke_claude(...)
        patch <- capture_patch(checkout); error <- invocation.error
    on checkout/subprocess failure: error <- descriptive note naming the instance
    write prediction record (patch defaults to "" when error is set)
    write metadata record (add "error" key only when error is set)
```
