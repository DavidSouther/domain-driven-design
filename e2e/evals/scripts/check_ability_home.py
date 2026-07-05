#!/usr/bin/env python3
"""T1 - the intent-review ability reference exists and is non-empty, in the
abilities/ directory (the thinking.md / refactor.md "consulted at a moment"
shape), not as a standalone phase reference.
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from _checker_utils import fail, read, REPO, INTENT_REVIEW  # noqa: E402


def main() -> int:
    if not INTENT_REVIEW.is_file():
        return fail(
            "T1 ability home: expected the intent-review ability at "
            f"{INTENT_REVIEW.relative_to(REPO)} (an ability like thinking.md / "
            "refactor.md), which does not exist"
        )
    if len(read(INTENT_REVIEW).strip()) < 200:
        return fail(
            f"T1 ability body: {INTENT_REVIEW.relative_to(REPO)} exists but is "
            "effectively empty; it must describe the intent-review mechanism"
        )
    return 0


if __name__ == "__main__":
    sys.exit(main())
