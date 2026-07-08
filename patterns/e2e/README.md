# `patterns/e2e/` — regression harness for the `patterns:*` plugin

An Ailly skill-eval suite that regression-tests the `patterns:*` skills on two independent failure surfaces:

- **Discovery** — given a coding situation, does the model select the right skill
  from the `using-patterns` routing table alone?
- **Invocation vs baseline** — once a skill is loaded, does the model produce code
  that structurally exhibits the pattern, *over* a no-skill baseline floor?

Built with the method in [`ailly_two/skills/ailly-skill-eval`](https://github.com/) and shaped after the worked example `ailly_two/e2e/patterns-eval` (which this harness does not modify).
The design lives in `.ailly/developer/2026-05-29-C-patterns-e2e/design.md`; the shared blueprint is `.ailly/developer/2026-05-29-A-skill-evals/design.md`.

## Cross-section under test (6 skills)

| Skill | Discovery neighbour | Invocation shape |
|---|---|---|
| `newtype` | `domain-objects` (value object) | branded primitive, constructor-only entry, no `as` at call sites |
| `configuring-logging` | `emitting-logs` (per-call cadence) | five-layer subscriber registry installed once at bootstrap |
| `emitting-logs` | `configuring-logging` (bootstrap cadence) | structured record, `EventName`, semantic-convention keys |
| `aggregate` | `unit-of-work` (atomic flush) | single root, encapsulated internals, mutation via named method |
| `parse-dont-validate` | `type-states` (lifecycle phase) | boundary parser returns a proof-bearing domain type, throws per failure |
| `repository` | — (standalone) | abstract interface in domain, two impls, no ORM leak on domain surface |

## Layout

```
patterns/e2e/
├── AGENTS.md            → symlink to ../../e2e/AGENTS.md (shared coding-agent constitution)
├── skills/             → symlink to ../skills (the live patterns skills tree)
├── profile.md          harness purpose + Full axis profile + TypeScript pin
├── assemblies/         discovery.yaml (8 cases), invocation.yaml + baseline.yaml (6 skills)
├── prompts/            discovery/*.md (8), invocation/*.md (6)
├── evals/
│   ├── discovery.yaml  text_contains / text_not_contains (+ judge on the paired cases)
│   ├── invocation.yaml script + judge + tokens(output) per skill
│   ├── baseline.yaml   byte-identical assertions to invocation
│   └── scripts/        _checker_utils.py + six check_<skill>.py structural checkers
├── ci.sh               assemble → run → eval → report, with the falsification gate
└── runs/, evals/reports/   gitignored; produced by ci.sh
```

### Live skills via in-project symlinks

Ailly mounts the `-p` project as a `vfs::PhysicalFS` jailed to that root; `vfs`'s path join clamps `..`, so a prefix path cannot reference a file outside the project directory.
The blueprint's out-of-project live paths (`../skills/...`, `../../e2e/AGENTS.md`) therefore do not resolve against this build.
The live intent is preserved with two in-project symlinks the OS follows at read time: `skills → ../skills` and `AGENTS.md → ../../e2e/AGENTS.md`.
Editing a source skill is reflected on the next `assemble` — no vending step.

## Running

The harness drives the `ailly` CLI.
Provide a binary on `$PATH` as `ailly`, or pass one explicitly, plus an `ANTHROPIC_API_KEY` (shell export or a project `.env`):

```sh
cd patterns/e2e
cp /path/to/.env .env                 # ANTHROPIC_API_KEY=...
AILLY=/path/to/ailly ./ci.sh
```

`ci.sh` runs five customer journeys and fails the build on any violation:

0. **Falsification grep** — `AGENTS.md`/`profile.md` must not leak a `patterns:<skill>`
   identifier into the baseline arm.
1. **assemble** — discovery 8, baseline 6, invocation 6 conversation files.
2. **run** — fill every blank assistant turn (model pinned `claude-sonnet-4-6`).
3. **eval** — score each suite; write a per-run report.
4. **report** — discovery single-run summary, then the baseline-vs-invocation
   comparison and the **falsification gate**: `improved > 0` and `regressed == 0`.

## Reading the result

The gate is the headline.
Across runs it holds `improved > 0 && regressed == 0`; the *specific* improving skill varies with model sampling.
A representative run (`2026-06-03T10-13-42Z`):

```
discovery: 18 / 20 (90%)
baseline vs invocation — improved 1, regressed 0, unchanged_pass 14, unchanged_fail 3
```

- **`emitting-logs`** is the consistent positive: without the skill the model writes an ad-hoc/interpolated log line; with it the record is structured under semantic-convention keys with an event name.
  The judge flips fail→pass every run; the script flips when the model emits the full record.
- **`configuring-logging`** improves when the model emits the whole five-layer
  registry (script + judge flip fail→pass); on a terser run it lands unchanged.
- **`newtype`, `aggregate`, `parse-dont-validate`, `repository`** are **null results**: a capable model already produces the brand / encapsulated root / boundary parser / layered repository with or without the skill, so both arms pass.
  They are retained to show what a skill that does not move a capable model looks like — `unchanged_pass`, contributing nothing to `improved`.
  The gate does not depend on them. (`repository` does flip fail→pass on runs where the baseline leaks an ORM type or collapses the two implementations.)

Do not weaken a checker to manufacture an `improved` on a null result; a null result is a true statement about the model, not a defect in the suite.

### Discovery finding: stale routing entry

`newtype-vs-evs-order-line` is a standing red (so discovery sits at 18/20, not 20/20).
It tests the correct property — an `OrderLine` that carries price math should route to the value-object skill — and asserts the real skill name on disk, `patterns:domain-objects`.
The model instead names `patterns:newtype`, for two reasons the harness surfaces:

1. `patterns/skills/using-patterns/SKILL.md` line 13 still routes the value-object row at `patterns:entities-value-objects-services`, a name that no longer exists on disk (the skill was renamed to `domain-objects`).
   No prompt can route to `domain-objects` through the table as written.
2. The prompt's "whether to wrap the underlying tuple in a new type" phrasing is a hard
   blur toward `newtype`.

This is the harness doing its job.
**Recommended fix (a separate edit to the source skill, out of scope here): update `using-patterns/SKILL.md:13` to name `patterns:domain-objects`.**
The skills are deliberately not modified by this harness.

## Two measurement fixes baked into this harness

Both correct artifacts that would otherwise produce false gate signals; neither weakens the gate (the real improvements and null results are unchanged):

- **`tokens` uses `metric: output`, not `total`.**
  The invocation arm loads the skill body into the prefix, so its *input* tokens are inherently larger; a `total` budget penalises the very arm that loads the skill and reads as a false `regressed` (observed: `emitting-logs` total 7358 vs baseline 2377 against a 6000 budget).
  `output` bounds only generated tokens — the size the budget is meant to guard — and is equal across arms.
- **`extract_code` reads agentic `write_file` output.**
  The rich coding-agent `AGENTS.md` primes the model to *act*: it frequently emits code inside simulated `write_file` / `create_file` tool-call JSON rather than markdown fences.
  The checkers now unescape `file_contents` payloads in addition to ``` fences, so they score the real code regardless of envelope (a missed `write_file` body was producing a false `newtype` script regression).
