#!/usr/bin/env python3
"""Structural checker for the `archaeology` invocation case.

Rules trace to archaeology/SKILL.md "Output Format":
- R1 research-note path convention `docs/research/<dated-dir>/archaeology.md`.
- R2 the note carries a `## Timeline` section (the archaeology-specific block).
- R3 at least one commit SHA (7-40 hex) — archaeology cites the commits its
  conclusions rest on.
"""

import re
import sys

from _md import candidate, fail

PATH = re.compile(r"docs/research/\d{4}-\d{2}-\d{2}-[\w-]+/archaeology\.md")
SHA = re.compile(r"\b[0-9a-f]{7,40}\b")


def main() -> int:
    text = candidate()

    if not PATH.search(text):
        return fail(
            "R1 path convention: no `docs/research/<YYYY-MM-DD-A-topic>/archaeology.md` "
            "path; the skill writes findings to that dated research-note path"
        )

    if "## Timeline" not in text:
        return fail(
            "R2 note structure: missing the `## Timeline` section; the "
            "archaeology note orders the relevant commits in a timeline"
        )

    if not SHA.search(text):
        return fail(
            "R3 commit citation: no commit SHA (7-40 hex) appears; archaeology "
            "cites the commits its conclusions rest on"
        )

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
