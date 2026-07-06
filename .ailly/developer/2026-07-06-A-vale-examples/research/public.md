# Public: Vale ecosystem — verifying the embedded transcript's claims and finding prior art for "examples in lint output"

## Findings

A prior assistant session (embedded verbatim in `.ailly/prompts/vale_examples`) proposed
building a `--examples` capability for Vale and made several factual claims about Vale's
mechanics and about seed sources. This pass verifies each against live sources and looks for
existing prior art. Most mechanics claims **hold**; the Red Hat seed-source claim is
**partly false**; and the "examples in output" feature is confirmed **not to exist** anywhere.

### Confirmed claims (Tier 1, official docs + empirical)

- **Org rename `errata-ai` → `vale-cli`.** Confirmed. The CLI now lives at
  `github.com/vale-cli/vale` (MIT), the action at `vale-cli/vale-action`, and a Vale LSP at
  `vale-cli/vale-ls`. Implication for this repo: `.github/workflows/vale.yml` still pins
  `errata-ai/vale-action@reviewdog` (the old org; GitHub redirects it, so it still runs).
  [1][2]
- **`--output=template` data shape.** Confirmed by docs and empirically (`vale 3.15.1`).
  The template receives a `Data` struct with `Files` (`[]ProcessedFile`) and `LintedTotal`;
  each `ProcessedFile` has `Path` and `Alerts` (`[]core.Alert`); `core.Alert` "has the same
  information as Vale's `--output=JSON` object" (`.Check`, `.Message`, `.Line`, `.Span`,
  `.Severity`, `.Link`, `.Action`, `.Match`). Templates use Sprig and live under
  `<StylesPath>/config/templates`. [3]
- **`substitution` `swap` field / `existence` `action` field.** Confirmed. `substitution`
  uses a `swap:` map of `bad: good` pairs (with `|` for alternatives); `existence` supports
  an `action:` block with `name` (`replace`/`edit`) and `params`. [4][5]
- **`vale sync` / `config/` non-clobber.** Confirmed. `vale sync` overwrites only the named
  package style folders under `StylesPath`; `config/` (vocabularies, dictionaries,
  templates) is preserved. Vale's own Packages docs ship the exact `.gitignore` the
  transcript quotes (ignore `StylesPath/*` except `config/`). So a sidecar under
  `styles/config/examples/` would survive re-sync. [6]

### Partly falsified claim: the Red Hat "reference guide" as an examples seed source

The transcript claims Red Hat's Vale rule reference guide "documents each rule with a
violation example and its resolution, rule by rule" and is "Apache/EPL-licensed." Both
specifics are wrong:

- **License is MIT**, not Apache/EPL. `redhat-documentation/vale-at-red-hat`'s `LICENSE`
  reads "MIT License, Copyright (c) 2021 Rolfe Dlugy-Hegwer." (MIT is still permissive and
  reusable, but differs from Apache/EPL on patent grant and NOTICE terms.) [7][8]
- **It is a Vale style *package*, not a worked-example guide.** The repo is `.yml` rule
  files + config + generated docs. Its auto-generated reference guide lists each rule's
  name, guideline/`message`, alert level, and reference links — but **no per-rule
  incorrect→corrected sentence pairs** and no inline swap tables. Harvesting it yields the
  same shape Vale rules already have (regex/term lists + a `message`), not curated bad→good
  prose. The actual worked prose lives in the *separate* Red Hat Supplementary Style Guide
  (different resource, separate licensing). [8][9][10]

  Net: Red Hat is **not** the low-effort "convert format" seed the transcript assumes.
  Seeding the hand-authored tier is closer to "write from scratch (informed by a style
  guide)" than "reformat an existing example set."

### Confirmed gap: no `--examples`, no examples database, no Vale skill

- **No `--examples` flag / examples feature exists in Vale.** Vale's CLI has `sync`,
  `ls-config`, `ls-metrics`, `ls-dirs`, `ls-vars` and flags `--config/--ext/--filter/--glob/
  --ignore-syntax/--no-exit/--no-wrap/--no-global/--output/--version` — nothing that prints
  a fix example keyed by rule. Vale's only fix affordances are single-token `substitution`
  actions and the per-rule `link` URL; it is explicitly not a formatter. No third-party
  plugin injects worked before/after examples either. The feature is genuinely net-new. [11]
- **A Vale MCP server exists, but it does not solve this.** `ChrisChinchilla/Vale-MCP`
  (MIT, TypeScript, current; successor to the archived `theletterf/vale-mcp-server`) exposes
  `vale_status`, `vale_sync`, `check_file`, `check_text` — it wraps `vale check` and returns
  severity-grouped markdown. It carries **no examples database** and is an MCP server, not
  the integration this task needs. [12][13]
- **No published Vale `SKILL.md` / Claude skill exists.** Neither the major skill
  directories (`VoltAgent/awesome-agent-skills`, `BehiSecc/awesome-claude-skills`) nor
  GitHub-scoped search surface one for the vale.sh prose linter. (Disambiguation: `agnix`
  lints SKILL.md/CLAUDE.md agent-config files with "156 rules" — an unrelated tool, not a
  Vale skill despite the name-overlap in searches.) Per the research-phase directive, record
  this omission explicitly: **there is no upstream Vale agentic skill for downstream phases
  to load.** [14][15]

## Sources

[1] "GitHub - vale-cli/vale," github.com/vale-cli/vale (MIT; org rename from errata-ai).
[2] "vale-cli/vale-action," github.com/vale-cli/vale-action (was errata-ai/vale-action).
[3] "Templates — Vale CLI," vale.sh/docs/templates (Data.Files/LintedTotal; ProcessedFile.Path/Alerts; core.Alert == JSON object; Sprig; config/templates).
[4] "substitution — Vale CLI," docs.vale.sh/checks/substitution (`swap:` bad:good map, `|` alternatives).
[5] "Styles — Vale CLI," vale.sh/docs/styles (`existence` `action:` name=edit/replace, `params`; check-type list).
[6] "Packages — Vale CLI," vale.sh/docs/keys/packages (`vale sync` overwrites style folders, preserves `config/`; shipped `.gitignore`).
[7] "LICENSE," raw.githubusercontent.com/redhat-documentation/vale-at-red-hat/main/LICENSE ("MIT License", Copyright 2021 Rolfe Dlugy-Hegwer).
[8] "redhat-documentation/vale-at-red-hat," github.com/redhat-documentation/vale-at-red-hat (style package; MIT; actively maintained, v656 May 2026).
[9] "Red Hat Style for Vale reference guide," redhat-documentation.github.io/vale-at-red-hat/reference-guide.html (rule name + guideline + level + links; no worked bad/good pairs).
[10] "Red Hat supplementary style guide," redhat-documentation.github.io/supplementary-style-guide/ (separate prose source, separate licensing).
[11] "CLI — Vale," vale.sh/docs/cli (full command/flag list; no `--examples`).
[12] "Vale-MCP," github.com/ChrisChinchilla/Vale-MCP (MIT; vale_status/vale_sync/check_file/check_text; no examples db).
[13] "vale-mcp-server (archived)," github.com/theletterf/vale-mcp-server (MIT; archived 2025-10-29; redirects to Vale-MCP).
[14] "VoltAgent/awesome-agent-skills," github.com/VoltAgent/awesome-agent-skills (no Vale/prose entry).
[15] "BehiSecc/awesome-claude-skills," github.com/BehiSecc/awesome-claude-skills (no Vale/prose entry).
