#!/usr/bin/env python3
"""Structural checker for `patterns:unit-of-work` invocation cases.

Reads a TypeScript candidate from stdin and applies ordered rules tracing to the
unit-of-work SKILL.md "Common Mistakes" section. First violated rule prints a
single-line reason to stdout and exits 1; all holding exits 0. stderr untouched.

Rules:
- R1 a Unit of Work abstraction exposes commit() and rollback().
- R2 a test double needs no database (a Fake/InMemory unit of work).
- R3 the handler scopes the work and commits inside a guaranteed-rollback boundary
  ("Forgetting the rollback path").
"""

import re
import sys

from _checker_utils import extract_code, fail, strip_comments


def main() -> int:
    src = strip_comments(extract_code(sys.stdin.read()))

    # R1 — commit and rollback on the abstraction.
    if not (re.search(r"\bcommit\s*\(", src) and re.search(r"\brollback\s*\(", src)):
        return fail(
            "R1 commit/rollback: the unit of work must expose both `commit()` and "
            "`rollback()`; deferred writes flush on commit, and any failure rolls back"
        )

    # R2 — a database-free test double.
    if not re.search(r"\b(?:Fake|InMemory|Stub|Test)\w*(?:UnitOfWork|UoW|Uow|Work)\b", src):
        return fail(
            "R2 test double: no `Fake`/`InMemory` unit of work; provide a test double "
            "that runs the same handler without a real database"
        )

    # R3 — scoped usage with guaranteed rollback, and a commit inside it.
    scoped = (
        re.search(r"\bfinally\b", src)
        or re.search(r"\b(?:await\s+)?using\b", src)
        or re.search(r"\bwith\b", src)
    )
    if not (scoped and re.search(r"\.\s*commit\s*\(|\bcommit\s*\(\s*\)", src)):
        return fail(
            "R3 scoped transaction: the handler does not commit inside a "
            "guaranteed-rollback scope (`try/finally`, `using`, or context manager); "
            "rollback on failure must be automatic, not left to a happy-path call"
        )

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
