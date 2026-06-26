#!/usr/bin/env python3
"""Structural checker for the `domain` invocation case.

Rules trace to domain/SKILL.md "Output Format":
- R1 research-note path convention `.ailly/research/<dated-dir>/domain.md`.
- R2 a `## Key Concepts` section (the domain-specific block defining terms and
  relationships).
- R3 a `## Sources` section.
"""

import re
import sys

from _md import candidate, fail

PATH = re.compile(r"\.ailly/research/\d{4}-\d{2}-\d{2}-[\w-]+/domain\.md")


def main() -> int:
    text = candidate()
    low = text.lower()

    if not PATH.search(text):
        return fail(
            "R1 path convention: no `.ailly/research/<YYYY-MM-DD-A-topic>/domain.md` "
            "path; the skill writes findings to that dated research-note path"
        )

    if "key concepts" not in low:
        return fail(
            "R2 note structure: no `## Key Concepts` section; the domain note defines "
            "the terms and their relationships under it"
        )

    if "## sources" not in low:
        return fail(
            "R3 note structure: missing a `## Sources` section listing the domain "
            "artifacts and DDD concepts consulted"
        )

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
