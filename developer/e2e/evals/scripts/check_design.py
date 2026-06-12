#!/usr/bin/env python3
"""Structural checker for the `design` invocation case.

Rules trace 1:1 to the design SKILL.md. "Design Docs" fixes the six required
sections; "The Feature Test" requires exactly one executable feature test
embedded with the design; "After the Design" requires the `*Draft YYYY-MM-DD*`
marker a human later clears.

Rules:
- R1 the six design-doc sections are all present (Purpose, Prior Art, User
  Journey and Metrics, Specification, Alternatives, Summary).
- R2 the draft marker is present (the artifact is offered as a draft for human
  review, not as a finished doc).
- R3 exactly one executable test function is embedded (the merged design writes
  the single end-to-end feature test, not zero and not a suite of unit tests).
"""

import re
import sys

from _checker_utils import code_text, fail, has_draft_marker, has_heading, read_stdin

SECTIONS = [
    "Purpose",
    "Prior Art",
    "User Journey and Metrics",
    "Specification",
    "Alternatives",
    "Summary",
]

TEST_DEF = re.compile(r"\bdef\s+test\w*\s*\(")


def main() -> int:
    text = read_stdin()

    # R1 — all six sections present.
    missing = [s for s in SECTIONS if not has_heading(text, s)]
    if missing:
        return fail(
            "R1 six sections required: design doc is missing section heading(s) "
            + ", ".join(missing)
            + "; the design skill fixes exactly Purpose, Prior Art, User Journey "
            "and Metrics, Specification, Alternatives, Summary"
        )

    # R2 — draft marker present.
    if not has_draft_marker(text):
        return fail(
            "R2 draft marker required: no *Draft YYYY-MM-DD* marker; the design "
            "skill writes the doc as a draft for a human to clear before the next "
            "phase"
        )

    # R3 — exactly one embedded feature test.
    n = len(TEST_DEF.findall(code_text(text)))
    if n == 0:
        return fail(
            "R3 one feature test required: found no `def test...` function; the "
            "merged design skill embeds one executable feature test that runs the "
            "user story end-to-end"
        )
    if n > 1:
        return fail(
            f"R3 one feature test required: found {n} test functions; the design "
            "skill writes a single end-to-end feature test, not a suite"
        )

    return 0


if __name__ == "__main__":
    sys.exit(main())
