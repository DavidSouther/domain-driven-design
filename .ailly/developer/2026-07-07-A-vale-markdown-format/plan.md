# Implementation Plan: Markdown formatter for consistent prose wrapping

**Feature test:** `developer/tests/test_rumdl_markdown_format.py` (run via `python3 developer/tests/test_rumdl_markdown_format.py`) **User story:** A contributor adds a multi-sentence paragraph on one line to some Markdown file; `scripts/rumdl-check.sh` fails on it, `scripts/rumdl-fix.sh` rewrites it to one-sentence-per-line, and `scripts/rumdl-check.sh` then passes cleanly.

**Environment check (done during planning, not a build step):** `rumdl 0.2.28` is already installed locally via Homebrew (`/opt/homebrew/bin/rumdl`, `brew list rumdl` confirms the Cellar receipt).
`rumdl check --help` confirms the CLI shape design assumed: `rumdl check [PATHS]...` and `rumdl check -f/--fix [PATHS]...`.
No install step is needed locally.
The one open install question is CI-side only (Step 4).

**Steps:**
- [x] Step 0: API surface area
- [x] Step 1: `.rumdl.toml` config
- [x] Step 2: `scripts/rumdl-check.sh`
- [x] Step 3: `scripts/rumdl-fix.sh`
- [x] Step 4: `.github/workflows/markdown-format.yml`
- [x] Step 5: Repo-wide reformat (isolated commit)

## Step 0: API surface area

No typed language is involved (TOML config + POSIX shell), so the "stub" here is the exact contract each artifact must satisfy — file paths, invocation shape, config keys, and exit codes — pinned down before any body is written:

```toml
# .rumdl.toml (repo root)
[global]
enable = ["MD013"]

[MD013]
line-length = 1000
reflow = true
reflow-mode = "sentence-per-line"
```

```text
scripts/rumdl-check.sh [path]
  - path defaults to "." (whole repo) when omitted
  - cd "$REPO_ROOT" first (mirrors vale-check.sh's REPO_ROOT resolution)
  - runs: rumdl check "$path"
  - exit 0 = clean, exit 1 = at least one MD013 finding

scripts/rumdl-fix.sh [path]
  - same $1/path convention as rumdl-check.sh
  - cd "$REPO_ROOT" first
  - runs: rumdl check --fix "$path"
  - exit 0 once every found issue is auto-fixed (steady state, since
    MD013 is 100% mechanically fixable per design/research)
```

```yaml
# .github/workflows/markdown-format.yml — structural shape only
name: Markdown Format
on: [push, pull_request]
jobs:
  markdown-format:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - uses: rvben/rumdl@v0   # see Step 4 for the exact `with:` inputs
```

No exemptions, no exclusion globs, and no `VALE_FIX_DRY_RUN`-style escape hatch — both scripts run unrestricted over whatever path they're given, per design's "no exemptions" resolution and the confirmed-mechanical nature of `MD013`'s fix.

## Step 1: `.rumdl.toml` config

**Enables:** `check_required_files()`'s first branch stops failing — the feature test's failure message moves from `FAIL: missing .rumdl.toml` to `FAIL: missing scripts/rumdl-check.sh`, a measurable, observable step forward even though the test is still RED.

Create `.rumdl.toml` at the repo root exactly as specified in Step 0 and in design.md's API/interface surface section (`[global] enable = ["MD013"]`; `[MD013] line-length = 1000`, `reflow = true`, `reflow-mode = "sentence-per-line"`).
No other rule groups, no `[MD013] length-mode`/`abbreviations`/`require-sentence-capital` overrides — those are deferred per design's Scope-of-rules note.

**Tests**

Manual/happy-path check (this becomes part of the feature test's dynamic branch once the scripts exist, so no separate test file is needed at this step — confirm by hand):

```text
run: rumdl check --config .rumdl.toml <(some multi-sentence one-line .md file)
assert: reports an MD013 finding, exit code 1
```

- Edge case: a file with genuinely one sentence per line already reports 0 findings, exit code 0 (confirms the config doesn't over-fire).
- Edge case: `rumdl check .` from repo root doesn't crash on the frontmatter-heavy `SKILL.md` files or table-heavy docs (already confirmed in design's dry run — regression-check only).

**Implementation Outline**

```text
write .rumdl.toml with the two sections from Step 0, verbatim.
```

## Step 2: `scripts/rumdl-check.sh`

**Enables:** the feature test's `check_required_files()` moves past `scripts/rumdl-check.sh` (failure message becomes `FAIL: missing scripts/rumdl-fix.sh`); also enables manually validating the "dirty check fails" half of the round trip described in the feature test's `run_check()` helper.

Mirror `scripts/vale-check.sh`'s shape (`set -uo pipefail`, `REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"`, `cd "$REPO_ROOT"`, optional `$1` defaulting to `.`), but unrestricted — no `find ... -not -path` exclusions, since this feature has no file exemptions.
The body is a single `rumdl check` invocation rather than `vale-check.sh`'s `find | xargs`, because `rumdl check <path>` already walks directories itself.

**Tests**

```text
test "dirty file fails":
  write a probe .md file with 3 sentences on one line
  result <- run scripts/rumdl-check.sh <probe-relative-path>
  assert result.returncode == 1

test "clean file passes":
  write a probe .md file already one-sentence-per-line
  result <- run scripts/rumdl-check.sh <probe-relative-path>
  assert result.returncode == 0
```

- Edge case: no `$1` given — script runs against the whole repo (`.`) without erroring on argument-count.
- Edge case: invoked from a different working directory (`REPO_ROOT`-relative `cd` must make this location-independent, matching `vale-check.sh`'s existing behavior).

**Implementation Outline**

```bash
#!/usr/bin/env bash
set -uo pipefail
REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$REPO_ROOT" || exit 1
path="${1:-.}"
rumdl check "$path"
```

## Step 3: `scripts/rumdl-fix.sh`

**Enables:** `check_required_files()` now passes entirely — the feature test proceeds into its dynamic branch (since `rumdl` is confirmed on PATH locally) and exercises the full round trip: dirty check fails, fix rewrites the probe file to the three expected OSPL lines, clean check then passes.
This step is expected to take the feature test from RED to GREEN.

Same shape as Step 2's script, with `rumdl check --fix "$path"` in place of `rumdl check "$path"`.
No LLM dispatch, no `xargs -P`, no manifest/worked-example machinery from `vale-fix.sh` — none of that applies, since `MD013`'s fix is fully mechanical (per design's Specification section).

**Tests**

```text
test "fix rewrites a dirty file to OSPL and check then passes":
  write a probe .md file with 3 sentences on one line
  fix_result <- run scripts/rumdl-fix.sh <probe-relative-path>
  assert fix_result.returncode == 0
  assert probe file's lines == one sentence per line, in order
  check_result <- run scripts/rumdl-check.sh <probe-relative-path>
  assert check_result.returncode == 0
```

- Edge case: running fix on an already-clean file is a no-op (idempotent — exit 0, file unchanged).
- Edge case: fix preserves code fences/tables/frontmatter byte-for-byte (already confirmed by design's dry run; regression-check only, not new ground).

**Implementation Outline**

```bash
#!/usr/bin/env bash
set -uo pipefail
REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$REPO_ROOT" || exit 1
path="${1:-.}"
rumdl check --fix "$path"
```

At the end of this step, run `python3 developer/tests/test_rumdl_markdown_format.py` for real — this is the point where it should print `PASS: rumdl-check.sh/rumdl-fix.sh enforce OSPL end-to-end` and exit 0.
Commit `.rumdl.toml` + both scripts together as the tool/config commit (design calls for this to be separate from the reformat commit, but Steps 1-3 can land as one commit or three — the feature test doesn't distinguish).

## Step 4: `.github/workflows/markdown-format.yml`

**Enables:** no feature-test assertion directly (the test doesn't inspect CI YAML), but it's an explicit item in design's Summary ship list and structurally parallels `vale.yml`, which the design names as required prior art to mirror.

Resolve the design's deferred "script invocation vs. action" choice: use the `rvben/rumdl@v0` action directly, **not** a raw `scripts/rumdl-check.sh` invocation — this is the closer structural parallel, since `vale.yml` itself doesn't shell out to `vale-check.sh` either; it calls `errata-ai/vale-action@reviewdog` directly with its own flags.
Follow the same `on: [push, pull_request]` / `actions/checkout@v3` / `ubuntu-latest` skeleton as `vale.yml`.
Unlike `vale.yml`'s `fail_on_error: false` (an advisory allowance for Vale's severity levels), this step must block the build on any nonzero exit — do not carry over an equivalent "advisory" flag; confirm the action's default behavior already fails the job on a lint error (expected, since `rumdl check` exits 1), and don't add a suppressing input if so.

**Tests**

No unit test (CI YAML has no test harness in this repo); the check is a manual dry run:

```text
push a branch with one deliberately-dirty .md file
observe: the markdown-format job fails
run scripts/rumdl-fix.sh on that file, push again
observe: the markdown-format job passes
```

- Edge case: confirm at build time whether `rvben/rumdl@v0` needs an explicit `with: args:`/`config:` input to pick up `.rumdl.toml`, or auto-discovers it at the repo root (not independently re-verified beyond research's citation of the action's existence — check the action's own README/`action.yml` before wiring the `with:` block).
- Edge case: the action should run at the repo root (no `files:`/glob restriction), consistent with "no exemptions."

**Implementation Outline**

```yaml
name: Markdown Format

on: [push, pull_request]

jobs:
  markdown-format:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - uses: rvben/rumdl@v0
        with:
          args: check .
```

(Exact `with:` key names TBD at build time per the edge case above — confirm against the action's published interface rather than guessing.)

## Step 5: Repo-wide reformat (isolated commit)

**Enables:** no new feature-test assertion (the test only round-trips a temp probe file, not the whole corpus), but this is design's explicitly required deliverable: "a full repo-wide reformat pass of all tracked Markdown files... landed as its own isolated commit, separate from the tool/config/CI-step commit(s)."

Run `scripts/rumdl-fix.sh .` once, unrestricted, over the whole repo, now that Steps 1-4 are committed.
Design's dry run recorded ~2387 issues across 298/320 tracked files at research time; expect a large diff touching all 19 `SKILL.md` files, the four root docs, e2e prompt/fixture Markdown, and `.ailly/developer/**` session artifacts (explicitly in scope per design's "no exemptions" resolution).
Review the diff for sanity (spot-check a `SKILL.md`, a table-bearing doc, and a code-fence-bearing doc for byte-identical non-prose spans) before committing.
This must be its own commit — do not fold it into Steps 1-4's commit(s) — so it can be reviewed, and if needed reverted, independently of the tool/config work.

**Tests**

```text
after running scripts/rumdl-fix.sh .:
  assert scripts/rumdl-check.sh . exits 0 (whole repo is clean)
  spot-check: git diff on a table-bearing and a code-fence-bearing file
    shows no changes inside the table/fence, only prose reflow outside it
```

- Edge case: `.rumdl.toml`'s `respect_gitignore = true` default means git-ignored paths (e.g. the gitignored `docs` dir per design) are silently skipped — confirm this is the intended boundary, not an oversight, before treating a partial `rumdl check .` exit-0 as "everything's covered."
- Edge case: if any file fails to auto-fix cleanly (contrary to design's "100% fixable" dry-run finding), surface it explicitly rather than silently committing a partially-dirty tree — re-run `scripts/rumdl-check.sh .` after the fix and treat nonzero as a blocker for this step, not a follow-up.

**Implementation Outline**

```text
scripts/rumdl-fix.sh .
git add -A -- '*.md'   # or equivalent scoped add; review before committing
git commit  # isolated reformat commit, separate from Steps 1-4's commit(s)
```
