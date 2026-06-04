#!/usr/bin/env python3
"""Structural checker for the `design` invocation case.

Rules trace 1:1 to the design SKILL.md "Design Docs" section, which fixes the
six required sections, and the "After the Design" section, which requires the
`*DRAFT YYYY-MM-DD*` marker a human later clears.

Rules:
- R1 the six design-doc sections are all present (Problem Statement, Prior Art,
  Metrics, Specification, Alternatives, Summary).
- R2 the draft marker is present (the artifact is offered as a draft for human
  review, not as a finished doc).
"""

import sys

from _checker_utils import fail, has_draft_marker, has_heading, read_stdin

SECTIONS = [
    "Problem Statement",
    "Prior Art",
    "Metrics",
    "Specification",
    "Alternatives",
    "Summary",
]


def main() -> int:
    text = read_stdin()

    # R1 — all six sections present.
    missing = [s for s in SECTIONS if not has_heading(text, s)]
    if missing:
        return fail(
            "R1 six sections required: design doc is missing section heading(s) "
            + ", ".join(missing)
            + "; the design skill fixes exactly Problem Statement, Prior Art, "
            "Metrics, Specification, Alternatives, Summary"
        )

    # R2 — draft marker present.
    if not has_draft_marker(text):
        return fail(
            "R2 draft marker required: no *DRAFT YYYY-MM-DD* marker; the design "
            "skill writes the doc as a draft for a human to clear before the next "
            "phase"
        )

    return 0


if __name__ == "__main__":
    sys.exit(main())
