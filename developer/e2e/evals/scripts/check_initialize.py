#!/usr/bin/env python3
"""Structural checker for the `initialize` invocation case.

Rules trace 1:1 to the initialize SKILL.md "Four Development Hooks" table (every
initialized project configures Format, Check, Test, and Lint hooks) and its
"Validation"/"Verification Command" sections (a clean build is confirmed).

Rules:
- R1 all four development hooks are named: Format, Check, Test, Lint.
- R2 the response frames them as hooks (configuration), not incidental verbs.
- R3 it validates the layout and/or verifies a clean build.
"""

import re
import sys

from _checker_utils import fail, read_stdin

HOOKS = ["format", "check", "test", "lint"]


def main() -> int:
    text = read_stdin()
    low = text.lower()

    # R1 — all four hooks named.
    missing = [h for h in HOOKS if not re.search(rf"\b{h}", low)]
    if missing:
        return fail(
            "R1 four hooks required: missing hook(s) "
            + ", ".join(missing)
            + "; the initialize skill configures Format, Check, Test, and Lint"
        )

    # R2 — framed as hooks.
    if "hook" not in low:
        return fail(
            "R2 hook framing required: the response never calls them hooks; the "
            "initialize skill configures the four as development hooks in the "
            "agent's settings"
        )

    # R3 — validation / clean-build verification.
    if not re.search(
        r"validat|verif|clean build|builds? (?:cleanly|clean)|zero (?:errors|warnings)",
        low,
    ):
        return fail(
            "R3 validation required: no layout validation or clean-build "
            "verification; the initialize skill validates the layout and confirms "
            "a clean build before declaring done"
        )

    return 0


if __name__ == "__main__":
    sys.exit(main())
