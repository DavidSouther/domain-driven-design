# Markdown formatter for consistent prose wrapping

## Topic and Intent

As part of the ongoing Vale documentation-linting work, add a formatter for consistent Markdown.
The repo currently mixes two conventions: one line/paragraph per block, and hard-wrapped lines around an 80-character width.
The user's framing floats a third, better target: One Sentence Per Line (OSPL), per the
[Asciidoctor recommended-practices page](https://asciidoctor.org/docs/asciidoc-recommended-practices/).

## Search/Expand

Full findings: `docs/research/2026-07-07-A-vale-markdown-format/codebase.md` and `docs/research/2026-07-07-A-vale-markdown-format/public.md`.

**Current state is genuinely mixed, and the split tracks document kind, not randomness.**
A census of all 312 `.md` files found 188 effectively unwrapped (one block per line, some lines over 600 characters) versus 95 soft-wrapped (60-100 chars) versus 29 short/structural files.
Every `SKILL.md` in the repo (19 checked), plus `README.md`, `DEVELOPMENT.md`, `AGENTS.md`, and `RELEASING.md`, are one-block-per-line.
By contrast, e2e prompt/fixture Markdown is hand-wrapped near 80 chars, and session work-products under `.ailly/developer/<session>/*.md` wrap near 86-96 chars.
`TASKS.md` contains both conventions in a single file, depending on which session appended each entry.

**No formatter tooling exists today.**
No `.prettierrc*`, `.editorconfig`, `.markdownlint*`, `.remarkrc*`, and no `package.json`/lockfile anywhere in the repo.
This is not a Node project.
`.vale.ini` and `styles/Ailly/*.yml` lint prose style only; no existing rule checks line width.
`SentenceLength.yml` and `SentenceWords.yml` scope to sentences, not physical lines, so they would not fire on or interact with a wrap formatter either way.
`.github/workflows/vale.yml` is the only CI step touching `.md` files, and it lints prose, not formatting.

**`scripts/vale-check.sh` / `scripts/vale-fix.sh` are the shape to follow.**
`vale-check.sh` is a pure lint pass (`find` + `xargs vale`).
`vale-fix.sh` is the fix half: it dedupes findings per file, looks up a worked example (auto-derived from the rule, then a hand-authored sidecar), and dispatches `claude -p --model haiku --allowedTools Read/Edit` per flagged file via `xargs -P 8`, with a `VALE_FIX_DRY_RUN=1` escape hatch for its own feature test.
A new Markdown-formatter script pair can follow the same check/fix split, same `REPO_ROOT`-relative invocation, and the same `.ailly`/`e2e` exclusions.

**OSPL is a source-only convention** (invisible in rendered output), whose core mechanic (a single newline is a soft break; a blank line starts a new block) transfers cleanly from AsciiDoc to CommonMark Markdown.
Markdown adds real wrinkles the AsciiDoc page does not address: blank lines between list items flip CommonMark from "tight" to "loose" list rendering, trailing whitespace or a trailing backslash can accidentally inject a rendered `<br>`, and some renderers (GitHub/Bitbucket comment boxes) are linebreak-sensitive.
Practitioner debate is genuinely split (a 2022 CPython core-dev discussion on OSPL for PEPs settled on "SHOULD," not "MUST") and, tellingly, no debate found engaged the sentence-boundary-detection problem at all.

**No mainstream general-purpose formatter implements OSPL.**
Prettier's `proseWrap` and `mdformat`'s `--wrap` only do fixed-width hard-wrap, no-wrap, or preserve; a 2018 Prettier feature request for OSPL went unmerged.
`remark-stringify` has no wrap option; its community word-wrap plugin is archived in favor of Prettier.
Two younger, lower-adoption tools implement true sentence-aware rewrapping with check-and-fix modes: **rumdl** (Rust; MD013 `reflow-mode = "sentence-per-line"` or `"semantic-line-breaks"`, with a built-in abbreviation list and a capitalization guard) and **flowmark** (semantic sentence-based wrapping via `--check`/`--inplace`, with a self-described "not perfect" regex splitter).
Neither, nor any tool surveyed, claims to fully solve sentence-boundary detection around abbreviations, decimals, or inline code.
Vale itself has no line-wrap or general autofix concept at all (no `vale --fix`; open issue errata-ai/vale#939).

**A confirmed, open, unresolved edge case in the front-runner tool.**
`rumdl` issue #111 asks how `sentence-per-line` reflow interacts with a configured `line-length` cap when a single sentence exceeds it.
The issue is open with no maintainer resolution.
This directly reproduces the tension in the user's own framing (OSPL versus an 80-char ceiling): the two are not simply composable, and a design choosing OSPL should pick a generous or disabled `line-length` for prose rather than assume the tool resolves the conflict.

## Libraries & Skills

*Before doing any work in this feature, load these skills via the Skill tool if either candidate below is chosen: none exist for Prettier/mdformat (mainstream, well-documented; no dedicated skill needed).*
*If `sembr/skills` is chosen, load its `sembr-reformat` skill per its own install instructions before implementing.*

- **rumdl** (`rvben/rumdl`, <https://rumdl.dev/md013/>) — Rust Markdown linter/formatter, markdownlint-compatible.
  Zero runtime dependencies: installable via `brew install rumdl`, `cargo install rumdl`, or a standalone binary, matching this repo's existing `brew install vale` pattern in `DEVELOPMENT.md`.
  Config lives in `.rumdl.toml`.
  Getting started: `rumdl check .` (lint) and `rumdl check --fix .` / `rumdl fmt .` (rewrite).
  Ships an official GitHub Action (`rvben/rumdl@v0`), directly parallel to this repo's existing `errata-ai/vale-action@reviewdog` step in `.github/workflows/vale.yml`.
  No published Claude Code skill; it is a conventional CLI tool.
  **Chosen** — see Resolved Decisions and the spike comparison at `spike.md`.
- **flowmark** (`jlevy/flowmark`, <https://github.com/jlevy/flowmark>) — **Correction:** distributed via PyPI/`uv` (`pip install flowmark` or `uv tool install flowmark`), plus a separate Rust port `flowmark-rs`, not an npm package as originally recorded here.
  `--check`/`--inplace`/ `--auto` modes, semantic (sentence-based) wrapping.
  No published Claude Code skill.
  Close runner-up in the spike comparison.
- **"sembr" is two separate projects implementing the same
  <https://sembr.org/> spec, not one:**
  - `sembr/skills` (<https://github.com/sembr/skills>) — the `sembr-reformat` Anthropic Agent Skill, which asks an LLM to apply semantic line breaks by judgment.
    Install via `/plugin marketplace add sembr/skills` in Claude Code.
    MIT-licensed, 4 stars, 3 commits.
    Not installed for the spike (a global, marketplace-sourced install was judged too heavy for a same-file comparison); a hand-applied approximation of its stated rule was used instead and produced output competitive with rumdl.
  - `admk/sembr` (PyPI package `sembr`, `uv tool install "sembr[mlx]"`) — a standalone, scriptable CLI backed by a small fine-tuned BERT model, no LLM required.
    Installed and run for real in the spike.
    **Disqualified**: it corrupted prose text (dropped spaces, e.g. "This step is complete" → "Thisstepis complete") and broke Markdown inline syntax by splitting bold and code spans mid-token (96 of 577 output lines had an unbalanced backtick count), plus dropped blank lines around blockquotes in a way that risks CommonMark's lazy-continuation rule swallowing adjacent paragraphs.
    These are correctness bugs, not style disagreements — this tool is not a viable candidate as tested.
- **Prettier** / **mdformat** — only relevant if the design phase resolves the target convention to hard-wrap-at-N or no-wrap rather than OSPL.
  Both are mainstream, mature, and would need no dedicated skill, but would also introduce a Node (Prettier) or Python (mdformat) toolchain into a repo that currently has neither.

## Falsification/Refine

- **Size: a single feature**, not a project and not a bug.
  One bounded capability (consistent, enforced Markdown prose-wrapping) delivered as a config file plus a check/fix script pair plus a CI step, following the `vale-check.sh`/`vale-fix.sh` shape already in the repo.
- **Off-the-shelf fits.**
  No bespoke sentence-splitter is justified: every tool surveyed converges on the same unsolved boundary-detection problem (abbreviations, decimals, inline code), and a bespoke tool would re-solve it with less scrutiny than `rumdl`/`flowmark`/`sembr-reformat` have already applied.
  Vale is orthogonal either way; it has no wrap concept to extend.
- **Verified, not assumed: no live merge conflict.**
  The sibling session `2026-07-06-C-vale-term-dictionary`'s `summary.md` records that its new `styles/Ailly/*.yml` files were blocked by an uncommitted, in-progress edit to `.vale.ini` at the time that session ran.
  `git diff -- .vale.ini` today shows no uncommitted changes, and the current `styles/Ailly/` directory (`EmDash`, `LongParenthetical`, `Parentheticals`, `PassiveVoice`, `Readability`, `RepeatedWords`, `SentenceLength`, `SentenceWords`, `Using`, `WordChoice`) matches `.vale.ini`'s `Packages = Ailly` / `BasedOnStyles = Ailly` exactly.
  That session's pending edit was resolved (most likely folded into the later "Vale pass with Ailly rules" / "Consolidated several disparate and mediocre styles" commits).
  There is no coordination conflict for this feature to worry about.
- **A framing correction worth carrying into design:** "one block per line" (the current convention for `SKILL.md`/root docs) and OSPL are not as opposed as they first look.
  Both exist for the same reason — clean, reviewable diffs.
  They diverge only when a block contains more than one sentence: one-block-per-line keeps multiple sentences on one line, OSPL splits them.
  Framing OSPL as "finishing what one-block-per-line already started" (rather than "replacing it") may change how disruptive design judges the reformat of ~200 already-unwrapped durable-reference files to be.
- **Smallest version:** pick one target convention, add one config file, one check/fix script pair (or two new subcommands folded into the existing `vale-*.sh` scripts), one CI step mirroring `vale.yml`, and one fix pass across the repo to normalize existing files.
  Whether that normalization pass belongs in this feature's own diff or should follow as a separate, later "run the formatter once" step is a genuine open question below, not resolved here.
- **No related follow-ups found.** `TASKS.md` and both sibling in-progress
  session folders were read in full; none mention Markdown formatting,
  line width, `prettier`, or `markdownlint`.

## Scope

**In scope for design:**

- ~~Choosing the target wrap convention~~ — **resolved: OSPL**, see
  Resolved Decisions.
- ~~Choosing the tool~~ — **resolved: `rumdl`**, see Resolved Decisions
  and `spike.md`.
- A check script and a fix script, following `vale-check.sh`/
  `vale-fix.sh`'s shape and exclusions.
- A CI step parallel to `.github/workflows/vale.yml`.
- ~~Whether `SKILL.md` files, root docs..., e2e prompt/fixture Markdown,
  and `.ailly/developer/**` session artifacts are all in scope~~ —
  **resolved: no exemptions, all convert**, see Resolved Decisions.
- The repo-wide reformat pass (all ~312 files, resolved to ship now as an
  isolated commit) still needs its own plan step, separate from the
  tool/config/CI-step work.

**Out of scope for this feature (deferred, not decided against):**

- Building a bespoke sentence-boundary splitter.
  Existing tooling covers this need.
- Extending Vale itself to do formatting; it has no such capability and
  none is being requested of it.
- The unrelated deferred Vale follow-ups already logged in `TASKS.md` (`vale-generate-examples.sh`, surfacing worked examples in `vale-check.sh`'s human output).
  Untouched by this topic.

## Resolved Decisions

**Resolved by this research:**

- An off-the-shelf tool should back this feature; no bespoke formatter is
  justified.
- The feature is correctly sized as a single feature, not a project or a
  bug.
- There is no live conflict with the sibling `vale-term-dictionary`
  session; `.vale.ini` is clean.
- If OSPL is the chosen convention, the design must explicitly set
  `line-length` generously (or disable it for prose) rather than assume
  the tool composes OSPL with an 80-char ceiling automatically — `rumdl`
  issue #111 shows that composition is unresolved upstream.
- **Tool: `rumdl`.**
  Decided against flowmark, `sembr-reformat`, standalone `sembr`, Prettier, and mdformat after running all of them (or a faithful approximation, for the LLM-judgment skill) against the same real file — see `spike.md` for the full comparison and raw outputs under `spike/`.
  Deciding factors: rumdl left tables, code fences, and frontmatter byte-identical to the source (mechanical, predictable diffs); the standalone `sembr` CLI corrupted prose text and broke Markdown inline syntax (disqualifying); mdformat corrupts YAML frontmatter without an extra plugin and both mdformat and Prettier hard-wrap mid-sentence inside blockquotes regardless of the wrap convention chosen. flowmark was the closest competitor (its semantic mode handles bold run-in labels — `**Model check.** Detect...` — more gracefully than rumdl's mechanical split) but rumdl's zero-dependency `brew install` matches this repo's existing `vale` install pattern most directly.
  The bold-run-in-label disagreement between the two may be better solved by a prose-style convention (e.g. a colon instead of a period after the label) than by tool choice — see `spike.md`.

- **Convention: OSPL.**
  Chosen over hard-wrap-at-N and over standardizing the existing one-block-per-line convention as-is.
- **Scope: reformat now, isolated commit.**
  The initial feature's diff ships the tool, the config, and a full repo-wide reformat pass of all ~312 existing Markdown files, landed as its own commit separate from the tool/config/CI-step commit(s) — not deferred as a follow-up task.
- **No exemptions.**
  `SKILL.md` files (all 19), the four root docs (`README.md`, `DEVELOPMENT.md`, `AGENTS.md`, `RELEASING.md`), e2e prompt/fixture Markdown, and `.ailly/developer/**` session artifacts all convert to OSPL and are enforced by rumdl going forward — no `--exclude` carve-out.
  This includes the files the harness loads directly into agent context at runtime (`SKILL.md`), not only human-read docs.

**Open for the human before design:**

*(none remaining — all decisions above were made in the same research session; see conversation history for the reasoning behind each.)*

## Sources

See per-skill notes for full IEEE-style citations:

- `docs/research/2026-07-07-A-vale-markdown-format/codebase.md`
- `docs/research/2026-07-07-A-vale-markdown-format/public.md`
- `spike.md` — hands-on tool comparison on a real file, resolving the
  tool-choice question above; raw outputs under `spike/`.

Additional direct fetches performed during the library docs review pass (not delegated to a subagent):

- [1] "MD013 — Keep lines short for better readability," rumdl
  documentation, <https://rumdl.dev/md013/> — fetched directly for the
  exact `reflow-mode` config schema (`default`, `normalize`,
  `sentence-per-line`, `semantic-line-breaks`) and `length-mode`,
  `abbreviations`, `require-sentence-capital` keys.
- [2] "How does reflow sentence_per_line interact with line length?"
  rvben/rumdl issue #111, <https://github.com/rvben/rumdl/issues/111> — fetched directly; confirmed open/unresolved as of 2026-07-07.
- [3] "rumdl," rvben/rumdl, <https://github.com/rvben/rumdl> — fetched
  directly for install paths (`brew`, `cargo`, binary, winget, Docker),
  `rumdl check`/`rumdl fmt` CLI shape, and GitHub Action availability.
- [4] "Semantic Line Breaks (SemBr)," <https://sembr.org/> — fetched
  directly for the "SemBr Agent Skills" mention and install command.
- [5] "skills," sembr/skills, <https://github.com/sembr/skills> — fetched
  directly for the `sembr-reformat` skill's install paths, license (MIT),
  and maturity signals (4 stars, 3 commits).
