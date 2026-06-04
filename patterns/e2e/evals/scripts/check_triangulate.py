#!/usr/bin/env python3
"""Structural checker for `patterns:triangulate` invocation cases.

Reads a TypeScript/Jest candidate from stdin and applies ordered rules tracing to
the triangulate SKILL.md "Common Mistakes" section. First violated rule prints a
single-line reason to stdout and exits 1; all holding exits 0. stderr untouched.

Rules:
- R1 two or more examples (the technique needs two reference points).
- R2 the two examples are non-degenerate — distinct expected values, so the second
  cannot pass the fake ("Picking triangulation tests that don't diverge").
- R3 a real, generalized implementation exists — the final implementation is not a
  bare hardcoded constant ("Refactoring after one example" / the fake must be
  replaced).
"""

import re
import sys

from _checker_utils import extract_code, fail, strip_comments

EXPECTED = re.compile(r"(?:toBe|toEqual|toStrictEqual)\s*\(\s*(-?\d+(?:\.\d+)?)\s*\)")


def main() -> int:
    src = strip_comments(extract_code(sys.stdin.read()))

    # R1 — two or more examples.
    cases = re.findall(r"\b(?:test|it)\s*\(", src)
    expects = re.findall(r"\bexpect\s*\(", src)
    if len(cases) < 2 and len(expects) < 2:
        return fail(
            "R1 two examples: fewer than two tests/assertions; triangulation needs a "
            "second example with different inputs to force generalization"
        )

    # R2 — non-degenerate: at least two distinct expected numeric values.
    values = set(EXPECTED.findall(src))
    if len(values) < 2:
        return fail(
            "R2 non-degenerate examples: the expected values do not differ "
            f"({sorted(values) or 'none found'}); pick a second example whose expected "
            "output a hardcoded constant cannot produce"
        )

    # R3 — a generalized implementation: some function returns an expression over its
    # parameters, not a bare constant.
    params_seen = []
    for m in re.finditer(r"\bfunction\s+\w+\s*\(([^)]*)\)\s*\{(.*?)\}", src, re.DOTALL):
        params, body = m.group(1), m.group(2)
        names = [p.split(":")[0].strip() for p in params.split(",") if p.strip()]
        params_seen.extend(names)
        if names and any(re.search(r"\b" + re.escape(n) + r"\b", body) for n in names):
            return 0
    # Arrow form: const f = (a, b) => a + b;
    for m in re.finditer(r"\b(?:const|let)\s+\w+\s*=\s*\(([^)]*)\)\s*(?::[^=]+)?=>\s*([^;\n]+)", src):
        params, body = m.group(1), m.group(2)
        names = [p.split(":")[0].strip() for p in params.split(",") if p.strip()]
        if names and any(re.search(r"\b" + re.escape(n) + r"\b", body) for n in names):
            return 0

    return fail(
        "R3 generalized implementation: no function body references its parameters; "
        "the final implementation still looks like a hardcoded fake rather than the "
        "real, generalized code the second test forced"
    )


if __name__ == "__main__":
    raise SystemExit(main())
