#!/usr/bin/env python3
"""Structural checker for the `domain:glossary` invocation case.

Rules, each tracing to the glossary SKILL.md "Glossary File Format" / "Rules":
- R1 term heading: a level-2 heading naming the term `OrderManifest`.
- R2 Definition: a `**Definition:**` field with a real (non-placeholder) value.
- R3 Context: a `**Context:**` field with a real value.
- R4 Source: a `**Source:**` field with a real value
       ("Every entry must include Definition, Context, and Source").
- R5 Synonyms: a `**Synonyms:**` field listing both named synonyms
       ("manifest" and "shipment list") — the prompt supplied synonyms, and the
       skill says include Synonyms only when synonyms exist.
- R6 draft marker: `[DRAFT]` ("Terms not confirmed by a domain expert must be
       marked **[DRAFT]**").
"""

import sys

from _checker_utils import (
    decoded_artifacts,
    field_has_real_value,
    field_value,
    fail,
    has_draft_marker,
    has_heading,
    read_candidate,
)


def main() -> int:
    text = decoded_artifacts(read_candidate())

    # R1 — term heading.
    if not has_heading(text, "OrderManifest", level=2):
        return fail(
            "R1 term heading: no level-2 heading naming the term `OrderManifest`"
        )

    # R2 — Definition with a real value.
    if not field_has_real_value(text, "Definition"):
        return fail(
            "R2 Definition: missing `**Definition:**` field or it still holds a "
            "`<placeholder>`"
        )

    # R3 — Context with a real value.
    if not field_has_real_value(text, "Context"):
        return fail(
            "R3 Context: missing `**Context:**` field or it still holds a "
            "`<placeholder>`"
        )

    # R4 — Source with a real value.
    if not field_has_real_value(text, "Source"):
        return fail(
            "R4 Source: missing `**Source:**` field; every entry must record a "
            "source"
        )

    # R5 — Synonyms listing both named synonyms.
    synonyms = field_value(text, "Synonyms")
    if synonyms is None:
        return fail(
            "R5 Synonyms: missing `**Synonyms:**` field; the prompt named two "
            "interchangeable terms that must be recorded as synonyms"
        )
    lowered = synonyms.lower()
    if "manifest" not in lowered or "shipment list" not in lowered:
        return fail(
            "R5 Synonyms: the `**Synonyms:**` field does not list both "
            '"manifest" and "shipment list"'
        )

    # R6 — draft marker.
    if not has_draft_marker(text):
        return fail(
            "R6 draft marker: no `[DRAFT]` marker; an unconfirmed term must be "
            "marked DRAFT until human-approved"
        )

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
