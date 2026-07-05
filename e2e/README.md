# Root `e2e/` — static feature-test suites

Every plugin's `<plugin>/e2e/` (e.g. `patterns/e2e/`, `developer/e2e/`) runs a
model-driven harness: `ailly assemble` builds a conversation, `ailly run`
fills it against a live model, and `ailly eval`/`ailly report` score it
against `judge`, `text_contains`, `text_not_contains`, `script`, and `tokens`
assertions. See that plugin's own `e2e/README.md` for the fuller
architecture — the `assemblies/` + `evals/` + `evals/scripts/` shape, the
falsification-grep gate, and the baseline-vs-invocation comparison.

Root `e2e/` is different on purpose. DEVELOPMENT.md's "## Evals" section
says feature tests (as opposed to per-plugin unit tests) are authored here,
and Ailly's own reference-architecture feature tests are deterministic
source-level contract checks over this repository's own markdown files
(does `SKILL.md` route to a given ability reference; does a phase reference
mention a given mechanism; and so on) — not scored LLM transcripts. There is
nothing here for a model to grade, and per `research/e2e/README.md`, every
step in the `ailly` pipeline past `assemble` (`run`, `eval`, `report`) calls
a live model. Delegating to that pipeline for a check that needs no model
would mean either paying for a model call that changes nothing about the
check's outcome, or silently becoming non-deterministic where it doesn't
need to be.

## The static-suite convention

Root `e2e/` therefore runs a lighter, bespoke driver instead of the `ailly`
binary, while keeping the same file-layout convention a reader already
knows from the plugin harnesses:

- `evals/<suite>.yaml` — the same `name` / `cases` / `assertions` shape as a
  plugin's eval file, restricted to `type: script` assertions (a static
  suite has no transcript for `text_contains` / `judge` / `tokens` to
  score against).
- `evals/scripts/check_*.py` (plus a shared `_checker_utils.py`) — one
  checker per case, at the same path plugin checkers use
  (`evals/scripts/check_<thing>.py`), following the identical contract:
  exit `0` with no output on success; exit `1` with **exactly one** reason
  line on stdout on failure; never write to stderr (doing so turns a normal
  `Fail` into an `Errored` outcome, exactly as documented in every plugin's
  `_checker_utils.py`). The one difference: a static checker reads
  repository files directly from disk instead of reading a model's
  transcript from stdin — there is no transcript.
- `assemblies/<suite>.yaml` — kept for the same reason: so `e2e/` shows the
  familiar three-way `assemblies` / `evals` / `evals/scripts` split. Its
  `matrix`, `prefix`, and `conversation` fields are intentionally empty
  (`model: none`), since there is no conversation to assemble.

`ci.sh` never calls the `ailly` binary for this suite type. It runs
`run_static_evals.py`, which hand-parses the restricted YAML subset above
(no PyYAML dependency exists anywhere in this repo's e2e tooling; every
existing `ci.sh` already hand-parses a restricted YAML subset of its own —
see each plugin's `assert_filled()` awk state machine — this driver follows
that same precedent, in Python) and runs each case's checker directly,
aggregating pass/fail and exiting non-zero if any case fails.

## Running it

```sh
./e2e/ci.sh
```

No `ANTHROPIC_API_KEY`, no `.env`, and no network access are required.
