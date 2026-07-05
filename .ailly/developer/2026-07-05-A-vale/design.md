# Adopt Vale.sh Prose Linting

**Libraries & Skills:** none required (per `research.md`; no framework-specific skill applies to a static-config, file-placement task).

## Purpose

The repository has no automated prose linter. Writing style preferences (no em-dashes, no filler, no sycophancy, active voice, term consistency, and so on) live only in `~/.claude/CLAUDE.md` and reviewer memory, so they drift and go unenforced in PRs. This adds Vale.sh — a style linter for prose — wired to a GitHub Actions check and a local CLI workflow, using the rule set the user specified verbatim in `.ailly/prompts/vale.md`. This design adopts that spec exactly; it does not redesign or trim the rules.

## Prior Art

- `.ailly/prompts/vale.md` — the authoritative, user-specified rule spec (11 custom rules, `.vale.ini`, GitHub Actions workflow). Treated as ground truth for every file's exact content.
- `.github/workflows/nightly-release.yml` — the repo's one existing workflow; establishes that `.github/workflows/` already exists and holds a single file today.
- `DEVELOPMENT.md` — the existing home for contributor-facing local-tooling instructions (commit conventions, evals, releasing); the natural place for "install and run vale locally," not `README.md` (confirmed in `research.md`).
- No existing prose-linting or YAML-parsing infrastructure exists anywhere in this repo's tooling: `PyYAML` and `pytest` are both absent from the system Python and from `.github/scripts/.venv`; every existing static checker in `e2e/run_static_evals.py` and each plugin's `ci.sh` hand-parses a restricted YAML subset instead of depending on a parser library. This design follows that same precedent rather than introducing a new dependency.

## User Journey and Metrics

A contributor edits a markdown file, then:

1. **Locally:** installs Vale once (`brew install vale`, or a downloaded binary), runs `vale sync` once to pull the `Google` and `Joblint` base styles, then runs `vale <file-or-glob>` before pushing. Vale prints file:line:col findings tagged `error` / `warning` / `suggestion` per `DEVELOPMENT.md`'s new section.
2. **In CI:** every push and pull request runs `.github/workflows/vale.yml`, which lints `README.md` and every markdown file, posting inline PR review comments (via `errata-ai/vale-action`'s `reviewdog` reporter). Only `error`-level findings fail the workflow; `warning` and `suggestion` are visible but non-blocking (`fail_on_error: false`).

**Metrics:** presence of the config, rule files, and workflow (structural, checked by the feature test below); no runtime metric is collected since Vale is a lint gate, not a service. Success is "the check exists and runs," not a numeric threshold — retrofitting existing prose to pass is explicitly out of scope (per `research.md`).

## Specification

All file content below is copied **verbatim** from `.ailly/prompts/vale.md` except where this section calls out a deviation explicitly.

1. **`.vale.ini`** (repo root) — copied verbatim, including its two `[*.md]` blocks (Vale merges repeated glob sections; this is normal Vale usage, not a defect), **except** the `Rules =` line — see **Open Artifact Decisions** below for the one change made to it.
2. **`styles/DDD/*.yml`** — 11 files, each copied verbatim from its spec block:
   `EmDashes.yml`, `Parentheticals.yml`, `Filler.yml`, `Sycophancy.yml`, `PassiveVoice.yml`, `Nominalizations.yml`, `Consistency.yml`, `TechnicalClarity.yml`, `SentenceLength.yml`, `WordChoice.yml`, `Redundancy.yml`.
   - **Caveat (adopted as-is, not redesigned):** `Parentheticals.yml` contains **two** YAML documents (`Parentheticals` then `LongParenthetical`, separated by a `---` document marker), because the spec gives both rule bodies but only one `File:` label. This is unusual for Vale, which conventionally expects one rule per file — if `vale sync`/Vale itself only reads the first document from a multi-document rule file, `LongParenthetical` may silently not run. Flagging this now per the "adopt exactly" instruction; splitting it into its own file is a follow-up if Vale rejects it, not a change to make now.
   - Vale addresses a custom rule as `<StyleName>.<Filename-without-extension>`, **not** by the YAML file's internal `name:` field. This is why the spec's own Rules= line already uses `DDD.Consistency` (file `Consistency.yml`, internal `name: TermConsistency`) and `DDD.TechnicalClarity` (file `TechnicalClarity.yml`, internal `name: TechnicalJargon`) rather than the internal names. The same convention applies to the three rules missing from Rules= (see Open Artifact Decisions): the file `Redundancy.yml` (internal `name: RedundantPhrases`) is addressed as `DDD.Redundancy`, not `DDD.RedundantPhrases`.
3. **`.github/workflows/vale.yml`** — copied verbatim: triggers on `[push, pull_request]`, checks out, runs `errata-ai/vale-action@reviewdog` against `README.md,**/*.md` with `fail_on_error: false` and `reporter: github-pr-review`.
4. **`DEVELOPMENT.md`** — append a new `## Prose Linting (Vale)` section (not `README.md`; contributor tooling docs already live in `DEVELOPMENT.md`) covering:
   - Install: `brew install vale` (macOS) or download a binary from the Vale releases page.
   - Sync base styles once (and after `.vale.ini` changes): `vale sync`.
   - Run locally: `vale README.md`, or `vale **/*.md` for the whole repo (shell-glob caveat: enable `globstar` or pass an explicit file list).
   - Severity meaning, copied from the spec's Notes section: `error` blocks merge-worthy judgment, `warning` should be fixed, `suggestion` is optional; `<!-- vale off -->` / `<!-- vale on -->` suspends checks locally for sentences that need an exception.

## Alternatives

- **Trim to only the 8 rules named in the spec's literal Rules= line, and don't create the other 3 rule files.** Rejected: the spec fully defines all 11 rules and discusses them together in the Notes section (severity levels reference nominalization and sentence length as active checks); shipping only 8 would silently drop rules the user's spec clearly intends to run, not "adopt exactly."
- **Split `Parentheticals.yml` into two files now** (`Parentheticals.yml` + `LongParenthetical.yml`) to sidestep the multi-document risk. Rejected for this pass: the user asked to adopt the spec exactly, and the spec's own structure (one `File:` label covering both blocks) reads as one file. Recorded as a caveat instead, resolvable later if Vale can't load it.
- **Off-the-shelf alternative to Vale itself:** none considered — Vale is the explicitly named, non-negotiable tool.

## Summary

Adds four artifact groups — `.vale.ini`, 11 rule files under `styles/DDD/`, a GitHub Actions workflow, and a `DEVELOPMENT.md` section — with every rule body copied verbatim from `.ailly/prompts/vale.md`. The one substantive judgment call is closing the gap between the spec's 11 defined rule files and its 8-name `Rules=` line; see below. No existing repository prose is retrofitted to pass; that is explicitly deferred.

### Open Artifact Decisions

**`.vale.ini` `Rules =` line:** the spec's `Rules =` line names only 8 of the 11 rule files it fully defines, omitting `DDD.SentenceLength`, `DDD.WordChoice`, and the rule in `Redundancy.yml`. Options: (a) copy the line exactly as given (8 names; the 3 remaining files exist on disk but never run), or (b) add the missing 3 to the line so all 11 defined rules are active.
Proposed: **(b)** — add all 11, using filename-derived IDs consistent with Vale's addressing convention already implicit in the other 8 entries: `DDD.EmDashes, DDD.Parentheticals, DDD.Filler, DDD.Sycophancy, DDD.PassiveVoice, DDD.Nominalizations, DDD.Consistency, DDD.TechnicalClarity, DDD.SentenceLength, DDD.WordChoice, DDD.Redundancy`. The spec's own Notes section discusses these three as active severity-tagged checks, and a rule file that never runs serves no purpose; this reads as an omission in the source spec, not an intentional exclusion. Confirm before clearing the draft.

**Feature test location:** no existing convention in this repo covers a generic (non-Ailly-skill) infrastructure feature test. `e2e/` (root and per-plugin) is explicitly scoped to Ailly's own skill/markdown contract checks (`e2e/README.md`); `.github/scripts/tests/` is scoped to `release.py`; `developer/tests/*.py` checks developer-plugin skill contracts specifically, but is the closest structural match: a standalone script, no `pytest`, no third-party library, `main()` returning 0/1 with one reason line per failure (both `PyYAML` and `pytest` are confirmed absent from this environment).
Proposed: `developer/tests/test_vale_lint_setup.py`, following that exact existing pattern. Confirm this placement (versus, say, a new root-level `tests/` directory) before clearing the draft.

## The Feature Test

**User story:** A contributor who has just cleared this draft opens the repository and expects to find every artifact this design promises — the Vale config, all 11 rule files (each syntactically sound YAML), the CI workflow, and the local-usage docs — all in place, so that installing Vale and running `vale sync` immediately works. Today none of these exist, so this fails.

**Test path:** `/Users/davidsouther/devel/davidsouther/domain-driven-design/developer/tests/test_vale_lint_setup.py`

**Runs today:** `python3 developer/tests/test_vale_lint_setup.py` (no `vale` binary, no `PyYAML`, no `pytest` required — matches this repo's existing `developer/tests/*.py` convention).

**Asserts:**
- `.vale.ini` exists at repo root and contains `StylesPath = styles`, `Vocab = DDD`, `BasedOnStyles = Google, Joblint`, and a `Rules =` line naming all 11 `DDD.*` rule IDs (per the Open Artifact Decision above).
- Each of the 11 `styles/DDD/*.yml` files exists and passes a hand-rolled structural YAML sanity check (no third-party parser available in this repo's toolchain, matching the precedent in `e2e/run_static_evals.py`): starts with a `---` document marker, uses no tab characters, and contains non-empty `name:`, `description:`, `message:`, `link:`, `level:`, and `scope:` keys. `Parentheticals.yml` is asserted to contain **two** `---`-separated documents, with `name: Parentheticals` in the first and `name: LongParenthetical` in the second.
- `.github/workflows/vale.yml` exists and contains `errata-ai/vale-action@reviewdog`, `fail_on_error: false`, and `reporter: github-pr-review`.
- `DEVELOPMENT.md` contains a section mentioning `vale sync` and `brew install vale` (or equivalent local-install instruction).

It currently fails (red) because none of these files exist yet.
