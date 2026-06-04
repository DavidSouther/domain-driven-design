#!/usr/bin/env python3
"""Structural checker for `patterns:type-states` invocation cases.

Reads a TypeScript candidate from stdin and applies ordered rules tracing to the
type-states SKILL.md "Common Mistakes" section. First violated rule prints a
single-line reason to stdout and exits 1; all holding exits 0. stderr untouched.

Rules:
- R1 each phase is its own type — two distinct state types, or a phantom-typed
  `Connection<S>`.
- R2 not a flat type with a boolean discriminant plus runtime guards ("Using enums
  + runtime checks instead of types").
- R3 a transition is typed — an operation returns the other phase's type, so misuse
  is a compile error.
"""

import re
import sys

from _checker_utils import extract_code, fail, strip_comments

STATE_TYPE = re.compile(
    r"\b(?:class|interface|type)\s+((?:Open|Closed|Connected|Disconnected|Active|Idle)\w*)\b"
)
PHANTOM = re.compile(r"\b(?:class|interface|type)\s+Connection\s*<\s*\w+")


def main() -> int:
    src = strip_comments(extract_code(sys.stdin.read()))

    # R1 — distinct state types, or a phantom-typed connection.
    states = set(STATE_TYPE.findall(src))
    if len(states) < 2 and not PHANTOM.search(src):
        return fail(
            "R1 one type per phase: fewer than two state types (e.g. "
            "`OpenConnection`/`ClosedConnection`) and no phantom `Connection<S>`; "
            "encode each lifecycle phase as its own type"
        )

    # R2 — not a flat boolean discriminant with a runtime guard.
    has_flag = re.search(r"\b(?:isOpen|is_open|open)\s*[:?]\s*boolean\b", src)
    has_guard = re.search(r"\bif\s*\([^)]*(?:isOpen|is_open)\b", src)
    if has_flag and has_guard:
        return fail(
            "R2 flat boolean + guard: a boolean `isOpen` field with an `if (isOpen)` "
            "runtime guard recreates the illegal-state problem; let the type, not a "
            "runtime check, decide which operations are available"
        )

    # R3 — a typed transition returns a phase type.
    if not (
        re.search(
            r"\)\s*:\s*(?:Open|Closed|Connected|Disconnected|Active|Idle)\w*\b", src
        )
        or re.search(r"\)\s*:\s*Connection\s*<", src)
    ):
        return fail(
            "R3 typed transition: no operation returns a phase type; a transition must "
            "consume the old state and return the new one so a stale handle cannot be "
            "reused"
        )

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
