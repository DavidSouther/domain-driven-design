# research:internal findings — stellar_commander issue #81 (motivating case)

## Query
The issue body cites `DavidSouther/stellar_commander#81` as the encountered
motivating case. Read it for the concrete naming convention and layout this
ability should be able to explain.

## Findings
- Issue #81, "Scenarios page-object refactor: `src/pages/` layout per Code
  Structure doc" (open, deferred from #77, parent #77).
- The Code Structure doc (Notion, mirrored in that repo's DEVELOPMENT.md)
  prescribes `scenarios/src/pages/` with page objects named
  `<Console>_<action>.py`: examples given are `Menu_LoadGame.py`,
  `System_findObject.py`, `Helm_setManeuver.py`.
- Scope of #81: introduce the `src/pages/` layout, extract shared
  server/driver fixtures and a console-rail navigation helper into the page
  layer, and migrate existing scenario tests onto the page objects without
  changing what they assert — i.e., the assertions stay in the tests; only
  the setup/navigation/selector logic moves into the page objects. This is
  the same page-vs-test split the public sources describe.
- Decided in that repo's own #77 design review that this refactor is a
  separate feature, not scope creep on their console foundation work — i.e.
  the pattern is being applied deliberately and incrementally, which is a
  useful "when to reach for this" cue: introduce page objects when a
  console/screen accumulates enough scenario tests that fixtures and
  selectors start duplicating across them, not from the first test.

## Relevance to issue #27
Supplies a ready-made, real, non-invented worked example
(`Menu_LoadGame`, `System_findObject`, `Helm_setManeuver`) for the new
reference's Core Pattern section, and a naming rule (`<Console>_<action>`,
one file per console/screen) to state explicitly in the reference.

## Sources
[3] D. Souther, "Scenarios page-object refactor: src/pages/ layout per Code
Structure doc," DavidSouther/stellar_commander, issue #81 (open, read-only via
`gh issue view 81 -R DavidSouther/stellar_commander`). Accessed Jul. 3, 2026.
