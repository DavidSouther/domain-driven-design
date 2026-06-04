#!/usr/bin/env python3
"""Structural checker for the `thinking` invocation case.

Rules trace 1:1 to the thinking SKILL.md "Thinking Doc Format" and its hard
constraint that every proposed step has a specific predicted outcome ("'Try X'
without a predicted outcome is not acceptable").

Rules:
- R1 a root-cause analysis section is present (diagnosis, not a guess).
- R2 an ordered "Next Steps" section is present.
- R3 at least two steps name a predicted/expected outcome (the skill forbids
  "try X and see" — every step states what the result should be).
"""

import re
import sys

from _checker_utils import fail, has_heading, read_stdin

EXPECTED_OUTCOME = re.compile(r"expected\s+(?:outcome|result)", re.IGNORECASE)


def main() -> int:
    text = read_stdin()

    # R1 — root-cause analysis present.
    if not has_heading(text, "Root Cause"):
        return fail(
            "R1 root-cause analysis required: no 'Root Cause' section; the "
            "thinking skill diagnoses what is actually wrong before proposing "
            "steps"
        )

    # R2 — ordered next steps present.
    if not has_heading(text, "Next Steps"):
        return fail(
            "R2 next steps required: no 'Next Steps' section; the thinking skill "
            "produces a concrete ordered plan"
        )

    # R3 — steps carry predicted outcomes.
    n = len(EXPECTED_OUTCOME.findall(text))
    if n < 2:
        return fail(
            f"R3 predicted outcomes required: found {n} 'expected outcome' "
            "statement(s); the thinking skill requires every step to name its "
            "predicted outcome, not 'try X and see'"
        )

    return 0


if __name__ == "__main__":
    sys.exit(main())
