#!/usr/bin/env python3
"""Structural checker for the `red-green-refactor` invocation case.

Rules trace 1:1 to the red-green-refactor SKILL.md: "Type-First: write
signatures with stub bodies before writing any tests", and "Add one test per
iteration" using arrange-act-assert.

Rules:
- R1 exactly one test function (one test per iteration, not a suite, not zero).
- R2 a type-first stub is shown (signatures written with stub bodies — the
  Python forms the skill names: `...`, `raise NotImplementedError`, etc.).
- R3 the first stub appears before the first test (signatures precede tests —
  the type-first ordering the skill mandates).
"""

import re
import sys

from _checker_utils import fail, read_stdin

TEST_DEF = re.compile(r"\bdef\s+test\w*\s*\(")
# Type-first stub markers: the Python stub forms the skill enumerates, plus the
# usual placeholders a stub body takes before implementation replaces it.
STUB = re.compile(
    r"raise\s+NotImplementedError"
    r"|NotImplementedError"
    r"|not\s+implemented"
    r"|^\s*\.\.\.\s*$"
    r"|#\s*stub"
    r"|\bTODO\b",
    re.IGNORECASE | re.MULTILINE,
)


def main() -> int:
    text = read_stdin()

    # R1 — exactly one test.
    tests = list(TEST_DEF.finditer(text))
    if len(tests) == 0:
        return fail(
            "R1 one test required: found no `def test...` function; the cycle "
            "writes one arrange-act-assert test for the step"
        )
    if len(tests) > 1:
        return fail(
            f"R1 one test required: found {len(tests)} test functions; the cycle "
            "adds one test per iteration, and this prompt is a single step"
        )

    # R2 — a type-first stub is shown.
    stub = STUB.search(text)
    if not stub:
        return fail(
            "R2 type-first stub required: no stub body shown (e.g. `...` or "
            "`raise NotImplementedError`); the skill writes signatures with stub "
            "bodies before the test"
        )

    # R3 — stub precedes the test (signatures before tests).
    if stub.start() > tests[0].start():
        return fail(
            "R3 type-first ordering: the stub appears after the test; the skill "
            "writes type-first signatures before writing any test"
        )

    return 0


if __name__ == "__main__":
    sys.exit(main())
