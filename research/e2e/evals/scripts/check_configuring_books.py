#!/usr/bin/env python3
"""Structural checker for the `configuring-books` invocation case.

Rules trace to configuring-books/SKILL.md "Configure Checklist", "Contract"
(typed Not-Available), and the etiquette (keyless sources, User-Agent):
- R1 names at least three default sources (Open Library, Gutendex / Gutenberg,
  Internet Archive, Google Books).
- R2 the four-stage wiring is visible: MCP probe, HTTP fallback, smoke-test.
- R3 the typed Not-Available routing signal for unconfigured optional sources.
- R4 at least one source is correctly called out as keyless (Gutendex /
  Internet Archive need no credentials).
- R5 the Open Library polite User-Agent is named.
"""

import re
import sys

from _md import candidate, count_present, fail

SOURCES = ["Open Library", "Gutendex", "Gutenberg", "Internet Archive", "Google Books"]
KEYLESS = ["keyless", "no key", "no api key", "no credentials", "none required", "no account"]


def not_available_routing(low: str) -> bool:
    if "not-available" in low:
        return True
    if "not available" in low and any(w in low for w in ("routing", "signal", "typed")):
        return True
    return False


def main() -> int:
    text = candidate()
    low = text.lower()

    present = count_present(text, SOURCES)
    if present < 3:
        return fail(
            f"R1 default sources: only {present} of Open Library, Gutendex/Gutenberg, "
            "Internet Archive, Google Books named; the checklist covers the default stack"
        )

    stages = {
        "MCP probe": "mcp" in low,
        "HTTP fallback": "fallback" in low or "http" in low,
        "smoke-test": "smoke" in low,
    }
    missing = [name for name, ok in stages.items() if not ok]
    if missing:
        return fail(
            f"R2 wiring stages: missing {', '.join(missing)}; each source probes an "
            "MCP, falls back to HTTP, and smoke-tests the capability"
        )

    if not not_available_routing(low):
        return fail(
            "R3 Not-Available routing: no typed Not-Available result for unconfigured "
            "optional sources; the practice skill treats it as a routing signal"
        )

    if not any(k in low for k in KEYLESS):
        return fail(
            "R4 keyless sources: no source called out as needing no key (Gutendex and "
            "Internet Archive are keyless); the wiring distinguishes keyed from keyless"
        )

    if not any(t in low for t in ("user-agent", "user agent", "user_agent")):
        return fail(
            "R5 Open Library etiquette: the polite User-Agent (with a contact email) "
            "is not named; it is required for Open Library"
        )

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
