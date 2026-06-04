#!/usr/bin/env python3
"""Structural checker for the `configuring-papers` invocation case.

Rules trace to configuring-papers/SKILL.md "Configure Checklist", "Contract"
(typed Not-Available), and the etiquette env vars:
- R1 names at least four default sources (Crossref, Unpaywall, OpenAlex,
  Semantic Scholar, ArXiv).
- R2 the four-stage wiring per source is visible: MCP probe, HTTP fallback,
  credential/env, smoke-test.
- R3 the typed Not-Available routing signal for unconfigured optional sources.
- R4 at least one exact etiquette env var (CROSSREF_MAILTO, UNPAYWALL_EMAIL,
  OPENALEX_API_KEY, SEMANTIC_SCHOLAR_API_KEY, CORE_API_KEY).
"""

import re
import sys

from _md import candidate, count_present, fail

SOURCES = ["Crossref", "Unpaywall", "OpenAlex", "Semantic Scholar", "ArXiv"]
ENV_VARS = re.compile(
    r"CROSSREF_MAILTO|UNPAYWALL_EMAIL|OPENALEX_API_KEY|SEMANTIC_SCHOLAR_API_KEY|CORE_API_KEY"
)


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
    if present < 4:
        return fail(
            f"R1 default sources: only {present}/5 of Crossref, Unpaywall, OpenAlex, "
            "Semantic Scholar, ArXiv named; the checklist covers the default stack"
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
            "MCP, falls back to HTTP, sets credentials, and smoke-tests the capability"
        )

    if not not_available_routing(low):
        return fail(
            "R3 Not-Available routing: no typed Not-Available result for unconfigured "
            "optional sources; the practice skill treats it as a routing signal"
        )

    if not ENV_VARS.search(text):
        return fail(
            "R4 etiquette env vars: no exact env var named (e.g. CROSSREF_MAILTO, "
            "OPENALEX_API_KEY); polite-pool and key etiquette is part of the wiring"
        )

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
