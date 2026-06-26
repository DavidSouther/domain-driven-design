#!/usr/bin/env python3
"""Structural checker for the `papers` invocation case.

Rules trace to papers/SKILL.md "Output format" and "Common mistakes":
- R1 research-note path convention `.ailly/research/<dated-dir>/papers.md`.
- R2 a `## Sources` section.
- R3 at least one numbered IEEE-style citation `[N]`.
- R4 no wiring-leak preface (the "Re-teaching the wiring" mistake): setup
  instructions like "first install" belong in the configuring skill, not here.
"""

import re
import sys

from _md import candidate, fail

PATH = re.compile(r"\.ailly/research/\d{4}-\d{2}-\d{2}-[\w-]+/papers\.md")
CITATION = re.compile(r"\[\d+\]")
LEAK = [
    "first install",
    "first, install",
    "make sure you have configured",
    "make sure you've configured",
    "make sure you have installed",
    "you must install",
    "you must first",
    "before you can",
    "ensure you have installed",
    "set up the mcp",
]


def main() -> int:
    text = candidate()
    low = text.lower()

    if not PATH.search(text):
        return fail(
            "R1 path convention: no `.ailly/research/<YYYY-MM-DD-A-topic>/papers.md` "
            "path; the skill writes findings to that dated research-note path"
        )

    if "## Sources" not in text:
        return fail(
            "R2 note structure: missing a `## Sources` section; the papers note "
            "lists every source consulted under it"
        )

    if not CITATION.search(text):
        return fail(
            "R3 IEEE citations: no numbered `[N]` citation; the skill cites in a "
            "loose IEEE style"
        )

    for phrase in LEAK:
        if phrase in low:
            return fail(
                f"R4 wiring leak: a setup preface ('{phrase}') appears; configuration "
                "belongs in research:configuring-papers, not in per-query practice"
            )

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
