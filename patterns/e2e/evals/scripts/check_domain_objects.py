#!/usr/bin/env python3
"""Structural checker for `patterns:domain-objects` invocation cases.

Reads a TypeScript candidate from stdin and applies ordered rules tracing to the
domain-objects SKILL.md "Common Mistakes" section. First violated rule prints a
single-line reason to stdout and exits 1; all holding exits 0. stderr untouched.

Rules:
- R1 an Entity with identity — `Batch` carries an `id`.
- R2 a Value Object without identity — `Money` has amount + currency and no `id`
  ("Giving a Value Object an id").
- R3 a Domain Service Function — `allocate` is a free function spanning batches, not
  a method on a single entity ("Putting cross-entity logic inside one entity").
"""

import re
import sys

from _checker_utils import extract_code, fail, strip_comments


def class_or_type_block(src: str, name: str) -> str:
    """Return the `class <name> {...}` or `interface/type <name> {...}` block text."""
    m = re.search(r"\b(?:class|interface|type)\s+" + name + r"\b[^{]*\{", src)
    if not m:
        return ""
    open_brace = src.index("{", m.end() - 1)
    depth = 0
    for i in range(open_brace, len(src)):
        if src[i] == "{":
            depth += 1
        elif src[i] == "}":
            depth -= 1
            if depth == 0:
                return src[open_brace : i + 1]
    return src[open_brace:]


def main() -> int:
    src = strip_comments(extract_code(sys.stdin.read()))

    # R1 — Entity Batch with an id.
    batch = class_or_type_block(src, "Batch")
    if not batch:
        return fail("R1 entity: no `Batch` entity type defined")
    if not re.search(r"\bid\b\s*[:?]", batch) and not re.search(r"\b(?:readonly\s+)?id\b", batch):
        return fail(
            "R1 entity identity: `Batch` has no `id` field; an entity carries a stable "
            "identity that persists as its state changes"
        )

    # R2 — Value Object Money without an id.
    money = class_or_type_block(src, "Money")
    if not money:
        return fail("R2 value object: no `Money` value type defined")
    if re.search(r"\bid\b\s*[:?]", money):
        return fail(
            "R2 value object has an id: `Money` carries an `id`; a value object is "
            "equal by its fields and must not be given identity"
        )

    # R3 — Domain Service Function allocate as a free function.
    if re.search(r"\ballocate\s*\([^)]*\)\s*[:{]", src) and not re.search(
        r"\b(?:function\s+allocate|const\s+allocate\s*=|export\s+function\s+allocate)\b", src
    ):
        return fail(
            "R3 domain service function: `allocate` appears to be a method, not a free "
            "function; cross-batch logic belongs in a standalone domain service "
            "function, not inside a single entity"
        )
    if not re.search(r"\b(?:function\s+allocate|const\s+allocate\s*=)", src):
        return fail(
            "R3 domain service function: no free `allocate` function; the cross-batch "
            "operation must live in a standalone function, not on one entity"
        )

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
