#!/usr/bin/env python3
"""Structural checker for the `plan` invocation case.

Rules trace 1:1 to the plan SKILL.md: "3-7 incremental steps" ("Step Criteria"),
each step naming "which assertion in the feature test it enables" via the
`**Enables:**` line ("Plan Format"), and the `*Draft YYYY-MM-DD*` marker
("Output Artifacts").

Rules:
- R1 between 3 and 7 step headings (`## Step N`). An optional Step 0 (domain
  model) is allowed on top, so the accepted range is 3..8 headings.
- R2 every implementation step (number >= 1) carries an `Enables:` line tying it
  to the feature test.
- R3 the draft marker is present.
"""

import re
import sys

from _checker_utils import fail, has_draft_marker, read_stdin

STEP_HEADING = re.compile(r"^\s{0,3}#{1,6}\s+Step\s+(\d+)\b.*$", re.MULTILINE)
ENABLES = re.compile(r"\benables\s*:", re.IGNORECASE)


def main() -> int:
    text = read_stdin()

    matches = list(STEP_HEADING.finditer(text))
    numbers = [int(m.group(1)) for m in matches]

    # R1 — 3..7 implementation steps, plus an optional Step 0 (so 3..8 headings).
    n = len(matches)
    impl_steps = [x for x in numbers if x >= 1]
    if len(impl_steps) < 3:
        return fail(
            f"R1 step count: found {len(impl_steps)} implementation step(s); the "
            "plan skill requires at least 3 (fewer means the steps are too large)"
        )
    if len(impl_steps) > 7:
        return fail(
            f"R1 step count: found {len(impl_steps)} implementation steps; the "
            "plan skill caps at 7 (more means the design should be simplified)"
        )

    # R2 — every implementation step has an Enables line.
    for idx, m in enumerate(matches):
        if numbers[idx] < 1:
            continue  # Step 0 (domain model) need not name an enabled assertion.
        start = m.end()
        end = matches[idx + 1].start() if idx + 1 < len(matches) else len(text)
        if not ENABLES.search(text[start:end]):
            return fail(
                f"R2 enables line required: Step {numbers[idx]} has no `Enables:` "
                "line; the plan skill ties each step to the feature-test assertion "
                "it advances"
            )

    # R3 — draft marker present.
    if not has_draft_marker(text):
        return fail(
            "R3 draft marker required: no *Draft YYYY-MM-DD* marker; the plan "
            "skill saves the plan as a draft for human review"
        )

    return 0


if __name__ == "__main__":
    sys.exit(main())
