#!/usr/bin/env python3
"""Structural checker for `patterns:visibility` invocation cases.

Reads a TypeScript candidate from stdin and applies ordered rules tracing to the
visibility SKILL.md "Common Mistakes" section. First violated rule prints a
single-line reason to stdout and exits 1; all holding exits 0. stderr untouched.

Rules:
- R1 no getter hands back the live mutable collection ("Public getter, private
  setter" returning the live list).
- R2 no public setter for an invariant field — state changes are named methods
  ("`get` plus `set` instead of a domain method").
- R3 a named mutation method exists (`cancel`/`addLine`/…), and the constructor is
  private so there is no path to a half-built object ("Constructor that accepts
  every field").
"""

import re
import sys

from _checker_utils import extract_code, fail, strip_comments


def main() -> int:
    src = strip_comments(extract_code(sys.stdin.read()))

    # R1 — no getter returns a mutable collection by reference.
    if re.search(r"\bget\s+\w*(?:lines|items|entries)\w*\s*\(\s*\)\s*:\s*(?!readonly)(?:\w+\[\]|Array\s*<)", src, re.I):
        return fail(
            "R1 live-collection getter: a getter returns a mutable array; return a "
            "`readonly` view, a frozen copy, or an iterator so callers cannot mutate "
            "the internal collection"
        )

    # R2 — no public setter for an invariant field.
    if re.search(r"\bset\s+(?:status|total|lines|state|balance)\s*\(", src):
        return fail(
            "R2 public setter on an invariant field: a setter lets a caller assign "
            "state directly; replace it with a named domain method that checks the "
            "invariant"
        )
    if re.search(r"\b(?:public\s+)?(?:status|total)\s*[:=]\s*[^:]", src) and not re.search(
        r"\b(?:private|readonly|#)\s*(?:status|total)\b|#(?:status|total)\b", src
    ):
        # A public, assignable status/total field (no private/readonly/#).
        if re.search(r"^\s*(?:public\s+)?(?:status|total)\s*[:=]", src, re.MULTILINE):
            return fail(
                "R2 public mutable field: `status`/`total` is publicly assignable; make "
                "it private and expose it as a derived/read-only value"
            )

    # R3 — a named mutation method and a private constructor.
    if not re.search(r"\b(?:cancel|addLine|addItem|ship|deposit|withdraw|place|close|open)\s*\(", src):
        return fail(
            "R3 named mutation method: no named domain operation (e.g. `cancel()`, "
            "`addLine()`); express every state change as a method that checks invariants"
        )
    if not re.search(r"\bprivate\s+constructor\b", src):
        return fail(
            "R3 private constructor: no `private constructor`; route construction "
            "through a builder/factory so there is no path to a half-built object"
        )

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
