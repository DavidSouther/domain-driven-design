"""Shared utilities for structural checker scripts.

Each checker reads a candidate from stdin, applies ordered rules, and either
exits 0 (all rules hold) or exits 1 with a single-line reason on stdout. stderr
is never written to so the eval runner records Fail, not Errored.

`extract_code` understands two output envelopes:

1. Markdown fenced blocks (```ts ... ```).
2. Simulated agentic tool calls — `"file_contents": "<escaped source>"` emitted by
   a `write_file`/`create_file` the model narrates instead of printing a fence.
   The rich coding-agent AGENTS.md in this harness primes the model to *act*, so
   it frequently writes files this way; without unescaping that JSON the checker
   would score the surrounding prose (or a partial trailing fence) and miss the
   real code. Both envelopes are collected and concatenated so the rules always
   see every line of source the model actually produced, in whichever shape.
"""

import json
import re
import sys

FENCE = re.compile(r"```[^\n]*\n(.*?)```", re.DOTALL)
# `"file_contents": "<json-string-body>"`, allowing escaped quotes/backslashes.
FILE_CONTENTS = re.compile(
    r'"(?:file_contents|contents|content|code|new_str|new_string)"\s*:\s*"((?:[^"\\]|\\.)*)"'
)


def _unescape(body: str) -> str:
    """Decode a JSON string body (`\\n`, `\\"`, `\\t`, `\\uXXXX`, …) to source."""
    try:
        return json.loads('"' + body + '"')
    except (ValueError, json.JSONDecodeError):
        return (
            body.replace("\\n", "\n")
            .replace("\\t", "\t")
            .replace('\\"', '"')
            .replace("\\\\", "\\")
        )


def extract_code(src: str) -> str:
    """Return all code the model produced, joined together.

    Collects markdown fenced blocks and tool-call `file_contents` payloads. The
    runner pipes the whole assistant message (prose, tables, fenced code, tool
    calls); validate the code, not the explanation. Falls back to the whole
    input when neither envelope is present.
    """
    blocks = FENCE.findall(src)
    blocks += [_unescape(m) for m in FILE_CONTENTS.findall(src)]
    return "\n".join(blocks) if blocks else src


def strip_comments(src: str) -> str:
    """Remove block and line comments so comment prose cannot satisfy a rule.

    `://` (URLs) is preserved via the negative lookbehind on `//`.
    """
    src = re.sub(r"/\*.*?\*/", " ", src, flags=re.DOTALL)
    src = re.sub(r"(?<!:)//[^\n]*", " ", src)
    return src


def fail(reason: str) -> int:
    """Write a single-line reason to stdout and return exit code 1.

    Leaves stderr untouched so the runner records Fail, not Errored.
    """
    sys.stdout.write(reason + "\n")
    return 1
