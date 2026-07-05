#!/usr/bin/env python3
"""T6 - reuses long-loop's dispatch/dated-block entry-format machinery, but
notates questions into the session's `reviews/` folder (sibling to
`research/`), resolved and closed once answered -- NOT written in place into
the artifact under review, and inventing no permanent standing block there.
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from _checker_utils import fail, read, INTENT_REVIEW  # noqa: E402


def main() -> int:
    if not INTENT_REVIEW.is_file():
        return fail("T6 ability missing: cannot check the recording mechanism")
    low = read(INTENT_REVIEW).lower()
    if "long-loop" not in low and "long loop" not in low:
        return fail(
            "T6 machinery reuse: the ability must reference long-loop's "
            "dispatch / dated-block entry-format machinery that it reuses"
        )
    if "reviews" not in low:
        return fail(
            "T6 reviews folder: the ability must record its questions in the "
            "session's `reviews/` folder (sibling to `research/`), not in "
            "place inside the artifact under review"
        )
    if "resolved" not in low or "closed" not in low:
        return fail(
            "T6 resolve/close: the ability must state that each `reviews/` "
            "entry is RESOLVED and CLOSED once the human answers it, rather "
            "than living on as a permanent block inside the artifact"
        )
    return 0


if __name__ == "__main__":
    sys.exit(main())
