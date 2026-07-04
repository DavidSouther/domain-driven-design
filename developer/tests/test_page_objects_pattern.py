#!/usr/bin/env python3
"""Feature test: Page Objects ability in the testing patterns catalog (issue #27).

The primary user story (design.md, "User Journey and Metrics"): a developer
hits a design pressure where an acceptance/e2e test repeatedly drives the same
UI surface (a screen or console) and selector/wait knowledge is duplicated
across tests. They consult `patterns:using-patterns`. Its routing table names
a `page-objects` pattern and points at `references/patterns/page-objects.md`.
That reference teaches: when to reach for a page object; naming (one page
object per screen/console, verb-phrase methods describing user intent, e.g.
`System_findObject`, `Helm_setManeuver`); the split between what belongs in
the page object (selectors, waits) and what stays in the test (assertions);
and how it composes with arrange-act-assert (the page object's methods are
the Act, the test still owns its own Arrange/Assert).

This is a contract check on the source-of-truth files, mirroring the shape of
`test_subagent_model_mandate.py` and `test_fable5_softblock.py`: it needs no
model and no pytest, and exits 0 (every rule holds) or 1 with a single reason
line on stdout. It starts RED: today neither the routing table nor the
reference file mentions page objects at all.
"""

import re
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
SKILL = REPO / "patterns" / "skills" / "using-patterns" / "SKILL.md"
REFERENCE = (
    REPO
    / "patterns"
    / "skills"
    / "using-patterns"
    / "references"
    / "patterns"
    / "page-objects.md"
)

REQUIRED_SECTIONS = [
    "Overview",
    "When to Use",
    "Core Pattern",
    "Quick Reference",
    "Common Mistakes",
    "Composes With",
]


def fail(reason: str) -> int:
    print(reason)
    return 1


def section(text: str, heading: str) -> str:
    """Return the body of the `##` section with this heading, up to the next
    `##` heading (case-insensitive), or "" if the heading is absent."""
    match = re.search(rf"(?im)^##\s+{re.escape(heading)}\s*$", text)
    if not match:
        return ""
    rest = text[match.end():]
    nxt = re.search(r"(?m)^##\s+", rest)
    return rest[: nxt.start()] if nxt else rest


def main() -> int:
    # T1 - the routing table names the pattern and its reference path.
    if not SKILL.is_file():
        return fail(f"T1 {SKILL.relative_to(REPO)} not found")
    skill_text = SKILL.read_text(encoding="utf-8")
    if "page-objects" not in skill_text:
        return fail(
            f"T1 routing: {SKILL.relative_to(REPO)} does not name a "
            "'page-objects' pattern anywhere"
        )
    if "references/patterns/page-objects.md" not in skill_text:
        return fail(
            f"T1 routing: {SKILL.relative_to(REPO)} does not point at "
            "references/patterns/page-objects.md"
        )

    # T2 - a discriminator distinguishes page-objects from arrange-act-assert,
    # since both are testing-shaped patterns and the issue asks explicitly how
    # they relate.
    discriminators = section(skill_text, "Discriminators That Are Easy to Confuse")
    if not discriminators or "page-objects" not in discriminators:
        return fail(
            "T2 discriminator: 'Discriminators That Are Easy to Confuse' does "
            "not distinguish page-objects from arrange-act-assert"
        )

    # T3 - the reference file exists.
    if not REFERENCE.is_file():
        return fail(f"T3 {REFERENCE.relative_to(REPO)} not found")
    ref_text = REFERENCE.read_text(encoding="utf-8")

    # T4 - the reference follows the sibling pattern-file shape.
    missing_sections = [h for h in REQUIRED_SECTIONS if not section(ref_text, h)]
    if missing_sections:
        return fail(
            f"T4 shape: {REFERENCE.relative_to(REPO)} is missing section(s) "
            f"{missing_sections}"
        )

    # T5 - naming convention: one page object per screen/console, methods
    # named as verb phrases describing user intent, not raw selectors.
    ref_low = ref_text.lower()
    if "verb" not in ref_low:
        return fail(
            f"T5 naming: {REFERENCE.relative_to(REPO)} does not document "
            "verb-phrase method naming"
        )
    if "screen" not in ref_low and "console" not in ref_low:
        return fail(
            f"T5 naming: {REFERENCE.relative_to(REPO)} does not scope one "
            "page object per screen/console"
        )

    # T6 - the page-vs-test split: selectors/waits live in the page object;
    # assertions stay in the test.
    if "selector" not in ref_low or "wait" not in ref_low:
        return fail(
            f"T6 split: {REFERENCE.relative_to(REPO)} does not state that "
            "selectors and waits belong in the page object"
        )
    if "assert" not in ref_low:
        return fail(
            f"T6 split: {REFERENCE.relative_to(REPO)} does not state that "
            "assertions stay in the test, not the page object"
        )

    # T7 - relation to arrange-act-assert: the reference cross-links it under
    # Composes With, explaining the page object's methods are the Act.
    composes = section(ref_text, "Composes With")
    if "arrange-act-assert" not in composes.lower():
        return fail(
            f"T7 composition: {REFERENCE.relative_to(REPO)}'s Composes With "
            "section does not cross-link arrange-act-assert"
        )

    print("PASS: page-objects pattern contract holds")
    return 0


if __name__ == "__main__":
    sys.exit(main())
