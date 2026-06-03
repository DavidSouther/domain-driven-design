#!/usr/bin/env python3
"""Structural checker for the `domain:domain-model` invocation case.

Rules, each tracing to the domain-model SKILL.md "Record the Domain Map":
- R1 subdomains table: a Markdown table that has a Classification column.
- R2 classification labels: at least two of Core / Generic / Supporting appear
       (the skill classifies every context as one of the three).
- R3 boundary map: a "Boundary Map" section heading.
- R4 per-context block: at least one bounded-context block with a
       `**Responsibilities:**` field (the per-context file format).
- R5 draft marker: `[DRAFT]` ("Mark all newly created files as **[DRAFT]**").
"""

import re

from _checker_utils import decoded_artifacts, fail, has_draft_marker, read_candidate


def main() -> int:
    text = decoded_artifacts(read_candidate())

    # R1 — a Markdown table with a Classification column header.
    table_row = re.search(r"^\s*\|.*classification.*\|", text, re.IGNORECASE | re.MULTILINE)
    if table_row is None:
        return fail(
            "R1 subdomains table: no Markdown table with a 'Classification' "
            "column; the subdomains table is the skill's core artifact"
        )

    # R2 — classification labels present.
    labels = [
        label
        for label in ("Core", "Generic", "Supporting")
        if re.search(r"\b" + label + r"\b", text)
    ]
    if len(labels) < 2:
        return fail(
            "R2 classification labels: fewer than two of Core / Generic / "
            f"Supporting appear (found {labels}); contexts are not classified"
        )

    # R3 — Boundary Map section.
    if not re.search(r"boundary\s*map", text, re.IGNORECASE):
        return fail(
            "R3 boundary map: no 'Boundary Map' section describing what flows "
            "between contexts"
        )

    # R4 — at least one per-context block.
    if re.search(r"\*\*\s*Responsibilities\s*:?\s*\*\*", text, re.IGNORECASE) is None:
        return fail(
            "R4 per-context block: no `**Responsibilities:**` field; the "
            "per-bounded-context block was not produced"
        )

    # R5 — draft marker.
    if not has_draft_marker(text):
        return fail(
            "R5 draft marker: no `[DRAFT]` marker; newly created domain files "
            "must be marked DRAFT"
        )

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
