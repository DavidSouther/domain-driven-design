# Arrange-Act-Assert

## Overview

Structure every test as three distinct, visually separated phases: **Arrange** the preconditions, **Act** by invoking the code under test exactly once, then **Assert** the outcomes. The blank lines between phases are not style — they make the test's intent immediately readable and force each test to exercise one behavior.

An equivalent framing from BDD: **Given** the system is in a known state, **When** an operation occurs, **Then** observable behavior changes in a specific way. GWT nudges phrasing toward user-visible behavior rather than internal mechanics.

## When to Use

- Writing any test from scratch (apply the structure before writing code, not after).
- Reviewing an existing test that is hard to understand at a glance.
- A test failure message doesn't tell you what was being tested.
- A test exercises more than one behavior ("and it also...").

**When NOT to use:** Parameterized/property-based tests where the framework iterates inputs — the framework owns the structure. Acceptance tests expressed in Gherkin already use Given/When/Then natively; don't duplicate AAA sections inside step definitions.

## Core Pattern

**Before** — phases are interleaved, intent is hidden:

```python
def test_checkout():
    cart = Cart()
    cart.add(Item("book", 12.00))
    assert cart.total() == 12.00      # assertion mid-setup
    cart.add(Item("pen", 1.50))
    result = cart.checkout()
    assert result.status == "ok"
    assert cart.total() == 0          # which behavior does this test?
```

**After** — one blank line per boundary, one behavior per test:

```python
def test_checkout_clears_cart():
    # Arrange
    cart = Cart()
    cart.add(Item("book", 12.00))
    cart.add(Item("pen", 1.50))

    # Act
    cart.checkout()

    # Assert
    assert cart.total() == 0


def test_checkout_returns_ok_status():
    cart = Cart()
    cart.add(Item("book", 12.00))

    result = cart.checkout()

    assert result.status == "ok"
```

The comment labels (`# Arrange`, `# Act`, `# Assert`) are optional when blank lines already make the structure obvious. Prefer blank lines alone; add labels only where the phase boundary might be misread.

## Quick Reference

| Phase | What goes here | One rule |
|-------|----------------|----------|
| **Arrange** | Create objects, seed databases, stub dependencies | No assertions |
| **Act** | Call the function or method under test | Exactly one call |
| **Assert** | Check return values and observable side-effects | No further calls to the system under test |

Given-When-Then maps directly: Given → Arrange, When → Act, Then → Assert.

## Common Mistakes

- **Assertions in the Arrange phase.** Checking preconditions mid-setup conflates "did I set up correctly?" with "did the code behave correctly?". Trust your setup; assert only in the Assert phase.
- **Multiple Acts.** Two calls to the system under test mean two behaviors. Split into two tests; each failure will point at one behavior.
- **Arrange spanning the whole method.** When the setup is long enough to need internal structure, extract a builder or factory helper so the test body stays three clean blocks.
- **No blank lines.** Omitting the visual separators hides the structure. Readers have to deduce phase boundaries from context. Always separate with blank lines.
- **Asserting on Act's return value inline.** `assert system.do_thing() == expected` collapses Act and Assert into one line, losing the phase separation and making the act itself unreadable when it fails.
- **Shared mutable state between tests.** State that bleeds from one test's Arrange into another's Act turns failures into mysteries. Use `setUp`/`beforeEach` only for truly invariant context; keep test-specific setup local to that test's Arrange.

## Composes With

- **the builder pattern (`references/patterns/builder.md`)** — long Arrange phases often signal a missing builder; replace multi-line object construction with a fluent builder call.
- **the parse-dont-validate pattern (`references/patterns/parse-dont-validate.md`)** — tests for parse functions have a natural AAA shape: Arrange raw input, Act by parsing, Assert the domain type.
- **the type-states pattern (`references/patterns/type-states.md`)** — tests for state-machine transitions map directly: Arrange the object in its starting state, Act to trigger the transition, Assert the resulting state.
