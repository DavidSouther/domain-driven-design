#!/usr/bin/env python3
"""Feature test: Code Mode is documented as a shape reference and routed from SKILL.md.

Code Mode is an ultra-condensed variant of the developer:ailly five-phase loop,
purpose-built for small standalone scripts and automations. Its deliverable is
documentation: a new shape reference at
`developer/skills/ailly/references/shapes/code-mode.md`, plus a routing entry in
`developer/skills/ailly/SKILL.md` following the existing Quick-loop / Long-loop /
Bugfix / Project Shape pattern.

This is a source-level contract over developer:ailly, matching the existing
`developer/tests/*.py` convention (standalone script, no third-party deps,
`main()` returns 0 when the contract holds or 1 with one reason line). It stays
red until the reference file and the routing wiring exist.
"""

import re
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
SKILL = REPO / "developer" / "skills" / "ailly" / "SKILL.md"
CODE_MODE = REPO / "developer" / "skills" / "ailly" / "references" / "shapes" / "code-mode.md"


def fail(reason: str) -> int:
    print(reason)
    return 1


def section(text: str, heading: str) -> str:
    """Return the body of a `## <heading>` section, up to the next `## ` heading."""
    match = re.search(rf"(?im)^##\s+{re.escape(heading)}\s*$", text)
    if not match:
        return ""
    rest = text[match.end():]
    nxt = re.search(r"(?m)^##\s+", rest)
    return rest[: nxt.start()] if nxt else rest


def main() -> int:
    # R1: the shape reference file must exist.
    if not CODE_MODE.exists():
        return fail(
            "R1 Code Mode shape reference must exist at "
            "developer/skills/ailly/references/shapes/code-mode.md"
        )
    ref = CODE_MODE.read_text(encoding="utf-8").lower()

    # R2: it must state when Code Mode applies -- the script/automation boundary
    # that separates it from a feature (quick-loop / standard loop).
    if "standalone script" not in ref and "small script" not in ref:
        return fail(
            "R2 code-mode.md must scope Code Mode to standalone scripts/automations, "
            "not application features"
        )

    # R3: the cursory research step is a research:public check for an
    # off-the-shelf tool that fits the task before writing anything.
    if "research:public" not in ref:
        return fail("R3 code-mode.md must route the cursory tool check through research:public")
    if "off-the-shelf" not in ref:
        return fail(
            "R3 code-mode.md must describe checking for an off-the-shelf tool before writing a script"
        )

    # R4: the design+plan collapse into a single combined planning doc, and
    # there is no feature test / no TDD -- the script is run once and inspected.
    if "combined" not in ref:
        return fail(
            "R4 code-mode.md must collapse research/design/plan into one combined planning doc"
        )
    if "no feature test" not in ref:
        return fail("R4 code-mode.md must state that Code Mode writes no feature test")
    if "run it once" not in ref:
        return fail(
            "R4 code-mode.md Build step must be run-it-once-and-inspect-the-output, not TDD"
        )

    # R5: ambiguity is handled by reusing intent-review.md as-is; the single
    # human-cleared gate is what resolves a raised question (intent-review never
    # auto-clears on its own).
    if "intent-review.md" not in ref:
        return fail("R5 code-mode.md must reuse intent-review.md for ambiguous clarifications")

    # R6: SKILL.md must route to the shape with its own section, following the
    # Quick-loop / Long-loop / Bugfix / Project Shape precedent.
    skill = SKILL.read_text(encoding="utf-8")
    code_mode_section = section(skill, "Code Mode")
    if not code_mode_section:
        return fail("R7 SKILL.md must document Code Mode in its own `## Code Mode` section")
    if "references/shapes/code-mode.md" not in code_mode_section:
        return fail("R7 SKILL.md Code Mode section must point to references/shapes/code-mode.md")

    # R8: SKILL.md's routing table must carry a Code Mode row pointing at the reference.
    routing = section(skill, "Routing")
    if "references/shapes/code-mode.md" not in routing:
        return fail("R8 SKILL.md Routing table must include a Code Mode row -> references/shapes/code-mode.md")

    print("PASS: Code Mode shape reference and routing contract holds")
    return 0


if __name__ == "__main__":
    sys.exit(main())
