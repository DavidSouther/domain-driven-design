# Design: Page Objects Pattern for the Testing Patterns Catalog

## Purpose

The `patterns:using-patterns` catalog teaches test *structure*
(arrange-act-assert) and a green-bar *strategy* (triangulate), but has no
ability for the Page Object pattern: encapsulating a UI surface (a screen or
console) behind an object that exposes verb-phrase, user-intent methods
(`System_findObject`, `Helm_setManeuver`) so acceptance tests read as
journeys and a selector change localizes to one file. Issue #27, encountered
downstream in `stellar_commander#81`, asks for this ability routed from
`patterns:using-patterns` alongside `arrange-act-assert`, with a reference
under `references/patterns/`.

## Prior Art

- **Selenium's Page Object Models guide** and **Fowler's `PageObject`
  bliki** (research.md, sources [1][2]) converge on the same two rules this
  design encodes: the page object owns locators/waits and is the single
  place UI structure knowledge lives; methods are verb phrases describing
  intent, never raw selectors; and assertions never live in the page
  object — that stays in the test.
- **`arrange-act-assert.md`** and **`triangulate.md`** (this repo) are the
  two existing testing-technique references and set the shape this design
  follows: no per-language subdirectory, an Overview / When to Use / Core
  Pattern / Quick Reference / Common Mistakes / Composes With structure, and
  a `Composes With` cross-link back to sibling patterns.
- **`stellar_commander#81`** (research.md, source [3]) is confirmed live
  prior art for the naming convention: `<Console>_<Action>` methods
  (`Menu_LoadGame`, `System_findObject`, `Helm_setManeuver`) on one page
  object per console.

## User Journey and Metrics

A developer is writing or reviewing an acceptance/e2e test that drives a UI
screen or console repeatedly (`stellar_commander`'s `System` console,
`Helm` console, etc.). Selectors and waits are duplicated across tests, or a
UI change breaks several unrelated tests at once. They consult
`patterns:using-patterns`; its routing table names `page-objects` for this
discriminator (a reusable UI surface behind verb-phrase actions, not a
single test's phases) and points at
`references/patterns/page-objects.md`. That reference teaches: when to
reach for a page object versus keeping a test flat; the naming convention
(one page object per screen/console, verb-phrase methods per user action);
the split of responsibility (selectors and waits live in the page object;
assertions stay in the test); and how it composes with
`arrange-act-assert` (the page object's method calls are the test's Act;
the test still owns its own Arrange and Assert).

**Metric:** the routing table and reference exist and are internally
consistent — a developer following the routing table from a UI-duplication
symptom reaches the reference in one hop, and the reference never tells
them to assert inside the page object or to skip verb-phrase naming.

## Specification

- **New reference:**
  `patterns/skills/using-patterns/references/patterns/page-objects.md`,
  matching the sibling shape (Overview, When to Use, Core Pattern with
  Before/After, Quick Reference, Common Mistakes, Composes With). No
  per-language subdirectory (matches `arrange-act-assert.md` and
  `triangulate.md`, both single files).
  - **Naming:** one page object per screen/console; methods are verb
    phrases naming the user action, not the DOM/console structure. Worked
    example reuses the issue's own live names —
    `System_findObject`, `Helm_setManeuver` — from `stellar_commander#81`.
  - **Split:** selectors and waits are private to the page object; the page
    object never asserts. The test arranges the page object, acts through
    its verb-phrase methods, and asserts on the page object's return values
    or observable state.
  - **Composes With:** cross-links `arrange-act-assert.md` (the page
    object's methods are the Act) and, briefly, `triangulate.md` is not
    cross-linked (no natural relationship).
- **Routing table row** in
  `patterns/skills/using-patterns/SKILL.md`: one new row for `page-objects`,
  discriminator worded as "a UI screen or console is driven repeatedly
  across acceptance/e2e tests and selector/wait duplication should localize
  behind verb-phrase actions."
- **Discriminator entry** in "Discriminators That Are Easy to Confuse":
  `page-objects` vs. `arrange-act-assert` — encapsulating a *reusable UI
  surface* across many tests (page-objects) versus structuring *one test's*
  phases (arrange-act-assert). No second discriminator against
  `bootstrap-and-service` is added: that pattern governs wiring the
  application's composition root, a different concern from UI test
  encapsulation, and the issue does not report confusion between them.
- **e2e eval case** (`patterns/e2e/prompts/invocation/page-objects.md`,
  a `check_page_objects.py` structural checker, and matching
  `evals/invocation.yaml` / `assemblies/invocation.yaml` entries): deferred
  to the Build phase, following the same default research.md already
  recorded. This mirrors two patterns already shipped without an e2e case
  (`configuring-feature-flags`, `using-feature-flags`), so shipping the
  reference and routing first, with the eval case as fast-follow inside the
  same Build session if time allows, is consistent with existing practice
  rather than a gap.
- **Feature test:** `developer/tests/test_page_objects_pattern.py` (already
  present on disk from an earlier pass at this session, confirmed RED — see
  "Feature Test" below).

## Alternatives

- **A new top-level `patterns:page-objects` skill**, independent of
  `using-patterns`. Rejected — the issue explicitly asks for routing
  through `patterns:using-patterns` alongside `arrange-act-assert`, and
  every other testing technique in this catalog is a reference, not its own
  skill.
- **Per-language subdirectory** (`page-objects/python.md`, etc.), matching
  the domain-object-shaped patterns. Rejected for this pass — page objects
  are an organizational/structural convention like arrange-act-assert and
  triangulate (neither of which has language variants), not a
  language-idiom pattern; a language split can be added later if a concrete
  need surfaces.
- **Recommended:** one reference file plus one routing-table row plus one
  discriminator entry, matching the two existing testing-technique patterns
  exactly — the smallest change that satisfies the issue.

## Summary

Add `patterns/skills/using-patterns/references/patterns/page-objects.md`
(no language subdirectory), one routing-table row, and one discriminator
entry (page-objects vs. arrange-act-assert) to
`patterns/skills/using-patterns/SKILL.md`. Deferred to Build: the e2e
discovery/invocation/checker case under `patterns/e2e/`, as a fast-follow
inside the same feature if time allows, consistent with two patterns
already shipped without one.

### Open Artifact Decisions

**Feature test file path:** `developer/tests/test_page_objects_pattern.py`
already exists on disk (untracked, from an earlier pass at this same
session) and is confirmed RED. No skill template prescribes this exact
path; it follows the sibling convention (`test_<topic>.py`, flat under
`developer/tests/`, no pytest, exits 0/1 with a one-line reason).
Proposed: keep the file as-is; it already asserts the full contract this
design specifies (routing row, discriminator, reference existence and
shape, naming, the page-vs-test split, and the `arrange-act-assert`
cross-link).

## Feature Test

**User story:** Given a developer facing UI-selector duplication across
acceptance tests, when they consult `patterns:using-patterns`, then its
routing table names `page-objects` and points at
`references/patterns/page-objects.md`, whose contents teach one-page-object-
per-screen/console naming with verb-phrase methods, keep selectors and
waits in the page object and assertions in the test, and cross-link
`arrange-act-assert` as the pattern this composes with.

**Test path:** `developer/tests/test_page_objects_pattern.py`

This is a contract check on the source-of-truth files (mirroring
`test_subagent_model_mandate.py` and `test_fable5_softblock.py`'s shape): it
asserts `patterns/skills/using-patterns/SKILL.md` names `page-objects` and
its reference path, and carries a discriminator distinguishing it from
`arrange-act-assert`; and that
`patterns/skills/using-patterns/references/patterns/page-objects.md` exists,
has the sibling pattern-file's required sections, documents verb-phrase
naming scoped to one screen/console, states selectors and waits belong in
the page object and assertions stay in the test, and cross-links
`arrange-act-assert` under Composes With. It needs no model and no pytest,
and exits 0 (every rule holds) or 1 with a single reason line. Confirmed
RED: today neither file mentions page objects at all
(`python3 developer/tests/test_page_objects_pattern.py` prints
`T1 routing: patterns/skills/using-patterns/SKILL.md does not name a
'page-objects' pattern anywhere` and exits 1).
