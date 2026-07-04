# research:public findings — Page Object pattern

## Query
Public prior art on the Page Object pattern for UI/acceptance test automation:
origin, canonical shape, naming, and the page/test responsibility split.

## Findings
- Page Object Model was popularized by Martin Fowler as an adaptation of the
  Facade/Adapter patterns to UI test automation. A page object is a class that
  serves as the interface to one page (or screen/console); tests call its
  methods instead of touching the UI directly [2].
- Selenium's own project documentation states the canonical division of
  responsibility: "Page objects themselves should never make verifications or
  assertions. This is part of your test and should always be within the test's
  code." Page objects hold locators and validate that the correct page loaded;
  methods are named as verb phrases representing user services
  (`loginAs(username, password)`), not raw selector accessors, and return the
  next page object to support chained, readable journeys [1].
- Consequence cited by both sources: because all locator/UI-structure knowledge
  lives in one class per screen, a UI change requires editing only that one
  page object, not every test that exercises the screen [1][2].

## Relevance to issue #27
Confirms the issue's own claims 1:1: selectors/waits belong in the page,
assertions belong in the test, and methods should be named as user intent
(matching the issue's `System_findObject`, `Helm_setManeuver` examples). No
conflicting guidance found across sources.

## Sources
[1] Selenium Project, "Page object models," Selenium Documentation.
https://www.selenium.dev/documentation/test_practices/encouraged/page_object_models/
(accessed Jul. 3, 2026).
[2] M. Fowler, "PageObject," martinfowler.com bliki, 2013.
https://martinfowler.com/bliki/PageObject.html (accessed Jul. 3, 2026).
