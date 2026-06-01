# `patterns/e2e/` — Regression Harness for the `patterns` Plugin

*DRAFT 2026-05-29*

## Problem Statement

The `patterns` plugin ships seventeen `SKILL.md` files. The only existing coverage is `ailly_two/e2e/patterns-eval`, which exercises three skills (`newtype`, `configuring-logging`, `emitting-logs`) and lives in a separate repository as a *demo project for ailly users*. There is no in-repo regression harness for this plugin, so any edit to a `description:` line or a structural rule in a SKILL body can silently regress without notice. The other fourteen patterns skills are entirely uncovered.

The harness must catch two failure surfaces — routing regressions from blurred `description:` frontmatter, and invocation regressions from softened structural constraints — and it must do so against the *live* `patterns/skills/*/SKILL.md` tree so an author's next edit is graded on the next run with no vending step.

`ailly_two/e2e/patterns-eval` stays where it is, unmodified, as the demo project for the ailly audience. This is a separate harness with a different audience (regression coverage for this plugin), reusing patterns-eval's prompt text and check-script placeholders forward where they apply.

## Prior Art

- **`ailly_two/e2e/patterns-eval`** — the shape this harness inherits. Three suites (`discovery`, `invocation`, `baseline`), one assembly per suite over a matrix, prompts under `prompts/<suite>/<name>.md`, evals under `evals/<suite>.yaml`, placeholder Python check scripts under `evals/scripts/check_<skill>.py`, a `ci.sh` driver that assembles → runs (gated on `ANTHROPIC_API_KEY`) → evals → reports. The three covered skills' prompts and scripts copy forward verbatim; the assemblies are reauthored against live `../skills/<name>/SKILL.md` paths instead of vended `context/skills/<name>/SKILL.md` copies.
- **`docs/developer/2026-05-29-A-skill-evals/design.md`** — the blueprint that fixes the per-plugin layout, the live-path convention, the falsification rule, the `e2e/AGENTS.md` shared template, the `profile.md` per-plugin appendix, and the per-plugin profile selection. The `patterns` section in that doc enumerates the six-skill cross-section and the eight discovery / six invocation cases this design fleshes out.
- **`e2e/AGENTS.md`** — the shared coding-agent constitution, loaded at position zero of every prefix. Already present at the repo root. The bare-word grep relaxation in the falsification convention applies because words like `repository`, `aggregate`, and `parse` appear in any coding-agent prompt.

## Metrics

Inherited from the blueprint. A passing harness exhibits a non-degenerate falsification gap.

| Metric | Source | Target |
|---|---|---|
| Discovery pass rate | `evals/discovery.yaml` (8 cases) | ≥ 0.9 |
| Invocation pass rate | `evals/invocation.yaml` (6 cases) | ≥ 0.8 |
| Baseline pass rate | `evals/baseline.yaml` (6 cases, same prompts as invocation, no SKILL.md loaded) | as low as the prompt allows |
| **Falsification gap** | invocation pass rate − baseline pass rate | ≥ 0.5 |

The check scripts for `newtype`, `configuring-logging`, `emitting-logs`, `aggregate`, `parse-dont-validate`, and `repository` ship as placeholders today; until the upstream eval-script slice lands, the gap is read primarily from the judge and `tokens` assertions per case. Once scripts are wired, structural assertions dominate.

## Specification

### Layout

```
patterns/e2e/
├── profile.md                              ← purpose + axis profile (Full triple)
├── assemblies/
│   ├── discovery.yaml                      ← matrix over case, 8 cases
│   ├── invocation.yaml                     ← matrix over skill, 6 skills
│   └── baseline.yaml                       ← matrix over skill, 6 skills, no SKILL.md prefix
├── prompts/
│   ├── discovery/
│   │   ├── newtype-mixed-ids.md            ← copied verbatim from patterns-eval
│   │   ├── newtype-vs-evs-order-line.md    ← copied verbatim
│   │   ├── configuring-first-log-line.md   ← copied verbatim
│   │   ├── emitting-order-placed.md        ← copied verbatim
│   │   ├── paired-add-propagator.md        ← copied verbatim
│   │   ├── paired-log-handler-success.md   ← copied verbatim
│   │   ├── aggregate-vs-unit-of-work.md    ← new
│   │   └── parse-vs-type-states.md         ← new
│   └── invocation/
│       ├── newtype.md                      ← copied verbatim
│       ├── configuring-logging.md          ← copied verbatim
│       ├── emitting-logs.md                ← copied verbatim
│       ├── aggregate.md                    ← new
│       ├── parse-dont-validate.md          ← new
│       └── repository.md                   ← new
├── evals/
│   ├── discovery.yaml                      ← 8 cases, mostly text_contains / text_not_contains, judge on the 2 new pairs
│   ├── invocation.yaml                     ← 6 cases, each = script + judge + tokens
│   ├── baseline.yaml                       ← 6 cases, identical assertions to invocation
│   ├── scripts/
│   │   ├── check_newtype.py                ← copied verbatim from patterns-eval (placeholder)
│   │   ├── check_configuring_logging.py    ← copied verbatim (placeholder)
│   │   ├── check_emitting_logs.py          ← copied verbatim (placeholder)
│   │   ├── check_aggregate.py              ← new placeholder, same shape
│   │   ├── check_parse_dont_validate.py    ← new placeholder
│   │   └── check_repository.py             ← new placeholder
│   └── reports/                            ← .gitignore'd, populated by ci.sh
├── runs/                                   ← .gitignore'd, populated by ci.sh
├── .gitignore                              ← runs/, evals/reports/, .env
└── ci.sh                                   ← adapted from patterns-eval; repo_root = ${project_dir}/../..
```

No `context/` directory. No vended copies. No fixtures (none of the six skills are phase-dependent the way the `developer` plugin's are).

### Profile

`patterns/e2e/profile.md` is a short appendix to the shared `e2e/AGENTS.md`. It declares (1) the harness's purpose — "this directory tests the `patterns:*` skill plugin" — and (2) the axis profile — `Full` (discovery + invocation + baseline). It does not name the skills under test or paraphrase any skill content; the same falsification grep that runs on `AGENTS.md` runs on `profile.md`.

Draft text (single short paragraph, ≤ 80 words):

> This directory is a regression harness for the `patterns:*` skill plugin. It exercises the full discovery + invocation + baseline triple: discovery checks that routing prompts select the correct skill from `description:` frontmatter alone; invocation checks that loaded skills produce code with the expected structural signature; baseline runs the same invocation prompts with no skill loaded as a falsification floor. A non-degenerate gap between invocation and baseline is the headline signal.

### Assemblies (live paths)

`discovery.yaml`:

```yaml
name: discovery
model: claude-sonnet-4-6

matrix:
  case:
    - newtype-mixed-ids
    - newtype-vs-evs-order-line
    - configuring-first-log-line
    - emitting-order-placed
    - paired-add-propagator
    - paired-log-handler-success
    - aggregate-vs-unit-of-work
    - parse-vs-type-states

prefix:
  - { kind: file,   path: ../../e2e/AGENTS.md,                       cache: true }
  - { kind: file,   path: ./profile.md,                              cache: true }
  - { kind: system, path: ../skills/using-patterns/SKILL.md,         cache: true }

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
    - newtype
    - configuring-logging
    - emitting-logs
    - aggregate
    - parse-dont-validate
    - repository

prefix:
  - { kind: file,   path: ../../e2e/AGENTS.md,                       cache: true }
  - { kind: file,   path: ./profile.md,                              cache: true }
  - { kind: system, path: ../skills/using-patterns/SKILL.md,         cache: true }
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
    - newtype
    - configuring-logging
    - emitting-logs
    - aggregate
    - parse-dont-validate
    - repository

prefix:
  - { kind: file, path: ../../e2e/AGENTS.md, cache: true }
  - { kind: file, path: ./profile.md,        cache: true }

conversation:
  - { role: user, path: "prompts/invocation/{{ skill }}.md" }
  - { role: assistant }
```

The two `kind: file` entries are common to all three assemblies; the discovery and invocation assemblies add `using-patterns/SKILL.md` (and invocation adds the named skill). Baseline drops every `kind: system` entry. This is the mechanical falsification convention from the blueprint.

### Prompts

**Discovery, copied verbatim from `ailly_two/e2e/patterns-eval/prompts/discovery/`:**

- `newtype-mixed-ids.md` — UserId/OrderId mix-up with bare strings → `patterns:newtype`.
- `newtype-vs-evs-order-line.md` — OrderLine carries price math → `patterns:entities-value-objects-services`, not `patterns:newtype`.
- `configuring-first-log-line.md` — first log line in `main` has nowhere to go → `patterns:configuring-logging`.
- `emitting-order-placed.md` — `order.placed` in a handler, pipeline already bootstrapped → `patterns:emitting-logs`.
- `paired-add-propagator.md` — install W3C `traceparent` propagator → `patterns:configuring-logging`.
- `paired-log-handler-success.md` — record successful `create_order`, registry already running → `patterns:emitting-logs`.

**Discovery, newly authored:**

- `aggregate-vs-unit-of-work.md` — frames a consistency-boundary question:

  > An order and its line items must be saved together — either every change persists or nothing does. The team is asking which design pattern names the rule that keeps them together. Which `patterns:*` skill applies?

  Expected: `patterns:aggregate` (the consistency boundary), not `patterns:unit-of-work` (the durable transactional flush that wraps the aggregate operation). The two pair on transactional-consistency vocabulary; the split is whose responsibility it is. Assertions: `text_contains: patterns:aggregate`, `text_not_contains: patterns:unit-of-work`, and a judge prompt confirming the answer cites *invariants across multiple objects* rather than *atomic flush at commit*.

- `parse-vs-type-states.md` — frames a "make illegal states unrepresentable" question:

  > I keep null-checking `customer.shippingAddress` everywhere it gets used. It is only ever set after the customer confirms their cart, but the type does not say so. Which `patterns:*` skill applies?

  Expected: `patterns:type-states` (lifecycle phase encoded as separate types, with `shippingAddress` only present in the confirmed-cart state). `patterns:parse-dont-validate` is the wrong answer — there is no boundary parse here; the data is already inside the domain and the bug is shape, not validity. Assertions: `text_contains: patterns:type-states`, `text_not_contains: patterns:parse-dont-validate`, judge prompt confirming the answer cites *distinct lifecycle phases* rather than *boundary parsing*.

**Invocation, copied verbatim from `ailly_two/e2e/patterns-eval/prompts/invocation/`:**

- `newtype.md`
- `configuring-logging.md`
- `emitting-logs.md`

**Invocation, newly authored:**

- `aggregate.md`:

  > Model an `Order` aggregate that owns a non-empty list of `LineItem`s. The aggregate root must be the only public entry point: callers may not construct, mutate, or read `LineItem`s except through `Order` methods. Adding a line item must keep the order's total in sync. Show the aggregate-root type and one example call site that adds a line and commits the change.

  The structural signature: a single root class/struct with private internal collection, no public getter that returns a mutable handle to the internal `LineItem[]`, all mutations expressed as named methods on the root, and the example call site never touches `LineItem` directly.

- `parse-dont-validate.md`:

  > Given a raw `dict` (Python) / `unknown` (TypeScript) / `serde_json::Value` (Rust) of untrusted input that *should* describe an order — `{ "id": "...", "customer_email": "...", "total_cents": ... }` — produce a `parse_order(raw) -> Order` function that returns a parsed domain `Order` value or raises a specific, actionable error per failure mode. Downstream functions that take an `Order` must not re-check any of the fields the parser already proved.

  Structural signature: a single `parse_order` entry point at the boundary, return type is a domain type (not `bool`, not `Result<bool, ...>`), one error variant per failure mode, no `Optional`/`null` for fields the parser proves present, and downstream functions accept the parsed type without guard.

- `repository.md`:

  > Define an `OrderRepository` interface in the domain layer with `get(order_id) -> Optional[Order]` and `add(order) -> None`. Provide two concrete implementations: `InMemoryOrderRepository` for tests and `SqlOrderRepository` for production. A domain service `place_order(cmd, repo: OrderRepository) -> OrderId` must depend only on the abstract interface — no SQL types, ORM sessions, or HTTP clients leak across the domain boundary.

  Structural signature: abstract interface defined in (or imported from) the domain module; two concrete subclasses/implementations clearly separated; the domain service's type signature names only the abstract; no ORM session, connection, or driver type appears in domain-side code.

### Evals

**`evals/discovery.yaml`** — 8 cases. The six reused cases inherit the exact assertion shapes from `ailly_two/e2e/patterns-eval/evals/discovery.yaml`. The two new cases follow the same pattern: a `text_contains` assertion on the expected skill ID, a `text_not_contains` assertion on the foil, and a `judge` assertion that ties the choice to the right rationale (consistency boundary vs flush, lifecycle phase vs boundary parse). The judge prompt prevents a model from naming the right skill for the wrong reason.

**`evals/invocation.yaml`** — 6 cases. Each case = `script` (placeholder for now) + `judge` (structural rules in prose) + `tokens` (< 6000 or 8000). The judge prompts for the three reused skills inherit from patterns-eval verbatim. The three new judges:

- `aggregate` — "The code defines a single aggregate-root type whose public surface is the only entry point for mutations. The internal collection of line items is not exposed by a public getter that returns a mutable handle. Adding a line item is expressed as a named method on the root, not field assignment from the call site."
- `parse-dont-validate` — "A single parser function at the boundary returns a parsed domain `Order` (not `bool`, not `Optional`). Errors are specific per failure mode. Downstream code that takes an `Order` does not re-check any field the parser proved."
- `repository` — "The repository interface is defined in the domain module. Two concrete implementations are provided. The domain service signature names only the abstract interface — no SQL session, ORM type, or driver appears anywhere on the domain-side surface."

**`evals/baseline.yaml`** — mechanically identical to `evals/invocation.yaml`. Same assertions, same scripts, same judges, same token budgets. The only thing that changes is the absence of the `kind: system` prefix entries in `baseline.yaml` (the assembly).

### Check scripts

All six scripts use the same placeholder body inherited from patterns-eval — read stdin, write `{"status": "placeholder", "reason": "eval-script not yet wired"}`, exit 0. Each script's header docstring enumerates the rule set the eventual implementation must encode. The three new scripts:

- `check_aggregate.py` — eventual rule set: single root type detected; internal collection has no public mutable accessor; mutations are method calls on the root; no cross-aggregate object references (line items reach the order, not the other way round).
- `check_parse_dont_validate.py` — eventual rule set: single `parse_X` function at boundary; return type is a domain type, not `bool`/`Optional`; one error variant per failure mode; downstream signatures take the parsed type without guards.
- `check_repository.py` — eventual rule set: abstract repository interface in domain module; ≥ 2 concrete implementations; domain service type signature names only the abstract; no ORM/SQL/driver types in domain-side code.

The placeholder pattern matches patterns-eval: header docstring + `main()` that reads stdin and writes placeholder JSON. When the upstream eval-script slice lands, the rule sets in the docstrings become the test code.

### ci.sh

Copied from `ailly_two/e2e/patterns-eval/ci.sh` with three changes per the blueprint:

1. `expected_count()` table: `discovery=8`, `baseline=6`, `invocation=6` (was `6/3/3`).
2. `repo_root="$(cd "${project_dir}/../.." && pwd)"` — already correct for this layout (`patterns/e2e/ci.sh` resolves `../..` to repo root).
3. The `cargo run --quiet --` invocations become `ailly` directly per the blueprint ("`ailly` itself is invoked as a CLI from the user's environment"). The harness expects `ailly` on `$PATH`.

The four CUJs (assemble, run gated on `ANTHROPIC_API_KEY`, eval, report) carry forward unchanged. The `cd "${repo_root}"` at the top is preserved so ailly's project resolution sees the repo root.

A bare-word grep step asserts neither `AGENTS.md` (at the repo `e2e/`) nor `profile.md` contains any `patterns:<skill-name>` literal:

```bash
# Falsification grep — fail if either file leaks a plugin-prefixed skill identifier.
for f in ../../e2e/AGENTS.md profile.md; do
  if grep -E 'patterns:[a-z-]+' "${project_dir}/${f#./}" >/dev/null 2>&1; then
    echo "FAIL: ${f} contains a 'patterns:*' identifier; baseline arm leaks the answer." >&2
    exit 1
  fi
done
```

This runs before the assemble step. It guards the falsification convention mechanically.

### Falsification

The blueprint's mechanical rule applies directly: drop every `kind: system` from invocation to produce baseline, keep both `kind: file` entries. The two `kind: file` entries (`../../e2e/AGENTS.md` and `./profile.md`) carry the coding-agent mindset and the harness purpose; neither names any patterns skill. The `ci.sh` grep enforces the rule.

The six invocation prompts deliberately name what the call site should look like (a single root, a single parse function, a single abstract interface) without naming the pattern. A baseline model reading "Define an `OrderRepository` interface in the domain layer" will likely produce something interface-shaped, but is unlikely to put the interface in the right layer, separate the two concrete implementations cleanly, or keep the domain service signature ORM-free without the skill loaded. The gap is the headline signal.

## Alternatives

**Migrate `ailly_two/e2e/patterns-eval` into `patterns/e2e/` and delete the original.** Considered and rejected. The two harnesses serve different audiences — patterns-eval is a demo project for ailly users (shows the tool's CUJ end-to-end on a real example), and `patterns/e2e/` is a regression harness for this plugin (runs on every commit to this repo). They share prompt text and check-script placeholders, but their assembly shape diverges (vended `context/` vs live `../skills/`), and their CI cadence diverges (ailly's own CI vs this repo's). Keeping both costs O(6) duplicated prompts and is the simplest divergence to maintain.

**Vended `context/skills/<name>/SKILL.md` copies under `patterns/e2e/`.** Considered and rejected (blueprint). Pinning is real, but every edit to a `patterns/skills/*/SKILL.md` would require a sync step, paid on every commit — and the most likely use case is exercising the *current* revision. Worktree pin for a sweep, live paths for the default.

**Fewer invocation cases — drop the three new prompts and run just the patterns-eval three.** Considered and rejected. The whole point of the in-repo harness is coverage broader than patterns-eval gives. Adding three is the minimum that expresses three distinct shape classes: aggregate (root + private internals), parse-dont-validate (boundary function with proof-bearing return), repository (layered interface). Two more discovery cases cover the two hardest blurs (consistency vs flush, illegal-states variants).

**Use a single `evals/all.yaml` with per-case suite tags instead of three suite files.** Considered and rejected. Patterns-eval splits by suite and `ci.sh` indexes by suite name throughout; following the existing shape keeps the CI driver identical except for the `expected_count` table.

**Implement real check scripts now instead of placeholders.** Considered and rejected. The blueprint defers script bodies to the `knowledge: eval-script` slice; until then the placeholder convention is what patterns-eval ships and what this harness inherits. The judge assertions carry the structural rules in prose for now.

**Run baseline at a different model than invocation to compare context-vs-capability.** Considered and rejected as out of scope. The blueprint pins one model (`claude-sonnet-4-6`) across the three suites; sweep tooling lands later.

## Summary

A new `patterns/e2e/` directory adjacent to `patterns/skills/`, shaped after `ailly_two/e2e/patterns-eval` but with live `../skills/<name>/SKILL.md` paths instead of vended copies. Six prompts and three check-script placeholders copy forward from patterns-eval verbatim. Three invocation prompts (`aggregate`, `parse-dont-validate`, `repository`) and two discovery prompts (`aggregate-vs-unit-of-work`, `parse-vs-type-states`) are newly authored. Three new check-script placeholders are stubs with the eventual rule sets in the header docstring. `ci.sh` is adapted with `expected_count` `8/6/6`, `repo_root` two levels up, an `ailly` CLI entry point, and a leading bare-word grep that enforces the falsification convention on `AGENTS.md` and `profile.md`.

`ailly_two/e2e/patterns-eval` is not modified.

**Deferred decisions.**

- Concrete bodies of `check_aggregate.py`, `check_parse_dont_validate.py`, and `check_repository.py`. The blueprint pins these behind the `knowledge: eval-script` slice; structural rule sets land in the docstring now, tests land when the slice lands.
- Whether the two new discovery prompts need the same paired-blur judge assertion the existing `paired-add-propagator` and `paired-log-handler-success` cases have. Authored as `text_contains` + `text_not_contains` + `judge` here; if early runs show the model passes the text checks but cites the wrong rationale, the judge prompt becomes the canonical guard.
- Model-version sweep across `sonnet-4-6` and the next minor (e.g., `sonnet-4-7`). The blueprint pins one model; sweep tooling lands when baseline metrics stabilise.
- Whether `ci.sh` should fail-fast on the falsification grep or report and continue. Authored as `exit 1` here — leaking a skill ID into `AGENTS.md` or `profile.md` invalidates the baseline arm and should block the run.
- The exact wording of the two new discovery-judge prompts. Sketched in the spec; final phrasing tuned after first run produces real responses.
- Whether `using-patterns/SKILL.md` should also appear in baseline. The blueprint says no — baseline drops every `kind: system` entry, including the routing skill — and this design follows it. Reconsider only if baseline pass rates are anomalously low because the model lacks any context for "what is a patterns skill"; if so, that is a signal the routing skill itself is too thin, not that the harness should change.
- The `newtype-vs-evs-order-line` reused case and its eval assert on `patterns:entities-value-objects-services`, but the skill on disk is `patterns:domain-objects` (`patterns/skills/domain-objects/SKILL.md`, frontmatter `name: domain-objects`). The routing table in `patterns/skills/using-patterns/SKILL.md` also still points at the older `entities-value-objects-services` identifier. Reusing patterns-eval verbatim faithfully reproduces this inconsistency; the case will fail until either the routing skill is updated to name `domain-objects` and the reused eval is updated to match, or the skill is renamed back. Resolving this is a separate edit to the source skills outside the scope of this harness design.
