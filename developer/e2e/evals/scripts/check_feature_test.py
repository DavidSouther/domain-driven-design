#!/usr/bin/env python3
"""Structural checker for the `feature-test` invocation case.

Rules trace 1:1 to the feature-test SKILL.md: a plain-language user story
("User Story Format"), exactly one executable test ("Write one test that…"), and
the `*Draft YYYY-MM-DD*` marker ("Output Artifacts").

Rules:
- R1 a user story is present (a "User Story" heading, or a Given/When/Then).
- R2 exactly one executable test function (single end-to-end test, not a suite
  of unit tests and not zero).
- R3 the draft marker is present.
"""

import re
import sys

from _checker_utils import code_text, fail, has_draft_marker, has_heading, read_stdin

TEST_DEF = re.compile(r"\bdef\s+test\w*\s*\(")
GIVEN_WHEN_THEN = re.compile(r"\bgiven\b.*\bwhen\b.*\bthen\b", re.IGNORECASE | re.DOTALL)


def main() -> int:
    text = read_stdin()

    # R1 — user story present.
    if not (has_heading(text, "User Story") or GIVEN_WHEN_THEN.search(text)):
        return fail(
            "R1 user story required: no 'User Story' section and no "
            "Given/When/Then; the feature-test skill writes the story in plain "
            "language before the test"
        )

    # R2 — exactly one executable test.
    n = len(TEST_DEF.findall(code_text(text)))
    if n == 0:
        return fail(
            "R2 one executable test required: found no `def test...` function; "
            "the feature-test skill writes one executable test that runs the "
            "user story end-to-end"
        )
    if n > 1:
        return fail(
            f"R2 one executable test required: found {n} test functions; the "
            "feature-test skill writes a single end-to-end test, not a suite"
        )

    # R3 — draft marker present.
    if not has_draft_marker(text):
        return fail(
            "R3 draft marker required: no *Draft YYYY-MM-DD* marker; the "
            "feature-test skill marks the artifact as a draft for human review"
        )

    return 0


if __name__ == "__main__":
    sys.exit(main())
