# Research: Page Objects Pattern (issue #27)

## Topic and Intent

The patterns plugin teaches test structure (`arrange-act-assert`) and test-driving
implementations (`triangulate`) but has no ability for the Page Object pattern:
encapsulating a UI surface behind an object that exposes user-intent, verb-phrase
actions (`System_findObject`, `Helm_setManeuver`) so acceptance tests read as
journeys and selector changes localize to one file. Add a `page-objects` ability
to `patterns:using-patterns`, routed alongside `arrange-act-assert`, with a
reference at `references/patterns/page-objects.md`.

## Search/Expand

Public prior art (general lens) confirms a stable, well-established shape for this
pattern with two consistent rules that map directly onto the issue's own framing:

- The page object owns locators (selectors) and waits; it is the single place UI
  structure knowledge lives. When the UI changes, only the page object changes [1].
- The page object exposes methods as **verb phrases** describing user intent
  (`loginAs(...)`, `typeUsername(...)`), never raw selectors or WebElements, and
  methods return the next page object (or self) to support chaining into a
  readable journey [1][2].
- Assertions belong in the test, not the page object. "Page objects themselves
  should never make verifications or assertions" — that stays in the test's code
  [1]. This is the same in/out split the issue names: "waits and selectors in the
  page; assertions in the test."
- Originated by Martin Fowler as an adaptation of Facade/Adapter to UI test
  automation; the primary payoff is encapsulation that keeps test code about
  intent, not DOM/console structure [2].

## Libraries & Skills

This is a documentation-only ability (a markdown reference added to the patterns
plugin's own catalog) — no runtime library or framework is being integrated, so
there is no third-party getting-started guide or example to load. The relevant
"library" is the patterns plugin's own authoring convention, not an external one:

Before doing any work in this feature, load these skills via the active harness's
skill-loading mechanism: `general:writing-pattern-skills` (the authoring
convention for a new pattern skill — frontmatter, section structure, and the
`references/patterns/` layout) during Design and Build. No other framework skill
applies; this ability does not touch a specific test framework's API surface, so
no per-framework skill (e.g. a Selenium/Playwright skill) is in scope. If a later
phase discovers the concrete triggering example needs framework-specific code
(e.g. a TypeScript/Playwright or Python/Selenium snippet), note that as a Design
decision rather than pulling in a framework skill here.

## Falsification/Refine

- **Size**: a single feature — one new pattern reference plus one routing-table
  row and one discriminator note in `patterns/skills/using-patterns/SKILL.md`.
  Comparable in scope to the existing `arrange-act-assert` and `triangulate`
  additions (both are single markdown files with no per-language subdirectory,
  since the pattern is a structural/organizational convention rather than a
  language-specific idiom).
- **Off-the-shelf?** No — this plugin's pattern catalog is bespoke to this repo's
  authoring convention (frontmatter + Overview/When to Use/Core Pattern/Quick
  Reference/Common Mistakes/Composes With). Wholesale reuse of an external
  "Page Object" writeup would not match that shape or cross-link the sibling
  patterns.
- **Collaboration?** No other team/skill owns this; it is a self-contained
  addition to `patterns:using-patterns`.
- **Smallest version that meets intent**: one reference file
  (`references/patterns/page-objects.md`) covering: when to use it (acceptance/
  UI/e2e tests exercising a screen or console repeatedly), naming (one page
  object per screen/console; verb-phrase methods per user action — the issue's
  own examples `System_findObject`, `Helm_setManeuver` are directly reusable),
  the page-vs-test split (selectors + waits in the page; assertions in the
  test), and how it composes with `arrange-act-assert` (the page object's
  methods are the Act; the test still keeps its own Arrange/Assert). Plus one
  routing-table row in `SKILL.md` and one discriminator entry distinguishing
  page-objects from arrange-act-assert (structuring one test's phases vs.
  encapsulating a reusable UI surface across many tests).
- Whether the e2e eval harness (`patterns/e2e/{prompts,evals}`) gets a
  `page-objects` invocation/discovery case and checker script (mirroring
  `triangulate`'s `check_triangulate.py`) is a Build-phase decision, not
  Research's to make — noted here so Design can size it, not resolved here.

## Scope

**In scope for Design/Build:**
- New reference `patterns/skills/using-patterns/references/patterns/page-objects.md`
  following the existing pattern-file shape (Overview, When to Use, Core Pattern
  with Before/After code, Quick Reference, Common Mistakes, Composes With).
- One new routing-table row in
  `patterns/skills/using-patterns/SKILL.md`, discriminated against
  `arrange-act-assert` (and, if needed, against `bootstrap-and-service`, since
  both involve wiring test-support objects — Design should confirm whether that
  second discriminator is warranted or whether page-objects only needs to be
  distinguished from arrange-act-assert).
- Naming convention: one page object per screen/console, verb-phrase methods
  per user-visible action (the issue's `System_findObject`, `Helm_setManeuver`
  examples), no assertions inside the page object, selectors/waits localized to
  the page object.

**Out of scope for this feature:**
- Building or modifying the `stellar_commander` `scenarios/src/pages/` layout
  itself (DavidSouther/stellar_commander#81 tracks that downstream consumer;
  this feature only adds the teaching ability upstream in this repo).
- Any framework-specific (Selenium/Playwright/Cypress) binding code — the
  reference teaches the pattern generically, consistent with how
  `arrange-act-assert` and `triangulate` have no per-language subdirectory.
- Per-language subdirectories (`python.md`/`rust.md`/`typescript.md`) — matched
  against the two existing test-technique patterns, neither of which has them;
  this is an organizational pattern, not a language-idiom pattern, so Design
  should default to no subdirectory unless it finds a concrete need.

## Resolved Decisions

- **Where the ability lives**: `patterns:using-patterns`, alongside
  `arrange-act-assert` and `triangulate`, not a new top-level skill — decided
  directly from the issue's own instruction ("routed from
  `patterns:using-patterns` alongside arrange-act-assert").
- **No per-language variants**: decided by precedent — the two other
  test-technique patterns in this catalog ship as single files.
- **No framework skill dependency**: decided because the ability is about the
  organizational pattern (what/where), not about driving any specific browser
  or test-automation library.
- **Real-world naming source**: the `<Console>_<Action>` naming
  (`Menu_LoadGame`, `System_findObject`, `Helm_setManeuver`) is confirmed live
  in `DavidSouther/stellar_commander#81` ("Scenarios page-object refactor:
  `src/pages/` layout per Code Structure doc"), so the reference can use these
  exact names as its worked example instead of inventing new ones.

**Open for the human (non-blocking, Design can proceed on the stated defaults):**
- Whether to add an e2e discovery/invocation/checker case under `patterns/e2e/`
  in this same feature or as a fast-follow. Default if not overridden: add a
  minimal invocation case and structural checker in Build, mirroring
  `triangulate`'s, since every other cataloged pattern in `patterns/e2e/prompts`
  has one and an ability without an eval is untested against drift.
- Whether page-objects needs a second discriminator entry (vs.
  `bootstrap-and-service`) in `SKILL.md`. Default: add it only if Design finds
  the two are actually confused in practice; the issue does not raise this
  confusion, so it is not required.

## Sources

[1] Selenium Project, "Page object models," Selenium Documentation. [Online].
Available: https://www.selenium.dev/documentation/test_practices/encouraged/page_object_models/
[Accessed: Jul. 3, 2026].

[2] M. Fowler, "PageObject," martinfowler.com bliki, 2013. [Online]. Available:
https://martinfowler.com/bliki/PageObject.html [Accessed: Jul. 3, 2026].

[3] D. Souther, "Scenarios page-object refactor: src/pages/ layout per Code
Structure doc," DavidSouther/stellar_commander, issue #81 (open). [Online].
Available: https://github.com/DavidSouther/stellar_commander/issues/81
[Accessed: Jul. 3, 2026].
