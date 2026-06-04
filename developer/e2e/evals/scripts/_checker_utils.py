"""Shared utilities for the developer-plugin structural checkers.

Each checker reads the assistant turn from stdin, applies an ordered list of
rules drawn 1:1 from the skill body it scores, and either exits 0 (all rules
hold) or exits 1 with a single-line reason on stdout. stderr is never written
to, so the eval runner records a genuine Fail, not an Errored broken checker.

The developer skills produce Markdown artifacts (a design doc, a feature test, a
plan, a TDD-cycle write-up), so these helpers parse Markdown structure —
headings, draft markers, fenced code — rather than a single source dialect.
"""

import re
import sys

FENCE = re.compile(r"```[^\n]*\n(.*?)```", re.DOTALL)
# A draft marker the skills emit, e.g. *Draft 2026-06-03* or *DRAFT 2026-06-03*.
# The date is required so a bare word "draft" in prose cannot satisfy the rule.
DRAFT_MARKER = re.compile(r"\*\s*draft\s+\d{4}-\d{2}-\d{2}\s*\*", re.IGNORECASE)


def read_stdin() -> str:
    """The whole assistant turn (prose, tables, fenced code)."""
    return sys.stdin.read()


def fenced_blocks(text: str) -> list[str]:
    """Contents of every fenced code block, in order."""
    return FENCE.findall(text)


def code_text(text: str) -> str:
    """Fenced code joined together, or the whole input if there are no fences."""
    blocks = fenced_blocks(text)
    return "\n".join(blocks) if blocks else text


def has_heading(text: str, title: str) -> bool:
    """True if a Markdown heading (any level) names `title`, case-insensitively.

    Matches `## Problem Statement`, `### problem statement`, etc. Bold-only
    pseudo-headings (`**Problem Statement**` on its own line) also count, since
    skills vary the emphasis style.
    """
    heading = re.compile(
        r"^\s{0,3}(?:#{1,6}\s+|\*\*)" + re.escape(title) + r"\b",
        re.IGNORECASE | re.MULTILINE,
    )
    return bool(heading.search(text))


def has_draft_marker(text: str) -> bool:
    return bool(DRAFT_MARKER.search(text))


def fail(reason: str) -> int:
    """Write a single-line reason to stdout and return exit code 1.

    Leaves stderr untouched so the runner records Fail, not Errored.
    """
    sys.stdout.write(reason.replace("\n", " ").strip() + "\n")
    return 1
