# Design: CLI Case Filtering for `assemble`/`run`/`eval`

**Feature-step A of the project** `.ailly/developer/2026-07-06-A-ailly-evals/` (`developer/skills/ailly/references/shapes/project/project-cycle.md`).
Closes [`ailly/issues/197`](https://github.com/DavidSouther/ailly/issues/197).
Repo: `/Users/david.souther/devel/davidsouther/ailly/ailly_two` (branch `main_two`).

**Load before working on this feature-step:** `ailly_two/skills/ailly-skill-eval/SKILL.md` (with `references/method.md`) — the project's method for skill-eval-suite anatomy (discovery/invocation axes, assertion palette, baseline-falsification gate). `DESIGN.md` at the `ailly_two` repo root is the authoritative schema for `assembly`/`conversation`/`evaluation` YAML.

## Purpose

Today, `assemble`, `run`, and `eval` each process every case in their target unconditionally — a full matrix expansion, every conversation file in a run directory, every conversation under `--over`.
Iterating on one skill's `SKILL.md` means paying for every other skill's live model calls too.
This feature adds a `--case <name>` selector, repeatable, to all three commands so a developer can scope a single edit-test cycle to just the case(s) they changed.

## Prior Art

- `run` already supports pointing `target` at a single conversation *file* instead of a directory (`src/cli/run.rs:106-144`, `resolve_keys`) — the one existing "narrow the scope" idiom in the CLI today.
  It has no partial-directory selector: pointing at a directory always processes every file in it.
- `DESIGN.md` (repo root, "assembly" section) documents a `--var <axis>=<value>` flag for `assemble` that would restrict one matrix axis before expansion.
  **This is unimplemented** — no CLI flag, no code path, no test references it anywhere in `src/`.
  It predates this feature as aspirational text, not working prior art.
  It can be removed.
- The codebase already has one unified, if implicit, case identity: an assembly matrix binding's derived filename (`filename_for`, `src/content/repository.rs:549-559`, e.g. `"missing-fields.yaml"`) is exactly the conversation filename `run` and `eval` key off of (`ConversationKey.name`, `ConversationName`), which is exactly the string an `evaluation` suite's `Case.name` matches against (`src/knowledge/eval.rs:395-412`, `matches_for`).
  One string — the case name — already identifies "this case" across all three schemas; this feature's filter selects against that existing identity rather than inventing a new one.
- The existing single-`*`-wildcard glob idiom (`matches_glob`, `src/content/repository.rs:527-545`, used for prefix-block content resolution) was considered and rejected for `--case` — see Alternatives.

## User Journey and Metrics

**Journey:** A developer edits `context/skills/newtype/SKILL.md` in a discovery/invocation suite like `e2e/patterns-eval/`.
They run:

```text
ailly assemble invocation --case newtype
ailly run runs/<id> --case newtype
ailly eval invocation --over runs/<id> --case newtype
```

`assemble` writes only `newtype.yaml` (not every skill in the matrix).
`run` fills only `newtype.yaml`'s blank assistant turn, leaving any other file already in that run directory untouched.
`eval` scores only the conversation(s) matching `newtype`, against only the suite cases that name or bind to it.
Omitting `--case` on any command is unchanged from today's behavior — the flag is strictly additive.

**Concrete success bound (resolving the parent project design's deferred "exact numeric target"):** wall-clock time is not the metric — it is dominated by external model/API latency this feature does not control, and would make the feature test flaky.
Instead, the bound is stated as a live-call-count reduction, with a worked concrete example rather than an abstract "K not N": `e2e/patterns-eval`'s `invocation` suite today assembles and runs 3 skill cases (`newtype`, `configuring-logging`, `emitting-logs`), so an unfiltered edit-test cycle pays 3 live model calls.
`--case newtype` cuts this to exactly 1 — a **66% reduction for this suite today**, and the reduction approaches `(N-1)/N` as a suite's case count N grows, since a filtered cycle always costs exactly 1 call regardless of N. The feature test pins the mechanism this bound depends on (filtering to K named cases results in exactly K conversations written/processed/matched, never N) as a deterministic, CI-safe count; empirically measuring the real wall-clock/cost reduction against a live suite is a Build-phase manual verification step, not something the automated feature test can assert without live credentials and API-latency flakiness.

**Failure mode:** a `--case` value that matches nothing in the target (typo, wrong skill name) is a hard error naming precisely the value(s) that failed to match and listing the case names that *were* available.
This fires per-value, not only when every requested value misses: `--case newtype --case nwetype` (one real, one typo) still errors on `nwetype` — silently running a partial, smaller-than-intended set would be exactly the "silently doing nothing" failure mode this design rejects, just partial rather than total.

## Specification

Add one repeatable, optional flag, reusing the same name and matching rule everywhere:

```text
--case <NAME>      (repeatable: --case a --case b selects both "a" and "b")
```

- **Matching is exact-string, not glob.** `--case newtype` matches only the case literally named `newtype`. (Considered and rejected: single-`*`-glob — see Alternatives.)
- **Omitted `--case`** (empty list) means "no filter" — identical to today's behavior on all three commands.
  This is the regression-safety guarantee: existing scripts and CI invocations are unaffected.
- **Shared filter concept**, not three separate ones: a single predicate (`name` matches if the filter list is empty, or contains `name`) is reused by all three handlers, each applying it at the point where it already iterates cases:
  - `assemble` (`src/cli/assemble.rs`, `run_with_project`'s loop over `assembly.expand_matrix()`): compute the binding's would-be case name the same way `ConversationKey::from_binding` already does (`src/content/repository.rs:51-58` — `filename_for(binding)` then strip `.yaml`), and skip staging bindings that don't pass the filter.
  - `run` (`src/cli/run.rs`, `resolve_keys`): after listing `ConversationKey`s for a directory target, drop keys whose `name` doesn't pass the filter.
    A file target combined with `--case` is filtered the same way (the single resolved key either passes or the command errors "matched nothing"), so the two paths behave consistently rather than needing a special case.
  - `eval` (`src/cli/eval.rs`, the `run` handler): filtering here has **two** parts, not one, because of an interaction with existing suite-matching behavior this design must not break.
    After listing conversation keys under `--over`, drop keys whose `name` doesn't pass the filter, before loading and handing conversations to `evaluate()` — but `evaluate()` (`src/knowledge/eval.rs:280-292`) already synthesizes a `Malformed` outcome for any suite `Case` with a `name:` that matches **zero** loaded conversations ("no conversation found for case name"), which `EvalCmdOutcome::has_failures` (`src/cli/eval.rs:63-70`) treats as a failing run.
    Filtering only the conversation list would therefore make a filtered `eval` invocation fail on every *other* named case in the suite it didn't ask about — the opposite of "scores only the case(s) you asked for."
    So the loaded suite's `cases` list must **also** be filtered before calling `evaluate()`: drop any case whose `name` is `Some` and not in the `--case` list; leave cases with `name: None` (unnamed, `when:`-only, or fully open cases) untouched, since `evaluate()`'s malformed synthesis is guarded by `case.name.is_some()` and an unnamed case with zero matches simply contributes nothing to the report.
    This is independent of and unrelated to the separate, already-in-flight `docs/developer/2026-06-26-A-eval-static-doc` feature (lifting a single non-conversation *document* into a synthetic conversation) — that feature concerns `--over` pointing at one file that isn't a conversation at all; this feature concerns `--over` pointing at a directory of many conversations and narrowing which of them, and which suite cases, are in play.
- **Unknown case error**: after filtering, if **any** requested `--case` value matched nothing in the target — not only when every requested value misses — return a new error variant (one per command's existing error enum, e.g. `AssembleError::UnknownCase`, `RunCmdError::UnknownCase`, `EvalCmdError::UnknownCase`) naming exactly the value(s) that failed to match and the case names that were actually available.
  A request mixing one real name and one typo must still error on the typo, not silently proceed with the smaller, unintended set.
- **`AssembleArgs`, `RunArgs`, `EvalCmdArgs`** each gain one new field, `cases: Vec<String>` (empty by default), threaded from a new `#[arg(long = "case")] cases: Vec<String>` on the corresponding `main.rs` `Command` variant.
  Adding this field is a mechanical but wide-reaching change: `AssembleArgs`'s doc comment (`src/cli/assemble.rs:16-17`) already notes its field list is "fixed by the feature test's struct-literal call site"; `RunArgs` and `EvalCmdArgs` carry no such comment today but the same concern applies in practice, since dozens of existing unit tests across all three modules construct these structs by literal.
  That includes at least one file this feature-step does not otherwise touch: `tests/eval_static_document.rs`, owned by the separate, already-in-flight `docs/developer/2026-06-26-A-eval-static-doc` session, builds an exhaustive 3-field `EvalCmdArgs` literal that will need a fourth `cases: vec![]` line once this field lands — a one-line, backward-compatible addition, but a real point of contact between the two efforts worth naming rather than leaving as a surprise.
  The Plan phase should size a step for updating existing call sites (likely via `#[derive(Default)]` plus `..Default::default()` at each site) separately from the step that implements the filtering logic itself.

## Alternatives

1. **Implement `DESIGN.md`'s documented `--var <axis>=<value>` for `assemble`, plus a separate name-based filter for `run`/`eval`.**
   Rejected: `--var` is axis-level (meaningful only pre-expansion, inside `assemble`) and has no natural equivalent for `run`/`eval`, which operate on already-materialized files with no axis structure left.
   Building two different selection mechanisms for what the codebase already treats as one identity (case name) would be more surface area for no real benefit, and would leave the *existing* unimplemented `--var` promise still-unfulfilled everywhere except `assemble`.
   This feature instead corrects `DESIGN.md` to document `--case` and removes (or marks superseded) the `--var` paragraph, since it describes behavior that was never built and would otherwise sit alongside a real, similar-but-different flag.
2. **Single-`*`-wildcard glob matching** (`--case 'discovery-*'`), reusing the existing `matches_glob` idiom.
   Rejected for v1: adds a pattern language to document and test for a use case (selecting several related cases at once) the repeatable exact-match flag already covers by naming them individually; can be added later as a strict superset without breaking the exact-match contract, if repeated demand shows up.
3. **Filter inside the repository/content layer** (teach `VfsConversationRepository::list` and `expand_matrix` to accept a filter) rather than in each CLI handler.
   Rejected: `VfsConversationRepository::list` is a generic, reusable listing primitive with other callers; `expand_matrix` operates on `Binding`s before the filename that `--case` matches against even exists.
   Filtering in each CLI handler, over one shared predicate, keeps the generic content/repository layer unaware of a CLI-only concern and keeps the diff smaller and more reviewable.

## Summary

**Deferred, not decided here:**

- Glob/pattern matching for `--case` (Alternative 2) — revisit if exact-match-plus-repetition proves too verbose in practice.
- Whether `--case` should also accept `when:`-style binding-subset matching (e.g. `--case domain=prose-bio`) rather than only a flat name — the parent project's research and this design both found no existing need for it; `assemble`/`run`/`eval` today have no notion of "the current binding" outside the derived filename.

**Fixed during review (not left open):** an internal review caught that filtering only `eval`'s conversation list, without also filtering the loaded suite's `cases`, would make a filtered run fail on every other named case in the suite (`evaluate()`'s existing "no conversation found for case name" `Malformed` synthesis, `src/knowledge/eval.rs:280-292`).
The Specification above and the feature test (`assertions_malformed == 0` assertion) now both account for this: `eval`'s filter drops non-matching *named* suite cases alongside non-matching conversations, before calling `evaluate()`.

**Open Artifact Decisions:**

- **Error variant names** (`AssembleError::UnknownCase`, `RunCmdError::UnknownCase`, `EvalCmdError::UnknownCase`) and the exact wording of the "matched nothing" message: not prescribed by any existing convention.
  Proposed above; the Plan/Build phase may adjust wording as long as the requested and available names both appear.
- **`DESIGN.md` correction**: replacing the unimplemented `--var` paragraph with `--case`'s documented behavior is an in-scope doc fix for this feature-step, not a separate follow-up — flagging here since it's an edit to a file this design doesn't otherwise touch.

**Feature test:** `tests/cli_case_filter.rs` (`ailly_two`), function `case_filter_scopes_assemble_run_and_eval_to_selected_cases`.
RED until `cases: Vec<String>` and the shared filter predicate are threaded through `assemble`/`run`/`eval`.

**Next steps.**
This is the draft gate: do not continue into `developer:plan` or any implementation skill in this session, even if asked.
Review this `design.md` and the feature test, make any edits, then remove the `*Draft 2026-07-06*` marker above and start a new session running `developer:ailly` (or `developer:plan` directly) to move into the plan phase for this feature-step.
