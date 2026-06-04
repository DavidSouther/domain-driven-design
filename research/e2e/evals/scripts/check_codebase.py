#!/usr/bin/env python3
"""Structural checker for the `codebase` invocation case.

Rules trace to codebase/SKILL.md "Output Format" and "Common Mistakes":
- R1 research-note path convention `docs/research/<dated-dir>/codebase.md`.
- R2 the note carries `## Findings` and `## Sources` sections.
- R3 no git-history tooling (the "Using git for context" mistake): `git log`,
  `git blame`, `git show`, `git diff` are archaeology tools, out of scope here.
  `git rev-parse` (allowed, for the current SHA) is not flagged.
"""

import re
import sys

from _md import candidate, fail

PATH = re.compile(r"docs/research/\d{4}-\d{2}-\d{2}-[\w-]+/codebase\.md")
GIT_HISTORY = re.compile(r"git\s+(log|blame|show|diff)\b", re.IGNORECASE)


def main() -> int:
    text = candidate()

    if not PATH.search(text):
        return fail(
            "R1 path convention: no `docs/research/<YYYY-MM-DD-A-topic>/codebase.md` "
            "path; the skill writes findings to that dated research-note path"
        )

    if "## Findings" not in text or "## Sources" not in text:
        return fail(
            "R2 note structure: missing a `## Findings` and/or `## Sources` "
            "section; the codebase note is structured under both"
        )

    if GIT_HISTORY.search(text):
        return fail(
            "R3 no git history: a `git log/blame/show/diff` appears; codebase "
            "research is current-state only (history is archaeology's domain)"
        )

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
