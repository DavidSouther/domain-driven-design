#!/usr/bin/env python3
"""T3 - all four verbatim question categories from issue #33 are present."""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from _checker_utils import fail, read, INTENT_REVIEW, CATEGORIES  # noqa: E402


def main() -> int:
    if not INTENT_REVIEW.is_file():
        return fail("T3 ability missing: cannot check categories")
    text = read(INTENT_REVIEW)
    missing = [c for c in CATEGORIES if c not in text]
    if missing:
        return fail(
            f"T3 categories: the ability is missing verbatim category label(s) "
            f"{missing}; all four (Research gap / Design assumption / Plan "
            "scope / Implementation surprise) must appear"
        )
    return 0


if __name__ == "__main__":
    sys.exit(main())
