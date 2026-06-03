"""Shared utilities for the general/e2e structural checkers.

The general skills produce Markdown artifacts — SKILL.md files and review prose —
so the checkers operate on the raw candidate text rather than extracting a single
source dialect. (A SKILL.md contains its own fenced code blocks, so naively
un-fencing an outer ```markdown wrapper would truncate it; the YAML `---` fence
and heading lines survive whether or not the model wraps the answer in a fence.)

Each checker reads the candidate on stdin, applies an ordered list of rules, and
either exits 0 (every rule holds) or exits 1 with a single-line reason on stdout.
stderr is never written to, so the eval runner records a genuine Fail, not an
Errored broken checker.
"""

import re
import sys


def read_candidate() -> str:
    """Return the whole assistant message piped in on stdin."""
    return sys.stdin.read()


def fail(reason: str) -> int:
    """Write a single-line reason to stdout and return exit code 1.

    Leaves stderr untouched so the runner records Fail, not Errored.
    """
    sys.stdout.write(reason + "\n")
    return 1


# A YAML frontmatter block: an opening `---` line, body, a closing `---` line.
# The inner region must BEGIN with a `key:` line. That requirement is what keeps
# the matcher from mis-pairing the real frontmatter fences against the `---`
# horizontal rules and ```markdown wrappers a model sprinkles between two
# emitted SKILL.md files. Non-greedy so the closing fence is the nearest one.
_FRONTMATTER = re.compile(
    r"(?ms)^---[ \t]*\n([ \t]*[A-Za-z_][\w-]*[ \t]*:.*?)\n---[ \t]*$"
)


def frontmatter_blocks(src: str) -> list[str]:
    """Inner text of each frontmatter block that carries a `name:` field.

    Filtering on `name:` rejects spurious matches from a `---` ... `---`
    horizontal-rule pair inside a body. The writing-paired-skills artifact
    produces two such blocks; a single SKILL.md produces one.
    """
    blocks = []
    for match in _FRONTMATTER.finditer(src):
        inner = match.group(1)
        if re.search(r"(?m)^\s*name\s*:", inner):
            blocks.append(inner)
    return blocks


def field(frontmatter_inner: str, key: str) -> str | None:
    """Value of a top-level `key:` line in a frontmatter block, or None."""
    match = re.search(rf"(?m)^\s*{re.escape(key)}\s*:\s*(.+?)\s*$", frontmatter_inner)
    return match.group(1).strip() if match else None


def headings(src: str) -> list[str]:
    """All ATX heading texts (any level), stripped of leading #'s and spaces."""
    return [m.group(1).strip() for m in re.finditer(r"(?m)^#{1,6}\s+(.+?)\s*#*\s*$", src)]
