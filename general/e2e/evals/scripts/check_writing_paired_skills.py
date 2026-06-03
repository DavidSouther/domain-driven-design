#!/usr/bin/env python3
"""Structural checker for `general:writing-paired-skills` invocation cases.

The artifact is two SKILL.md files split from one mixed-cadence skill: a wiring
half and a practice half. Each rule traces to a structural property
writing-paired-skills prescribes — the Frontmatter Conventions (cadence clause),
the symmetric "When NOT to use" cross-reference, and the published Contract.
On the first violated rule it prints a single-line reason to stdout and exits 1;
if every rule holds it exits 0. stderr is left untouched.

Rules:
- R1 two frontmatter blocks (two skills).
- R2 the two skills have distinct names.
- R3 the two descriptions show the cadence split: one once/bootstrap cadence and
     one every/each cadence.
- R4 symmetric cross-reference: each body names the other skill, under a
     "When NOT to use" line.
- R5 at least one body publishes a contract (a Contract heading/label, or an
     "after this skill runs … may assume" statement).
"""

import re
import sys

from _checker_utils import _FRONTMATTER, fail, field, read_candidate

WIRING_CADENCE = re.compile(
    r"(?i)\b(once|bootstrap\w*|per process|per environment|at (?:process )?start|set ?up)\b"
)
PRACTICE_CADENCE = re.compile(
    r"(?i)\b(every|each (?:time|change|cycle|emit|commit)|per call|per change|per check|call site)\b"
)
CONTRACT = re.compile(
    r"(?im)(^#{1,6}\s*contract\b|after this skill runs|after .{0,40}has run|may assume\b)"
)


def main() -> int:
    src = read_candidate()

    matches = [
        m for m in _FRONTMATTER.finditer(src) if re.search(r"(?m)^\s*name\s*:", m.group(1))
    ]
    if len(matches) < 2:
        return fail(
            f"R1 two skills: found {len(matches)} frontmatter block(s) with a name:, "
            "expected 2 (a wiring skill and a practice skill)"
        )

    b1, b2 = matches[0], matches[1]
    fm1, fm2 = b1.group(1), b2.group(1)
    name1, name2 = field(fm1, "name"), field(fm2, "name")
    if not name1 or not name2:
        return fail("R1 two skills: a frontmatter block is missing name:")
    if name1 == name2:
        return fail(f"R2 distinct names: both skills are named {name1!r}")

    # Search the whole frontmatter inner, not the parsed description: a folded
    # YAML description spans several lines and the cadence clause ("applies once
    # at start" / "applies every time") usually lands on a continuation line.
    has_wiring = bool(WIRING_CADENCE.search(fm1) or WIRING_CADENCE.search(fm2))
    has_practice = bool(PRACTICE_CADENCE.search(fm1) or PRACTICE_CADENCE.search(fm2))
    if not (has_wiring and has_practice):
        return fail(
            "R3 cadence clause: the two descriptions do not show a once/bootstrap "
            "(wiring) vs every/each (practice) cadence split"
        )

    body1 = src[b1.end() : b2.start()]
    body2 = src[b2.end() :]

    def cross_references(body: str, other: str) -> bool:
        return bool(re.search(r"(?i)when not to use", body)) and other in body

    if not cross_references(body1, name2):
        return fail(
            f"R4 cross-reference: the first skill body does not name {name2!r} "
            "under a 'When NOT to use' line"
        )
    if not cross_references(body2, name1):
        return fail(
            f"R4 cross-reference: the second skill body does not name {name1!r} "
            "under a 'When NOT to use' line"
        )

    if not (CONTRACT.search(body1) or CONTRACT.search(body2)):
        return fail(
            "R5 contract: neither body publishes a contract (a Contract heading or an "
            "'after this skill runs … may assume' statement); the wiring skill must "
            "publish it and the practice skill cite it"
        )

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
