#!/usr/bin/env python3
"""Structural checker for the `public` invocation case.

Rules trace to public/SKILL.md "Output Format":
- R1 research-note path convention `docs/research/<dated-dir>/public.md`.
- R2 a `## Sources` section.
- R3 at least one markdown-link citation to a URL — the public skill cites with
  `[Title](url)` links, not bare text.
"""

import re
import sys

from _md import candidate, fail

PATH = re.compile(r"docs/research/\d{4}-\d{2}-\d{2}-[\w-]+/public\.md")
MD_LINK = re.compile(r"\[[^\]]+\]\(https?://[^)]+\)")


def main() -> int:
    text = candidate()

    if not PATH.search(text):
        return fail(
            "R1 path convention: no `docs/research/<YYYY-MM-DD-A-topic>/public.md` "
            "path; the skill writes findings to that dated research-note path"
        )

    if "## Sources" not in text:
        return fail(
            "R2 note structure: missing a `## Sources` section listing the URLs "
            "consulted"
        )

    if not MD_LINK.search(text):
        return fail(
            "R3 markdown-link citations: no `[Title](url)` link; the public skill cites "
            "open-internet sources as markdown links"
        )

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
