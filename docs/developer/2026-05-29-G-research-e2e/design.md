# `research/e2e/` — Regression Harness for the `research` Plugin

*DRAFT 2026-05-29*

## Problem Statement

The `research` plugin ships eleven `SKILL.md` files. None has regression coverage today. The plugin is unusual among the six in this repo because most of its skills depend on **external transports** — MCP servers, HTTP APIs, polite-pool email parameters, marketplace plugins, SSO handshakes. A harness for this plugin must catch two failure surfaces (discovery from `description:` frontmatter, invocation from the body) while also handling a controlled variable the other plugins do not have: **tool availability**. Some cases are runnable in CI on a fresh checkout with nothing configured; others require credentials the developer or CI environment may or may not have.

The harness must run the assemble half of every case unconditionally (assembly only reads files; it works without secrets), and gate the run-and-eval half per-case on the presence of the env var(s) that case requires. Cases that need credentials must not silently pass on a credential-less environment and must not silently fail either — they must announce themselves as skipped, with the missing env var named, so an operator can configure the harness and re-run.

`ailly_two/e2e/patterns-eval` is the shape this harness inherits. The `configuring-papers` ↔ `papers` and `configuring-books` ↔ `books` pairs mirror patterns-eval's `configuring-logging` ↔ `emitting-logs` bootstrap-vs-per-use pairing exactly; the discovery cases that distinguish wiring from practice are authored against that shape.

## Prior Art

- **`ailly_two/e2e/patterns-eval`** — the working reference harness. Three suites (`discovery`, `invocation`, `baseline`), one assembly per suite over a matrix, prompts under `prompts/<suite>/<name>.md`, evals under `evals/<suite>.yaml`, placeholder Python check scripts under `evals/scripts/check_<skill>.py`, a `ci.sh` driver that assembles → runs (gated on `ANTHROPIC_API_KEY`) → evals → reports. The `configuring-logging` ↔ `emitting-logs` paired-blur discovery cases (`paired-add-propagator`, `paired-log-handler-success`) are the model for this harness's two pair families.
- **`docs/developer/2026-05-29-A-skill-evals/design.md`** — the blueprint that fixes the per-plugin layout, the live-path convention, the falsification rule, the `e2e/AGENTS.md` shared template, the `profile.md` per-plugin appendix, the per-plugin profile selection, and (in the `research` subsection) the controlled-variable convention for tool availability. This design instantiates that subsection in concrete files.
- **`docs/developer/2026-05-29-C-patterns-e2e/design.md`** — the sibling per-plugin design that this one mirrors in structure and tone. Differences are concentrated in the `ci.sh` per-case gating, the env-var matrix, and the bootstrap-vs-per-use discovery pairs.
- **`e2e/AGENTS.md`** — the shared coding-agent constitution, loaded at position zero of every prefix. Already present at the repo root. The bare-word grep relaxation in the falsification convention applies because words like `paper`, `book`, `code`, and `archaeology` (and especially their unprefixed forms) appear naturally in any coding-agent prompt.

## Metrics

Inherited from the blueprint, with the controlled variable added as a runtime axis.

| Metric | Source | Target |
|---|---|---|
| Discovery pass rate | `evals/discovery.yaml` (8 cases) | ≥ 0.9 |
| Invocation pass rate (always-runnable subset) | `evals/invocation.yaml` cases for `codebase`, `archaeology`, `configuring-papers`, `configuring-books` | ≥ 0.8 |
| Invocation pass rate (conditional subset, when credentials present) | `evals/invocation.yaml` cases for `papers`, `books`, `internal` | ≥ 0.8 |
| Baseline pass rate | `evals/baseline.yaml` (same 6 cases as invocation, no SKILL.md loaded) | as low as the prompt allows |
| **Falsification gap** | invocation pass rate − baseline pass rate (per subset) | ≥ 0.5 |
| **Skip reporting integrity** | `ci.sh` prints `SKIP: missing $VAR` for every conditional case whose env var is absent; no conditional case silently passes or fails | 100% |

The check scripts ship as placeholders until the upstream eval-script slice lands; until then the falsification gap is read primarily from the judge and `tokens` assertions per case. The skip-reporting metric is unique to this harness — it is the only one where a credential-less CI environment can legitimately exercise only a subset of cases, and the operator must be able to tell the difference between "ran and passed" and "skipped because uncredentialed".

## Specification

### Layout

```
research/e2e/
├── profile.md                                  ← purpose + axis profile (Full triple) + controlled-variable note
├── assemblies/
│   ├── discovery.yaml                          ← matrix over case, 8 cases
│   ├── invocation.yaml                         ← matrix over skill, 7 skills (note: 6 cross-section + `internal`*)
│   └── baseline.yaml                           ← matrix over skill, 7 skills, no SKILL.md prefix
├── prompts/
│   ├── discovery/
│   │   ├── papers-question.md                  ← new
│   │   ├── books-question.md                   ← new
│   │   ├── codebase-question.md                ← new
│   │   ├── archaeology-question.md             ← new
│   │   ├── configuring-papers-trigger.md       ← new (bootstrap-vs-per-use)
│   │   ├── configuring-books-trigger.md        ← new (bootstrap-vs-per-use)
│   │   ├── papers-vs-public.md                 ← new (neighbour disambiguation)
│   │   └── internal-vs-codebase.md             ← new (neighbour disambiguation)
│   └── invocation/
│       ├── papers.md                           ← new, conditional
│       ├── books.md                            ← new, conditional
│       ├── codebase.md                         ← new, always-runnable
│       ├── archaeology.md                      ← new, always-runnable
│       ├── configuring-papers.md               ← new, always-runnable (plan, not execution)
│       ├── configuring-books.md                ← new, always-runnable
│       └── internal.md                         ← new, conditional
├── evals/
│   ├── discovery.yaml                          ← 8 cases, mostly text_contains / text_not_contains, judge on the 2 paired-blur cases
│   ├── invocation.yaml                         ← 7 cases, each = script + judge + tokens
│   ├── baseline.yaml                           ← 7 cases, identical assertions to invocation
│   ├── scripts/
│   │   ├── check_papers.py                     ← placeholder; eventual rules in docstring
│   │   ├── check_books.py                      ← placeholder
│   │   ├── check_codebase.py                   ← placeholder
│   │   ├── check_archaeology.py                ← placeholder
│   │   ├── check_configuring_papers.py         ← placeholder
│   │   ├── check_configuring_books.py          ← placeholder
│   │   └── check_internal.py                   ← placeholder
│   └── reports/                                ← .gitignore'd, populated by ci.sh
├── runs/                                       ← .gitignore'd, populated by ci.sh
├── .gitignore                                  ← runs/, evals/reports/, .env
└── ci.sh                                       ← adapted from patterns-eval; per-case env-var gating
```

*Note on the seventh skill in the matrix.* The blueprint's `research` subsection names a six-skill cross-section (`papers`, `books`, `codebase`, `archaeology`, `configuring-papers`, `configuring-books`). This design also includes `internal` in the invocation/baseline matrix because (a) `internal` is the canonical conditional case — its tool availability is the entire question its skill answers ("discover what is configured before searching") — and (b) including it gives the harness three conditional cases (`papers`, `books`, `internal`), exercising the per-case env-var gate on enough distinct variables to confirm the pattern works. `internal` appears as an invocation case but **not** as its own dedicated discovery case beyond the `internal-vs-codebase` neighbour disambiguation already authored. This is one skill more than the blueprint specified; the addition is justified by the controlled-variable goal and stays within the "minimal cross-section" spirit.

No `context/` directory. No vended copies. No fixtures (no skill in this cross-section is phase-dependent the way the `developer` plugin's are).

### Profile

`research/e2e/profile.md` is a short appendix to the shared `e2e/AGENTS.md`. It declares (1) the harness's purpose, (2) the axis profile (Full triple), and (3) the controlled-variable note that some invocation cases require external transports and are gated per-case in CI. It does not name the skills under test or paraphrase any skill content. The same falsification grep that runs on `AGENTS.md` runs on `profile.md`.

Draft text (single short paragraph, ≤ 100 words):

> This directory is a regression harness for the `research:*` skill plugin. It exercises the full discovery + invocation + baseline triple: discovery checks that routing prompts select the correct skill from `description:` frontmatter alone; invocation checks that loaded skills produce findings with the expected structural signature; baseline runs the same invocation prompts with no skill loaded as a falsification floor. Several invocation cases depend on external transports (MCP servers, HTTP APIs, polite-pool emails); the CI driver gates those per-case on environment variables and prints a clear skip notice when credentials are absent. A non-degenerate gap between invocation and baseline — on whichever subset is runnable in the current environment — is the headline signal.

### Assemblies (live paths)

`discovery.yaml`:

```yaml
name: discovery
model: claude-sonnet-4-6

matrix:
  case:
    - papers-question
    - books-question
    - codebase-question
    - archaeology-question
    - configuring-papers-trigger
    - configuring-books-trigger
    - papers-vs-public
    - internal-vs-codebase

prefix:
  - { kind: file,   path: ../../e2e/AGENTS.md,                       cache: true }
  - { kind: file,   path: ./profile.md,                              cache: true }
  - { kind: system, path: ../skills/using-research/SKILL.md,         cache: true }

conversation:
  - { role: user, path: "prompts/discovery/{{ case }}.md" }
  - { role: assistant }
```

`invocation.yaml`:

```yaml
name: invocation
model: claude-sonnet-4-6

matrix:
  skill:
    - codebase
    - archaeology
    - configuring-papers
    - configuring-books
    - papers
    - books
    - internal

prefix:
  - { kind: file,   path: ../../e2e/AGENTS.md,                       cache: true }
  - { kind: file,   path: ./profile.md,                              cache: true }
  - { kind: system, path: ../skills/using-research/SKILL.md,         cache: true }
  - kind: system
    path: "../skills/{{ skill }}/SKILL.md"
    cache: true

conversation:
  - { role: user, path: "prompts/invocation/{{ skill }}.md" }
  - { role: assistant }
```

`baseline.yaml`:

```yaml
name: baseline
model: claude-sonnet-4-6

matrix:
  skill:
    - codebase
    - archaeology
    - configuring-papers
    - configuring-books
    - papers
    - books
    - internal

prefix:
  - { kind: file, path: ../../e2e/AGENTS.md, cache: true }
  - { kind: file, path: ./profile.md,        cache: true }

conversation:
  - { role: user, path: "prompts/invocation/{{ skill }}.md" }
  - { role: assistant }
```

All three assemblies share the two `kind: file` entries. Discovery and invocation add `using-research/SKILL.md`; invocation adds the named skill. Baseline drops every `kind: system` entry. The matrix order in invocation and baseline lists the always-runnable cases first and the conditional ones last — this is purely cosmetic for readability, since each case stands alone in its own conversation file.

### Env-var matrix

This is the headline table for the controlled variable. `ci.sh` reads from it (via a `case_env_var()` shell function — see below) to decide whether to run each case.

| Case | Suite | Gating env var(s) | Source of requirement | Runnable in fresh CI? |
|---|---|---|---|---|
| All discovery cases | discovery | none | the model is reasoning from `description:` frontmatter, not calling any transport | yes |
| `codebase` | invocation, baseline | none | `research:codebase` uses LSP and `Grep`/`Glob`; local-only | yes |
| `archaeology` | invocation, baseline | none | `research:archaeology` uses local `git`; local-only | yes |
| `configuring-papers` | invocation, baseline | none | invocation case asks for a *configuration plan*, not its execution; produces a checklist, not API calls | yes |
| `configuring-books` | invocation, baseline | none | same shape on the books side | yes |
| `papers` | invocation, baseline | `CROSSREF_MAILTO` | `configuring-papers/SKILL.md` line 54 — Crossref polite pool requires `CROSSREF_MAILTO`; this is the minimal viable transport for a DOI→metadata smoke that exercises the practice skill | no |
| `books` | invocation, baseline | `OPENLIBRARY_USER_AGENT` | `configuring-books/SKILL.md` line 55 — Open Library is keyless but requires `OPENLIBRARY_USER_AGENT` containing a contact email; this is the minimal viable transport for an ISBN→edition smoke | no |
| `internal` | invocation, baseline | at least one of `LINEAR_TOKEN`, `NOTION_TOKEN`, `SLACK_TOKEN`, `GITHUB_TOKEN` | `internal/SKILL.md` lines 40–46 — the skill discovers via `ListMcpResourcesTool` and dispatches to whichever internal MCP is configured; any one configured server is enough to exercise the skill's surface | no |

Two notes.

1. **The minimal gates are deliberately the cheapest viable transport per skill, not the richest.** `papers` only needs `CROSSREF_MAILTO` to exercise its DOI→metadata routing path; richer cases (OpenAlex topic search, ArXiv preprints, PubMed) require additional env vars but are not required to consider the case "runnable". The check scripts and judge prompts accept any subset of the source priority being exercised.
2. **The seed prompt mentioned `OPENALEX_EMAIL` as a placeholder.** No such variable appears in `configuring-papers/SKILL.md`. OpenAlex uses `OPENALEX_API_KEY` after Feb 2026, and the polite-pool contact for Crossref is `CROSSREF_MAILTO`. This design follows the SKILL.md verbatim.

### Prompts

**Discovery (eight cases).** Each prompt is a short coding-situation framing (1–3 sentences) ending in "Which `research:*` skill applies?". The expected skill ID and foil are in the eval file, not in the prompt.

- `papers-question.md`:
  > A teammate quoted "Section 4 of the Cambridge ICN cache-invalidation paper". I have neither the DOI nor the venue confirmed. I need to find it, get the abstract, and check what cites it. Which `research:*` skill applies?

  Expected: `research:papers`. Foils to watch: `research:public` (the model might think "it's on the web" → public; the correct routing is `papers` because the question is *citable, identifier-keyed* literature, not open-web doc lookup).

- `books-question.md`:
  > I want to quote Evans's *Domain-Driven Design* blue book chapter on Anti-Corruption Layers. I have the title but not the ISBN-13. Which `research:*` skill applies?

  Expected: `research:books`. Foil: `research:public`.

- `codebase-question.md`:
  > Where is `OrderManifest` defined in this repo right now, and what implements it? Which `research:*` skill applies?

  Expected: `research:codebase`. Foil: `research:archaeology` (model might assume "history" because of "implements"; correct answer is `codebase` for current-state questions).

- `archaeology-question.md`:
  > The auth middleware in `src/auth/` was removed some time in 2024. Why? Which `research:*` skill applies?

  Expected: `research:archaeology`. Foil: `research:codebase`.

- `configuring-papers-trigger.md`:
  > I just cloned this project on a fresh machine. I want to set up paper-fetching so future research sessions can answer DOI questions. Which `research:*` skill applies?

  Expected: `research:configuring-papers` (the bootstrap, run once per environment), **not** `research:papers` (the per-query practice). This is the bootstrap-vs-per-use shape — same as patterns-eval's `paired-add-propagator`. Assertions include a judge that confirms the answer cites *bootstrap* / *setup* / *configure* rather than *answer a question*.

- `configuring-books-trigger.md`:
  > I want to add Open Library and Internet Archive support for this project so I can resolve ISBNs. Which `research:*` skill applies?

  Expected: `research:configuring-books`, not `research:books`. Same bootstrap-vs-per-use shape on the books side.

- `papers-vs-public.md`:
  > What's the difference between MAC and DAC access control in operating systems? Which `research:*` skill applies?

  Expected: `research:public` (general concept, answerable from open-web docs; no specific citable paper named), **not** `research:papers` (which is for *identifier-keyed academic literature*). This case prevents the model from over-eagerly routing every research question with a technical topic to `papers`.

- `internal-vs-codebase.md`:
  > What did the team decide in the ADR for the auth migration last quarter? Which `research:*` skill applies?

  Expected: `research:internal` (ADRs typically live in a doc store — Confluence/Notion/Linear/GitHub PRs), **not** `research:codebase` (the *code* of the auth migration is in the repo, but the *decision rationale* is in internal docs).

**Invocation (seven cases).** Each prompt is a concrete task that exercises the skill's structural rules. All prompts assume the model has the skill loaded and writes findings to the conventional output path.

- `papers.md` (conditional on `CROSSREF_MAILTO`):
  > Given the DOI `10.1145/3007787.3001177` ("In-Datacenter Performance Analysis of a Tensor Processing Unit", ISCA 2017), produce a research note at `docs/research/2026-05-29-A-tpu-isca/papers.md` with the canonical metadata (title, authors, year, venue), a working OA-PDF link if one exists, and an IEEE-style Sources block. Use the Crossref / Unpaywall capabilities; do not fabricate URLs.

  Structural signature: file path matches `docs/research/YYYY-MM-DD-A-<topic>/papers.md`; a `## Findings` section with inline `[N]` citations; a `## Sources` section in loose IEEE format; at least one entry resolves to a real DOI URL; no hallucinated `10.xxxx/...` strings the script cannot verify by regex shape.

- `books.md` (conditional on `OPENLIBRARY_USER_AGENT`):
  > Given the title "Domain-Driven Design: Tackling Complexity in the Heart of Software" by Eric Evans, produce a research note at `docs/research/2026-05-29-A-ddd-blue/books.md` with the canonical ISBN-13, publisher and year of the original edition, and a link to where the user can read the table of contents. Use the Open Library / Google Books capabilities; the user has not configured O'Reilly, so do not assume it.

  Structural signature: file path matches `docs/research/YYYY-MM-DD-A-<topic>/books.md`; an ISBN-13 appears in the Sources block (13 digits, optionally with hyphens); a `## Findings` section with inline citations; a `## Sources` section in IEEE format; the answer degrades gracefully if O'Reilly is not configured (no "you must first install …" preface, which would be a wiring leak).

- `codebase.md` (always-runnable):
  > Where is the `general:review` skill's "rubric" concept defined or referenced in this repo? Produce a research note at `docs/research/2026-05-29-A-review-rubric/codebase.md` with file paths and line numbers, the current commit short SHA, and at least one usage example excerpt.

  Structural signature: file path matches `docs/research/YYYY-MM-DD-A-<topic>/codebase.md`; at least one `path/to/file.ext:NNN` reference appears in the Findings or Sources block; the current commit SHA appears in the Sources block; the answer reflects current state only (no `git log` excerpts, no commit messages).

- `archaeology.md` (always-runnable):
  > Why was the file `developer/skills/design/SKILL.md` last modified, and what was the rationale? Produce a research note at `docs/research/2026-05-29-A-design-skill-change/archaeology.md` with the relevant commit SHA(s), commit messages, and a brief narrative.

  Structural signature: file path matches `docs/research/YYYY-MM-DD-A-<topic>/archaeology.md`; at least one 7+ hex commit SHA appears; the `## Timeline` block exists; commit messages are quoted or summarized; no file *content* from the current commit is reproduced (that would be a `codebase` leak).

- `configuring-papers.md` (always-runnable; this case asks for a *plan*, not its execution):
  > A teammate has cloned this project on a fresh machine and has no papers MCP installed. Produce a configuration plan they can walk top-to-bottom: probe order per source (MCP first, HTTP fallback), the env vars to set, the marketplace plugins to install where applicable, and a one-line smoke test per source confirming the capability contract holds. Include at minimum: Crossref, Unpaywall, OpenAlex, Semantic Scholar, ArXiv. Note which sources are conditional and would return Not-Available if skipped.

  Structural signature: the output enumerates a checklist; each item names a source, a transport (MCP probe or HTTP fallback), the env var(s) it sets, and a smoke-test query; the four-stage structure (probe → fallback → env → smoke) is visible per source; the Not-Available routing signal is mentioned at least once.

- `configuring-books.md` (always-runnable; same shape on the books side):
  > A teammate has cloned this project on a fresh machine and wants to set up books research. Produce a configuration plan covering at minimum Open Library, Gutendex / Project Gutenberg, Internet Archive, and Google Books, with the same four-stage structure per source (probe → fallback → env → smoke).

  Structural signature: as above; the four-stage structure per source; the keyless sources (Gutendex, Internet Archive) are correctly identified as not needing env vars; the polite User-Agent for Open Library is mentioned.

- `internal.md` (conditional on any of `LINEAR_TOKEN` / `NOTION_TOKEN` / `SLACK_TOKEN` / `GITHUB_TOKEN`):
  > The team decided some time in the last six months to migrate from session-based auth to token-based auth. Find the rationale by searching internal sources. Produce a research note at `docs/research/2026-05-29-A-auth-migration/internal.md` with which MCP server(s) were queried, the matching documents/threads/tickets, and a short synthesis. If no internal MCP is configured, the case is skipped at `ci.sh` and this prompt is never reached.

  Structural signature: file path matches `docs/research/YYYY-MM-DD-A-<topic>/internal.md`; the `## Sources` block names which MCP server was queried; at least one result citation appears; the discovery step (`ListMcpResourcesTool`) is mentioned at least once.

### Evals

**`evals/discovery.yaml`** — 8 cases. Each case has the canonical shape: a `text_contains` assertion on the expected skill ID (`research:<name>`), a `text_not_contains` assertion on the foil, and on the two bootstrap-vs-per-use cases (`configuring-papers-trigger`, `configuring-books-trigger`) and the two neighbour cases (`papers-vs-public`, `internal-vs-codebase`) a `judge` assertion that ties the choice to the right rationale. The judge prompt prevents a model from naming the right skill for the wrong reason.

Example for `configuring-papers-trigger`:

```yaml
- name: configuring-papers-trigger
  assertions:
    - { type: text_contains, value: "research:configuring-papers" }
    - { type: text_not_contains, value: "research:papers" }
    - type: judge
      prompt: |
        The answer selects research:configuring-papers because the question is
        about bootstrapping the sources once per environment, not about
        answering a research question. It does not recommend research:papers as
        the primary skill for this prompt.
```

**`evals/invocation.yaml`** — 7 cases. Each case = `script` (placeholder for now) + `judge` (structural rules in prose) + `tokens` (< 6000 or 8000). Judge prompts encode the structural signature from the prompt block above. Token budgets are set per case based on the expected output length (configuration plans are larger; codebase notes are smaller).

| Case | Token budget |
|---|---|
| `codebase` | < 5000 |
| `archaeology` | < 5000 |
| `configuring-papers` | < 9000 (a configuration plan over 5+ sources is verbose) |
| `configuring-books` | < 9000 |
| `papers` | < 6000 |
| `books` | < 6000 |
| `internal` | < 6000 |

**`evals/baseline.yaml`** — mechanically identical to `evals/invocation.yaml`. Same assertions, same scripts, same judges, same token budgets. The only thing that changes is the absence of the `kind: system` prefix entries in `baseline.yaml` (the assembly).

### Check scripts

All seven scripts use the placeholder body inherited from patterns-eval — read stdin, write `{"status": "placeholder", "reason": "eval-script not yet wired"}`, exit 0. Each script's header docstring enumerates the rule set the eventual implementation must encode.

- `check_papers.py` — eventual rules: output path matches `docs/research/YYYY-MM-DD-A-<topic>/papers.md`; ≥ 1 DOI matches the `10.\d{4,9}/[-._;()/:A-Z0-9]+` regex; ≥ 1 IEEE-style numbered citation `[N]` in Findings; no plausible-looking-but-unverifiable DOIs (the script cannot verify online but can flag the shape).
- `check_books.py` — eventual rules: output path matches `…/books.md`; ≥ 1 ISBN-13 matches `\d{3}-?\d{1,5}-?\d{1,7}-?\d{1,7}-?\d`; ≥ 1 IEEE-style citation; no "first install …" preface (wiring leak).
- `check_codebase.py` — eventual rules: output path matches `…/codebase.md`; ≥ 1 `path/to/file.ext:NNN` reference; a 7+ hex SHA in Sources; no `git log` / `git blame` excerpts (would be archaeology, not codebase).
- `check_archaeology.py` — eventual rules: output path matches `…/archaeology.md`; ≥ 1 7+ hex commit SHA; `## Timeline` heading present; no current-file-content reproduction.
- `check_configuring_papers.py` — eventual rules: enumerates ≥ 5 sources; each source has a probe stage, a fallback stage, an env-var declaration (or "none required"), and a smoke-test line; Not-Available is mentioned at least once.
- `check_configuring_books.py` — same shape on the books side; the keyless sources are correctly marked.
- `check_internal.py` — eventual rules: output path matches `…/internal.md`; the `## Sources` block names the MCP server queried; `ListMcpResourcesTool` is mentioned; ≥ 1 result citation appears.

The placeholder pattern matches patterns-eval: header docstring + `main()` that reads stdin and writes placeholder JSON. When the upstream eval-script slice lands, the rule sets in the docstrings become the test code.

### ci.sh

Adapted from `ailly_two/e2e/patterns-eval/ci.sh` with four changes:

1. `expected_count()` table: `discovery=8`, `baseline=7`, `invocation=7`.
2. `repo_root="$(cd "${project_dir}/../.." && pwd)"` — already correct for this layout (`research/e2e/ci.sh` resolves `../..` to repo root).
3. `cargo run --quiet --` invocations become `ailly` directly per the blueprint.
4. **Per-case env-var gating** — the run and eval phases iterate per-case for the invocation and baseline suites, consulting a `case_env_var()` function to decide whether to skip each case. Discovery cases run unconditionally (no transports required).

The per-case gating pattern, lifted directly so an implementer can copy it:

```bash
# Return 0 (run) or 1 (skip with notice) for a given case.
# The case name is the matrix key from the assembly (e.g. "papers", "codebase").
case_env_var() {
  local case_name="$1"
  case "${case_name}" in
    # Always-runnable: no env var required.
    codebase|archaeology|configuring-papers|configuring-books)
      return 0
      ;;
    # Conditional: a single env var must be set.
    papers)
      if [[ -z "${CROSSREF_MAILTO:-}" ]]; then
        echo "SKIP: case '${case_name}' requires CROSSREF_MAILTO; set it in shell or .env to run."
        return 1
      fi
      return 0
      ;;
    books)
      if [[ -z "${OPENLIBRARY_USER_AGENT:-}" ]]; then
        echo "SKIP: case '${case_name}' requires OPENLIBRARY_USER_AGENT; set it in shell or .env to run."
        return 1
      fi
      return 0
      ;;
    # Conditional: at least one of a set must be set.
    internal)
      if [[ -z "${LINEAR_TOKEN:-}" && -z "${NOTION_TOKEN:-}" \
         && -z "${SLACK_TOKEN:-}" && -z "${GITHUB_TOKEN:-}" ]]; then
        echo "SKIP: case '${case_name}' requires at least one of LINEAR_TOKEN, NOTION_TOKEN, SLACK_TOKEN, GITHUB_TOKEN; set one to run."
        return 1
      fi
      return 0
      ;;
    *)
      echo "FAIL: unknown case '${case_name}'" >&2
      exit 1
      ;;
  esac
}
```

The run and eval loops then look like:

```bash
# Per-case run: each conversation file is named "<case>-<hash>.yaml" or similar
# under the suite's run_dir; the case name is recoverable from the filename.
# (Exact extraction depends on ailly's naming convention; the design is the gate, not the parser.)
run_suite_per_case() {
  local suite="$1"
  local run_dir
  run_dir="$(get_run_dir "${suite}")"

  shopt -s nullglob
  local files=("${run_dir}"/*.yaml)
  shopt -u nullglob

  local ran=0
  local skipped=0
  local f
  for f in "${files[@]}"; do
    local case_name
    case_name="$(extract_case_name "${f}")"   # helper: parses matrix key from filename
    if case_env_var "${case_name}"; then
      cargo run --quiet -- -p "${project_dir}" run "${f}"   # or `ailly run ${f}`
      ran=$((ran + 1))
    else
      skipped=$((skipped + 1))
    fi
  done

  echo "OK: ailly run ${suite} ran ${ran} case(s), skipped ${skipped} case(s)."
}
```

Discovery runs as a single batch (the assemble step writes a directory; the run step processes the whole directory) because every discovery case is unconditional. Invocation and baseline run per-case so each conditional case can be skipped individually.

The eval phase mirrors the run phase: invocation and baseline iterate per-case via `case_env_var()`; discovery runs as one batch.

Beyond the per-case gate, the existing `ANTHROPIC_API_KEY` outer gate from patterns-eval is preserved — without `ANTHROPIC_API_KEY`, the run phase is skipped entirely (no per-case loop reached). The outer gate is the credential floor for any model invocation; the per-case gate is the transport floor for the specific skill.

The falsification grep step from the patterns-eval design carries forward, adapted to the `research:` prefix:

```bash
# Falsification grep — fail if either file leaks a plugin-prefixed skill identifier.
for f in ../../e2e/AGENTS.md profile.md; do
  if grep -E 'research:[a-z-]+' "${project_dir}/${f#./}" >/dev/null 2>&1; then
    echo "FAIL: ${f} contains a 'research:*' identifier; baseline arm leaks the answer." >&2
    exit 1
  fi
done
```

This runs before the assemble step. It guards the falsification convention mechanically.

### Falsification

The blueprint's mechanical rule applies directly: drop every `kind: system` from invocation to produce baseline, keep both `kind: file` entries. The two `kind: file` entries (`../../e2e/AGENTS.md` and `./profile.md`) carry the coding-agent mindset and the harness purpose; neither names any research skill. The `ci.sh` grep enforces the rule.

The seven invocation prompts deliberately name what the deliverable should look like (a `papers.md` file with a Findings and Sources block, a configuration plan with probe-fallback-env-smoke per source) without naming the skill or its routing table. A baseline model reading "Given the DOI `10.1145/3007787.3001177`, produce a research note at `docs/research/2026-05-29-A-tpu-isca/papers.md`" will likely produce *something*, but is unlikely to use the IEEE citation format, place the file under the research-notes convention, or correctly distinguish DOI-fan-out vs Crossref vs Unpaywall capabilities without the skill loaded. The gap is the headline signal.

The conditional cases add a wrinkle: the falsification gap is only readable when the case actually runs. The `ci.sh` skip notices feed the operator's mental model; an environment that skips half the conditional cases produces a gap measurement on the always-runnable half plus whichever conditional cases ran. The harness reports this honestly rather than papering over it.

## Alternatives

**Drop `internal` from the matrix and use the seed-prompt six-skill cross-section verbatim.** Considered and rejected. The blueprint's `research` subsection names six skills, but the controlled-variable goal of this harness — explicitly exercise the per-case env-var gate — is strengthened by having three conditional cases (`papers`, `books`, `internal`) rather than two. `internal` is also the only skill in the plugin whose *entire premise* is discovering what transports are configured; excluding it from invocation coverage would leave the most controlled-variable-relevant skill untested. Adding one skill beyond the cross-section is a tightly scoped deviation.

**Strategy A: gate the entire run phase on the full superset of env vars** (`CROSSREF_MAILTO && OPENLIBRARY_USER_AGENT && (LINEAR_TOKEN || NOTION_TOKEN || SLACK_TOKEN || GITHUB_TOKEN)`). Considered and rejected — chosen by the user as the path-not-taken. This trades fewer skip cases for an all-or-nothing CI run: any one missing env var skips every conditional case, including the ones whose own gate would have been satisfied. The per-case gate (Strategy B) gives finer-grained feedback at the cost of slightly more shell code.

**Strategy C: fixture conversations that mock the MCP "Not-Available" response so the eval can assert the skill *handles* Not-Available correctly, without requiring the real transport.** This is the deferred enrichment named in the seed prompt. It would replace the per-case gate with a fixture-loaded prompt for each conditional case, eliminating the env-var dependency entirely. Authoring the fixture conversations requires fixing on a specific MCP response shape per source, which is itself a moving target (each MCP server publishes its own shape). Deferred until the MCP response contracts stabilize. See **Deferred decisions**.

**Strategy A+B hybrid: gate the run phase on `ANTHROPIC_API_KEY` (outer gate, as today) and add a single combined inner gate for "any transport configured" that runs all conditional cases or none.** Considered and rejected. This is worse than A: the operator pays the cost of configuring at least one transport just to run any conditional case, but doesn't get the cases whose own gate they satisfied. Strategy B is strictly more useful at the cost of one helper function.

**Vended `context/skills/<name>/SKILL.md` copies under `research/e2e/`.** Considered and rejected (blueprint). Pinning is real, but every edit to a `research/skills/*/SKILL.md` would require a sync step. Worktree pin for a sweep, live paths for the default.

**Single `evals/all.yaml` with per-case suite tags instead of three suite files.** Considered and rejected. Patterns-eval splits by suite and `ci.sh` indexes by suite name throughout; following the existing shape keeps the CI driver identical except for the per-case gate.

**Implement real check scripts now instead of placeholders.** Considered and rejected. The blueprint defers script bodies to the `knowledge: eval-script` slice; until then the placeholder convention is what patterns-eval ships and what this harness inherits. The judge assertions carry the structural rules in prose for now.

**Run the conditional invocation cases against fixture transports (recorded responses) in CI, and against real transports locally.** Considered as an evolution path. This is essentially Strategy C, deferred for the same reason — fixture authoring requires fixing the MCP response shape per source.

## Summary

A new `research/e2e/` directory adjacent to `research/skills/`, shaped after `ailly_two/e2e/patterns-eval` but with live `../skills/<name>/SKILL.md` paths instead of vended copies. Eight discovery prompts, seven invocation prompts, seven check-script placeholders. The seven-skill invocation matrix is one skill larger than the blueprint's six-skill cross-section by adding `internal`, justified by the controlled-variable goal — three conditional cases (`papers`, `books`, `internal`) on three distinct env-var gates exercise the per-case gating pattern thoroughly.

The `ci.sh` driver adopts **Strategy B**: it always runs `ailly assemble` for every case (assembly only reads files), and gates `ailly run` and `ailly eval` per-case on the case's required env var(s). A `case_env_var()` shell function consolidates the gating decision and prints a clear `SKIP: case '<name>' requires <VAR>` notice when a case is uncredentialed. The outer `ANTHROPIC_API_KEY` gate from patterns-eval is preserved.

**Env-var matrix.**

| Case | Gating env var |
|---|---|
| discovery (all 8) | none |
| `codebase`, `archaeology`, `configuring-papers`, `configuring-books` | none |
| `papers` | `CROSSREF_MAILTO` |
| `books` | `OPENLIBRARY_USER_AGENT` |
| `internal` | at least one of `LINEAR_TOKEN`, `NOTION_TOKEN`, `SLACK_TOKEN`, `GITHUB_TOKEN` |

**Files created.**

- `docs/developer/2026-05-29-G-research-e2e/design.md` (this document).

**Files proposed (to be created in a follow-up implementation session).**

- `research/e2e/profile.md`
- `research/e2e/assemblies/{discovery,invocation,baseline}.yaml`
- `research/e2e/prompts/discovery/{papers-question,books-question,codebase-question,archaeology-question,configuring-papers-trigger,configuring-books-trigger,papers-vs-public,internal-vs-codebase}.md` (8 files)
- `research/e2e/prompts/invocation/{papers,books,codebase,archaeology,configuring-papers,configuring-books,internal}.md` (7 files)
- `research/e2e/evals/{discovery,invocation,baseline}.yaml`
- `research/e2e/evals/scripts/check_{papers,books,codebase,archaeology,configuring_papers,configuring_books,internal}.py` (7 files)
- `research/e2e/ci.sh`
- `research/e2e/.gitignore`

**Deferred decisions.**

- **Strategy C — fixture conversations mocking the MCP Not-Available response.** Authoring fixture conversations per conditional skill that simulate the typed Not-Available response would let CI assert *handling* of Not-Available without requiring a real transport. Deferred because each MCP server publishes its own response shape and those contracts are not yet stable. Revisit once `configuring-papers` and `configuring-books` capability contracts harden.
- **Concrete bodies of all seven check scripts.** Blueprint pins these behind the `knowledge: eval-script` slice. Structural rule sets land in the docstrings now; tests land when the slice lands.
- **The `extract_case_name()` helper in `ci.sh`.** The per-case loop needs to recover the matrix key from the conversation filename. The exact parse depends on ailly's naming convention for matrix-keyed outputs; sketched as a helper here, implemented when the conversation-file naming is confirmed against the current ailly release.
- **Whether the `papers` invocation case should also gate on `UNPAYWALL_EMAIL`.** Currently gates only on `CROSSREF_MAILTO` (the cheapest viable transport). If first runs show the case routinely fails because the OA-PDF capability is unreachable without `UNPAYWALL_EMAIL`, tighten the gate to require both.
- **The exact wording of the four judge prompts (the two bootstrap-vs-per-use discovery cases and the two neighbour discovery cases).** Sketched in the spec; final phrasing tuned after first run produces real responses.
- **Whether `using-research/SKILL.md` should also appear in baseline.** Blueprint says no; this design follows it. Reconsider only if baseline pass rates are anomalously low because the model lacks any context for "what is a research skill".
- **Whether to add a `dependencies` invocation case.** `research:dependencies` is in the plugin but not in the cross-section. It is local-only (always runnable) and tests a third structural artifact shape (declared-dependency lookup). Would expand the matrix from 7 to 8 cases. Deferred unless the first runs show the cross-section misses a class of skills the harness should cover.
- **Model-version sweep.** Blueprint pins one model (`claude-sonnet-4-6`); sweep tooling lands when baseline metrics stabilise.
- **Whether `ci.sh` should fail-fast on the falsification grep or report and continue.** Authored as `exit 1` here — leaking a skill ID into `AGENTS.md` or `profile.md` invalidates the baseline arm and should block the run.
