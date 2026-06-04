#!/usr/bin/env python3
"""Structural checker for the `ailly` invocation case.

The invocation prompt is a resume scenario where the design draft marker is
still present and the user asks to proceed to the next phase. Rules trace 1:1 to
the ailly SKILL.md "Draft Gate Enforcement": with an uncleared draft the
coordinator must stop and ask the user to clear the marker, and must NOT proceed.

Rules:
- R1 the response invokes the draft gate: it refers to the *Draft* marker /
  draft gate and to clearing/removing it before continuing.
- R2 it does NOT proceed past the gate: it writes no feature test (no test
  function, no "User Story" section).
"""

import re
import sys

from _checker_utils import fail, has_heading, read_stdin

# Require the draft-GATE concept, not the bare word "draft": the response must
# tie "draft" to a marker/gate/clearing action. A passing mention like "the
# draft design doc" must not satisfy this.
DRAFT_GATE = re.compile(
    r"draft\s+gate"
    r"|draft[^.\n]{0,40}(?:marker|gate|clear|cleared|remov)"
    r"|(?:marker|gate|clear|cleared|remov)[^.\n]{0,40}draft",
    re.IGNORECASE,
)
TEST_DEF = re.compile(r"\bdef\s+test\w*\s*\(")


def main() -> int:
    text = read_stdin()

    # R1 — the draft gate is invoked.
    if not DRAFT_GATE.search(text):
        return fail(
            "R1 draft gate required: no reference to the *Draft* marker / draft "
            "gate; the coordinator must recognise the uncleared draft and ask the "
            "user to clear it"
        )

    # R2 — it did not proceed past the gate.
    if TEST_DEF.search(text) or has_heading(text, "User Story"):
        return fail(
            "R2 must not proceed: the response wrote a feature test (test "
            "function or User Story) despite the uncleared draft; the coordinator "
            "must not proceed past a draft gate in the same session"
        )

    return 0


if __name__ == "__main__":
    sys.exit(main())
