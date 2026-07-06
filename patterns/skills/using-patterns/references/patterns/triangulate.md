# Triangulation

## Overview

Triangulation is the most conservative of the three green bar strategies (alongside Fake It and Obvious Implementation). In radar triangulation, two reference points locate a position. The technique applies this principle: **abstract only when two or more examples demand it.**

The guiding principle: *as tests get more specific, the code gets more generic.*

Use it when you have faked an implementation and are unsure how to generalize. Also use it when exploring unfamiliar territory and you want tests to drive the design rather than guessing it.

## When to use

- You returned a hardcoded constant to pass the first test and aren't sure what the real implementation should look like.
- You are exploring an algorithm or formula you have not worked out analytically.
- Premature abstraction has burned you before in this area of the codebase.

**When NOT to use:**
- The correct implementation is immediately apparent. Use Obvious Implementation instead.
- You can already see the duplication between the fake code and the test, and you know exactly how to remove it. Just refactor; triangulation is unnecessary.
- You already have two passing examples and a clear pattern. Add the refactor, don't add more tests.

## Core pattern

**Step 1—Write a failing test and fake it:**

```python
def test_sum_first():
    assert sum(1, 2) == 3

# Fake implementation hardcoded to pass:
def sum(a, b):
    return 3
```

The test passes, but the implementation is wrong for any other inputs.

**Step 2—Add a second test that the fake cannot satisfy:**

```python
def test_sum_second():
    assert sum(3, 4) == 7  # fails: returns 3
```

The second test now exposes the fake implementation. It triangulates the position of the real implementation: you must generalize.

**Step 3—Write the real implementation:**

```python
def sum(a, b):
    return a + b
```

Both tests pass. Refactor if needed.

## The rule of three

Triangulation requires two examples before abstracting. The **Rule of Three** is a stricter variant:

| Occurrence | Action |
|------------|--------|
| First | Implement directly, no abstraction |
| Second | Notice the pattern; hold off |
| Third | Refactor with confidence |

Prefer the Rule of Three when the abstraction boundary is unclear or when the domain is new. Waiting for a third example prevents locking in an abstraction that only covers two narrow cases.

## Quick reference

| Situation | What to do |
|-----------|------------|
| First test passes with fake | Write a second test with different inputs |
| Second test exposes fake | Write the real implementation |
| Unsure if pattern is real | Wait for a third example (Rule of Three) |
| Implementation is obvious | Skip triangulation; use Obvious Implementation |
| Duplication is clear | Skip triangulation; refactor directly |

## Common mistakes

- **Refactoring after one example.** A single test can pass with a lucky constant. A lucky constant leaves the abstraction unproven. Add the second test first.
- **Triangulating the obvious.** If you already know `sum(a, b)` returns `a + b`, writing a fake and a second test is waste. Reserve triangulation for genuine uncertainty.
- **Picking triangulation tests that don't diverge.** The second test must fail on the fake. If `sum(1, 2) == 3` and `sum(0, 3) == 3` both pass the hardcoded `return 3`, the triangle is degenerate. Pick inputs whose expected output differs from the fake's constant.
- **Stopping at two examples when the pattern is still ambiguous.** Two data points can fit many curves. If the generalization still feels forced, add a third before abstracting.

## Composes with

- **the arrange-act-assert pattern (`references/patterns/arrange-act-assert.md`)**. Each test in the triangulation sequence is an independent AAA test. Do not combine the two examples into one test.
- **the red-green-refactor (build) phase** (`/ailly build`). Triangulation is a strategy for the green phase when uncertainty about the correct abstraction blocks the refactor step.

## Additional notes

Triangulation is a better pattern to use when debugging is likely. Triangulation has tests that approach the same capability from multiple angles. If failures arise in the future, they serve as good starting points for debugging sessions.