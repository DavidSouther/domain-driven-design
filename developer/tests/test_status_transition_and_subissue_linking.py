#!/usr/bin/env python3
"""Feature test: status-transition and sub-issue-linking rules in using.md.

Issue #22: `using.md` (the program-management practice reference) tells rule 4
to "link to the parent Epic" without saying *when* a sub-issue discovered
mid-build must be linked, and rule 5 says to "record phase progress" without
saying when to move the tracker's board card between Todo -> In Progress ->
Done. design.md (Specification) prescribes three prose additions:

1. Rule 4 gains: link each child issue as a sub-issue of its parent
   immediately when it is created, not deferred to cleanup.
2. Rule 5 gains: move the board card to In Progress at Research-phase start
   (first commit to the session branch), and to Done when Cleanup completes
   and the issue closes -- conditioned on the tracker exposing a status field.
3. Capability Routing gains a GitHub-specific note: the sub-issue endpoint
   takes the child's database id (an integer), not its issue number; `gh api
   -F` sends strings and is unreliable for it, so use `gh api --input -` with
   a JSON heredoc instead.

This is a source-level contract check on `using.md`'s prose, matching the
existing pattern in `test_subagent_model_mandate.py` and
`test_research_note_paths.py`. It needs no model and no pytest; it exits 0
when all rules hold, or 1 with a single reason line on stdout. It starts RED:
today `using.md` says only "link to the parent Epic via the link capability"
in rule 4, only "tick the task's checklist" in rule 5, and its Capability
Routing section says nothing about GitHub's id type or `gh api -F`.
"""

import re
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
USING = (
    REPO
    / "developer"
    / "skills"
    / "ailly"
    / "references"
    / "abilities"
    / "program-management"
    / "using.md"
)


def fail(reason: str) -> int:
    print(reason)
    return 1


def numbered_item(text: str, n: int) -> str:
    """Return the body of numbered list item `n.` up to the next `n+1.` item,
    or "" if item `n.` is not found."""
    m = re.search(rf"(?ms)^{n}\.\s+\*\*.*?(?=^{n + 1}\.\s+\*\*|\Z)", text)
    return m.group(0) if m else ""


def section(text: str, heading: str) -> str:
    m = re.search(rf"(?im)^##\s+{re.escape(heading)}\s*$", text)
    if not m:
        return ""
    rest = text[m.end():]
    nxt = re.search(r"(?m)^##\s+", rest)
    return rest[: nxt.start()] if nxt else rest


def main() -> int:
    if not USING.is_file():
        return fail(f"T0 {USING} not found")
    text = USING.read_text(encoding="utf-8")

    # T1 - rule 4 (Create/label tasks) prescribes linking each child issue as
    # a sub-issue immediately at creation, not deferred to cleanup.
    rule4 = numbered_item(text, 4)
    if not rule4:
        return fail("T1 rule 4 (Create/label tasks) not found as a numbered item")
    rule4_low = rule4.lower()
    if "immediately" not in rule4_low or "creat" not in rule4_low:
        return fail(
            "T1 rule 4 must say sub-issues are linked immediately when the "
            "child issue is created"
        )
    if "cleanup" not in rule4_low or "not deferred" not in rule4_low and "defer" not in rule4_low:
        return fail(
            "T1 rule 4 must explicitly say linking is not deferred to cleanup"
        )

    # T2 - rule 5 (Record phase progress) prescribes moving the board card to
    # In Progress at Research-phase start and to Done at Cleanup completion,
    # conditioned on the tracker's status field.
    rule5 = numbered_item(text, 5)
    if not rule5:
        return fail("T2 rule 5 (Record phase progress) not found as a numbered item")
    rule5_low = rule5.lower()
    if "in progress" not in rule5_low:
        return fail("T2 rule 5 must name the In Progress board-column trigger")
    if "research" not in rule5_low or "commit" not in rule5_low:
        return fail(
            "T2 rule 5 must tie the In Progress trigger to the Research "
            "phase's first commit to the session branch"
        )
    if "done" not in rule5_low:
        return fail("T2 rule 5 must name the Done board-column trigger")
    if "cleanup" not in rule5_low:
        return fail("T2 rule 5 must tie the Done trigger to Cleanup completing")
    if "status field" not in rule5_low:
        return fail(
            "T2 rule 5 must condition both triggers on the tracker exposing a "
            "status field"
        )

    # T3 - Capability Routing names GitHub's sub-issue id-type caveat and the
    # gh api --input workaround for gh api -F's string coercion.
    routing = section(text, "Capability Routing")
    if not routing:
        return fail("T3 no `## Capability Routing` section found")
    routing_low = routing.lower()
    if "database id" not in routing_low and "database identifier" not in routing_low:
        return fail(
            "T3 Capability Routing must say the sub-issue endpoint needs the "
            "child's database id, not its issue number"
        )
    if "issue number" not in routing_low:
        return fail(
            "T3 Capability Routing must contrast the database id against the "
            "issue number"
        )
    if "-f" not in routing_low:
        return fail("T3 Capability Routing must call out `gh api -F`'s string coercion")
    if "--input" not in routing_low:
        return fail(
            "T3 Capability Routing must prescribe `gh api --input -` with a "
            "JSON heredoc as the fix"
        )

    print("PASS: status-transition and sub-issue-linking rules hold")
    return 0


if __name__ == "__main__":
    sys.exit(main())
