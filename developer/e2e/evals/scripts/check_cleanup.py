#!/usr/bin/env python3
"""Structural checker for the `cleanup` invocation case.

Rules trace 1:1 to the (four-line) cleanup SKILL.md, whose entire body is four
closeout actions. A capable but un-skilled "tidy up my topic" answer gives
generic advice and does not name these specific steps.

Rules (at least three of the four closeout actions must be present):
- A: final refactoring AND review pass (incl. lint/formatters).
- B: extract deferred decisions into a TASKS file.
- C: remove the topic's docs/developer folder.
- D: open a PR or prepare a squash merge.
"""

import re
import sys

from _checker_utils import fail, read_stdin

ACTIONS = {
    "A refactor+review pass": lambda t: re.search(r"refactor", t) and re.search(r"review", t),
    "B deferred decisions -> TASKS": lambda t: re.search(r"defer", t) and re.search(r"\btasks?\b", t),
    "C remove topic folder": lambda t: re.search(r"(remove|delete|tear down|tear-down).{0,40}(folder|docs/developer|topic|director)", t)
        or re.search(r"(folder|docs/developer|topic|director).{0,40}(remove|delete)", t),
    "D PR or squash merge": lambda t: re.search(r"pull request|\bpr\b|squash|merge", t),
}


def main() -> int:
    low = read_stdin().lower()
    present = [name for name, test in ACTIONS.items() if test(low)]
    if len(present) < 3:
        missing = [n for n in ACTIONS if n not in present]
        return fail(
            f"cleanup closeout steps: only {len(present)}/4 present "
            f"({', '.join(present) or 'none'}); missing {', '.join(missing)}. The "
            "cleanup skill does final refactor+review, extracts deferred decisions "
            "into TASKS, removes the topic folder, and opens a PR / squash merge"
        )
    return 0


if __name__ == "__main__":
    sys.exit(main())
