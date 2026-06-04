#!/usr/bin/env python3
"""Structural checker for the `internal` invocation case.

Rules trace to internal/SKILL.md "Strategy", "Output Format", and the
"Searching without discovering" common mistake:
- R1 research-note path convention `docs/research/<dated-dir>/internal.md`.
- R2 a Sources section.
- R3 the discover-before-search step: name `ListMcpResourcesTool`, or otherwise
  describe discovering which MCP servers are available before searching.
- R4 names at least one internal source type (Slack, Confluence, Notion,
  Linear, Jira, GitHub, Google Drive) as a place queried.
"""

import re
import sys

from _md import candidate, count_present, fail

PATH = re.compile(r"docs/research/\d{4}-\d{2}-\d{2}-[\w-]+/internal\.md")
SERVERS = ["Slack", "Confluence", "Notion", "Linear", "Jira", "GitHub", "Google Drive"]


def discovers(low: str) -> bool:
    if "listmcpresourcestool" in low:
        return True
    if "mcp" in low and any(w in low for w in ("discover", "available", "which mcp")):
        return True
    return False


def main() -> int:
    text = candidate()
    low = text.lower()

    if not PATH.search(text):
        return fail(
            "R1 path convention: no `docs/research/<YYYY-MM-DD-A-topic>/internal.md` "
            "path; the skill writes findings to that dated research-note path"
        )

    if not re.search(r"(^|\n)\s*#{1,3}\s*Sources|\*\*Sources\*\*", text, re.IGNORECASE):
        return fail(
            "R2 note structure: no Sources section; the internal note lists which MCP "
            "servers and documents/threads/tickets were consulted"
        )

    if not discovers(low):
        return fail(
            "R3 discover-before-search: no MCP discovery step (ListMcpResourcesTool / "
            "discovering which servers are available); the skill discovers first"
        )

    if count_present(text, SERVERS) < 1:
        return fail(
            "R4 internal sources: no internal source type named (Slack, Confluence, "
            "Notion, Linear, Jira, GitHub, Google Drive) as a place queried"
        )

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
