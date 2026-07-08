# Markdown formatter for consistent prose wrapping

*Quick-loop design: sized to drive planning, not a full design document.*
*Purpose, Prior Art, and Alternatives are settled in `research.md`/`spike.md` and only summarized here; this doc's weight is the Specification, the API surface, and the one feature test.*

## Purpose

Every `.md` file in the repo converts to One-Sentence-Per-Line (OSPL) prose wrapping, enforced by `rumdl`, mirroring the existing `vale-check.sh`/`vale-fix.sh` check/fix shape.
This is orthogonal to Vale: Vale lints prose style (word choice, passive voice, sentence length); `rumdl` enforces physical line wrapping.
Neither subsumes the other.

## Prior Art

`scripts/vale-check.sh` / `scripts/vale-fix.sh` and `.github/workflows/vale.yml` are the shape to follow (`REPO_ROOT`-relative `cd`, optional `$1` path argument for single-file testing, `set -uo pipefail`).
Full tool comparison and decision rationale: `research.md` (Resolved Decisions) and `spike.md`.

One difference from that prior art, confirmed while drafting this design: `vale-fix.sh`'s narrowed file scope (`developer/skills domain/skills patterns/skills research/skills general/skills research/references`, excluding `e2e`) and its per-file Claude-Haiku dispatch exist because *prose-style* fixes need judgment, and e2e fixtures may deliberately contain the flagged patterns under test.
Neither reason applies to `rumdl`: its `--fix` is a deterministic, mechanical rewrite (confirmed in the spike — code fences, tables, and frontmatter survive byte-identical), so it is safe to run unrestricted, matching the "no exemptions" resolution in `research.md`.
The new scripts carry over vale's *invocation shape*, not its *exclusion* or *LLM-dispatch* logic.

## Specification

**Scope-of-rules decision (new, not previously resolved in research):** `rumdl` ships ~65 markdownlint-compatible rules.
This feature enables only `MD013` (line length / reflow), via `[global] enable = ["MD013"]`.
Enabling `rumdl`'s full default rule set was tried against the live repo during design (`rumdl check .` with all defaults active) and also flags things like MD041 ("first line must be a top-level heading") across files that intentionally lead with YAML frontmatter or non-heading content — a repo-wide heading-structure normalization is a different, unscoped feature.
Restricting to `MD013` keeps this feature's diff bounded to what `research.md` scoped: "consistent, enforced Markdown prose-wrapping," not full markdownlint adoption.
Confirmed against the real repo at design time: with only `MD013` enabled, `rumdl check .` finds 2387 issues across 298/320 tracked `.md` files, all reported as auto-fixable, and it does not crash on any file (dot-language fences, tables, and the 951-char frontmatter line in `SKILL.md` all included).

**Convention:** `reflow-mode = "sentence-per-line"` (OSPL) with `line-length` set generously (`1000`), not the repo's informal ~80-char norm — this sidesteps the open, unresolved upstream question (rumdl#111) of how sentence-per-line reflow composes with a tight `line-length` cap, by simply not imposing a cap tight enough for the question to bite.

**No exemptions:** every tracked `.md` file is in scope — all 19 `SKILL.md` files, the four root docs, e2e prompt/fixture Markdown, and `.ailly/developer/**` session artifacts. `rumdl`'s default `respect_gitignore = true` is left as-is, so only git-ignored paths (e.g. this repo's gitignored `docs` dir) are skipped — consistent with "no exemptions" applying to the tracked corpus, not to content that isn't part of the repo's distributed Markdown at all.

**Deferred, explicitly out of scope for this feature** (carried over from `research.md`, restated for the plan phase): the 951-char YAML frontmatter scalar in `SKILL.md` files is untouched by any Markdown-body wrap tool, including this one — a YAML-specific reflow (e.g. a literal/folded block scalar for `description`) is a separate, later feature if frontmatter readability becomes a real motivation.
Table cell-padding normalization is likewise untouched (`MD013` doesn't govern tables) and is not part of this feature.

### API / interface surface

**`.rumdl.toml`** (new, repo root):

```toml
[global]
enable = ["MD013"]

[MD013]
line-length = 1000
reflow = true
reflow-mode = "sentence-per-line"
```

**`scripts/rumdl-check.sh`** (new) — pure lint pass, no fixes:

- Invocation: `scripts/rumdl-check.sh [path]` — `path` defaults to `.` (whole repo); a single path argument lints just that file/dir, for isolated testing (mirrors `vale-check.sh`'s `$1` convention).
- Behavior: `cd "$REPO_ROOT"` then `rumdl check "$path"`.
- Exit code: `0` if clean, `1` if any `MD013` issue is found (confirmed real `rumdl` behavior, not assumed) — same pass/fail contract CI depends on.

**`scripts/rumdl-fix.sh`** (new) — mechanical rewrite in place:

- Invocation: `scripts/rumdl-fix.sh [path]` — same `path` convention as the check script.
- Behavior: `cd "$REPO_ROOT"` then `rumdl check --fix "$path"`.
- Exit code: `0` once every found issue is auto-fixed (confirmed: with only `MD013` enabled, 100% of found issues are fixable, so a clean exit is the expected steady state — unlike `vale-fix.sh`, there is no LLM dispatch, no dry-run flag, and no per-rule worked-example lookup, because there is nothing left needing judgment once the rewrite is mechanical).

**CI:** a new `.github/workflows/markdown-format.yml`, structurally parallel to `vale.yml` (`on: [push, pull_request]`, `actions/checkout@v3`, `ubuntu-latest`), installing `rumdl` and running `scripts/rumdl-check.sh` (or the `rvben/rumdl@v0` action directly) against the whole repo.
Unlike `vale.yml`'s `fail_on_error: false` (Vale's severity levels make some findings advisory-only), this check is binary — a file either matches the configured wrap convention or it doesn't — so this step fails the build on any nonzero exit.
The plan phase resolves the exact step shape (script invocation vs. the official action).

**Repo-wide reformat:** `scripts/rumdl-fix.sh` run once over `.`, landed as its own commit, isolated from the tool/config/CI-step commit(s), per `research.md`'s resolved scope.

## The One Feature Test

**User story:** A contributor adds a multi-sentence paragraph on one line to some Markdown file.
`scripts/rumdl-check.sh` run against that file fails, flagging it as not OSPL-wrapped.
The contributor runs `scripts/rumdl-fix.sh` against the same file; it rewrites the paragraph to one sentence per line.
`scripts/rumdl-check.sh` run again against the now-fixed file passes cleanly.

This is the end-to-end round trip that defines "done": the config file is correctly wired (OSPL convention, generous line-length), both scripts exist and run against a single path, and the check/fix contract (`1` when dirty, `0` when clean) holds in both directions.

**Test file:** `developer/tests/test_rumdl_markdown_format.py` — follows the existing standalone-script convention in `developer/tests/` (see `test_vale_lint_setup.py`, `test_vale_fix_examples.py`): a `main()` returning `0`/`1`, run directly via `python3 developer/tests/test_rumdl_markdown_format.py`, no pytest framework dependency.

**Current status: RED.**
Neither `.rumdl.toml` nor either script exists yet; the test fails at the "required files" precondition (see run output recorded below in this session's report).

## Summary

Ships: `.rumdl.toml` (scoped to `MD013` only, OSPL, generous `line-length`), `scripts/rumdl-check.sh`, `scripts/rumdl-fix.sh`, a new `markdown-format.yml` CI workflow, and a separate, isolated repo-wide reformat commit.
Deferred out of this feature: YAML frontmatter reflow, table cell-padding normalization, and adopting any `rumdl` rule beyond `MD013`.
The plan phase picks the exact CI step implementation (raw script invocation vs. `rvben/rumdl@v0` action) and sequences the reformat commit relative to the tool/config commit.
