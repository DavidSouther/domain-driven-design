#!/usr/bin/env python3
"""Feature test: research notes stay under .ailly, not docs/research.

The repository has two research-note homes:

- standalone `research:` skills write to `.ailly/research/<dated-topic>/`;
- when Ailly delegates research as part of a development task, notes stay inside
  that task session under `.ailly/developer/<session>/research/`.

This is a source-level contract check so the skill text, not a particular model
run, carries the path discipline.
"""

import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
AILLY_RESEARCH = REPO / "developer" / "skills" / "ailly" / "references" / "phases" / "research.md"
USING_RESEARCH = REPO / "research" / "skills" / "using-research" / "SKILL.md"
RESEARCH_SKILLS = {
    "archaeology": REPO / "research" / "skills" / "archaeology" / "SKILL.md",
    "books": REPO / "research" / "skills" / "books" / "SKILL.md",
    "codebase": REPO / "research" / "skills" / "codebase" / "SKILL.md",
    "dependencies": REPO / "research" / "skills" / "dependencies" / "SKILL.md",
    "domain": REPO / "research" / "skills" / "domain" / "SKILL.md",
    "internal": REPO / "research" / "skills" / "internal" / "SKILL.md",
    "papers": REPO / "research" / "skills" / "papers" / "SKILL.md",
    "public": REPO / "research" / "skills" / "public" / "SKILL.md",
}


def fail(reason: str) -> int:
    print(reason)
    return 1


def read(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def main() -> int:
    ailly = read(AILLY_RESEARCH)
    if "docs/research" in ailly:
        return fail("R1 Ailly research phase must not send task notes to docs/research")
    if ".ailly/developer/YYYY-MM-DD-A-<topic>/research/<skill>.md" not in ailly:
        return fail(
            "R1 Ailly research phase must place per-skill findings under the "
            "task session research folder"
        )
    if "overriding the standalone `.ailly/research/` default" not in ailly:
        return fail("R1 Ailly research phase must explicitly override the standalone default")

    using = read(USING_RESEARCH)
    if "docs/research" in using:
        return fail("R2 using-research convention must not create docs/research")
    if ".ailly/research/YYYY-MM-DD-A-<topic>/" not in using:
        return fail("R2 using-research must name the standalone .ailly/research default")
    if ".ailly/developer/<session-slug>/research/" not in using:
        return fail("R2 using-research must name the Ailly task-scoped research folder")

    for skill, path in RESEARCH_SKILLS.items():
        text = read(path)
        if "docs/research" in text:
            return fail(f"R3 {skill} skill must not mention docs/research")
        if ".ailly/research/YYYY-MM-DD-A-<topic>/" not in text:
            return fail(f"R3 {skill} skill must name the standalone .ailly/research path")
        if ".ailly/developer/<session-slug>/research/" not in text:
            return fail(f"R3 {skill} skill must honor task-scoped research folders")

    print("PASS: research note path contract holds")
    return 0


if __name__ == "__main__":
    sys.exit(main())
