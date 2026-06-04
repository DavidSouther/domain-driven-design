"""Shared helpers for the research invocation checkers.

Each checker reads the assistant's Markdown answer from stdin, applies an
ordered list of rules — each tracing to a structural marker the skill's output
format or "Common Mistakes" section teaches — and either exits 0 (all rules
hold) or exits 1 with a single-line reason on stdout. stderr is never written
to, so the eval runner records a genuine Fail, not an Errored broken checker.
"""

import sys


def candidate() -> str:
    """The whole assistant message: prose, headings, fenced blocks, paths."""
    return sys.stdin.read()


def fail(reason: str) -> int:
    """Write a single-line reason to stdout and return exit code 1.

    Leaves stderr untouched so the runner records Fail, not Errored.
    """
    sys.stdout.write(reason + "\n")
    return 1


def count_present(text: str, terms: list[str]) -> int:
    """How many of `terms` appear in `text` (case-insensitive)."""
    low = text.lower()
    return sum(1 for t in terms if t.lower() in low)
