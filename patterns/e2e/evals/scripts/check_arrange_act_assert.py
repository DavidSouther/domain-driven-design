#!/usr/bin/env python3
"""Structural checker for `patterns:arrange-act-assert` invocation cases.

Reads a TypeScript/Jest candidate from stdin and applies ordered rules tracing to
the arrange-act-assert SKILL.md "Common Mistakes" section. First violated rule
prints a single-line reason to stdout and exits 1; all holding exits 0. stderr
untouched so the runner records Fail, not Errored.

AAA structure is largely a readability discipline, so this checker is deliberately
conservative — it fails only clear violations and lets the judge carry the finer
signal.

Rules:
- R1 a test exists with at least one assertion.
- R2 phase separation present — AAA/GWT labels or blank lines between phases
  ("No blank lines").
- R3 the act is not collapsed onto an assertion ("Asserting on Act's return value
  inline").
"""

import re
import sys

from _checker_utils import extract_code, fail, strip_comments

LABELS = re.compile(r"//\s*(?:arrange|act|assert|given|when|then)\b", re.IGNORECASE)


def main() -> int:
    raw = extract_code(sys.stdin.read())  # keep comments: AAA labels are meaningful
    src = strip_comments(raw)

    # R1 — a test with an assertion.
    if not re.search(r"\b(?:test|it)\s*\(", src):
        return fail("R1 a test: no `test(`/`it(` block; write the behaviour as a test")
    if not re.search(r"\b(?:expect|assert)\s*\(", src):
        return fail("R1 an assertion: no `expect(`/`assert(`; the test asserts nothing")

    # R2 — phase separation (labels or a blank line between statements).
    if not (LABELS.search(raw) or re.search(r"\n[ \t]*\n", raw)):
        return fail(
            "R2 phase separation: no Arrange/Act/Assert labels and no blank lines; "
            "separate setup, the single action, and the checks into distinct phases"
        )

    # R3 — act not collapsed onto an assertion (e.g. `expect(cart.checkout()).` for
    # the action under test). Allow expectations on pure getters by only flagging a
    # call wrapped directly in expect() whose name is an imperative action verb.
    if re.search(
        r"\bexpect\s*\(\s*\w+\s*\.\s*(?:checkout|place|submit|save|cancel|process|run|execute)\s*\(",
        src,
    ):
        return fail(
            "R3 act collapsed into assert: the action under test is invoked inside "
            "`expect(...)`; perform the single Act on its own line, then Assert the "
            "observable outcome separately"
        )

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
