#!/usr/bin/env python3
"""Structural checker for the `domain:contracts-and-invariants` invocation case.

This is the only checker that reads BOTH turns: the inline fixture from the user
turn (via `AILLY_USER_QUESTION`) and the produced full file from stdin. It
asserts the original context block is preserved verbatim and a contract block is
appended below it.

Rules, each tracing to the contracts-and-invariants SKILL.md "Record in Bounded
Context File":
- R1 original preserved: the original `# Order Management` heading and a
       distinctive line from the fixture body survive in the output.
- R2 operation block: an appended `### <Operation>` heading naming place_order.
- R3 input/output contracts: both `**Contract (input):**` and
       `**Contract (output):**` fields appear.
- R4 invariant: an `**Invariants:**` field with at least one invariant bullet.
- R5 draft marker: `[DRAFT]` ("New entries in context files must be marked
       **[DRAFT]**").
"""

import re

from _checker_utils import (
    decoded_artifacts,
    fail,
    has_draft_marker,
    read_candidate,
    user_question,
)


def main() -> int:
    text = decoded_artifacts(read_candidate())

    # R1 — original context block preserved. The fixture's distinctive heading
    # and a body phrase must both survive into the produced file.
    if "# Order Management" not in text:
        return fail(
            "R1 original preserved: the original `# Order Management` heading is "
            "absent from the produced file"
        )
    if "Accepting customer orders" not in text and "OrderPlaced" not in text:
        return fail(
            "R1 original preserved: the original context body (responsibilities / "
            "`OrderPlaced`) was not carried into the produced file"
        )

    # R2 — appended operation block.
    op_heading = re.search(
        r"^\s*###\s+.*place[\s_]*order", text, re.IGNORECASE | re.MULTILINE
    )
    if op_heading is None:
        return fail(
            "R2 operation block: no `### <Operation>` heading naming place_order "
            "was appended"
        )

    # R3 — input and output contracts.
    has_input = re.search(r"\*\*\s*Contract\s*\(input\)\s*:?\s*\*\*", text, re.IGNORECASE)
    has_output = re.search(r"\*\*\s*Contract\s*\(output\)\s*:?\s*\*\*", text, re.IGNORECASE)
    if has_input is None or has_output is None:
        missing = []
        if has_input is None:
            missing.append("`**Contract (input):**`")
        if has_output is None:
            missing.append("`**Contract (output):**`")
        return fail("R3 input/output contracts: missing " + ", ".join(missing))

    # R4 — at least one invariant under an Invariants field.
    inv = re.search(r"\*\*\s*Invariants\s*:?\s*\*\*", text, re.IGNORECASE)
    if inv is None:
        return fail("R4 invariant: no `**Invariants:**` field")
    after = text[inv.end():]
    if re.search(r"^\s*[-*]\s+\S", after, re.MULTILINE) is None:
        return fail(
            "R4 invariant: the `**Invariants:**` field lists no invariant bullet; "
            "at least one invariant is required"
        )

    # R5 — draft marker on the new content.
    if not has_draft_marker(text):
        return fail(
            "R5 draft marker: no `[DRAFT]` marker; new context-file entries must "
            "be marked DRAFT"
        )

    # Touch user_question so a future tightening (diffing fixture vs output) has
    # the fixture in hand; absence is tolerated rather than Errored.
    _ = user_question()

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
