#!/usr/bin/env python3
"""T7 - the original-prompt anchor is defined as a best-effort choice between
a `.ailly/prompts/` file reference and research.md's Topic and Intent
section (resolved by the human as "whichever is genuinely available", not a
single mandated source, so either reference suffices).
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from _checker_utils import fail, read, INTENT_REVIEW  # noqa: E402


def main() -> int:
    if not INTENT_REVIEW.is_file():
        return fail("T7 ability missing: cannot check the prompt anchor")
    text = read(INTENT_REVIEW)
    if ".ailly/prompts" not in text and "Topic and Intent" not in text:
        return fail(
            "T7 prompt anchor: the ability must define how the original prompt "
            "is anchored -- either a `.ailly/prompts/` file reference or "
            "research.md's `Topic and Intent` section (resolved as best-effort, "
            "so either suffices)"
        )
    return 0


if __name__ == "__main__":
    sys.exit(main())
