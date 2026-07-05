#!/usr/bin/env python3
"""T8 - coordinator wiring: SKILL.md routes to the ability by its reference
path, and mentions intent review in prose.
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from _checker_utils import fail, read, REPO, SKILL  # noqa: E402


def main() -> int:
    if not SKILL.is_file():
        return fail(f"T8 {SKILL.relative_to(REPO)} not found")
    skill = read(SKILL)
    if "references/abilities/intent-review.md" not in skill:
        return fail(
            "T8 routing: SKILL.md must route to "
            "`references/abilities/intent-review.md` (a Routing-table row "
            "and/or a Draft Gate Enforcement pointer)"
        )
    if "intent review" not in skill.lower() and "intent-review" not in skill.lower():
        return fail(
            "T8 coordinator mention: SKILL.md must name intent review in prose "
            "(e.g. in Routing and Draft Gate Enforcement)"
        )
    return 0


if __name__ == "__main__":
    sys.exit(main())
