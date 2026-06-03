#!/usr/bin/env python3
"""Structural checker for the `domain:ubiquitous-language` invocation case.

Rules, each tracing to the ubiquitous-language SKILL.md "Output" / process:
- R1 candidate terms: the named candidate terms appear (at least three of the
       five from the prompt), evidence of a candidate-terms list.
- R2 source recorded: a per-term "Source" is present ("The source is required
       in the output").
- R3 question buckets: BOTH categorized question headings appear — "Ask a
       domain expert" and "Confirm with domain expert" (the two-bucket
       categorization is the skill's distinguishing output).
- R4 draft marker: `[DRAFT]` ("Mark all generated terms as **[DRAFT]**").
"""

import re

from _checker_utils import decoded_artifacts, fail, has_draft_marker, read_candidate

PROMPT_TERMS = ["OrderManifest", "Carrier", "Waybill", "Consignee", "LinearFeet"]


def main() -> int:
    text = decoded_artifacts(read_candidate())
    lowered = text.lower()

    # R1 — candidate terms present.
    present = [t for t in PROMPT_TERMS if t.lower() in lowered]
    if len(present) < 3:
        return fail(
            "R1 candidate terms: fewer than three of the prompt's candidate "
            f"terms appear (found {present}); no candidate-terms list was produced"
        )

    # R2 — a source is recorded for the candidate terms.
    if "source" not in lowered:
        return fail(
            "R2 source recorded: no 'Source' appears; each candidate term must "
            "record its research source"
        )

    # R3 — both question buckets.
    ask = re.search(r"ask\b.{0,20}\bdomain expert", lowered, re.DOTALL)
    confirm = re.search(r"confirm\b.{0,20}\bdomain expert", lowered, re.DOTALL)
    if ask is None or confirm is None:
        missing = []
        if ask is None:
            missing.append('"Ask … domain expert"')
        if confirm is None:
            missing.append('"Confirm … domain expert"')
        return fail(
            "R3 question buckets: missing categorized question heading(s): "
            + ", ".join(missing)
        )

    # R4 — draft marker.
    if not has_draft_marker(text):
        return fail(
            "R4 draft marker: no `[DRAFT]` marker; all generated terms must be "
            "marked DRAFT"
        )

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
