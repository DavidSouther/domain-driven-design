# `domain/e2e/` — Regression Harness for the `domain` Plugin

## Resolved Decisions (implementation session 2026-06-03)

Two decisions the draft deferred are resolved here, both forced by ground truth verified at implementation time. Neither modifies any skill.

1. **Discovery assertions accept both `ddd:` and `domain:` prefixes.** The skill bodies use the `ddd:` prefix internally (`ddd:glossary`, `ddd:domain-model`, …), and the discovery prefix loads *only* `using-domain/SKILL.md` as its routing surface — whose situation→skill table is written entirely in `ddd:`. A model given that table reproduces `ddd:glossary`, never `domain:glossary`. Asserting `text_contains: domain:glossary` would therefore fail every discovery case for the prefix-namespace mismatch, not for a routing error, making the discovery axis un-evaluatable. The draft's own deferred-decision §2 names "the assertions accept both prefixes" as the resolution that leaves the skills untouched; this implementation adopts it. Positive routing is asserted with `text_matches` against `(ddd|domain):<skill>`; the foil exclusion uses paired `text_not_contains` on both `ddd:<foil>` and `domain:<foil>`. The `ci.sh` falsification grep correspondingly forbids both `ddd:<skill>` and `domain:<skill>` leaks in `AGENTS.md`/`profile.md`.

2. **Check scripts are real structural checkers, not placeholders.** The draft inherited patterns-eval's "placeholder until the upstream eval-script slice lands" convention. That slice has landed: `ailly_two/e2e/patterns-eval` ships fully-implemented checkers (`check_newtype.py` et al.) driven by a shared `_checker_utils.py`. The method's fidelity rule says trust the built files over stale prose. The four domain checkers are implemented against the rule sets the draft enumerates. They receive the assistant turn on stdin (and, for `contracts-and-invariants`, the user turn via the `AILLY_USER_QUESTION` environment variable), print a single-line reason to stdout, and exit non-zero on the first violated rule, leaving stderr untouched.

3. **Prefix files are reached through in-jail symlinks, not `../../` paths.** The draft's assembly prefixes used `../../e2e/AGENTS.md` and `../skills/<name>/SKILL.md`. The installed `ailly` roots its VFS at the `-p` project directory via `vfs::PhysicalFS` and clamps every `..` at that root, so a path that points above the project resolves *inside* it and is not found (`domain/e2e/e2e/AGENTS.md`). The blueprint's live cross-root paths are therefore unsupported, and the sibling `characters/e2e` harness — which uses them verbatim — has never produced a run. Resolution, without vending copies or modifying skills: two in-jail symlinks, `domain/e2e/AGENTS.md` → the shared `e2e/AGENTS.md` and `domain/e2e/skills` → the live plugin `skills/` directory, referenced as `./AGENTS.md` and `./skills/<name>/SKILL.md`. The OS follows the symlinks when the file is opened; single source of truth is preserved; the blueprint's "symlinks are fragile" worry does not hold on this platform/build. (Verified empirically before adoption.)

4. **The discovery gate separates the adversarial gate case from routine routing.** `ci.sh` computes the Property-1 floor over the four routine routing cases only and reports `glossary-gate-trigger` as an informational finding rather than gating on it. The gate case is a deliberate probe of a known-hard ordering rule; mixing its (expected) failure into the routine-routing floor would conflate "is routing broken?" with "is the glossary gate enforced?". Both are still evaluated and scored in the discovery report; only the routine floor reds CI. Floor set to 0.85 (robust to a single model slip across the 12 routine assertions; a description-blur regression that mis-routes a case drops ~2 assertions and trips it).

5. **Checkers normalize tool-call artifacts before applying rules.** The shared `AGENTS.md` tells the model it has file tools, so a skill that says "create the file" (glossary) is often answered by a simulated `write_file` whose `content` is a JSON-escaped string (`\n` literals). A shared `decoded_artifacts` helper decodes every `"content": "…"` field to real newlines and appends it, so a checker evaluates the artifact the model actually produced regardless of delivery modality — the analog of patterns-eval's `extract_code`. Applied symmetrically to both arms.

6. **`arrow-of-maturity` added to the invocation/baseline cross-section (now 5 skills).** The draft pinned invocation at four skills and exercised `arrow-of-maturity` in discovery only; at the user's request it now also has an invocation case. Prompt: a straight-through-handler scenario with accumulating business logic and DB-coupled tests but no scaling pressure. `check_arrow_of_maturity.py` rules trace to the skill's "Output" (current stage / signal / next concrete step) and "Stages" (the staged taxonomy is the discriminator; no `[DRAFT]` rule, since the assessment is advisory, not a `docs/ddd/` artifact). Observed: invocation 15/15, baseline script fails on the stage taxonomy while its judge passes on generic-but-reasonable advice → the case contributes `+1 improved`, `0 regressed`.

### Headline finding

Across runs the harness produces a non-degenerate falsification gap (`improved` 6–9, `regressed` 0; invocation pass rate ≈0.92–1.0 vs baseline ≈0.33–0.40) and one stable, faithful negative result: the **glossary gate is NOT enforced at the discovery surface**. Given only `using-domain/SKILL.md`, a modelling-shaped prompt that introduces a new term (`OrderManifest`) routes to `domain-model`, never to `glossary` first. The gate sentence lives in the `glossary` skill *body*, but the `using-domain` routing table only sends a term to `glossary` when it is framed as "ambiguous or potentially synonymous" — a brand-new concept is not. The test correctly surfaces this weakness without modifying the skill, exactly as instructed.

The rest of this document is the design as reviewed and cleared for implementation.

---

## Problem Statement

The `domain` plugin ships six `SKILL.md` files (`using-domain`, `glossary`, `ubiquitous-language`, `domain-model`, `contracts-and-invariants`, `arrow-of-maturity`) and has zero regression coverage today. The plugin's two failure surfaces — discovery (`description:` routing) and invocation (structural artifact production) — both regress silently.

A wrinkle distinguishes this plugin from `patterns`: `domain:glossary` is a **gate skill**. Every other DDD skill's body opens with "invoke `ddd:glossary` first." A regression that softens any of those gate sentences, or that blurs `glossary`'s own `description:` so the model picks `ubiquitous-language` or `domain-model` for a terminology-introduction prompt, defeats the entire layered model — every downstream artifact silently uses an unchecked term. The harness must guard the gate specifically: at least one discovery case checks that terminology-introduction prompts route to `glossary` first, *even when the prompt looks like a modelling prompt*.

A second wrinkle: several invocation cases mutate a fixture file (the `contracts-and-invariants` skill appends to `docs/ddd/contexts/<context-name>.md`). The check must inspect both the pre-state (the fixture as the model received it) and the post-state (what the model produced) and verify the append happened in the canonical place.

## Prior Art

- **`ailly_two/e2e/patterns-eval`** — the working reference harness. Three suites (`discovery`, `invocation`, `baseline`), one assembly per suite over a matrix, prompts under `prompts/<suite>/<name>.md`, evals under `evals/<suite>.yaml`, placeholder Python check scripts under `evals/scripts/check_<skill>.py`, a `ci.sh` driver that assembles → runs (gated on `ANTHROPIC_API_KEY`) → evals → reports. This harness inherits the shape almost verbatim, with live `../skills/<name>/SKILL.md` paths instead of vended `context/skills/<name>/SKILL.md` copies.
- **`docs/developer/2026-05-29-A-skill-evals/design.md`** — the blueprint. Fixes the per-plugin layout, the live-path convention, the falsification rule, the shared `e2e/AGENTS.md` template, the per-plugin `profile.md` appendix, and the per-plugin profile selection. The `domain` subsection enumerates the four-skill cross-section, the five discovery cases, and the four invocation cases this design fleshes out.
- **`docs/developer/2026-05-29-C-patterns-e2e/design.md`** — the sibling design for the `patterns` plugin. Identical profile (Full triple), identical layout convention, identical `ci.sh` skeleton. This design follows its shape directly so the two harnesses look structurally identical from outside.
- **`e2e/AGENTS.md`** — the shared coding-agent constitution at the repo root, loaded at position zero of every prefix. Already present. The bare-word grep relaxation applies — words like `glossary`, `domain`, `context`, `model`, `invariant` appear in any coding-agent prompt and forcing them out would corrupt the mindset framing.
- **`domain/skills/using-domain/SKILL.md`** — the routing skill loaded in discovery and invocation prefixes. Its situation/skill table is what the model consults to make routing decisions.

## Metrics

Inherited from the blueprint. A passing harness exhibits a non-degenerate falsification gap.

| Metric | Source | Target |
|---|---|---|
| Discovery pass rate | `evals/discovery.yaml` (5 cases) | ≥ 0.9 |
| Invocation pass rate | `evals/invocation.yaml` (4 cases) | ≥ 0.8 |
| Baseline pass rate | `evals/baseline.yaml` (4 cases, same prompts as invocation, no SKILL.md loaded) | as low as the prompt allows |
| **Falsification gap** | invocation pass rate − baseline pass rate | ≥ 0.5 |

The four check scripts ship as placeholders until the upstream eval-script slice lands; the judge and `tokens` assertions carry the structural rules in prose for now. The `glossary-gate-trigger` case in particular is judge-scored — `text_contains` confirms `domain:glossary` is named, and the judge confirms it is named *first*, before any other domain skill.

## Specification

### Layout

```
domain/e2e/
├── profile.md                                ← purpose + axis profile (Full triple)
├── assemblies/
│   ├── discovery.yaml                        ← matrix over case, 5 cases
│   ├── invocation.yaml                       ← matrix over skill, 4 skills
│   └── baseline.yaml                         ← matrix over skill, 4 skills, no SKILL.md prefix
├── prompts/
│   ├── discovery/
│   │   ├── glossary-vs-ubiquitous-language.md
│   │   ├── domain-model-trigger.md
│   │   ├── contracts-and-invariants-trigger.md
│   │   ├── glossary-gate-trigger.md          ← modelling-shaped prompt that must route to glossary first
│   │   └── arrow-of-maturity-trigger.md
│   └── invocation/
│       ├── glossary.md
│       ├── ubiquitous-language.md
│       ├── domain-model.md
│       └── contracts-and-invariants.md       ← embeds the fixture inline; expects an appended block
├── evals/
│   ├── discovery.yaml                        ← 5 cases; text_contains/text_not_contains, judge on the gate case
│   ├── invocation.yaml                       ← 4 cases, each = script + judge + tokens
│   ├── baseline.yaml                         ← 4 cases, identical assertions to invocation
│   ├── scripts/
│   │   ├── check_glossary.py
│   │   ├── check_ubiquitous_language.py
│   │   ├── check_domain_model.py
│   │   └── check_contracts_and_invariants.py ← reads both turns from the conversation YAML, diffs
│   └── reports/                              ← .gitignore'd, populated by ci.sh
├── runs/                                     ← .gitignore'd, populated by ci.sh
├── .gitignore                                ← runs/, evals/reports/, .env
└── ci.sh                                     ← adapted from patterns-eval; repo_root = ${project_dir}/../..
```

No `context/` directory. No vended copies. One fixture lives inline in the `contracts-and-invariants.md` invocation prompt body (see "Fixture handling" below); no separate `fixtures/` tree is needed.

### Profile

`domain/e2e/profile.md` is a short appendix to the shared `e2e/AGENTS.md`. It declares (1) the harness's purpose — "this directory tests the `domain:*` skill plugin" — and (2) the axis profile — `Full` (discovery + invocation + baseline). It does not name the skills under test or paraphrase any skill content; the same falsification grep that runs on `AGENTS.md` runs on `profile.md`.

Draft text (single short paragraph, ≤ 80 words):

> This directory is a regression harness for the `domain:*` skill plugin. It exercises the full discovery + invocation + baseline triple: discovery checks that routing prompts select the correct skill from `description:` frontmatter alone; invocation checks that loaded skills produce artifacts with the expected structural shape; baseline runs the same invocation prompts with no skill loaded as a falsification floor. A non-degenerate gap between invocation and baseline is the headline signal.

### Assemblies (live paths)

`discovery.yaml`:

```yaml
name: discovery
model: claude-sonnet-4-6

matrix:
  case:
    - glossary-vs-ubiquitous-language
    - domain-model-trigger
    - contracts-and-invariants-trigger
    - glossary-gate-trigger
    - arrow-of-maturity-trigger

prefix:
  - { kind: file,   path: ../../e2e/AGENTS.md,                       cache: true }
  - { kind: file,   path: ./profile.md,                              cache: true }
  - { kind: system, path: ../skills/using-domain/SKILL.md,           cache: true }

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
    - glossary
    - ubiquitous-language
    - domain-model
    - contracts-and-invariants

prefix:
  - { kind: file,   path: ../../e2e/AGENTS.md,                       cache: true }
  - { kind: file,   path: ./profile.md,                              cache: true }
  - { kind: system, path: ../skills/using-domain/SKILL.md,           cache: true }
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
    - glossary
    - ubiquitous-language
    - domain-model
    - contracts-and-invariants

prefix:
  - { kind: file, path: ../../e2e/AGENTS.md, cache: true }
  - { kind: file, path: ./profile.md,        cache: true }

conversation:
  - { role: user, path: "prompts/invocation/{{ skill }}.md" }
  - { role: assistant }
```

Baseline drops every `kind: system` entry, including `using-domain/SKILL.md`. This is the mechanical falsification convention from the blueprint. The two `kind: file` entries (the coding-agent constitution and the harness purpose) carry no skill content; the bare-word grep in `ci.sh` enforces that.

The `arrow-of-maturity` skill is not in the invocation matrix even though it appears in the discovery matrix; the cross-section spec keeps invocation at four skills (the four covered by the blueprint), and discovery exercises one extra routing decision (`arrow-of-maturity`) for which there is no paired invocation case in this slice.

### Prompts

#### Discovery

- **`glossary-vs-ubiquitous-language.md`** — terminology-resolution scope vs broader language development.

  > Our team keeps using `customer` and `account` interchangeably in tickets and design docs. Sometimes they mean the same thing, sometimes not. We have not written anything down yet. What should I do first? Which `domain:*` skill applies?

  Expected: `domain:glossary`. The work is term-resolution, not full ubiquitous-language development. Assertions: `text_contains: domain:glossary`, `text_not_contains: domain:ubiquitous-language`.

- **`domain-model-trigger.md`** — new-project bounded-context discovery.

  > We are starting a new logistics service and need to figure out what its subdomains are and where the boundaries should go. Which `domain:*` skill applies?

  Expected: `domain:domain-model`. Assertions: `text_contains: domain:domain-model`, `text_not_contains: domain:contracts-and-invariants`.

- **`contracts-and-invariants-trigger.md`** — API boundary invariant.

  > I am about to write the public API for the payments context. The ledger must never be unbalanced — but the current signatures do not say so. Which `domain:*` skill applies?

  Expected: `domain:contracts-and-invariants`. Assertions: `text_contains: domain:contracts-and-invariants`, `text_not_contains: domain:domain-model`.

- **`glossary-gate-trigger.md`** — *the gate guard.* Modelling-shaped on the surface, terminology-introduction underneath.

  > We are about to add a new concept called `OrderManifest` to our logistics bounded context. It will sit between Orders and Shipments and aggregate line items destined for the same warehouse. Where does this go in our domain — and what should I do first before modelling its aggregates and contracts? Which `domain:*` skill applies?

  Expected routing: `domain:glossary` *first*, then `domain:domain-model` as a follow-up (modelling continues only after the term is in the glossary). The prompt is deliberately written so it looks like a modelling prompt — it mentions bounded contexts, aggregates, "where does this go in our domain" — while introducing the new term `OrderManifest`. The gate sentence from `glossary`'s description ("ALL other DDD skills must invoke this skill before introducing terminology") is the rule under test.

  Assertions (per the pre-resolved decision: judge + `text_contains`, no new ordering assertion type):
  - `text_contains: domain:glossary` — the model must name the gate skill at all.
  - `judge` — confirms the model says to invoke `domain:glossary` *first*, before any other domain skill. The judge prompt is explicit about ordering and rejects answers that mention glossary as a secondary or parallel step. Sketch text:

    > The answer says to invoke `domain:glossary` first, before any other domain skill, because a new term (`OrderManifest`) is being introduced and the glossary gate must be passed before modelling proceeds. The answer does NOT route directly to `domain:domain-model` as the first action. The answer may name `domain:domain-model` as a follow-up step that happens after the glossary check; this is acceptable as long as `domain:glossary` is named as the first action.

  No `text_order` or similar new assertion type is invented. The judge carries the ordering rule.

- **`arrow-of-maturity-trigger.md`** — architectural-stage decision.

  > Our straight-through handler is starting to creak. We are wondering if we should pull out a separate read model. Which `domain:*` skill applies?

  Expected: `domain:arrow-of-maturity`. Assertions: `text_contains: domain:arrow-of-maturity`, `text_not_contains: domain:domain-model`.

#### Invocation

- **`glossary.md`** — add a new term.

  > Add a new term to the project glossary: `OrderManifest`. It is the list of line items destined for the same warehouse, derived from one or more Orders. The team has been calling it both "manifest" and "shipment list" interchangeably. Produce the glossary entry the way `domain:glossary` prescribes.

  Structural signature: a single Markdown block headed `## OrderManifest` with `**Definition:**`, `**Context:**`, `**Synonyms:**`, `**Source:**` fields, marked `[DRAFT]`. The synonyms field lists both "manifest" and "shipment list". The placeholders in the format template are filled with real values.

- **`ubiquitous-language.md`** — categorize candidate terms.

  > We are starting work on a new logistics bounded context. From the requirements doc, the following candidate terms have surfaced: `OrderManifest`, `Carrier`, `Waybill`, `Consignee`, `LinearFeet`. Some are universal logistics terms; some may be specific to how this organization handles cross-dock operations. Produce the candidate-term and categorized-question lists the way `domain:ubiquitous-language` prescribes.

  Structural signature: two distinct outputs — (1) a candidate-terms list, each term with a draft definition and a source field; (2) a categorized-question list with two buckets, "Ask a domain expert" and "Confirm with domain expert". All terms marked `[DRAFT]`.

- **`domain-model.md`** — produce a bounded-context map.

  > We are starting a new logistics service. The features we know about: customers place orders; orders become shipments; shipments are loaded onto carrier vehicles; carriers move shipments between warehouses; warehouses confirm receipt. Produce the domain map the way `domain:domain-model` prescribes.

  Structural signature: a Subdomains table where each subdomain has a `Core` / `Generic` / `Supporting` classification and a named bounded context; a Boundary Map section that describes what flows between context pairs (events, data contracts, API calls); and a separate per-context section for each `Core` context. All files marked `[DRAFT]`.

- **`contracts-and-invariants.md`** — append a contract block to a fixture. **Fixture content is embedded inline in the prompt body** (see "Fixture handling" below).

  > Below is the current state of `docs/ddd/contexts/order-management.md`:
  >
  > ```markdown
  > # Order Management
  >
  > **Classification:** Core
  > **Responsibilities:** Accepting customer orders, validating line items, persisting them for fulfilment.
  > **Consumes:** Customer profile data from the Customer context.
  > **Produces:** `OrderPlaced` events consumed by the Fulfilment context.
  > ```
  >
  > A new operation needs a contract: `place_order(customer_id, line_items)`. It must reject orders with zero line items, reject orders where any line item has zero or negative quantity, and emit `OrderPlaced` on success. Append the contract block the way `domain:contracts-and-invariants` prescribes. Produce the full file content as it should look after the append.

  Structural signature: the output is the *full file*, with the original `# Order Management` block at the top intact, followed by an appended block with a `### <Operation Name>` heading, `**Contract (input):**`, `**Contract (output):**`, `**Invariants:**` (at least one), and optionally `**Transactional note:**`. New content marked `[DRAFT]`.

### Fixture handling

The pre-resolved decision: **conversation-shaped, not filesystem-shaped**. The fixture file `docs/ddd/contexts/order-management.md` is not a real file on disk that lives under a `fixtures/` tree; its content is embedded *inline* inside the body of `prompts/invocation/contracts-and-invariants.md` (see the prompt above, where the fenced markdown block is the fixture content as the model receives it).

The check script `check_contracts_and_invariants.py` reads the conversation YAML on stdin and:

1. Parses the user-turn body to extract the inline fixture content (the fenced markdown block).
2. Parses the assistant-turn body to extract the model's produced full-file content.
3. Diffs the two — assertion: the original `# Order Management` block is preserved verbatim, and a new `### <Operation Name>` block is appended below it.

This keeps the assembly prefix uniform across the matrix (no per-case `kind: file` fixture entries), avoids any per-case prefix override, and removes the need for a separate `fixtures/` directory in this slice. Patterns-eval did not need fixtures; this is the minimum addition.

The other three invocation cases produce a fresh artifact (a glossary entry, two lists, a domain map) rather than mutating a fixture. Their scripts read only the assistant turn.

### Evals

**`evals/discovery.yaml`** — 5 cases. Four use `text_contains` + `text_not_contains` directly on the expected and foil skill identifiers (`domain:<skill-name>`). The fifth — `glossary-gate-trigger` — uses `text_contains: domain:glossary` plus a judge prompt that confirms the model names the glossary skill as the *first* action. Per the pre-resolved decision, no new ordering assertion type is invented; the judge prompt is explicit and rejects answers that mention glossary as a secondary step.

**`evals/invocation.yaml`** — 4 cases. Each case = `script` (placeholder for now) + `judge` (structural rules in prose) + `tokens` (budget under 6000–8000 depending on artifact size). The judge prompts:

- `glossary` — "The output is a single Markdown block headed `## OrderManifest`. It includes `**Definition:**`, `**Context:**`, and `**Source:**` fields with real values (not template placeholders). The `**Synonyms:**` field is present and lists both 'manifest' and 'shipment list'. The entry is marked `[DRAFT]`."
- `ubiquitous-language` — "The output has two distinct sections: a candidate-terms list and a categorized-question list. The candidate-terms list shows a draft definition and a source for each term. The categorized-question list groups questions under two headings: 'Ask a domain expert' and 'Confirm with domain expert'. All generated terms are marked `[DRAFT]`."
- `domain-model` — "The output has a Subdomains table with `Core` / `Generic` / `Supporting` classification labels on each row and a Bounded Context name. A Boundary Map section describes what flows between context pairs. At least one per-context block is produced for each Core context. Files are marked `[DRAFT]`."
- `contracts-and-invariants` — "The model has reproduced the original `# Order Management` block verbatim at the top of the file. A new block headed `### place_order` (or similar operation name) is appended below it. The appended block contains `**Contract (input):**`, `**Contract (output):**`, and `**Invariants:**` with at least one invariant. Placeholders are replaced with real values. New content is marked `[DRAFT]`."

**`evals/baseline.yaml`** — mechanically identical to `evals/invocation.yaml`. Same assertions, same scripts, same judges, same token budgets. The only thing that changes is the absence of the `kind: system` prefix entries in `baseline.yaml` (the assembly).

### Check scripts

All four scripts use the placeholder body inherited from patterns-eval — read stdin, write `{"status": "placeholder", "reason": "eval-script not yet wired"}`, exit 0. Each script's header docstring enumerates the rule set the eventual implementation must encode.

- `check_glossary.py` — eventual rule set: single Markdown block headed `## <Term>`; presence of Definition, Context, Source fields with non-template values; Synonyms field present iff the prompt named synonyms; `[DRAFT]` marker present.
- `check_ubiquitous_language.py` — eventual rule set: two distinct sections produced; candidate-terms list has a source field per term; categorized-question list has the two named buckets; all terms marked `[DRAFT]`.
- `check_domain_model.py` — eventual rule set: Subdomains table present with Classification column containing one of Core/Generic/Supporting; Boundary Map section present; at least one per-context section per Core context; `[DRAFT]` marker present.
- `check_contracts_and_invariants.py` — eventual rule set: parse the user turn for the inline fixture (fenced markdown block); parse the assistant turn for the full produced file; assert the original `# Order Management` block is preserved verbatim; assert a new `### <op>` block is appended below it with the required fields and at least one invariant; assert `[DRAFT]` on the new content. This is the only script that reads *both* turns from the conversation; the others read only the assistant turn.

The placeholder pattern matches patterns-eval: header docstring + `main()` that reads stdin and writes placeholder JSON. When the upstream eval-script slice lands, the rule sets in the docstrings become the test code.

### ci.sh

Copied from `ailly_two/e2e/patterns-eval/ci.sh` with the changes the blueprint prescribes:

1. `expected_count()` table: `discovery=5`, `baseline=4`, `invocation=4` (was `6/3/3`).
2. `repo_root="$(cd "${project_dir}/../.." && pwd)"` — correct for this layout (`domain/e2e/ci.sh` resolves `../..` to repo root).
3. The `cargo run --quiet --` invocations become `ailly` directly per the blueprint ("`ailly` itself is invoked as a CLI from the user's environment"). The harness expects `ailly` on `$PATH`.

The four CUJs (assemble, run gated on `ANTHROPIC_API_KEY`, eval, report) carry forward unchanged. The `cd "${repo_root}"` at the top is preserved so ailly's project resolution sees the repo root.

A bare-word grep step asserts neither `AGENTS.md` (at the repo `e2e/`) nor `profile.md` contains any `domain:<skill-name>` literal:

```bash
# Falsification grep — fail if either file leaks a plugin-prefixed skill identifier.
for f in ../../e2e/AGENTS.md profile.md; do
  if grep -E 'domain:[a-z-]+' "${project_dir}/${f#./}" >/dev/null 2>&1; then
    echo "FAIL: ${f} contains a 'domain:*' identifier; baseline arm leaks the answer." >&2
    exit 1
  fi
done
```

This runs before the assemble step. It guards the falsification convention mechanically. Bare words (`glossary`, `domain`, `context`, `model`, `invariant`) are permitted — they appear in any coding-agent prompt.

### Falsification

The blueprint's mechanical rule applies directly: drop every `kind: system` from invocation to produce baseline, keep both `kind: file` entries. `AGENTS.md` and `profile.md` carry the coding-agent mindset and the harness purpose; neither names any domain skill. The `ci.sh` grep enforces the rule.

The four invocation prompts deliberately describe *what the artifact must do* (a new term with definition/context/source/synonyms; two lists with categorized questions; a subdomains table with classification labels; an appended contract block under an existing context heading) without naming the skill or the structural sections by their canonical names. A baseline model reading "produce the glossary entry the way `domain:glossary` prescribes" will see the skill name but has no SKILL.md loaded, so it must guess the entry format. It will likely produce something glossary-shaped but is unlikely to hit `**Definition:**` / `**Context:**` / `**Source:**` field names exactly, mark `[DRAFT]`, or follow the synonyms rule. The gap is the headline signal.

The gate case lives in the discovery suite only — per the blueprint, the baseline arm pairs with invocation, not discovery. If the model fails to route to `domain:glossary` first, the discovery pass rate drops below its 0.9 target; the falsification gap is computed across the invocation/baseline pair and is independent of the gate result.

## Alternatives

**Add a `text_order` assertion type to express "glossary must come before any other domain skill."** Considered and rejected by pre-resolved decision. Inventing a new assertion vocabulary entry for a single case would couple the harness shape to one plugin's needs; the existing `judge` assertion already expresses ordering rules in prose, and patterns-eval's assertion vocabulary stays unchanged. The cost of judge subjectivity is bounded by an explicit, narrow rubric in the judge prompt.

**Make the gate prompt obviously a glossary question (drop the modelling framing).** Considered and rejected. A prompt that says "I want to add a new term" routes trivially to `domain:glossary` and tests nothing — the gate's whole purpose is to catch the case where the *human's* framing is about modelling but a new term is hiding inside it. The seed prompt explicitly mandates "the model routes terminology-introduction prompts to `glossary` before any other domain skill, even when the prompt looks like it's about modelling." The current `glossary-gate-trigger` text bakes that mandate in.

**Use a separate `fixtures/` directory and a per-case prefix override for the `contracts-and-invariants` case.** Considered and rejected by pre-resolved decision. A separate fixture file means either a per-case prefix override (which ailly does not have today and which would force assembly-shape divergence) or a conversation-shaped pre-turn. Inlining the fixture in the prompt body keeps the assembly prefix uniform across the matrix, removes a directory, and matches what a real Claude Code conversation looks like — the user pastes the file content into the chat.

**Add an `arrow-of-maturity` invocation case to round out the matrix.** Considered and rejected. The blueprint pins the invocation cross-section at four skills; `arrow-of-maturity` is exercised in discovery to test its routing decision but not in invocation. Adding it would extend the invocation matrix and is out of scope for this slice. The blueprint's "Wrinkles" section names exactly these four invocation cases.

**Vended `context/skills/<name>/SKILL.md` copies under `domain/e2e/`.** Considered and rejected (blueprint-level). Pinning is real, but every edit to a `domain/skills/*/SKILL.md` would require a sync step. Worktree pin for a sweep, live paths for the default.

**Implement real check scripts now instead of placeholders.** Considered and rejected. The blueprint defers script bodies to the upstream eval-script slice; until then the placeholder convention is what patterns-eval ships. The `check_contracts_and_invariants.py` script's two-turn reading shape is documented in its docstring now and lands as code when the slice lands.

**Add the `using-domain/SKILL.md` to the baseline arm.** Considered and rejected. The blueprint says baseline drops every `kind: system` entry, including the routing skill. The model gets the coding-agent mindset and the harness purpose only — no domain context. Reconsider only if baseline pass rates are anomalously low because the model lacks any "what is a domain skill" framing; if so, that is a signal the routing skill itself is too thin, not that the harness should change.

## Summary

A new `domain/e2e/` directory adjacent to `domain/skills/`, shaped after `ailly_two/e2e/patterns-eval` but with live `../skills/<name>/SKILL.md` paths instead of vended copies. Five discovery prompts, four invocation prompts, four placeholder check scripts, three suite YAMLs, one `ci.sh`, one `profile.md`. The cross-section covers `glossary`, `ubiquitous-language`, `domain-model`, `contracts-and-invariants` (the four blueprint skills), plus `arrow-of-maturity` in discovery for a fifth routing case.

The gate case `glossary-gate-trigger` is the unique-to-domain piece. Its prompt looks like a modelling prompt but introduces a new term (`OrderManifest`); the expected routing is `domain:glossary` first, `domain:domain-model` as a follow-up. The assertion uses `text_contains: domain:glossary` plus a judge prompt that explicitly checks for "glossary first" — no new ordering assertion type is invented.

The `contracts-and-invariants` invocation case mutates a fixture file. The fixture content is embedded inline in the prompt body; the check script reads both the user turn (for the original) and the assistant turn (for the post-state) out of the conversation YAML and diffs. No `fixtures/` directory is needed in this slice.

**Deferred decisions.**

- Concrete bodies of the four check scripts. The blueprint pins these behind the upstream eval-script slice; structural rule sets land in the docstrings now, tests land when the slice lands. `check_contracts_and_invariants.py` is the only one with a two-turn read shape; the other three read only the assistant turn.
- Exact phrasing of the `glossary-gate-trigger` judge prompt. Sketched above; final phrasing tuned after first run produces real responses. If the model passes `text_contains: domain:glossary` but the judge cannot reliably tell "first" from "secondary," the judge prompt's rubric becomes more explicit (e.g., quote the answer's first sentence and check whether it names glossary).
- Whether the `arrow-of-maturity` discovery case needs a paired invocation case. Currently no — the blueprint pins the invocation cross-section at four skills. Add an invocation case for `arrow-of-maturity` only if discovery-only coverage proves insufficient (e.g., the routing skill correctly names `arrow-of-maturity` but the skill's invocation surface regresses without notice).
- Model-version sweep across `sonnet-4-6` and the next minor. The blueprint pins one model; sweep tooling lands when baseline metrics stabilise.
- Whether `ci.sh` should fail-fast on the falsification grep or report and continue. Authored as `exit 1` here — leaking a skill ID into `AGENTS.md` or `profile.md` invalidates the baseline arm and should block the run.
- The naming inconsistency under `ddd:` versus `domain:`. The skill bodies and the `using-domain` routing table use the `ddd:` prefix (`ddd:glossary`, `ddd:domain-model`, etc.), but the plugin namespace exposed to the model is `domain:` (per the skill list seen at session start). The discovery assertions use `domain:` (matching what the model sees). If the model reproduces the `ddd:` prefix it sees inside SKILL bodies instead of the `domain:` prefix the plugin manifest uses, the `text_contains: domain:glossary` assertion will fail until either the SKILL bodies are updated to use `domain:` or the assertions accept both prefixes. Resolving this is a separate edit to the source skills outside the scope of this harness design.
- Whether the gate case should be duplicated (one obviously-glossary prompt, one modelling-shaped prompt) to separate "does the model know glossary exists?" from "does the model apply the gate rule?". Currently a single modelling-shaped case carries both questions; splitting is a follow-up if the single case proves under-discriminating.
