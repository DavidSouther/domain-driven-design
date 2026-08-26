#!/usr/bin/env python3
"""Feature test: C3 review orchestration and continuous intent review.

User story:
Given a final artifact is prepared for handoff, when general:review runs,
then it performs one named C3 review and any applicable specialists, and its
skill contract names a cold evidence-located challenge to an independent
verifier that reports a failed or unresolved challenge instead of silently
selecting a verdict.
Given an Ailly artifact is being developed, intent review checks request
alignment at each phase or stage without invoking final-handoff C3 review.

This is a deterministic root-e2e contract test scoped to the skill
definitions only (general:review and developer:ailly). It stays red until
those skill files implement the whole story in prose. It does not assert
against any runtime implementation.
"""

import sys
from pathlib import Path
from typing import Optional
import re

sys.path.insert(0, str(Path(__file__).resolve().parent))
from _checker_utils import AILLY_DIR, GENERAL_REVIEW, INTENT_REVIEW, REPO, fail, read  # noqa: E402


def require(path: Path, phrase: str, reason: str) -> Optional[int]:
    if not path.is_file():
        return fail(f"C3 feature: missing {path.relative_to(REPO)}")
    if phrase.lower() not in read(path).lower():
        return fail(f"C3 feature: {reason}")
    return None


def require_pattern(path: Path, pattern: str, reason: str) -> Optional[int]:
    if not path.is_file():
        return fail(f"C3 feature: missing {path.relative_to(REPO)}")
    if not re.search(pattern, read(path), flags=re.IGNORECASE | re.DOTALL):
        return fail(f"C3 feature: {reason}")
    return None


def section(path: Path, heading: str) -> str:
    """Return one exact level-two Markdown section for scoped contract checks."""
    content = read(path)
    match = re.search(r"^##\s+" + re.escape(heading) + r"\s*$([\s\S]*?)(?=^##\s+|\Z)", content, flags=re.MULTILINE)
    return match.group(1) if match else ""


def main() -> int:
    c3 = section(GENERAL_REVIEW, "C3")
    if not c3:
        return fail("C3 feature: general:review must have an exact `## C3` section")
    if not re.search(
        r"Correctness.*?Conciseness.*?Clarity", c3, flags=re.IGNORECASE | re.DOTALL
    ):
        return fail("C3 feature: the `## C3` section must define Correctness, Conciseness, and Clarity")
    result = require_pattern(
        GENERAL_REVIEW,
        r"##\s+C3.*?Correctness.*?Conciseness.*?Clarity",
        "general:review must define C3 as Correctness, Conciseness, and Clarity",
    )
    if result is not None:
        return result
    result = require_pattern(
        GENERAL_REVIEW,
        r"specialist.*?description.*?matches.*?final artifact",
        "the final-handoff C3 contract must retain applicable-specialist composition",
    )
    if result is not None:
        return result
    result = require_pattern(
        GENERAL_REVIEW,
        r"final artifact.*?handoff.*?Intent review.*?(continuous|every phase|every stage)",
        "the handoff-only C3 boundary and continuous Intent-review boundary must be explicit",
    )
    if result is not None:
        return result
    result = require_pattern(
        GENERAL_REVIEW,
        r"cold challenger.*?evidence.*?(falsifiable|refut)",
        "the challenger must be cold, evidence-located, and falsifiable",
    )
    if result is not None:
        return result

    for phrase, reason in [
        ("every phase or stage", "Intent review must run continuously at every Ailly phase or stage"),
        ("original request", "Intent review must remain anchored to the original request"),
        ("never clears", "Intent review must not clear a human gate"),
    ]:
        result = require(INTENT_REVIEW, phrase, reason)
        if result is not None:
            return result

    result = require_pattern(
        AILLY_DIR / "SKILL.md",
        r"Intent review.*?(every phase|every stage|continuous)",
        "Ailly must wire a continuous Intent-review trigger into its coordinator",
    )
    if result is not None:
        return result

    for pattern, reason in [
        (r"findingId.*?counterclaim.*?evidence.*?(falsification|refut)", "the C3 section must describe a challenge packet with findingId, counterclaim, evidence, and a falsification condition"),
        (r"(accepted|rejected).*?unresolved.*?failed", "the C3 section must name all four challenge outcomes: accepted, rejected, unresolved, and failed"),
        (r"(both presentation orders|order.swap|order-swap)", "the C3 section must require the order-swap check for a consequential, disputed challenge"),
        (r"accepted.*?(remove|omit).*?rejected.*?(retain|keep).*?(unresolved|failed).*?(remove|omit)", "the C3 section must state how each challenge status controls whether a finding stays actionable"),
    ]:
        result = require_pattern(GENERAL_REVIEW, pattern, reason)
        if result is not None:
            return result

    return 0


if __name__ == "__main__":
    sys.exit(main())
