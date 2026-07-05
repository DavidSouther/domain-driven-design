#!/usr/bin/env python3
"""T10 - the Research phase's Topic and Intent instruction requires an
EXACT, VERBATIM quote of the user's original request, not merely a
paraphrase "in the user's own framing". This is load-bearing: the
original-prompt anchor's best-effort resolution falls back to this section,
so an anchor that is itself already a paraphrase would defeat the
backward-check before intent review ever runs.
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from _checker_utils import fail, read, REPO, RESEARCH_PHASE  # noqa: E402


def main() -> int:
    if not RESEARCH_PHASE.is_file():
        return fail(f"T10 {RESEARCH_PHASE.relative_to(REPO)} not found")
    low = read(RESEARCH_PHASE).lower()
    if "topic and intent" not in low:
        return fail(
            f"T10 {RESEARCH_PHASE.relative_to(REPO)} must still define a "
            "'Topic and Intent' section for this check to bind to"
        )
    if "verbatim" not in low or "quote" not in low:
        return fail(
            f"T10 verbatim quote: {RESEARCH_PHASE.relative_to(REPO)}'s Topic "
            "and Intent instruction must require an exact, VERBATIM QUOTE of "
            "the user's original request, not just a paraphrase 'in the "
            "user's own framing'"
        )
    return 0


if __name__ == "__main__":
    sys.exit(main())
