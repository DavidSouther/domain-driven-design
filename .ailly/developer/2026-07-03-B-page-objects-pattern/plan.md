# Implementation Plan: Page Objects Pattern for the Testing Patterns Catalog

**Feature test:** `developer/tests/test_page_objects_pattern.py`
**User story:** A developer facing UI-selector duplication across acceptance tests consults `patterns:using-patterns`, whose routing table names `page-objects` and points at `references/patterns/page-objects.md`, a reference that teaches one-page-object-per-screen/console naming with verb-phrase methods, keeps selectors/waits in the page object and assertions in the test, and cross-links `arrange-act-assert`.

**Libraries & Skills:** Load `general:writing-pattern-skills` (already loaded this session) before Step 3 — it fixes the section shape and voice for the new reference file. No other framework/library skill applies; carry this directive into the Build phase too, per research.md's Libraries & Skills note.

**Steps:**
- [ ] Step 0: API surface area
- [ ] Step 1: Routing table row (T1)
- [ ] Step 2: Discriminator entry (T2)
- [ ] Step 3: Reference file skeleton — Overview, When to Use, Core Pattern (T3, partial T4)
- [ ] Step 4: Quick Reference and Common Mistakes (T4 complete, T5, T6)
- [ ] Step 5: Composes With cross-link (T7, feature test green)

## Step 0: API surface area

This is a documentation-only change — no application code, no new types, entities, or function signatures. There is nothing to stub. The "surface area" here is the shape of the two artifacts the feature test pins:

- `patterns/skills/using-patterns/SKILL.md` — an existing file, edited in place in two places: one new row in the `## Routing Table`, and one new entry in the `## Discriminators That Are Easy to Confuse` section.
- `patterns/skills/using-patterns/references/patterns/page-objects.md` — a new file, matching the six-section shape of the sibling files `arrange-act-assert.md` and `triangulate.md` (`Overview`, `When to Use`, `Core Pattern`, `Quick Reference`, `Common Mistakes`, `Composes With`). No frontmatter (it is a reference, not a skill) and no per-language subdirectory (design.md's Specification: page objects are a structural convention like arrange-act-assert, not a language idiom).

The feature test (`developer/tests/test_page_objects_pattern.py`) already exists and is confirmed RED: `T1 routing: patterns/skills/using-patterns/SKILL.md does not name a 'page-objects' pattern anywhere`. It is the fixed target for Steps 1–5; no changes to the test itself are in scope for this plan.

## Step 1: Routing table row

**Enables:** T1 (the routing table names `page-objects` and points at `references/patterns/page-objects.md`).

Add one row to `patterns/skills/using-patterns/SKILL.md`'s `## Routing Table`, alongside the existing `arrange-act-assert` and `triangulate` rows. State the discriminator per design.md: a UI screen or console is driven repeatedly across acceptance/e2e tests and selector/wait duplication should localize behind verb-phrase actions.

**Tests**

No new automated test — this step targets T1 in `test_page_objects_pattern.py`.

```
test "T1 holds after step 1":
  run developer/tests/test_page_objects_pattern.py
  assert failure has moved past T1 (now fails at T2, or later)
```

- Edge case: the row must contain the literal substrings `page-objects` and `references/patterns/page-objects.md` — do not abbreviate the path or rely on a relative link that omits the `references/patterns/` prefix.
- Edge case: place the row near `arrange-act-assert` (both are testing-technique rows), not scattered among the domain-modeling rows, so a reader scanning the table finds testing patterns grouped together.

**Implementation Outline**

```
insert one row into the Routing Table, after the arrange-act-assert row:

| A UI screen or console is driven repeatedly across acceptance/e2e tests,
  and selector/wait duplication should localize behind verb-phrase actions |
  page-objects — `references/patterns/page-objects.md` |
```

## Step 2: Discriminator entry

**Enables:** T2 (the `## Discriminators That Are Easy to Confuse` section distinguishes `page-objects` from `arrange-act-assert`).

Add one bullet to the existing `## Discriminators That Are Easy to Confuse` section, following the shape of the existing `triangulate vs arrange-act-assert` entry. State the split per design.md: encapsulating a *reusable UI surface* across many tests (page-objects) versus structuring *one test's* phases (arrange-act-assert).

**Tests**

No new automated test — this step targets T2.

```
test "T2 holds after step 2":
  run developer/tests/test_page_objects_pattern.py
  assert failure has moved past T2 (now fails at T3, since the reference file does not exist yet)
```

- Edge case: the bullet must live inside the `## Discriminators That Are Easy to Confuse` section body (the test extracts that section by heading and next-heading boundary) — do not place it under `## Pattern Composition` or elsewhere.
- Edge case: the bullet must contain the literal substring `page-objects` (case as written elsewhere in the file is fine; the test lowercases before matching).

**Implementation Outline**

```
append one bullet to "## Discriminators That Are Easy to Confuse":

- **page-objects vs arrange-act-assert.** Encapsulating a reusable UI surface
  (a screen or console) behind verb-phrase actions, reused across many
  acceptance tests, routes to page-objects (`references/patterns/page-objects.md`).
  Structuring the arrange/act/assert phases of one test routes to
  arrange-act-assert (`references/patterns/arrange-act-assert.md`).
```

## Step 3: Reference file skeleton — Overview, When to Use, Core Pattern

**Enables:** T3 (the reference file exists), progress toward T4 (three of six required sections present), and progress toward T5 (verb-phrase naming and screen/console scoping stated in prose).

Create `patterns/skills/using-patterns/references/patterns/page-objects.md`. Load `general:writing-pattern-skills` before drafting (already loaded this session) so the voice matches `arrange-act-assert.md`: third person, present tense, reference-grade, named source (Fowler's `PageObject` bliki, research.md source [2]) in the Overview.

- **Overview:** name the pattern, state the core principle (a UI surface behind an object exposing user-intent methods; a selector change localizes to one file), cite Fowler.
- **When to Use:** bullets keyed to the symptom (acceptance/e2e test drives the same screen/console repeatedly; selectors/waits duplicated across tests; a UI change breaks several unrelated tests). Close with **When NOT to use** (a one-off test that touches a screen exactly once; a unit test with no UI surface).
- **Core Pattern:** Before/After framing per research.md's `stellar_commander#81` prior art — Before: a test with inline selectors/waits for the `System` console; After: a `SystemConsole` page object exposing `System_findObject`, with the test calling it. This section is where "verb phrase" and "console" (or "screen") land in prose, satisfying T5's substring checks.

**Tests**

No new automated test — this step targets T3 and moves T4/T5 forward. Confirm with:

```
test "T3 holds, T4 partial after step 3":
  run developer/tests/test_page_objects_pattern.py
  assert failure now reports T4 with missing_sections == ["Quick Reference", "Common Mistakes", "Composes With"]
```

- Edge case: headings must be exact `##` level, matching `arrange-act-assert.md` (`## Overview`, `## When to Use`, `## Core Pattern`) — the test's section-extraction regex is anchored to `^##\s+<heading>\s*$`, case-insensitive but not fuzzy on wording.
- Edge case: the word "verb" and at least one of "screen"/"console" must land inside the file body somewhere before Step 4 — Core Pattern is the natural place, but do not defer them expecting Step 4's Quick Reference to carry them; Quick Reference in Step 4 is a table, not prose, and may not restate the naming rule in words.

**Implementation Outline**

```
patterns/skills/using-patterns/references/patterns/page-objects.md

# Page Objects

## Overview
<name the pattern; core principle: one object per screen/console owns
selectors and waits behind verb-phrase, user-intent methods; cite Fowler's
PageObject bliki>

## When to Use
- <acceptance/e2e test drives the same screen/console repeatedly>
- <selectors/waits duplicated across several tests>
- <a UI change breaks multiple unrelated tests at once>

**When NOT to use:** <a test that touches a screen exactly once; a unit
test with no UI surface>

## Core Pattern
<Before: inline selectors/waits in a test for stellar_commander's System
console. After: a SystemConsole page object exposing System_findObject(...)
and Helm_setManeuver(...) as verb-phrase methods; the test calls them>
```

## Step 4: Quick Reference and Common Mistakes

**Enables:** T4 complete (all six sections present with non-empty bodies), T6 (selectors/waits belong in the page object, assertions stay in the test).

Add the remaining two sections to `page-objects.md`.

- **Quick Reference:** a table mapping responsibility to owner — selectors, waits, verb-phrase methods on the left column mapped to "page object"; assertions, test-specific data, and the test's own arrange/act/assert phases mapped to "test". This is where the literal words "selector", "wait", and "assert" land for T6.
- **Common Mistakes:** 4–6 bolded entries per the sibling shape, e.g. asserting inside the page object, exposing raw selectors as public methods instead of verb phrases, one page object spanning multiple screens/consoles, method names describing DOM structure instead of user intent.

**Tests**

No new automated test — this step targets T4 (fully) and T6.

```
test "T4 complete, T6 holds after step 4":
  run developer/tests/test_page_objects_pattern.py
  assert failure has moved past T4 and T6 (now fails at T7, since Composes With is still empty)
```

- Edge case: T6 requires both "selector" and "wait" to appear (independent of section), and "assert" to appear stating assertions stay in the test, not the page object — phrase the Quick Reference row and a Common Mistakes entry so the assertion rule reads as a rule ("the page object never asserts"), not just the bare word "assert" appearing incidentally elsewhere.
- Edge case: keep the `## Common Mistakes` heading present even though the file already has substantial content — the section-extraction test requires the heading to exist with a non-empty body before the next `##` heading (`## Composes With`, added in Step 5).

**Implementation Outline**

```
## Quick Reference
| Responsibility | Owner |
|---|---|
| Selectors / locators | Page object |
| Waits | Page object |
| Verb-phrase action methods | Page object |
| Assertions | Test |
| Arrange / Act / Assert phases | Test |

## Common Mistakes
- **Asserting inside the page object.** <corrective: return values/state; let the test assert>
- **Exposing raw selectors as public methods.** <corrective: verb-phrase intent methods only>
- **One page object spanning multiple screens/consoles.** <corrective: one object per screen/console>
- **Method names mirror DOM/console structure instead of user intent.** <corrective: name by action, e.g. System_findObject not System_clickSearchButton>
```

## Step 5: Composes With cross-link

**Enables:** T7 (the `Composes With` section cross-links `arrange-act-assert`), and completes T4 (sixth section present). Feature test should be fully green after this step.

Add the final `## Composes With` section to `page-objects.md`, cross-linking `references/patterns/arrange-act-assert.md` per design.md's Specification: the page object's verb-phrase method calls are the test's Act; the test still owns its own Arrange and Assert. Per design.md's Alternatives, do not cross-link `triangulate` — no natural relationship, and the issue does not report confusion there.

**Tests**

```
test "feature test green after step 5":
  run developer/tests/test_page_objects_pattern.py
  assert exit code 0
  assert stdout == "PASS: page-objects pattern contract holds"
```

- Edge case: T7 requires the literal substring `arrange-act-assert` inside the `Composes With` section body specifically (case-insensitive) — a mention elsewhere in the file (e.g. Core Pattern) does not satisfy T7; it must be in this section.
- Edge case: after this step, re-run `patterns/skills/using-patterns/SKILL.md`'s own sanity (no automated test exists for it beyond this feature test) to confirm the new routing row and discriminator entry from Steps 1–2 are still present and unmodified by the reference-file work in Steps 3–5 (they live in different files, so no conflict is expected, but confirm before calling the feature green).

**Implementation Outline**

```
## Composes With
- **`patterns:arrange-act-assert`** (`references/patterns/arrange-act-assert.md`)
  — the page object's verb-phrase method calls are the test's Act; the test
  still owns its own Arrange and Assert, and never asserts inside the page
  object.
```

## Notes for the Build phase

- Re-run `developer/tests/test_page_objects_pattern.py` after every step; it prints the single earliest-failing check by name (T1–T7), so progress is directly observable.
- No unit tests beyond the feature test itself: this is a two-file prose contract with one already-written contract test, mirroring `test_fable5_softblock.py`'s precedent (`.ailly/developer/2026-07-03-A-fable-5-softblock/`) — a second, narrower test would just re-check substrings the feature test already covers.
- Design.md defers the e2e discovery/invocation/checker case under `patterns/e2e/` (a `page-objects.md` prompt, `check_page_objects.py`, and `evals/invocation.yaml` / `assemblies/invocation.yaml` entries) to the Build phase as a fast-follow if time allows, consistent with `configuring-feature-flags`/`using-feature-flags` shipping without one. It is not a step in this plan and not required for the feature test to pass; do not block on it.
- Keep `general:writing-pattern-skills` loaded through Steps 3–5 so the reference file's voice and section shape stay aligned with `arrange-act-assert.md` and `triangulate.md` throughout.
