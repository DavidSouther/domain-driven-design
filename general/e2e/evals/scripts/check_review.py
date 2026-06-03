#!/usr/bin/env python3
"""Structural checker for `general:review` invocation cases.

The artifact is a review of a PR diff. Each rule traces to the Review Criteria
and Common Mistakes in the review skill. On the first violated rule it prints a
single-line reason to stdout and exits 1; if every rule holds it exits 0.
stderr is left untouched.

Rules:
- R1 an explicit rubric: >= 3 markdown list items.
- R2 names >= 3 of the four canonical criteria (correctness, completeness,
     clarity, conciseness).
- R3 flags >= 1 concrete issue grounded in this diff (not an all-clear).
- R4 does not produce inline edits (no `git apply`, no ```suggestion fence).
"""

import re
import sys

from _checker_utils import fail, read_candidate

CRITERIA = ("correctness", "completeness", "clarity", "conciseness")
ISSUE_TERMS = (
    "missing",
    "removed",
    "unrelated",
    "scope",
    "breaking",
    "rename",
    "renamed",
    "no test",
    "default",
    "required",
    "positional",
    "regress",
)
DIFF_REFS = ("is_admin", "format_timestamp", "fmt_ts", "user(", "/users", "test_")


def main() -> int:
    src = read_candidate()
    low = src.lower()

    items = re.findall(r"(?m)^\s*(?:[-*]|\d+[.)])\s+\S", src)
    if len(items) < 3:
        return fail(f"R1 rubric: {len(items)} list item(s); expected an explicit rubric of >= 3")

    named = [c for c in CRITERIA if c in low]
    if len(named) < 2:
        return fail(
            f"R2 criteria: named {len(named)} of correctness/completeness/clarity/"
            "conciseness, expected >= 2 (a rubric built from the skill's criteria)"
        )

    if not any(term in low for term in ISSUE_TERMS):
        return fail(
            "R3 issue: no concrete issue flagged (scope creep / removed test / "
            "breaking change / missing test)"
        )
    if not any(ref in low for ref in DIFF_REFS):
        return fail(
            "R3 issue: issues are not grounded in this diff (no reference to "
            "is_admin / format_timestamp / User / tests)"
        )

    if "git apply" in low or re.search(r"```+\s*suggestion", low):
        return fail(
            "R4 no inline edits: the review produced edits (a suggestion/patch); "
            "evaluation and editing must happen in separate agents"
        )

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
