#!/usr/bin/env python3
"""T4 - the distinct Research-phase variant, framed around blind-spots/gaps
("what can't we see"), NOT as an intent match.
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from _checker_utils import fail, read, INTENT_REVIEW  # noqa: E402


def main() -> int:
    if not INTENT_REVIEW.is_file():
        return fail("T4 ability missing: cannot check the research variant")
    low = read(INTENT_REVIEW).lower()
    if "blind spot" not in low and "blind-spot" not in low:
        return fail(
            "T4 research variant: the ability must define the Research-phase "
            "variant framed around blind spots (a distinct 'what can't we see' "
            "framing, not 'did this match intent')"
        )
    if "gap" not in low:
        return fail(
            "T4 research variant: the Research-phase variant must be framed "
            "around gaps as well as blind spots"
        )
    return 0


if __name__ == "__main__":
    sys.exit(main())
