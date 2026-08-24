# Triangulation

## Overview

Triangulation is the most conservative of the three green bar strategies (alongside Fake It and Obvious Implementation). Named after radar triangulation — where two reference points are required to locate a position — the technique says: **abstract only when two or more examples demand it.**

The guiding principle: *as tests get more specific, the code gets more generic.*

Use it when you have faked an implementation and are unsure how to generalize, or when you are exploring unfamiliar territory and want tests to drive the design rather than guessing it.

## When to Use

- You returned a hardcoded constant to pass the first test and aren't sure what the real implementation should look like.
- You are exploring an algorithm or formula you have not worked out analytically.
- Premature abstraction has burned you before in this area of the codebase.

**When NOT to use:**
- The correct implementation is immediately apparent — use Obvious Implementation instead.
- You can already see the duplication between the fake code and the test, and you know exactly how to remove it — just refactor; triangulation is unnecessary.
- You already have two passing examples and a clear pattern — add the refactor, don't add more tests.

## Core Pattern

**Step 1 — Write a failing test and fake it:**

```python
def test_sum_first():
    assert sum(1, 2) == 3

# Fake implementation — hardcoded to pass:
def sum(a, b):
    return 3
```

The test passes, but the implementation is wrong for any other inputs.

**Step 2 — Add a second test that the fake cannot satisfy:**

```python
def test_sum_second():
    assert sum(3, 4) == 7  # fails: returns 3
```

Now the fake implementation is exposed. The second test triangulates the position of the real implementation: you must generalize.

**Step 3 — Write the real implementation:**

```python
def sum(a, b):
    return a + b
```

Both tests pass. Refactor if needed.

## The Rule of Three

Triangulation requires two examples before abstracting. The **Rule of Three** is a stricter variant:

| Occurrence | Action |
|------------|--------|
| First | Implement directly, no abstraction |
| Second | Notice the pattern — hold off |
| Third | Refactor with confidence |

Prefer the Rule of Three when the abstraction boundary is unclear or when the domain is new. Waiting for a third example prevents locking in an abstraction that only covers two narrow cases.

## Quick Reference

| Situation | What to do |
|-----------|------------|
| First test passes with fake | Write a second test with different inputs |
| Second test exposes fake | Write the real implementation |
| Unsure if pattern is real | Wait for a third example (Rule of Three) |
| Implementation is obvious | Skip triangulation; use Obvious Implementation |
| Duplication is clear | Skip triangulation; refactor directly |

## Common Mistakes

- **Refactoring after one example.** A single test can pass with a lucky constant. The abstraction is unproven. Add the second test first.
- **Triangulating the obvious.** If you already know `sum(a, b)` returns `a + b`, writing a fake and a second test is waste. Reserve triangulation for genuine uncertainty.
- **Picking triangulation tests that don't diverge.** The second test must fail on the fake. If `sum(1, 2) == 3` and `sum(0, 3) == 3` both pass the hardcoded `return 3`, the triangle is degenerate — pick inputs whose expected output differs from the fake's constant.
- **Stopping at two examples when the pattern is still ambiguous.** Two data points can fit many curves. If the generalization still feels forced, add a third before abstracting.

## Composes With

- **the arrange-act-assert pattern (`references/patterns/arrange-act-assert.md`)** — each test in the triangulation sequence is an independent AAA test; do not combine the two examples into one test.
- **the red-green-refactor (build) phase** (`/ailly build`) — triangulation is a strategy for the green phase when the refactor step is blocked by uncertainty about the correct abstraction.
- **bifurcate (`references/patterns/bifurcate.md`)** — inverse pressure: triangulation adds examples to locate an implementation; bifurcation adds discriminating probes to shrink a hypothesis set during debugging. A hardcoded fake that passes one example routes here; several live root-cause explanations route to bifurcate.

## Additional Notes

Triangulation is a better pattern to use when debugging is likely. Because Triangulation has tests that approach the same functionality from multiple angles, if failures arise in the future, they serve as good starting points for debugging sessions.