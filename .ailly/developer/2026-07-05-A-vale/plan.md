# Implementation Plan: Adopt Vale.sh Prose Linting

**Feature test:** `developer/tests/test_vale_lint_setup.py`
**User story:** A contributor opens the repository and finds the Vale config, all 11 rule files, the CI workflow, and local-usage docs in place, so installing Vale and running `vale sync` works immediately.
**Steps:**
- [ ] Step 0: Artifact surface area
- [ ] Step 1: Write the failing feature test (RED)
- [ ] Step 2: Create `.vale.ini`
- [ ] Step 3: Create the 11 `styles/DDD/*.yml` rule files
- [ ] Step 4: Create `.github/workflows/vale.yml`
- [ ] Step 5: Add local execution instructions to `DEVELOPMENT.md`
- [ ] Step 6: Run the feature test to confirm GREEN

## Step 0: Artifact surface area

This is a static-configuration/documentation feature; there are no domain types or function signatures to stub. The "surface area" is the fixed inventory of artifacts and the content contract the feature test checks. No patterns from `patterns:using-patterns` apply (no domain objects, no persistence, no lifecycle).

Artifact inventory (paths only — content is written verbatim from `.ailly/prompts/vale.md` in later steps):

```
.vale.ini
styles/DDD/EmDashes.yml
styles/DDD/Parentheticals.yml        # two YAML documents: Parentheticals, LongParenthetical
styles/DDD/Filler.yml
styles/DDD/Sycophancy.yml
styles/DDD/PassiveVoice.yml
styles/DDD/Nominalizations.yml
styles/DDD/Consistency.yml
styles/DDD/TechnicalClarity.yml
styles/DDD/SentenceLength.yml
styles/DDD/WordChoice.yml
styles/DDD/Redundancy.yml
.github/workflows/vale.yml
DEVELOPMENT.md                        # append-only new section
```

Content contract each later step must satisfy (this is what `test_vale_lint_setup.py` asserts):

- `.vale.ini`: contains `StylesPath = styles`, `Vocab = DDD`, `BasedOnStyles = Google, Joblint`, and one `Rules =` line naming all 11 IDs: `DDD.EmDashes, DDD.Parentheticals, DDD.Filler, DDD.Sycophancy, DDD.PassiveVoice, DDD.Nominalizations, DDD.Consistency, DDD.TechnicalClarity, DDD.SentenceLength, DDD.WordChoice, DDD.Redundancy`.
- Each `styles/DDD/*.yml`: starts with `---`, no tab characters, non-empty `name:`, `description:`, `message:`, `link:`, `level:`, `scope:`. `Parentheticals.yml` has two `---`-separated documents (`name: Parentheticals`, then `name: LongParenthetical`).
- `.github/workflows/vale.yml`: contains `errata-ai/vale-action@reviewdog`, `fail_on_error: false`, `reporter: github-pr-review`.
- `DEVELOPMENT.md`: contains `vale sync` and `brew install vale` (or equivalent).

## Step 1: Write the failing feature test (RED)

**Enables:** the whole test file existing and failing for the right reason (every assertion below).

Write `developer/tests/test_vale_lint_setup.py` following the existing `developer/tests/*.py` convention (no `pytest`, no third-party YAML parser — hand-rolled checks; `main()` returns 0/1, prints one reason line per failure). No `PyYAML` or `pytest` is available in this environment, so YAML "parsing" is line/regex-based structural checking only, matching `e2e/run_static_evals.py`'s precedent.

Structure of the test (one check function per artifact group):

- `check_vale_ini()` — reads `.vale.ini`, asserts the four required substrings/lines from the Step 0 contract.
- `check_style_files()` — iterates the 11 expected filenames under `styles/DDD/`, asserts each exists and passes the structural sanity check (starts with `---`, no tabs, has the six required non-empty keys); special-cases `Parentheticals.yml` to require two `---`-documents with the two expected `name:` values.
- `check_workflow()` — reads `.github/workflows/vale.yml`, asserts the three required substrings.
- `check_development_md()` — reads `DEVELOPMENT.md`, asserts it mentions `vale sync` and `brew install vale`.
- `main()` — runs all four checks, collects failure reasons, prints them, returns 0 only if all pass.

Run it now: it must fail (RED) because none of the target files exist yet. Confirm the failure output names each missing artifact (not a crash/traceback), so later steps can be checked off one at a time as the reasons disappear.

**Tests**

```
test "feature test itself is runnable and red":
  exit_code <- run("python3 developer/tests/test_vale_lint_setup.py")
  assert exit_code == 1
  assert output mentions ".vale.ini" and "styles/DDD" and "vale.yml" and "DEVELOPMENT.md"
```

- Edge case: script must not raise an unhandled exception when files are absent (missing-file is an expected, reported failure, not a crash).
- Edge case: `Parentheticals.yml` check must fail with a distinct reason before the file exists (not conflated with the other 10 files' generic reason).

**Implementation Outline**

```
def read_or_none(path):
  return contents if exists else None

def check_vale_ini(): ...
def check_style_files(): ...  # loop over the 11 filenames, dispatch Parentheticals to a two-document check
def check_workflow(): ...
def check_development_md(): ...

def main():
  reasons = []
  for check in [check_vale_ini, check_style_files, check_workflow, check_development_md]:
    reasons += check()
  print each reason
  return 1 if reasons else 0

if __name__ == "__main__":
  sys.exit(main())
```

## Step 2: Create `.vale.ini`

**Enables:** `check_vale_ini()` passes.

Create `.vale.ini` at repo root, copied verbatim from `.ailly/prompts/vale.md`'s Installation section (both `[*.md]` blocks, `TokenIgnores` line included), with one deviation per `design.md`'s resolved Open Artifact Decision: the `Rules =` line names all 11 IDs, not the spec's original 8 — append `, DDD.SentenceLength, DDD.WordChoice, DDD.Redundancy` to the spec's line.

**Tests**

Re-run `test_vale_lint_setup.py`; `check_vale_ini()`'s reasons should disappear while the style-file, workflow, and doc reasons remain.

- Edge case: `Rules =` line must name exactly 11 comma-separated `DDD.*` IDs, matching `Redundancy.yml`'s filename stem (`DDD.Redundancy`, not `DDD.RedundantPhrases`) and `Consistency.yml`'s (`DDD.Consistency`, not `DDD.TermConsistency`).

**Implementation Outline**

Direct file write; no algorithm. Copy spec text, then string-edit the one `Rules =` line to add three IDs.

## Step 3: Create the 11 `styles/DDD/*.yml` rule files

**Enables:** `check_style_files()` passes for all 11 files.

Create `styles/DDD/` and each of the 11 YAML files, each copied verbatim from its spec block in `.ailly/prompts/vale.md`. `Parentheticals.yml` is the one file built from two spec blocks (`Parentheticals` then `LongParenthetical`) joined with a `---` document separator, per `design.md`'s adopted caveat — do not split into two files.

**Tests**

Re-run the feature test; all 11 per-file reasons should disappear, including the two-document check for `Parentheticals.yml`.

- Edge case: no tab characters in any file (YAML sanity check rejects tabs).
- Edge case: `Redundancy.yml`'s internal `name:` is `RedundantPhrases`, not `Redundancy` — the structural check only requires `name:` to be non-empty, not equal to the filename; do not "fix" this mismatch, it is intentional per the design's addressing-convention note.

**Implementation Outline**

Direct file writes, one per rule, verbatim from spec. No transformation logic beyond the `Parentheticals.yml` two-document join.

## Step 4: Create `.github/workflows/vale.yml`

**Enables:** `check_workflow()` passes.

Create `.github/workflows/vale.yml`, copied verbatim from the spec's "Usage in CI/CD" section: triggers on `[push, pull_request]`, `actions/checkout@v3`, `errata-ai/vale-action@reviewdog` with `files: 'README.md,**/*.md'`, `fail_on_error: false`, `reporter: github-pr-review`.

**Tests**

Re-run the feature test; `check_workflow()`'s reason should disappear.

- Edge case: file must be valid enough YAML that GitHub Actions would parse it (indentation matches the spec exactly; this is a copy, not a rewrite).

**Implementation Outline**

Direct file write; no algorithm.

## Step 5: Add local execution instructions to `DEVELOPMENT.md`

**Enables:** `check_development_md()` passes.

Append a new `## Prose Linting (Vale)` section to `DEVELOPMENT.md` covering, per `design.md`: install (`brew install vale` or a downloaded binary), `vale sync` to pull base styles, `vale README.md` / `vale **/*.md` (noting the `globstar` shell caveat) to run locally, and the severity-level meanings plus the `<!-- vale off -->` / `<!-- vale on -->` exception mechanism, copied from the spec's Notes section.

**Tests**

Re-run the feature test; `check_development_md()`'s reason should disappear. This should be the last remaining check before the whole file reports GREEN.

- Edge case: section is additive only — do not touch any existing `DEVELOPMENT.md` content.

**Implementation Outline**

Append-only edit to `DEVELOPMENT.md`; no algorithm.

## Step 6: Run the feature test to confirm GREEN

**Enables:** the full feature test (`developer/tests/test_vale_lint_setup.py`) exits 0 with no printed reasons.

Run `python3 developer/tests/test_vale_lint_setup.py` and confirm exit code 0 and empty failure output. No new code; this step is verification only, confirming steps 1-5 together satisfy every assertion written in step 1.

**Tests**

```
test "feature test is green":
  exit_code <- run("python3 developer/tests/test_vale_lint_setup.py")
  assert exit_code == 0
```

- Edge case: none — this step is a pure verification checkpoint, not new implementation.

**Implementation Outline**

N/A (verification only).
