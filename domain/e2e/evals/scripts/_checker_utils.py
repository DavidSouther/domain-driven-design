"""Shared helpers for the domain/e2e structural checkers.

The eval runner pipes the final assistant turn to the checker on stdin and puts
the rendered user turn in the `AILLY_USER_QUESTION` environment variable. Each
checker applies an ordered list of rules, each tracing 1:1 to a structural rule
in the corresponding `domain` SKILL.md. On the first violated rule it prints a
single-line reason to stdout and exits 1; if every rule holds it exits 0. stderr
is never written, so the runner records a genuine Fail, never an Errored broken
checker.

The domain skills produce Markdown (headings, bold field labels, tables), not
code, so these helpers search the raw assistant text for structural markers.
Fenced ```` ```markdown ```` wrappers do not interfere — the inner markers are
still literal substrings.
"""

import json
import os
import re
import sys


def read_candidate() -> str:
    """The final assistant turn, as piped to the checker on stdin."""
    return sys.stdin.read()


def decoded_artifacts(text: str) -> str:
    """The candidate plus any artifact embedded in a tool-call `content` field.

    The shared coding-agent constitution tells the model it has file tools, so a
    skill that says "create the file" (e.g. glossary) is often answered by a
    simulated `write_file` whose `content` parameter is a JSON-escaped string
    (`\\n` literals, not real newlines). Structural rules that anchor on line
    starts cannot see through that. This decodes every `"content": "..."` JSON
    string and appends it with real newlines, so the checker evaluates the
    artifact the model actually produced regardless of whether it was emitted as
    plain Markdown or written through a tool. The analog of patterns-eval's
    `extract_code`. Applied symmetrically to both arms, so it is not a thumb on
    the scale.
    """
    parts = [text]
    for match in re.finditer(r'"content"\s*:\s*"((?:\\.|[^"\\])*)"', text):
        try:
            parts.append(json.loads('"' + match.group(1) + '"'))
        except (ValueError, json.JSONDecodeError):
            pass
    return "\n\n".join(parts)


def user_question() -> str:
    """The rendered user turn the runner exposes out of band.

    Used by the contracts checker to recover the inline fixture the model was
    asked to append to.
    """
    return os.environ.get("AILLY_USER_QUESTION", "")


def fail(reason: str) -> int:
    """Write a single-line reason to stdout and return exit code 1.

    Leaves stderr untouched so the runner records Fail, not Errored.
    """
    sys.stdout.write(reason + "\n")
    return 1


def has_draft_marker(text: str) -> bool:
    """A `[DRAFT]` marker (any case, bold or not)."""
    return re.search(r"\[\s*draft\s*\]", text, re.IGNORECASE) is not None


def field_value(text: str, name: str):
    """Inline value after a bold field label, or None if the label is absent.

    Matches both `**Name:**` and `**Name**:` spellings, case-insensitively, and
    returns the remainder of the line. A return of `""` means the label exists
    but carries no inline value.
    """
    pattern = re.compile(
        r"\*\*\s*" + re.escape(name) + r"\s*:?\s*\*\*\s*:?[ \t]*(.*)",
        re.IGNORECASE,
    )
    match = pattern.search(text)
    if match is None:
        return None
    return match.group(1).strip()


def field_has_real_value(text: str, name: str) -> bool:
    """True when the field exists and its inline value is not a `<placeholder>`.

    The skill format templates use `<...>` angle-bracket placeholders; an output
    that leaves them unfilled has not actually been authored.
    """
    value = field_value(text, name)
    if not value:
        return False
    return not value.lstrip().startswith("<")


def has_heading(text: str, contains: str, level: int = 2) -> bool:
    """A Markdown ATX heading at `level` whose text contains `contains`.

    Internal whitespace is made flexible, so `## OrderManifest` and
    `## Order Manifest` both match `contains="OrderManifest"`.
    """
    spaced = r"\s*".join(re.escape(ch) for ch in contains if not ch.isspace())
    hashes = r"#" * level
    pattern = re.compile(
        r"^\s*" + hashes + r"\s+.*?" + spaced,
        re.IGNORECASE | re.MULTILINE,
    )
    return pattern.search(text) is not None
