# Spike: Markdown formatter comparison on one real file

Supporting artifact for `research.md`.
Not a phase deliverable, not gated by the draft marker.
Raw outputs for every arm below are saved alongside this file under `spike/`.

## File chosen

`developer/skills/ailly/SKILL.md` (265 lines).
Chosen over a plainer candidate because it stresses every structural edge case the research flagged, in one file:

- YAML frontmatter with a 951-character single-line `description` value
  (the single longest line in the file).
- A `dot`-language fenced code block (66 lines) that must survive verbatim.
- Two Markdown tables.
- Ordered and unordered lists, including multi-sentence bullets and a
  7-item numbered list with long items.
- Two blockquotes containing multi-sentence, user-facing dialogue strings.
- Bolded run-in labels (`**Model check.** Detect the running model...`) —
  the exact "abbreviation-adjacent" pattern the research called out as
  unsolved by any tool's sentence-boundary detection.
- An 11-sentence single-line paragraph (`## Next task`, the "when calling
  run" paragraph) and several other 2-8 sentence lines.

## Tools run

All installed fresh, isolated from the system Python/Node:

| Tool | Install | Version |
|---|---|---|
| rumdl | `brew install rumdl` | 0.2.28 |
| flowmark | `pip install flowmark` into a scratch venv | 0.7.2-class (PyPI current) |
| mdformat | `pip install mdformat mdformat-gfm mdformat-tables mdformat-frontmatter` into the same venv | 0.7.22 |
| Prettier | `npx prettier@3.9.4` | 3.9.4 |
| sembr-reformat (Claude skill) | not installed (hand-approximated, see below) | — |
| **sembr (standalone CLI)** | `uv tool install "sembr[mlx]"` | 0.4.2 |

**Correction to research.md:** flowmark is a Python (+ separate Rust port `flowmark-rs`) tool distributed via PyPI/`uv`, not an npm package as `research.md`'s Libraries & Skills section states.
`npm view flowmark` resolves to an unrelated squatted package.
No design decision changes because of this, but the install-path note needs fixing before this goes into a design doc.

**Second correction to research.md — "sembr" is two different projects, not one.**
`research.md`'s Libraries & Skills section only names `sembr/skills` (`sembr-reformat`, the LLM-judgment Claude Code skill, MIT, 4 stars, 3 commits).
There is a second, separate implementation of the same sembr.org spec: **`admk/sembr`** (PyPI package `sembr`), a standalone, scriptable CLI backed by a small fine-tuned BERT model (`admko/sembr2023-bert-small-nvfp4`), no LLM/agent required.
It runs fully offline after the first model download and needs no marketplace install.
This is a materially different candidate from what research.md evaluated and should be added to the design phase's options, evaluated on its own — see results below, which are not favorable.

**sembr-reformat (the skill) was not installed.**
Installing it means running `/plugin marketplace add sembr/skills`, a global, persistent change to the user's Claude Code environment for a 4-star, 3-commit project — too much for a spike whose only goal is a same-file comparison.
Instead, I hand-applied the published SemBr rule (sentence breaks mandatory, independent-clause breaks at comma/semicolon/colon/dash recommended, dependent-clause breaks optional for clarity) to the same file, using my own judgment the way the real skill would ask an LLM to.
Word-level diff against the original confirms zero content drift (only the necessarily repeated `>` blockquote markers differ).
Treat `07-sembr-simulated.md` as an approximation of the *skill's* behavior, not the skill itself.

**sembr (the standalone CLI) was installed and run for real** — `sembr -i original.md -o sembr-real.md --file-type markdown`.
First run downloaded a 434 MB model cache to `~/.cache/huggingface`; inference on this 265-line file took about 2 seconds, fully local, no API key.
Both the model download and the `uv tool install` are easy to undo (`uv tool uninstall sembr`, `rm -rf ~/.cache/huggingface`) if not wanted kept.

## Results at a glance

| Output | Lines | Longest line | Frontmatter | Tables | Code fence | Blockquote wrap |
|---|---|---|---|---|---|---|
| Original | 265 | 951 | — | one-block-per-row | untouched | one-block-per-line |
| rumdl (`sentence-per-line`) | 369 | 951 | untouched | untouched | untouched | sentence-per-line |
| flowmark `-s` (semantic) | 437 | 951 | untouched | separator normalized only | untouched | sentence-per-line, width-wrapped |
| flowmark default (width 88) | 412 | 951 | untouched | separator normalized only | untouched | width-wrapped |
| mdformat (`keep`, no plugin) | 264 | 966 | **corrupted** | column-aligned | untouched | untouched |
| mdformat (`keep`, +frontmatter plugin) | 264 | 966 | untouched | column-aligned | untouched | untouched |
| mdformat `--wrap 80` | 426 | 966 | untouched (w/ plugin) | column-aligned | untouched | hard-wrapped, ignores sentences |
| Prettier `--prose-wrap always` | 440 | 175 | rewrapped (valid YAML, verified) | column-aligned | untouched | hard-wrapped, ignores sentences |
| sembr (standalone CLI) | 577 | 951 | untouched | untouched | untouched | **corrupted text + broken spans** |

All nine preserved the `dot` code fence byte-for-byte (checked by hash).
That much every candidate gets right.

## Findings worth carrying into design

**mdformat corrupts YAML frontmatter without `mdformat-frontmatter`.**
Without the plugin, `---\nname: ailly\ndescription: "..."\n---` gets parsed as CommonMark: the `---` becomes a thematic break (`___...`) and `name: ailly description: "..."` becomes an `## ` heading.
Every `SKILL.md` in this repo depends on that frontmatter being intact YAML for the harness to read `name`/`description`.
This is a **repo-breaking default**, not a style nit — if mdformat is adopted, the frontmatter plugin and `mdformat_config` for it are non-negotiable, and this needs a regression check.

**Prettier's frontmatter handling is safe but noisy.**
It re-wraps the YAML double-quoted `description` scalar across multiple folded lines.
Verified via `pyyaml` that the parsed value is byte-identical to the original — YAML line-folding is lossless here.
But it means every edit to `description`'s wording reflows the entire frontmatter block, adding frontmatter churn to every diff touching a `SKILL.md`, on top of whatever body-wrap churn the OSPL choice already produces.

**None of the five candidates fix this file's actual worst line.**
The 951-character line the census in `research.md` would have flagged as the extreme outlier lives in YAML frontmatter, not the Markdown body.
Every tool here (rumdl, flowmark, mdformat, Prettier, and my sembr approximation) only reflows Markdown prose; none touch YAML scalar values.
If frontmatter readability is a real motivation, this feature's scope needs a second, YAML-specific answer (e.g. converting `description` to a folded/literal block scalar) — Markdown formatting choice alone doesn't reach it.
Worth a line in design.md's Scope section.

**Tight lists survive OSPL splitting in every sentence-aware tool.**
Research flagged a risk that splitting a multi-sentence bullet across lines could flip CommonMark from tight to loose list rendering.
In practice, both rumdl and flowmark used a 2-3 space hanging indent under the bullet marker for continuation sentences, not a blank line, so every multi-sentence bullet in this file stayed tight in every candidate's output, including my sembr approximation.
This risk is real in the abstract (per `rumdl` issue #111's neighborhood of unresolved edge cases) but did not reproduce on this file with any of the four tools' default behavior.

**rumdl and flowmark disagree on run-in bold labels — a real quality difference, not a bug.**
For `**Model check.** Detect the running model...`, rumdl's `sentence-per-line` splits mechanically on every `. `, giving `**Model check.**` its own line:

```
- **Model check.**
  Detect the running model and compare it to the model the guidance recommends...
```

flowmark's semantic mode keeps the bold label attached to the sentence it introduces:

```
- **Model check.** Detect the running model and compare it to the model the guidance
  recommends for the dispatch about to happen.
```

My sembr approximation made the same call as flowmark, by judgment.
This is the exact "abbreviation/label" boundary problem research.md named as unsolved — confirmed here as a live, visible quality difference between the two front-runner tools, not just a hypothetical.
If OSPL is chosen, this is a legitimate tie-breaker in flowmark's favor for a repo this dense with `**Label.** Explanation.` prose, unless rumdl's abbreviation list (mentioned in research.md) can be configured to cover it — untested in this spike.

**Hard-wrap tools (mdformat `--wrap N`, Prettier `always`) ignore sentence boundaries entirely inside blockquotes**, breaking mid-sentence:

```
> "This step is complete. Review `<path>`, make any changes, then remove the
> `*Draft YYYY-MM-DD*` marker from the top of the file. Intent review is at
> `<intent-review-path>`. Start a new session and run `developer:ailly` to
> continue."
```

versus rumdl/flowmark/sembr's one-sentence-per-quoted-line.
For user-facing dialogue strings like this file's draft-gate messages, that is a real readability regression from the "keep sentences visually distinct for future edits" motivation behind OSPL in the first place — another point against the hard-wrap-at-N option specifically for this repo's prose style.

**The standalone `sembr` CLI actively corrupts this file — it is not a viable candidate as run.**
Testing the real tool (not an approximation) surfaced defects well past a style disagreement:

- **Word-joining data loss.**
  The blockquote `"This step is complete.` came out as `"Thisstepis complete.` — three words fused with no spaces.
  This is not a line-break placement choice, it is lost content.
- **Broken inline spans.**
  The model breaks by token-count (`preferred_min/max_tokens_per_line: 8/10`) with no awareness of Markdown inline syntax, splitting bold and code spans across the line break it inserts.
  Counting lines with an odd number of backticks (a split code span) found 96 such lines in this 577-line output — for example ``` `/ailly design ...\n    ` ``` and
  ``` `developer/skills/ailly/references/phases/<phase>.\n    md` ```.
  One bold span breaks as `**\n    red-green-refactor**`, and another as `circumstances.\n** If the user asks`, leaving an unbalanced `**` that would open unintended bold formatting for the rest of the paragraph.
- **Dropped blank lines around blockquotes.**
  The blank line the original has between "tell the user:" and its blockquote is gone in the output; the same happens after the blockquote before the next paragraph.
  Given CommonMark's lazy-continuation rule for block quotes, at least one of these (the `**Do not proceed...**` paragraph immediately following a quote with no blank line) risks being parsed as part of the blockquote rather than as its own paragraph — unverified by rendering, but a real risk this spike surfaced, not a hypothetical one.
- Indentation of continuation lines is inconsistent (4 or 8 spaces,
  driven by wherever the model chose to break) rather than tied to list
  or quote structure, unlike rumdl/flowmark's clean hanging indents.

Full output at `spike/08-sembr-real-cli.md`.
Given this, the standalone `sembr` CLI should be considered **disqualified for this repo as tested**, not "immature but promising" — content corruption and broken inline Markdown are correctness bugs, not style preferences.
It's possible a non-default config (`preferred_min/max_tokens_per_line`, a different `predict_func`) does better; untested here, and the fundamental token-count-driven, syntax-unaware breaking strategy makes it unlikely to close the gap with rumdl/flowmark's parser-based approach regardless of tuning.

**On the run-in label question — the real fix may not be a tool choice at all.**
rumdl's, flowmark's, and the standalone `sembr`'s disagreement over where `**Model check.** Detect...` breaks stems from the source prose putting a bold label and its first sentence in the same breath, with only a shared period marking two different things (end of label, end of nothing since the label isn't a sentence).
If that pattern in the source were rewritten to drop the ambiguity — a colon (`**Model check:** Detect...`) or an em dash instead of a period — every tool's sentence-boundary detector would agree, because there would no longer be a real sentence boundary to disagree about.
Worth carrying into design as a possible prose-style convention alongside the wrap-tool choice, not just a tool-selection tie-breaker.

**Table reformatting is a diff-noise axis independent of the wrap decision.**
rumdl left both tables byte-identical to the original. flowmark normalized only the separator row (`|---|---|` → `| --- | --- |`) without touching cell padding. mdformat and Prettier both column-align every cell to the widest entry, meaning a single-cell edit anywhere in a table reflows every row.
This is orthogonal to the OSPL-vs-hard-wrap question and worth its own line item in design.md's Scope: whether table reformatting is wanted at all, independent of which prose-wrap tool wins.

## Not resolved by this spike

This was a same-file, default-config comparison, not a full evaluation.
It does not resolve:

- rumdl's abbreviation-list config, which might close the bold-label gap
  above — untested.
- flowmark's `--list-spacing`, `--cleanups`, `--smartquotes` options —
  untested, none needed for this file.
- Behavior on the ~200 already-unwrapped files at repo scale (this is one
  file).
- The real `sembr-reformat` *skill's* actual output, idempotency, or
  check-mode — only my own approximation of its stated rule was tested
  (the standalone `sembr` *CLI* tested above is a different project).
- Non-default `sembr` CLI config (token-length bounds, `predict_func`)
  that might reduce the span-breaking and blank-line defects — untested,
  and unlikely to fully close the gap given the tool's fundamentally
  syntax-unaware, token-count-driven breaking strategy.

## Raw outputs

All nine files under `spike/`, plus the `.rumdl.toml` config used:

- `spike/00-original.md`
- `spike/01-rumdl-sentence-per-line.md`
- `spike/02-flowmark-semantic.md`
- `spike/03-flowmark-default-wrap88.md`
- `spike/04-mdformat-keep-with-frontmatter-plugin.md`
- `spike/05-mdformat-wrap80.md`
- `spike/06-prettier-prosewrap-always.md`
- `spike/07-sembr-simulated.md` (hand-approximation of the `sembr-reformat` skill)
- `spike/08-sembr-real-cli.md` (real output from the standalone `sembr` CLI)
- `spike/rumdl-config-used.toml`
