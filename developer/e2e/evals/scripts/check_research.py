#!/usr/bin/env python3
"""Structural checker for the `research` invocation case.

Rules trace 1:1 to the research SKILL.md "research.md Sections" list, which fixes
the six required sections, and the "Output Artifacts" section, which requires the
`*Draft YYYY-MM-DD*` marker a human later clears.

Rules:
- R1 the six research-doc sections are all present (Topic and Intent,
  Search/Expand, Falsification/Refine, Scope, Resolved Decisions, Sources).
- R2 the draft marker is present (the artifact is offered as a draft for human
  review, not as a finished doc).
"""

import re
import sys

from _checker_utils import fail, has_draft_marker, read_stdin

SECTIONS = [
    "Topic and Intent",
    "Search/Expand",
    "Falsification/Refine",
    "Scope",
    "Resolved Decisions",
    "Sources",
]


def has_section(text: str, title: str) -> bool:
    """Like _checker_utils.has_heading, but tolerant of whitespace around a `/`.

    The two phase sections are written "Search/Expand" and "Falsification/Refine"
    in the contract, but a model legitimately renders either side of the slash
    with spaces ("Search / Expand"). Matching the slash loosely keeps the
    invocation arm from failing its own checker on a cosmetic spacing choice,
    without weakening the rule (the baseline arm still omits the sections).
    """
    pattern = r"\s*/\s*".join(re.escape(part) for part in title.split("/"))
    heading = re.compile(
        r"^\s{0,3}(?:#{1,6}\s+|\*\*)" + pattern + r"\b",
        re.IGNORECASE | re.MULTILINE,
    )
    return bool(heading.search(text))


def main() -> int:
    text = read_stdin()

    # R1 — all six sections present.
    missing = [s for s in SECTIONS if not has_section(text, s)]
    if missing:
        return fail(
            "R1 six sections required: research doc is missing section heading(s) "
            + ", ".join(missing)
            + "; the research skill fixes exactly Topic and Intent, Search/Expand, "
            "Falsification/Refine, Scope, Resolved Decisions, Sources"
        )

    # R2 — draft marker present.
    if not has_draft_marker(text):
        return fail(
            "R2 draft marker required: no *Draft YYYY-MM-DD* marker; the research "
            "skill writes the doc as a draft for a human to clear before the next "
            "phase"
        )

    return 0


if __name__ == "__main__":
    sys.exit(main())
