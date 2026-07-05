# Adopt Vale.sh Prose Linter

## Topic and Intent

> "Adopt the following vale.sh rules, exactly. Quickloop the specific details for adding it to the repo, with github action integration and local execution instructions."

The user wants to integrate vale.sh (a prose style linter) into the domain-driven-design repository, following a fully-specified rule set already written at `.ailly/prompts/vale.md`. The integration should include: `.vale.ini` configuration, custom rule YAML files under `styles/DDD/`, a GitHub Actions workflow at `.github/workflows/vale.yml`, and local execution instructions added to the repository documentation.

## Search/Expand

Vale.sh is a style linter for prose written in Go, widely used in technical documentation. Key findings:

- **Getting Started**: Vale.sh requires installation (via Homebrew: `brew install vale` on macOS, or by downloading a binary from the GitHub release page).
- **Local Execution**: Running `vale sync` pulls built-in styles (Google, Joblint) from the Vale repository; custom styles are placed in `styles/DDD/`.
- **CI Integration**: Vale.sh integrates with GitHub Actions via the `errata-ai/vale-action` action, which supports reviewdog reporter for inline PR comments.
- **No existing linting infrastructure**: The repository currently has no prose linter configured, making this a net-new addition.

## Libraries & Skills

Vale.sh is the target tool; no published agentic skills exist for it in the local codebase. The task requires no framework-specific skills — it is a straightforward configuration and file-placement exercise.

**Before doing any work in this feature, load these skills via the active harness's skill-loading mechanism:** none apply.

## Falsification/Refine

**Task size:** Single feature (add prose linting to CI/local workflow).

**Off-the-shelf solution:** Vale.sh is the specified tool; the rule set is fully defined in `.ailly/prompts/vale.md`. No custom rule authoring or substantial design is needed.

**Smallest version:** The full spec provided in `.ailly/prompts/vale.md` is the smallest complete version. All 11 rule files, the `.vale.ini` config, GitHub Actions workflow, and local execution instructions are interdependent and cannot be reduced further without breaking the intent.

**Key constraints:**
- Adopt rules exactly as specified (no redesign).
- Vale CLI not currently available locally — users must install via Homebrew or binary download.
- `.github/workflows/` directory exists with one workflow (`nightly-release.yml`), so placement is straightforward.
- README.md and DEVELOPMENT.md have clear structure; local execution instructions can be appended to DEVELOPMENT.md.

## Scope

**In Scope:**
- Create `.vale.ini` in repository root with BasedOnStyles = Google, Joblint; StylesPath = styles; Vocab = DDD.
- Create 11 custom rule YAML files under `styles/DDD/`:
  - `EmDashes.yml`
  - `Parentheticals.yml`
  - `Filler.yml`
  - `Sycophancy.yml`
  - `PassiveVoice.yml`
  - `Nominalizations.yml`
  - `Consistency.yml`
  - `TechnicalClarity.yml`
  - `SentenceLength.yml`
  - `WordChoice.yml`
  - `Redundancy.yml`
- Create `.github/workflows/vale.yml` with errata-ai/vale-action, fail_on_error = false, reporter = github-pr-review.
- Add "local execution instructions" section to DEVELOPMENT.md (how to install vale, run locally, interpret results).

**Out of Scope:**
- Modifying rule definitions from the provided spec.
- Creating exception patterns beyond those mentioned in the spec (<!-- vale off --> / <!-- vale on -->).
- Retrofitting existing prose in the repository to pass the linter (that is a separate task).
- Integrating other prose linters (alex, proselint, prettier) at this time.

## Resolved Decisions

1. **Vale CLI availability:** Vale is not installed locally. Users must install via `brew install vale` (macOS) or download a binary. This will be documented in DEVELOPMENT.md's local execution section.
2. **GitHub Actions workflow placement:** Place at `.github/workflows/vale.yml`; directory exists and follows the same pattern as `nightly-release.yml`.
3. **Documentation placement:** Add local execution instructions to DEVELOPMENT.md under a new "Prose Linting" or "Local Tools" subsection.
4. **Rule file count:** 11 YAML files as specified, not fewer; all are essential for the intended coverage.

**Open questions for human review:**
- Should the `.vale.ini` suppress the Google and Joblint base styles for any file types (currently applies only to `*.md` files)?
- Should DEVELOPMENT.md also cross-reference the vale rules (e.g., link to the `styles/DDD/` directory) so writers understand the conventions?
- Is `fail_on_error: false` in the GitHub Actions workflow acceptable (warnings do not block merge, only errors do)?

## Sources

1. Vale.sh official repository: https://github.com/errata-ai/vale
2. Errata-ai vale-action GitHub Action: https://github.com/marketplace/actions/vale-lint
3. Vale documentation: https://vale.sh/docs/ (CLI, config format, rule authoring)
4. User specification: `.ailly/prompts/vale.md` (this session's task input)
