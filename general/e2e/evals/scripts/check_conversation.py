#!/usr/bin/env python3
"""Structural checker for `general:conversation` invocation cases.

The artifact is an interactive turn that pauses for the user's decision rather
than implementing. conversation's output is prose interaction, not a structured
document, so the script is a light, robust guard and the judge carries the
nuanced assessment (options vs recommendation, most-blocking-first, suggestions
not decisions). The script deliberately does NOT require a `y`/`yes` accept: the
skill prescribes that only for *suggestions* (a recommendation), not for a
clarifying question, so demanding it universally would be a false negative.

On the first violated rule it prints a single-line reason to stdout and exits 1;
if every rule holds it exits 0. stderr is left untouched.

Rules:
- R1 pauses instead of implementing: no fenced code block (the prompt says do
     not implement; conversation makes suggestions, it does not act).
- R2 engages the user: asks at least one question rather than just answering.
- R3 one question at a time: not an interrogation (<= 5 question marks).
"""

import re
import sys

from _checker_utils import fail, read_candidate


def main() -> int:
    src = read_candidate()

    if re.search(r"(?m)^\s*```", src):
        return fail(
            "R1 pause instead of implementing: the response contains a code block; "
            "the prompt said not to implement — conversation suggests, it does not act"
        )

    if "?" not in src:
        return fail(
            "R2 engage the user: the response asks no question; conversation makes "
            "suggestions and lets the user decide"
        )

    qmarks = src.count("?")
    if qmarks > 5:
        return fail(
            f"R3 one question at a time: {qmarks} question marks; conversation asks "
            "the most-blocking question, not an interrogation"
        )

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
