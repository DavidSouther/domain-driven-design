#!/usr/bin/env python3
"""Structural checker for the `refactor` invocation case.

Rules trace 1:1 to the refactor SKILL.md: it names code smells from a fixed
catalog ("Code Smells to Target"), writes a plan of one refactoring at a time,
and never changes behaviour while restructuring ("Never refactor behavior and
structure simultaneously").

Rule:
- R1 at least two distinct named code smells from the skill's catalog appear
  (the skill's diagnostic vocabulary, which un-skilled rewriting does not use).

The behaviour-preserving, one-at-a-time discipline is left to the judge: it is a
semantic property the model phrases many ways, so matching it by keyword is
brittle. R1 — the named-smell vocabulary — is the mechanical signal the script
owns; the judge owns "did it preserve behaviour and work one smell at a time".
"""

import re
import sys

from _checker_utils import fail, read_stdin

# The skill's catalog of smells (case-insensitive substrings / patterns).
SMELLS = [
    r"three[- ]strikes",
    r"duplicat",            # duplicated / duplication
    r"conditional complexity",
    r"combinatorial explosion",
    r"temporary field",
    r"long method",
    r"long parameter list",
    r"large class",
    r"magic (?:constant|number)",
    r"type embedded in name",
    r"uncommunicative name",
    r"inconsistent name",
    r"dead code",
    r"alternative classes",
    r"primitive obsession",
    r"data clump",
    r"message chain",
    r"parallel inheritance",
    r"incomplete library",
    r"inappropriate intimacy",
    r"middle man",
    r"indecent exposure",
    r"feature envy",
    r"lazy class",
    r"divergent change",
    r"shotgun surgery",
    r"solution sprawl",
]


def main() -> int:
    text = read_stdin()

    # R1 — at least two distinct named smells.
    found = {s for s in SMELLS if re.search(s, text, re.IGNORECASE)}
    if len(found) < 2:
        return fail(
            f"R1 named smells required: found {len(found)} catalog smell(s); the "
            "refactor skill diagnoses code by named smells (Long Method, Magic "
            "Constant, duplication, …) before resolving them"
        )

    return 0


if __name__ == "__main__":
    sys.exit(main())
