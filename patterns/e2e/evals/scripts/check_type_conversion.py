#!/usr/bin/env python3
"""Structural checker for `patterns:type-conversion` invocation cases.

Reads a TypeScript candidate from stdin and applies ordered rules tracing to the
type-conversion SKILL.md "Common Mistakes" section. First violated rule prints a
single-line reason to stdout and exits 1; all holding exits 0. stderr untouched.

Rules:
- R1 a named conversion is defined once (a static `from`/`tryFrom` factory or a
  named conversion function), not ad-hoc inline.
- R2 a call site invokes the named conversion rather than reaching into internals.
- R3 no `as` cast between the numeric domain types ("`as` cast between domain
  types"); the cast, if any, lives inside the conversion, not at call sites.
"""

import re
import sys

from _checker_utils import extract_code, fail, strip_comments


def main() -> int:
    src = strip_comments(extract_code(sys.stdin.read()))

    # R1 — a named conversion defined once.
    if not (
        re.search(r"\bstatic\s+(?:from|tryFrom|parse)\w*\s*\(", src)
        or re.search(r"\b(?:function|const)\s+(?:to|from)[A-Z]\w*\s*[=(]", src)
        or re.search(r"\bimplements\s+(?:From|TryFrom)\b", src)
    ):
        return fail(
            "R1 named conversion: no `static from`/`tryFrom` factory or named "
            "conversion function; define each conversion explicitly and once on the "
            "target type, not inline at call sites"
        )

    # R2 — a call site uses the named conversion.
    if not re.search(r"\.\s*(?:from|tryFrom|into|to[A-Z]\w*)\s*\(|[A-Z]\w+\s*\.\s*from\s*\(", src):
        return fail(
            "R2 conversion used at the call site: no call to a `from`/`tryFrom`/`into`/"
            "`to*` conversion; call sites must invoke the named conversion instead of "
            "extracting and rewrapping the inner primitive"
        )

    # R3 — no `as` cast between the numeric domain types at the call surface.
    m = re.search(r"\bas\s+(Dollars|Cents)\b", src)
    if m:
        return fail(
            f"R3 `as` cast between domain types: `as {m.group(1)}` performs a silent "
            "primitive cast; a total conversion (`From`/`from`) owns this, no `as` at "
            "the call site"
        )

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
