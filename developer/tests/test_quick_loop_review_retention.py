#!/usr/bin/env python3
"""Feature test: quick-loop pauses before cleanup for artifact review.

Quick-loop auto-clears research/design/plan draft gates, but cleanup is different:
cleanup removes or tidies the session folder, so the coordinator must leave the
intermediate artifacts visible after the feature test turns green. The only
opt-out is an explicit "no review" at quick-loop start.

This is a source-level contract over `developer:ailly`. It exits 0 when the
contract holds, or 1 with a single reason line on stdout.
"""

import re
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
AILLY = REPO / "developer" / "skills" / "ailly" / "SKILL.md"


def fail(reason: str) -> int:
    print(reason)
    return 1


def section(text: str, heading: str) -> str:
    match = re.search(rf"(?im)^##\s+{re.escape(heading)}\s*$", text)
    if not match:
        return ""
    rest = text[match.end():]
    nxt = re.search(r"(?m)^##\s+", rest)
    return rest[: nxt.start()] if nxt else rest


def main() -> int:
    text = AILLY.read_text(encoding="utf-8")
    quick = section(text, "Quick-loop Mode")
    if not quick:
        return fail("R1 coordinator must document Quick-loop Mode")

    low = quick.lower()
    if "pauses before cleanup" not in low and "pause before cleanup" not in low:
        return fail("R2 quick-loop must pause before cleanup for artifact review")
    if "no review" not in low:
        return fail('R3 quick-loop must document the "no review" opt-out')
    if not all(term in low for term in ("research.md", "design.md", "plan.md", "thinking/")):
        return fail(
            "R4 quick-loop review pause must name the intermediate artifacts, including thinking/"
        )
    if "remove the session folder" not in low:
        return fail("R4 quick-loop review pause must keep the session folder visible")
    if "ask me to proceed" not in low and "user asks to proceed" not in low:
        return fail("R5 quick-loop cleanup must resume only when the user asks to proceed")
    if "cleanup immediately" not in low:
        return fail('R6 quick-loop must run cleanup immediately only for "no review"')

    print("PASS: quick-loop review retention contract holds")
    return 0


if __name__ == "__main__":
    sys.exit(main())
