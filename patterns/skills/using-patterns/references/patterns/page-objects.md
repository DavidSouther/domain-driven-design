# Page objects

## Overview

A page object encapsulates one UI surface (a screen, a page, or a console) behind an object.
That object exposes verb-phrase, user-intent methods like `System_findObject` and `Helm_setManeuver` instead of raw selectors.
The object owns every locator and wait for that surface.
A test drives the surface only through the object's methods, never through a direct selector.
The core principle, from Fowler's `PageObject` bliki: when the UI changes, exactly one file changes with it.
The acceptance tests that read like user journeys never see the difference.

## When to use

- An acceptance or e2e test drives the same screen or console repeatedly across several test cases.
- Multiple tests duplicate selectors and waits for one UI surface.
- A single UI change (a renamed button, a moved control) breaks several unrelated tests at once.
- A test reads as a sequence of low-level DOM/console interactions rather than a sequence of user actions.

**When not to use:** a one-off test that touches a screen exactly once, where the encapsulation cost is not repaid.
A unit test with no UI surface to encapsulate.
Route that to `arrange-act-assert` instead.

## Core pattern

**Before:** the test inlines selectors and waits for `stellar_commander`'s `System` console, so a control rename breaks every test that touches it:

```python
def test_system_console_finds_object():
    driver.find_element(By.ID, "system-console").click()
    driver.find_element(By.CSS_SELECTOR, "[data-role=search-input]").send_keys("Sol-3")
    wait.until(EC.element_to_be_clickable((By.ID, "search-btn"))).click()
    result = driver.find_element(By.CLASS_NAME, "search-result").text
    assert result == "Sol-3"
```

**After:** a `SystemConsole` page object owns the selectors and waits behind a verb-phrase method; the test only acts through it and asserts on the return value:

```python
class SystemConsole:
    def __init__(self, driver, wait):
        self._driver = driver
        self._wait = wait

    def System_findObject(self, name: str) -> str:
        self._driver.find_element(By.ID, "system-console").click()
        self._driver.find_element(By.CSS_SELECTOR, "[data-role=search-input]").send_keys(name)
        self._wait.until(EC.element_to_be_clickable((By.ID, "search-btn"))).click()
        return self._driver.find_element(By.CLASS_NAME, "search-result").text


def test_system_console_finds_object():
    system = SystemConsole(driver, wait)

    result = system.System_findObject("Sol-3")

    assert result == "Sol-3"
```

Naming follows one pattern: one page object per screen or console (`SystemConsole`, `HelmConsole`).
Name methods as verb phrases describing the user's intent (`System_findObject`, `Helm_setManeuver`), never the DOM or console structure the method happens to tap.

## Quick reference

| Responsibility | Owner |
|---|---|
| Selectors / locators | Page object |
| Waits | Page object |
| Verb-phrase action methods | Page object |
| Assertions | Test |
| Arrange / Act / Assert phases | Test |

## Common mistakes

- **Asserting inside the page object.**
  The page object never asserts; it returns values or exposes observable state, and the test asserts on what it returns.
- **Exposing raw selectors as public methods.**
  A method like `getSearchButton()` leaks DOM structure back into the test.
  Expose only verb-phrase intent methods like `System_findObject`.
- **One page object spanning multiple screens or consoles.**
  Split by surface: one page object per screen or console, not one page object for the whole app.
- **Method names mirror DOM/console structure instead of user intent.**
  `System_clickSearchButton` describes the DOM; `System_findObject` describes the user's action.
  Name by intent.
- **Re-deriving selectors in the test "just this once."**
  Any selector or wait written directly in a test, even for a quick check, defeats the localization the page object exists to provide.
  Move it into the page object instead.

## Composes with

- **`patterns:arrange-act-assert`** (`references/patterns/arrange-act-assert.md`).
  The page object's verb-phrase method calls are the test's Act.
  The test still owns its own Arrange and Assert, and never asserts inside the page object.
