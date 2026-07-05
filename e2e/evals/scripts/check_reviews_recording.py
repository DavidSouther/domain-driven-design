#!/usr/bin/env python3
"""T6 - the `reviews/` folder recording convention (long-loop's dispatch and
dated-block entry-format machinery, reused for posing rather than deciding,
with a resolved-and-closed discipline, NOT written in place into the
artifact under review) lives in `general:review`, the shared home for
review conventions. intent-review.md cross-references it rather than
re-explaining it.
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from _checker_utils import fail, read, GENERAL_REVIEW, INTENT_REVIEW  # noqa: E402


def main() -> int:
    if not GENERAL_REVIEW.is_file():
        return fail("T6 general:review missing: cannot check the recording mechanism")
    low = read(GENERAL_REVIEW).lower()
    if "long-loop" not in low and "long loop" not in low:
        return fail(
            "T6 machinery reuse: general:review must reference long-loop's "
            "dispatch / dated-block entry-format machinery that it reuses"
        )
    if "reviews" not in low:
        return fail(
            "T6 reviews folder: general:review must record findings in a "
            "`reviews/` folder, not in place inside the artifact under review"
        )
    if "resolved" not in low or "closed" not in low:
        return fail(
            "T6 resolve/close: general:review must state that each `reviews/` "
            "entry is RESOLVED and CLOSED once the human answers it, rather "
            "than living on as a permanent block inside the artifact"
        )
    if not INTENT_REVIEW.is_file():
        return fail("T6 ability missing: cannot check the recording cross-reference")
    intent_low = read(INTENT_REVIEW).lower()
    if "general:review" not in intent_low and "general/skills/review" not in intent_low:
        return fail(
            "T6 cross-reference: intent-review.md must point at general:review "
            "for the `reviews/` folder mechanism rather than re-explaining it"
        )
    return 0


if __name__ == "__main__":
    sys.exit(main())
