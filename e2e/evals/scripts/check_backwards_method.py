#!/usr/bin/env python3
"""T2 - the backwards-from-the-original-prompt method and the probative
question template ("...is that what you intended?" anchored to the original
request) must both appear in the ability.
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from _checker_utils import fail, read, INTENT_REVIEW  # noqa: E402


def main() -> int:
    if not INTENT_REVIEW.is_file():
        return fail("T2 ability missing: cannot check the backwards method")
    low = read(INTENT_REVIEW).lower()
    if "original" not in low or not any(t in low for t in ("prompt", "request", "ask")):
        return fail(
            "T2 backwards method: the ability must work backwards from the "
            "user's ORIGINAL prompt/request; that anchor language is missing"
        )
    if not any(
        t in low
        for t in ("is that what you intended", "did you intend", "what you intended")
    ):
        return fail(
            "T2 question template: the ability must carry the probative "
            "'is that what you intended?' question form"
        )
    if "backward" not in low and "backwards" not in low:
        return fail(
            "T2 direction: the ability must state it reasons BACKWARD from the "
            "original prompt through the accumulated artifacts"
        )
    return 0


if __name__ == "__main__":
    sys.exit(main())
