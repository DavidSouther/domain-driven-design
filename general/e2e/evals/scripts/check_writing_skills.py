#!/usr/bin/env python3
"""Structural checker for `general:writing-skills` invocation cases.

The artifact is a single SKILL.md (`condition-based-waiting`). Each rule traces
to a structural property writing-skills prescribes — the SKILL.md Structure
section, the CSO "Use when" rule, and the 1024-char frontmatter cap. On the
first violated rule it prints a single-line reason to stdout and exits 1; if
every rule holds it exits 0. stderr is left untouched so the runner records a
genuine Fail, never an Errored broken checker.

Rules:
- R1 one YAML frontmatter block with name: and description:.
- R2 name matches the requested skill (condition-based-waiting).
- R3 description starts with "Use when" (CSO: triggering conditions).
- R4 a level-1 (#) title heading is present.
- R5 at least one conventional section heading.
- R6 frontmatter <= 1024 characters.
"""

import re
import sys

from _checker_utils import fail, field, frontmatter_blocks, headings, read_candidate

CONVENTIONAL = (
    "overview",
    "when to use",
    "core pattern",
    "quick reference",
    "common mistakes",
    "implementation",
    "checklist",
)


def main() -> int:
    src = read_candidate()

    blocks = frontmatter_blocks(src)
    if not blocks:
        return fail("R1 frontmatter: no YAML frontmatter block with a name: field")
    fm = blocks[0]
    name = field(fm, "name")
    desc = field(fm, "description")
    if not name or not desc:
        return fail("R1 frontmatter: frontmatter missing name: or description:")

    if name != "condition-based-waiting":
        return fail(f"R2 name: expected condition-based-waiting, got {name!r}")

    if not re.match(r"(?i)use when\b", desc):
        return fail(f"R3 description: must start with 'Use when' (CSO); got {desc[:48]!r}")

    if not re.search(r"(?m)^#\s+\S", src):
        return fail("R4 heading: no level-1 (#) title heading")

    section_set = [h.lower() for h in headings(src)]
    if not any(any(c in h for c in CONVENTIONAL) for h in section_set):
        return fail(
            "R5 sections: no conventional section heading (Overview / When to Use / "
            "Core Pattern / Quick Reference / Common Mistakes / Implementation / Checklist)"
        )

    if len(fm) > 1024:
        return fail(f"R6 frontmatter size: {len(fm)} chars exceeds the 1024 cap")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
