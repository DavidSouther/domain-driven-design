#!/usr/bin/env python3
"""Structural checker for the `books` invocation case.

Rules trace to books/SKILL.md "Output format" and "Common mistakes":
- R1 research-note path convention `.ailly/research/<dated-dir>/books.md`.
- R2 a `## Sources` section.
- R3 an ISBN-13 (the question asks for the canonical ISBN-13).
- R4 no wiring-leak preface (the "Re-teaching the wiring" mistake).
"""

import re
import sys

from _md import candidate, fail

PATH = re.compile(r"\.ailly/research/\d{4}-\d{2}-\d{2}-[\w-]+/books\.md")
ISBN13 = re.compile(r"97[89][\d -]{10,17}")
LEAK = [
    "first install",
    "first, install",
    "make sure you have configured",
    "make sure you've configured",
    "make sure you have installed",
    "you must install",
    "you must first",
    "before you can",
    "ensure you have configured",
    "set up the mcp",
]


def has_isbn13(text: str) -> bool:
    for m in ISBN13.finditer(text):
        digits = re.sub(r"\D", "", m.group(0))
        if len(digits) == 13:
            return True
    return False


def main() -> int:
    text = candidate()
    low = text.lower()

    if not PATH.search(text):
        return fail(
            "R1 path convention: no `.ailly/research/<YYYY-MM-DD-A-topic>/books.md` "
            "path; the skill writes findings to that dated research-note path"
        )

    if "## Sources" not in text:
        return fail(
            "R2 note structure: missing a `## Sources` section; the books note "
            "lists every source consulted under it"
        )

    if not has_isbn13(text):
        return fail(
            "R3 ISBN-13: no 13-digit ISBN found; the question asks for the canonical "
            "ISBN-13 and the note should carry it"
        )

    for phrase in LEAK:
        if phrase in low:
            return fail(
                f"R4 wiring leak: a setup preface ('{phrase}') appears; configuration "
                "belongs in research:configuring-books, not in per-query practice"
            )

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
