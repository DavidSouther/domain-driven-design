#!/usr/bin/env python3
"""Structural checker for `general:writing-pattern-skills` invocation cases.

The artifact is a pattern SKILL.md (`value-object`) plus a references/python.md
file. Each rule traces to the canonical pattern-skill template and Common
Mistakes in writing-pattern-skills. On the first violated rule it prints a
single-line reason to stdout and exits 1; if every rule holds it exits 0.
stderr is left untouched.

Rules:
- R1 frontmatter with name: value-object and a description:.
- R2 description starts with "Use when".
- R3 all six canonical sections present: Overview, When to Use, Core Pattern,
     Quick Reference, Common Mistakes, Composes With.
- R4 Common Mistakes has >= 3 bolded entries.
- R5 Composes With names >= 1 cross-reference in plugin:skill form.
- R6 a references/python.md file with runnable-looking Python (class/def).
"""

import re
import sys

from _checker_utils import fail, field, frontmatter_blocks, read_candidate

CANONICAL = [
    "overview",
    "when to use",
    "core pattern",
    "quick reference",
    "common mistakes",
    "composes with",
]
PLUGIN_SKILL = re.compile(r"\b(patterns|general|developer|domain|research|characters):[a-z][a-z-]+")


def section_body(src: str, name: str) -> str:
    """Text from the `name` heading to the next heading of any level."""
    head = re.search(rf"(?im)^#{{1,6}}\s*{re.escape(name)}\b.*$", src)
    if not head:
        return ""
    rest = src[head.end() :]
    nxt = re.search(r"(?m)^#{1,6}\s+\S", rest)
    return rest[: nxt.start()] if nxt else rest


def main() -> int:
    src = read_candidate()

    blocks = frontmatter_blocks(src)
    if not blocks:
        return fail("R1 frontmatter: no YAML frontmatter block with a name: field")
    # Find the value-object block among all frontmatter blocks; the output may
    # also quote neighbouring patterns' frontmatter as Composes-With examples.
    fm = next((b for b in blocks if field(b, "name") == "value-object"), None)
    if fm is None:
        names = ", ".join(repr(field(b, "name")) for b in blocks)
        return fail(f"R1 name: no frontmatter block named value-object (found: {names})")
    desc = field(fm, "description")
    if not desc:
        return fail("R1 frontmatter: value-object frontmatter missing description:")

    if not re.match(r"(?i)use when\b", desc):
        return fail(f"R2 description: must start with 'Use when'; got {desc[:48]!r}")

    missing = [
        s for s in CANONICAL if not re.search(rf"(?im)^#{{1,6}}\s*{re.escape(s)}\b", src)
    ]
    if missing:
        return fail(f"R3 sections: missing canonical section(s): {', '.join(missing)}")

    bolded = re.findall(r"\*\*[^*\n]+\*\*", section_body(src, "common mistakes"))
    if len(bolded) < 3:
        return fail(f"R4 common mistakes: {len(bolded)} bolded entr(ies), expected >= 3")

    if not PLUGIN_SKILL.search(section_body(src, "composes with")):
        return fail("R5 composes with: no plugin:skill cross-reference (e.g. `patterns:newtype`)")

    if "references/python.md" not in src:
        return fail("R6 references: no references/python.md file in the output")
    after = src.split("references/python.md", 1)[1]
    if not re.search(r"(?m)^\s*(class\s|def\s|@dataclass)", after):
        return fail(
            "R6 references: references/python.md has no runnable-looking Python "
            "(a class/def/@dataclass)"
        )

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
