#!/usr/bin/env python3
"""T5 - the ability runs by default at the draft gate, NEVER clears the
gate itself, and states it SUPPLEMENTS the human's existing review rather
than replacing the human as gate-clearer.
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from _checker_utils import fail, read, INTENT_REVIEW  # noqa: E402


def main() -> int:
    if not INTENT_REVIEW.is_file():
        return fail("T5 ability missing: cannot check gate discipline")
    low = read(INTENT_REVIEW).lower()
    if "draft gate" not in low and "draft-gate" not in low:
        return fail(
            "T5 gate timing: the ability must state it runs by default at the "
            "draft gate"
        )
    if not any(
        t in low
        for t in (
            "does not clear",
            "never clears",
            "not auto-clear",
            "without clearing",
            "not an autonomous gate",
        )
    ):
        return fail(
            "T5 never-clears invariant: the ability must state it NEVER clears "
            "the draft marker itself (unlike long-loop's auto-clearing reviewer)"
        )
    if "supplement" not in low:
        return fail(
            "T5 supplements: the ability must state it SUPPLEMENTS the human's "
            "existing draft-gate review rather than replacing the human as "
            "gate-clearer"
        )
    return 0


if __name__ == "__main__":
    sys.exit(main())
