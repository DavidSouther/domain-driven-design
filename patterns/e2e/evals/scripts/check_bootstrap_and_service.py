#!/usr/bin/env python3
"""Structural checker for `patterns:bootstrap-and-service` invocation cases.

Reads a TypeScript candidate from stdin and applies ordered rules tracing to the
bootstrap-and-service SKILL.md "Common Mistakes" section. First violated rule prints
a single-line reason to stdout and exits 1; all holding exits 0. stderr untouched.

Rules:
- R1 an application service layer exists, distinct from the HTTP handler.
- R2 the service knows no protocol — its definition references no HTTP request/
  response/status types ("Protocol knowledge in services").
- R3 a single composition root constructs the concretes and injects them
  ("Scattered wiring").
"""

import re
import sys

from _checker_utils import extract_code, fail, strip_comments

HTTP_TOKENS = re.compile(
    r"\b(?:Request|Response|Req|Res)\b|\bres\s*\.|\breq\s*\.|\breply\s*\.|\.\s*status\s*\(|res\.json"
)


def service_block(src: str) -> str:
    """Return the `class *Service { ... }` block, or '' if the service is not a class."""
    m = re.search(r"\bclass\s+\w*Service\b[^{]*\{", src)
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

    # R1 — a service layer distinct from the handler.
    if not re.search(r"\b(?:class|interface|const|function)\s+\w*Service\b", src):
        return fail(
            "R1 application service: no `*Service` layer; extract the use case from the "
            "HTTP handler into a service that orchestrates domain + ports"
        )

    # R2 — the service speaks no protocol.
    block = service_block(src)
    if block and HTTP_TOKENS.search(block):
        return fail(
            "R2 protocol in the service: the `*Service` references HTTP "
            "request/response/status; a service that accepts `Request` or returns "
            "status codes cannot be reused across adapters — keep protocol in the "
            "adapter"
        )

    # R3 — a single composition root constructs concretes and injects them.
    constructs_repo = re.search(r"\bnew\s+\w*(?:Repository|Repo|Store|Db|Client)\s*\(", src)
    injects_service = re.search(r"\bnew\s+\w*Service\s*\(", src)
    if not (constructs_repo and injects_service):
        return fail(
            "R3 composition root: no single place that constructs the concrete "
            "repository and injects it into the service (`new *Repository(...)` then "
            "`new *Service(repo)`); wire concretes once at startup, not scattered"
        )

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
