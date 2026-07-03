#!/usr/bin/env python3
"""Structural checker for the `design-artifacts` invocation case.

Rules R1-R3 mirror `check_design.py` 1:1 (the response must still be a
well-formed design doc). R4 is the load-bearing, new rule this checker exists
for: the design phase reference must instruct the model to surface a novel,
un-prescribed artifact choice in an **Open Artifact Decisions** section. The
`design-artifacts` prompt plants exactly such an artifact (a disposition
record whose name and format nothing prescribes); a response that settles it
silently in prose, rather than naming it in the section, fails R4.

Rules:
- R1 the six design-doc sections are all present (Purpose, Prior Art, User
  Journey and Metrics, Specification, Alternatives, Summary).
- R2 the draft marker is present (the artifact is offered as a draft for human
  review, not as a finished doc).
- R3 exactly one executable test function is embedded (the design writes the
  single end-to-end feature test, not zero and not a suite of unit tests).
- R4 an **Open Artifact Decisions** heading is present, surfacing the planted
  artifact choice instead of settling it silently.
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

OPEN_ARTIFACT_DECISIONS_HEADING = "Open Artifact Decisions"


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
            "design skill embeds one executable feature test that runs the "
            "user story end-to-end"
        )
    if n > 1:
        return fail(
            f"R3 one feature test required: found {n} test functions; the design "
            "skill writes a single end-to-end feature test, not a suite"
        )

    # R4 — Open Artifact Decisions heading present (load-bearing).
    if not has_heading(text, OPEN_ARTIFACT_DECISIONS_HEADING):
        return fail(
            "R4 Open Artifact Decisions section required: no "
            "'Open Artifact Decisions' heading; the design skill surfaces novel, "
            "un-prescribed artifact choices in a named section rather than "
            "settling them silently in prose"
        )

    return 0


if __name__ == "__main__":
    sys.exit(main())
