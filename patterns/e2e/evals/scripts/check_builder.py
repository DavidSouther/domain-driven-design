#!/usr/bin/env python3
"""Structural checker for `patterns:builder` invocation cases.

Reads a TypeScript candidate from stdin and applies ordered rules tracing to the
builder SKILL.md "Common Mistakes" section. First violated rule prints a single-line
reason to stdout and exits 1; all holding exits 0. stderr untouched.

Rules:
- R1 a builder exists — a `build()` that produces the product, reached via a
  `builder(...)` factory or a `*Builder`.
- R2 fluent optional setters — `with*`/chainable methods for the optional fields.
- R3 the product constructor is private, so callers cannot bypass validation
  ("Public constructor alongside builder").
"""

import re
import sys

from _checker_utils import extract_code, fail, strip_comments


def main() -> int:
    src = strip_comments(extract_code(sys.stdin.read()))

    # R1 — a builder that builds.
    if not re.search(r"\bbuild\s*\(\s*\)", src):
        return fail(
            "R1 a builder: no `build()` method; accumulate configuration in a builder "
            "and produce the validated product from `build()`"
        )
    if not re.search(r"\bbuilder\s*\(|\b\w*Builder\b", src):
        return fail(
            "R1 a builder entry point: no `builder(...)` factory or `*Builder` type; "
            "required fields belong on the builder entry point, not on `build()`"
        )

    # R2 — fluent optional setters (a `with*` method declaration or call).
    if not re.search(r"\bwith[A-Z]\w*\s*\(", src):
        return fail(
            "R2 fluent optional setters: no `with*` methods; expose optional fields as "
            "discoverable chainable setters that return the builder"
        )

    # R3 — product constructor is private.
    if not re.search(r"\bprivate\s+constructor\b", src):
        return fail(
            "R3 private product constructor: no `private constructor`; make the "
            "product's constructor private so callers cannot bypass the builder's "
            "validation"
        )

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
