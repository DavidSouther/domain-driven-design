# Per-Plugin E2E Skill Evals

## Problem Statement

This repository ships six skill plugins — `characters`, `developer`, `domain`, `general`, `patterns`, `research` — totalling roughly 50 `SKILL.md` files. None have regression coverage, though `ailly_two/e2e/patterns-eval` exercises 3 of the 17 `patterns:*` skills as part of its e2e suite. The other five plugins have nothing.

A `SKILL.md` has two distinct failure surfaces.

1. **Discovery.** The `description:` frontmatter is what causes the model to load this skill instead of a neighbour. An edit that blurs the trigger language can silently route the model to the wrong skill.
2. **Invocation.** The body of the skill is what causes the model, once loaded, to produce code or artifacts in the prescribed structure. An edit that softens a constraint can silently change the output without changing what the model says it is doing.

Both regress without notice today. The harness must catch the first by routing decisions and the second by structural assertions on the produced text.

## Prior Art

`ailly_two/e2e/patterns-eval` is the working reference and the only source of harness shape so far. Its design is recapitulated here in summary; the new harnesses inherit it almost verbatim.

| Element | Form | Role |
|---|---|---|
| `AGENTS.md` | Markdown, position zero of every prefix | The harness's own constitution; defines purpose, scope, and a single source of truth for the assemblies. |
| `assemblies/discovery.yaml` | YAML, matrix over `case` | Loads only the `using-<plugin>` routing skill. Asks the model to name the right skill from a coding situation. |
| `assemblies/invocation.yaml` | YAML, matrix over `skill` | Loads `using-<plugin>` plus the named skill. Asks the model to produce a structural artifact. |
| `assemblies/baseline.yaml` | YAML, identical matrix to invocation | Loads `AGENTS.md` (and `profile.md` in the new harnesses) only. Runs the same prompts against zero skill context. |
| `prompts/discovery/<case>.md` | Markdown | One per discovery case. Short coding-situation framing ending in "Which `<plugin>:*` skill applies?" |
| `prompts/invocation/<skill>.md` | Markdown | One per invocation case. Concrete task that exercises the skill's structural rules. |
| `evals/<suite>.yaml` | YAML | Per-case assertions: `text_contains`, `text_not_contains`, `judge` prompt, `script` runtime, `tokens` budget. |
| `evals/scripts/check_<skill>.py` | Python | Reads conversation stdin, writes a JSON verdict. Encodes the skill's "Common Mistakes" section as structural rules. Ships as a placeholder until the upstream eval-script slice lands. |
| `ci.sh` | Bash, `set -euo pipefail` | Drives `cargo run ailly` through assemble → run → eval → report for each suite. Asserts file counts and filled-assistant invariants. Skips the run phase when `ANTHROPIC_API_KEY` is absent. |

## Metrics

A harness is operating within constraints when its three pass rates produce a non-degenerate falsification gap.

| Metric | Source | Target |
|---|---|---|
| Discovery pass rate | `evals/discovery.yaml` assertions | ≥ 0.9 |
| Invocation pass rate | `evals/invocation.yaml` assertions | ≥ 0.8 |
| Baseline pass rate | `evals/baseline.yaml` assertions (identical to invocation) | as low as the prompt allows |
| **Falsification gap** | invocation pass rate − baseline pass rate | ≥ 0.5 |

The falsification gap is the headline signal. A high invocation rate is necessary but not sufficient: if the baseline scores nearly as high, the skill is not contributing, and the prompt has merely encoded its own answer.

## Specification — Shared Blueprint

### Layout

Add a shared `e2e/` directory at the repo root for eval-only artifacts (the `AGENTS.md` template), and a per-plugin `e2e/` directory at the same level as each plugin's `skills/`. The skill content stays where it is.

```
<repo>/
├── e2e/                              ← shared eval-only resources
│   └── AGENTS.md                     ← coding-agent mindset; loaded by every plugin's harness
├── <plugin>/
│   ├── skills/
│   │   └── <skill-name>/SKILL.md     ← the source of truth, unchanged
│   └── e2e/
│       ├── profile.md                ← per-plugin harness purpose + axis profile
│       ├── assemblies/
│       │   ├── discovery.yaml        ← present iff plugin profile includes discovery
│       │   ├── invocation.yaml       ← present iff plugin profile includes invocation
│       │   └── baseline.yaml         ← present iff invocation present
│       ├── prompts/
│       │   ├── discovery/<case>.md
│       │   └── invocation/<skill>.md
│       ├── fixtures/                 ← optional, for phase-dependent skills
│       │   └── <fixture>.md
│       ├── evals/
│       │   ├── discovery.yaml
│       │   ├── invocation.yaml
│       │   ├── baseline.yaml
│       │   ├── scripts/check_<skill>.py
│       │   └── reports/
│       ├── runs/
│       └── ci.sh
```

### Live SKILL.md references

The assembly prefix points at `../skills/<name>/SKILL.md` directly. No `context/` tree, no vending step. Edits to a skill take effect on the next `ailly assemble`.

```yaml
# <plugin>/e2e/assemblies/invocation.yaml — illustrative
name: invocation
model: claude-sonnet-4-6

matrix:
  skill: [list-of-skills-in-the-minimal-cross-section]

prefix:
  - { kind: file,   path: ../../e2e/AGENTS.md,                    cache: true }
  - { kind: file,   path: ./profile.md,                           cache: true }
  - { kind: system, path: ../skills/using-<plugin>/SKILL.md,      cache: true }
  - kind: system
    path: "../skills/{{ skill }}/SKILL.md"
    cache: true

conversation:
  - { role: user, path: "prompts/invocation/{{ skill }}.md" }
  - { role: assistant }
```

```yaml
# <plugin>/e2e/assemblies/discovery.yaml — illustrative
name: discovery
model: claude-sonnet-4-6

matrix:
  case: [list-of-cases]

prefix:
  - { kind: file,   path: ../../e2e/AGENTS.md,                    cache: true }
  - { kind: file,   path: ./profile.md,                           cache: true }
  - { kind: system, path: ../skills/using-<plugin>/SKILL.md,      cache: true }

conversation:
  - { role: user, path: "prompts/discovery/{{ case }}.md" }
  - { role: assistant }
```

```yaml
# <plugin>/e2e/assemblies/baseline.yaml — illustrative
name: baseline
model: claude-sonnet-4-6

matrix:
  skill: [same-list-as-invocation]

prefix:
  - { kind: file, path: ../../e2e/AGENTS.md, cache: true }
  - { kind: file, path: ./profile.md,        cache: true }

conversation:
  - { role: user, path: "prompts/invocation/{{ skill }}.md" }
  - { role: assistant }
```

Pinning an older revision for a sweep is a `git worktree add` of the old SHA, not a vended copy.

### Per-plugin profile

Each plugin declares which axes it runs in its `e2e/profile.md`. The profile selects which assemblies and evals exist. Three profiles cover the six plugins:

| Profile | Discovery | Invocation | Baseline | Used by |
|---|---|---|---|---|
| **Full** | yes | yes | yes | `developer`, `domain`, `general`, `patterns`, `research` |
| **Invocation + baseline** | no | yes (judge) | yes (judge) | `characters` |

Characters skips discovery because voice loading is rule-based (skill-plugin presence) rather than model-driven from `description:` frontmatter, and voice fidelity is judge-scored rather than structurally scoreable.

### ci.sh template

Copy `ailly_two/e2e/patterns-eval/ci.sh` to `<plugin>/e2e/ci.sh`. Three parameters change per plugin:

1. `expected_count()` table — number of cases per suite.
2. The list of suites driven (`discovery`, `baseline`, `invocation`) — drop the suites the profile excludes.
3. `repo_root` — `${project_dir}/../..` for this repo, since the e2e directory is two levels under the repo root rather than one.

`ailly` itself is invoked as a CLI from the user's environment (`ailly -p "${project_dir}" assemble <suite>`), not as `cargo run`. Per-plugin ci.sh files are independent; a top-level GitHub Actions workflow can run them as a matrix.

### AGENTS.md template

Patterns-eval's `AGENTS.md` is a four-sentence note about the harness's purpose. The new harnesses use a richer template that puts the model into a coding-agent mindset before any skill loads, so discovery and invocation runs reflect what a model actually receives inside Claude Code, Cursor, Aider, or another coding agent — not a model with no operating context.

The canonical template lives at [`e2e/AGENTS.md`](../../../e2e/AGENTS.md) — a shared eval-only artifact, deliberately placed outside the repo root so it is not picked up by Claude Code, Cursor, or other agents during real work in this repository. The harness loads it into every eval prefix to put the model into the coding-agent mindset before any skill loads. It covers:

- Identity and environment (an interactive coding agent in a project directory).
- Communication style (terse, direct, code-references with file paths, no preambles).
- How to approach tasks (read before act, match conventions, scope changes, no unsolicited docs, no defensive scaffolding).
- Working with code (read failing output, smallest change, tests with the code, run the checks).
- Safety (read freely, act carefully, never bypass safety affordances, surface unexpected state, refuse what should be refused).

Each per-plugin harness loads the root `AGENTS.md` directly and appends a short `e2e/profile.md` to the prefix declaring (1) the harness's purpose ("this directory tests the `<plugin>` skill plugin") and (2) the axis profile it runs (`Full` or `Invocation + baseline`). `profile.md` does not name the skills under test or paraphrase any skill content; the same falsification grep that runs on `AGENTS.md` also runs on `profile.md`.

### Falsification convention

Baseline assemblies are mechanically identical to invocation assemblies with one change: drop every `kind: system` prefix entry that points at a SKILL.md, keep both `kind: file` entries (`../../e2e/AGENTS.md` and `./profile.md`). `AGENTS.md` describes the coding-agent mindset; `profile.md` declares the harness's purpose and axis profile. The observable constraint: neither file may contain any plugin-prefixed skill identifier (e.g. `patterns:newtype`, `developer:design`) and neither may reproduce a heading or numbered list verbatim from the body of a skill the harness tests. Bare common words that overlap with skill names (`design`, `review`, `refactor`, `repository`, `builder`) are permitted — they appear in any coding-agent prompt and forcing them out would corrupt the mindset framing. `ci.sh` enforces the constraint with a grep for the `<plugin>:<skill>` pattern across both files. The post-run comparison report (`ailly report <baseline-id> <invocation-id>`) produces the `improved` / `regressed` / `unchanged_pass` / `unchanged_fail` summary the falsification gap is read from.

## Specification — Per-Plugin Profiles

Each subsection is a one-page profile: axis selection, minimal cross-section of skills to cover, headline discovery and invocation cases as one-line summaries, plugin-specific wrinkles, and a seed prompt to start the next `developer:design` session that fleshes out concrete prompts and check scripts.

### `characters`

- **Source skills (6).** `using-characters`, `voice-ailly`, `voice-david`, `voice-jacki`, `voice-jefri`, `voice-rupert`.
- **Profile.** Invocation + baseline. Voice fidelity is judge-scored; no `description:` selection because voice loading is rule-based (skill-plugin presence) rather than model-driven discovery.
- **Minimal cross-section (4).** `voice-jefri`, `voice-jacki`, `voice-rupert`, `voice-david`. Two paired families: developer-plugin voices (Jefri TDD vs Jacki design exploration) and DDD voices (Rupert domain/patterns vs Ailly general/research). David is the user's own voice and tests a different surface: not a routing partner but a tone the model adopts when drafting on the user's behalf.
- **Invocation cases (4).**
  - `voice-jefri` — produce a short rationale for choosing a test name. Judge confirms the disciplined-TDD diction.
  - `voice-jacki` — produce a sketch caption for a layout alternative. Judge confirms the design-exploration affect.
  - `voice-rupert` — produce a glossary entry explanation. Judge confirms the ubiquitous-language gentle-giant cadence.
  - `voice-david` — draft a one-paragraph status update on a PR. Judge confirms the informal-technical register.
- **Falsification.** Baseline answers in neutral Claude voice. Each judge prompt is paired: "does this match the named voice?" — invocation should pass, baseline should fail.
- **Wrinkles.** No structural Python checker is possible; every assertion is `judge`. The token budget assertion is the only quantitative guard against the model padding.
- **Seed prompt.**
  > Design `e2e/` for the `characters` plugin. Read the blueprint in `docs/developer/2026-05-29-A-skill-evals/design.md` and the existing voice SKILL.md files. Profile is invocation-only with judge-based assertions. Produce the four invocation prompts and four matching judge prompts for `voice-jefri`, `voice-jacki`, `voice-rupert`, `voice-david`. Defer Python checkers; voice scoring is judge-only.

### `developer`

- **Source skills (13).** `ailly`, `cleanup`, `design`, `feature-test`, `git-workflow`, `initialize`, `is-clean`, `plan`, `red-green-refactor`, `refactor`, `thinking`, `using-developer`, `visual-design`.
- **Profile.** Full triple.
- **Minimal cross-section (4).** `design`, `feature-test`, `plan`, `red-green-refactor`. The phase-gated cluster is the entire reason this plugin exists; covering one phase per gate is the minimum.
- **Discovery cases (6, with paired-blur).**
  - `design-vs-feature-test` — "I have a vague idea, where do I start?" → `design` (not `feature-test`).
  - `feature-test-vs-plan` — "design is approved, the file is checked in, draft removed, what's next?" → `feature-test` (not `plan`, even though both are middle-loop artifacts).
  - `plan-vs-rgr` — "feature test is failing as expected, what now?" → `plan` (not `red-green-refactor`).
  - `rgr-vs-thinking` — "I'm in red-green-refactor and the compiler keeps rejecting my types" → `thinking` (not loop back to `red-green-refactor`).
  - `refactor-vs-rgr` — "tests are green, want to clean up before merging" → `refactor` (not start another `red-green-refactor` step).
  - `is-clean-vs-cleanup` — "is this branch ready for me to start work on something new?" → `is-clean` (a check); "I'm done with this branch" → `cleanup` (an action).
- **Invocation cases (4, fixture-dependent).**
  - `design` — produce a design doc from a one-paragraph problem statement. Script asserts the section headings (Problem Statement, Prior Art, Metrics, Specification, Alternatives, Summary) and the `*Draft YYYY-MM-DD*` marker.
  - `feature-test` — produce a feature-test from a fixture `design.md`. Script asserts the file is a single executable test, encodes one user story, and uses the project's test framework signature.
  - `plan` — produce 3–7 incremental steps from a fixture `design.md` + `feature-test.md`. Script asserts step count in range and that each step has a measurable acceptance criterion.
  - `red-green-refactor` — given a fixture `plan.md` and a stub file, produce a TDD cycle output. Script asserts a single failing assertion, a single minimum change, and no surrounding cleanup.
- **Falsification.** Baseline produces unstructured prose; invocation produces the artifact format with the markers and section structure. The phase fixtures live under `fixtures/` and are referenced from the per-case invocation prompt itself (the prompt embeds the fixture path in its instructions), keeping the assembly prefix uniform across the matrix. The exact mechanism — whether ailly grows a per-case prefix override or fixtures are inlined into the prompt body — is deferred to the developer plugin's feature-test session.
- **Wrinkles.** Fixtures must avoid pre-encoding the answer. A fixture `design.md` for the `feature-test` case should be a *passing* design (clear problem and constraints) but must not include the test's name or skeleton. Fixtures should be reused across the matrix to keep the dependency tree shallow.
- **Seed prompt.**
  > Design `e2e/` for the `developer` plugin. Read the blueprint in `docs/developer/2026-05-29-A-skill-evals/design.md` and the four phase SKILL.md files. Profile is full triple. Produce the six discovery prompts (with paired-blur cases for design/feature-test, feature-test/plan, plan/rgr, rgr/thinking, refactor/rgr, is-clean/cleanup) and the four invocation prompts. Author fixtures under `fixtures/` for the feature-test, plan, and rgr invocation cases. Sketch the four `check_<skill>.py` scripts as placeholders.

### `domain`

- **Source skills (6).** `arrow-of-maturity`, `contracts-and-invariants`, `domain-model`, `glossary`, `ubiquitous-language`, `using-domain`.
- **Profile.** Full triple.
- **Minimal cross-section (4).** `glossary`, `ubiquitous-language`, `domain-model`, `contracts-and-invariants`. `glossary` is the gate skill ("ALL other DDD skills must invoke this skill before introducing terminology"), which gives it a special role in discovery.
- **Discovery cases (5).**
  - `glossary-vs-ubiquitous-language` — "we keep using `customer` and `account` interchangeably, what should I do?" → `glossary` (term-resolution scope) vs. `ubiquitous-language` (broader language-development scope).
  - `domain-model-trigger` — "what are the bounded contexts in this system?" → `domain-model`.
  - `contracts-and-invariants-trigger` — "the API for the payment context shouldn't let an unbalanced ledger through" → `contracts-and-invariants`.
  - `glossary-gate-trigger` — "we want to introduce a new concept called `OrderManifest`" → `glossary` (must run before any other domain skill).
  - `arrow-of-maturity-trigger` — "are we ready to add a separate read model?" → `arrow-of-maturity`.
- **Invocation cases (4).**
  - `glossary` — add a new term with definition, synonyms, ambiguities; script asserts the glossary file format.
  - `ubiquitous-language` — categorize candidate terms by expert-resolution priority; script asserts the three-column output.
  - `domain-model` — produce a bounded-context map; script asserts the Core/Generic/Supporting labels exist and the boundary lines are explicit.
  - `contracts-and-invariants` — append a contract block to a fixture `bounded-context.md`; script asserts the canonical block heading and the at-least-one invariant.
- **Falsification.** Baseline produces ad-hoc domain write-ups without the canonical artifact structure or the glossary cross-references.
- **Wrinkles.** Several invocation cases mutate a fixture file (e.g., add to `bounded-context.md`). The script must read both the prior and post text from the conversation to assert the append happened in the canonical place.
- **Seed prompt.**
  > Design `e2e/` for the `domain` plugin. Read the blueprint in `docs/developer/2026-05-29-A-skill-evals/design.md` and the four cross-section SKILL.md files. Profile is full triple. Pay particular attention to the glossary-gate behaviour — at least one discovery case must check that the model routes terminology-introduction prompts to `glossary` before any other domain skill, even when the prompt looks like it's about modelling.

### `general`

- **Source skills (7).** `conversation`, `dispatching-parallel-agents`, `review`, `using-general`, `writing-paired-skills`, `writing-pattern-skills`, `writing-skills`.
- **Profile.** Full triple, but reduced surface — many skills are pure-routing meta.
- **Minimal cross-section (4).** `writing-skills`, `writing-paired-skills`, `writing-pattern-skills`, `review`. The three `writing-*` skills are a three-way discovery blur ("I want to write a SKILL.md") and the only family with structural invocation. `review` is the producer of a critique with a recognisable shape.
- **Discovery cases (5).**
  - `writing-skills-vs-writing-pattern-skills` — "I want to add a SKILL.md for an HTTP-client builder pattern" → `writing-pattern-skills`.
  - `writing-skills-vs-writing-paired-skills` — "I have a setup-once skill and a per-call-site skill, are they wired right?" → `writing-paired-skills`.
  - `writing-skills-baseline` — "I want to add a general-purpose SKILL.md" → `writing-skills` (the catch-all).
  - `review-trigger` — "I think this PR is ready, can you sanity-check it?" → `review`.
  - `conversation-vs-review` — "let's discuss whether this approach is right" → `conversation` (not `review`, which is a final-pass critique).
- **Invocation cases (4).**
  - `writing-skills` — produce a new SKILL.md from a one-line description. Script asserts the frontmatter has `name:` and `description:`, the description starts with "Use when", and the body has a recognisable structure.
  - `writing-paired-skills` — given a single SKILL.md that mixes two cadences, split into a paired pair. Script asserts two files were produced, both cross-reference each other in the body, and neither stands alone.
  - `writing-pattern-skills` — produce a pattern SKILL.md and the `references/` directory. Script asserts the conventional pattern-skill body sections (Problem, Solution, Common Mistakes, References).
  - `review` — produce a review of a fixture PR diff. Script asserts the rubric structure (placeholder/contradiction/ambiguity/scope checks at minimum).
- **Falsification.** Baseline produces a generic markdown file or critique without the conventional structure.
- **Wrinkles.** `using-general` is the routing prefix and is not itself a discovery target. `dispatching-parallel-agents` is excluded from the cross-section — its output is a tool-call sequence, awkward to assert structurally from a single completion.
- **Seed prompt.**
  > Design `e2e/` for the `general` plugin. Read the blueprint in `docs/developer/2026-05-29-A-skill-evals/design.md` and the four cross-section SKILL.md files. Profile is full triple. The three `writing-*` skills are the heart of discovery — author a paired-blur case for each pair so an edit to one description that drifts toward another lights up exactly that one case.

### `patterns`

- **Source skills (17).** Existing patterns-eval covers `newtype`, `configuring-logging`, `emitting-logs`. Aim: a fuller cross-section for the in-repo harness, independent of the demo-purpose patterns-eval in the ailly repo.
- **Profile.** Full triple.
- **Minimal cross-section (6).** Inherit the existing 3 (newtype, configuring-logging, emitting-logs). Add 3 to cover the remaining hard blurs: `aggregate` vs `unit-of-work` (both about transactional consistency); `parse-dont-validate` vs `type-states` (both about making illegal states unrepresentable); `repository` (the canonical persistence pattern, no near neighbour, but a clean invocation test).
- **Discovery cases (8).**
  - Reuse the six discovery cases from patterns-eval (`newtype-mixed-ids`, `newtype-vs-evs-order-line`, `configuring-first-log-line`, `emitting-order-placed`, `paired-add-propagator`, `paired-log-handler-success`).
  - `aggregate-vs-unit-of-work` — "the order and the line items must commit together or not at all" → `aggregate` (consistency boundary) vs `unit-of-work` (transactional commit). The two pair on transactional-consistency vocabulary but split on whose responsibility it is.
  - `parse-vs-type-states` — "I keep null-checking the same field, how do I make it unnecessary?" → `parse-dont-validate` (one boundary parse) vs `type-states` (lifecycle-phase encoding). They overlap on "make illegal states unrepresentable".
- **Invocation cases (6).**
  - `newtype` — wrap a `String` `UserId`; structural check on private inner primitive, single constructor, no `as` casts. (Reused from patterns-eval.)
  - `configuring-logging` — install the five-layer subscriber registry in main. (Reused from patterns-eval.)
  - `emitting-logs` — emit `order.placed` with semantic-convention keys. (Reused from patterns-eval.)
  - `aggregate` — express a consistency boundary for an order with line items; script asserts a single aggregate root and that line-item access goes through the root.
  - `parse-dont-validate` — turn a `dict` of untrusted input into a parsed domain object; script asserts the boundary `parse(...)` returns a typed value (not bool) and downstream code does not re-check fields.
  - `repository` — produce an in-memory + SQL pair behind one trait/interface; script asserts the domain layer imports only the trait, never a concrete backend.
- **Falsification.** Same as patterns-eval. Baseline produces idiomatic code without the named pattern's structural signature.
- **Wrinkles.** The existing `ailly_two/e2e/patterns-eval` is the demo project for ailly users; this new `patterns/e2e/` is the regression harness for this plugin. They co-exist with different audiences. Copy the prompt files and check scripts forward where they apply (six prompts under `prompts/discovery/`, three under `prompts/invocation/`, three `evals/scripts/check_*.py`); reauthor the assemblies against the live-paths blueprint rather than copying patterns-eval's vended-context assemblies. Do not migrate or modify the demo project.
- **Seed prompt.**
  > Design `e2e/` for the `patterns` plugin. Read the blueprint in `docs/developer/2026-05-29-A-skill-evals/design.md`, the six cross-section SKILL.md files, and the existing `ailly_two/e2e/patterns-eval` for reused content. Profile is full triple. Reuse the three patterns-eval cases verbatim under `prompts/` and add the three new pairs (aggregate vs unit-of-work, parse-dont-validate vs type-states, repository standalone). Author placeholder check scripts for the three new skills.

### `research`

- **Source skills (11).** `archaeology`, `books`, `codebase`, `configuring-books`, `configuring-papers`, `dependencies`, `domain`, `internal`, `papers`, `public`, `using-research`.
- **Profile.** Full triple, with a controlled variable: tool availability.
- **Minimal cross-section (6).** `papers`, `books`, `codebase`, `archaeology`, `configuring-papers`, `configuring-books`. Two paired families (papers + configuring-papers, books + configuring-books) mirror the patterns-eval `emitting-logs`/`configuring-logging` shape exactly.
- **Discovery cases (8).**
  - `papers-question` — "what does the Cambridge ICN paper say about cache invalidation?" → `papers`.
  - `books-question` — "what does Evans's blue book say about Anti-Corruption Layers?" → `books`.
  - `codebase-question` — "where is `OrderManifest` defined?" → `codebase`.
  - `archaeology-question` — "why was the auth middleware removed in 2024?" → `archaeology`.
  - `configuring-papers-trigger` — "I want to set up paper-fetching for this project" → `configuring-papers` (bootstrap) vs `papers` (per-question use).
  - `configuring-books-trigger` — same shape on the books side.
  - `papers-vs-public` — "what's the difference between MAC vs DAC access control?" — answerable from public web, no specific paper. → `public` (not `papers`).
  - `internal-vs-codebase` — "what did we decide in the auth migration ADR?" → `internal` (a doc store, not source code).
- **Invocation cases (6).**
  - `papers` — given a citation, produce DOI / OA-PDF / topic links. Judge confirms the source priority. Script can assert URL shape.
  - `books` — given an ISBN, produce edition info and where to read. Same judge + URL-shape script.
  - `codebase` — given a symbol, produce file paths and line numbers. Script asserts at least one valid `<path>:<line>` reference appears.
  - `archaeology` — given a question about a removal, produce the commit SHA and rationale. Script asserts a 7+ hex SHA appears.
  - `configuring-papers` — produce a configuration plan (MCP probe, HTTP fallback, env vars, smoke test). Script asserts the four-stage structure.
  - `configuring-books` — same shape on the books side.
- **Falsification.** Baseline answers from training data without citations or with hallucinated DOIs. The judge prompts require a verifiable citation; placeholder scripts assert URL shape.
- **Wrinkles.** Many research skills depend on MCP servers being available. The harness must declare which cases are runnable in CI without external credentials. Default: `codebase`, `archaeology` (git-local) are always runnable; `papers`, `books`, `internal` are runnable only when configured. The CI script gates these behind environment variables (e.g. `OPENALEX_EMAIL`, `ANTHROPIC_API_KEY`, `LINEAR_TOKEN`).
- **Seed prompt.**
  > Design `e2e/` for the `research` plugin. Read the blueprint in `docs/developer/2026-05-29-A-skill-evals/design.md` and the six cross-section SKILL.md files. Profile is full triple. Two paired families (papers/configuring-papers, books/configuring-books) need the bootstrap-vs-per-use discovery shape. Tool availability is a controlled variable — annotate which cases require which MCP server or env var and reflect that in `ci.sh` gating.

## Alternatives

**Umbrella project at the repo root (`e2e/skill-evals/`).** Considered and rejected. An umbrella means one big matrix over `plugin × suite × case`, sharing assemblies. It minimises duplicated YAML at the cost of cross-plugin coupling — every plugin's content must be present for any to run, and a CI failure in one plugin reads as a failure across all. Per-plugin projects scale plugin-by-plugin and stay aligned with the source skills.

**Vended SKILL.md copies under `e2e/context/`.** Considered and rejected. Pinning is a real benefit (matches patterns-eval). But every source edit then needs a sync step, and the most likely use case — exercise the current revision — pays that cost on every commit. Live `../skills/...` paths are simpler. Pinning for a sweep can be done with a worktree.

**Symlinks under `e2e/context/`.** Considered and rejected. Layout-preserving but platform-fragile and possibly opaque to ailly's path resolution.

**Single golden plugin (pilot) before the others.** Considered and rejected as a *design* approach, but adopted as the *execution* approach. The design covers all six plugins so the harness shape is fixed; per-plugin sessions implement them one at a time.

**Multi-turn conversations for phase-gated developer skills.** Considered and rejected in favour of fixture files in the prefix. A `kind: file` entry pointing at `fixtures/design.md` is mechanically simpler than a pre-baked assistant turn and keeps the conversation single-shot.

**Judge-only for all invocation arms.** Considered and rejected. Judge prompts are necessary but not sufficient — a well-crafted prompt can talk the judge into a "yes" without actually producing the structural artifact. Script + judge + token budget is the patterns-eval pattern and the new harnesses keep it.

**Minimal AGENTS.md (patterns-eval style).** Considered and rejected. Patterns-eval's four-sentence AGENTS.md sets no operating context, leaving the model in a default-blank state that no real coding agent ever shows it. Routing decisions and structural invocation are sensitive to the prior — a model that thinks it is in Claude Code or Cursor reads `description:` frontmatter under different conventions than a blank-context model does. The richer template pulls the harness closer to in-use conditions; the bare-word grep relaxation in the falsification convention keeps the leak surface manageable.

## Summary

Six new `<plugin>/e2e/` projects, each shaped like `ailly_two/e2e/patterns-eval` but with live `../skills/...` references in place of vended copies. Five plugins run the full discovery + invocation + baseline triple; `characters` runs invocation + baseline only. Per-plugin `ci.sh` drives the assemble → run → eval → report sequence independently.

**Deferred decisions.**

- Concrete prompt text and judge prompts per case. Each per-plugin section's seed prompt is what kicks off the next `developer:design` session that produces those.
- Python check script bodies. Inherit patterns-eval's placeholder convention until the upstream eval-script slice is in place.
- Fixture content for `developer` (design.md / feature-test.md / plan.md fixtures). Authored during the developer plugin's session.
- Model-version sweep strategy. Each `assemblies/*.yaml` pins `claude-sonnet-4-6` for now; sweep tooling lands when the baseline metrics are stable.
- CI workflow at the repo root. Per-plugin `ci.sh` files run locally and per-plugin; a GitHub Actions matrix that calls each `ci.sh` is a follow-up.
- Whether `ailly_two/e2e/patterns-eval` evolves alongside the in-repo `patterns/e2e/`. Default: they diverge by audience (demo vs regression) and patterns-eval is not migrated.
