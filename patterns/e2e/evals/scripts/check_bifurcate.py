#!/usr/bin/env python3
"""Structural checker for `patterns:bifurcate` invocation cases.

Reads the full assistant message from stdin and applies ordered rules tracing to
the bifurcate reference "Common Mistakes" section. First violated rule prints a
single-line reason to stdout and exits 1; all holding exits 0. stderr untouched.

Rules:
- R0 a test or probe snippet is present (fenced code or a test/function body).
- R1 two or more live hypotheses named explicitly.
- R2 a discriminating probe with predicted pass/fail (or two-outcome) partition.
- R3 the observation refutes one partition (falsification, not confirmation).
- R4 a second bifurcation step on the surviving space (recursive practice).
"""

import re
import sys

from _checker_utils import fail


def main() -> int:
    raw = sys.stdin.read()
    text = raw.lower()

    # R0 — a probe snippet exists (the invocation prompt requires a fence).
    if not re.search(r"```", raw):
        return fail(
            "R0 probe snippet: include a small test or probe in a code fence; "
            "prose alone is not a bifurcating observation"
        )

    # R1 — at least two hypotheses / causes / candidates.
    numbered = len(re.findall(r"^\s*\d+[\.)]\s+\S", raw, re.MULTILINE))
    hypothesis_markers = len(
        re.findall(
            r"\b(?:hypothes(?:is|es)|candidate|root cause|could be|plausible cause)\b",
            text,
        )
    )
    either_or = len(re.findall(r"\bor\b", text))
    if numbered < 2 and hypothesis_markers < 2 and either_or < 2:
        return fail(
            "R1 two hypotheses: name at least two live candidate causes explicitly "
            "before designing the probe"
        )

    # R2 — predicted partition: pass/fail or explicit outcome → which half survives.
    partition_patterns = [
        r"if\s+(?:pass|fail|true|false|success|error)",
        r"(?:pass(?:es|ing)?|fail(?:s|ing)?)\s*(?:→|=>|:|-)\s*\S",
        r"rules?\s+out",
        r"refute[sd]?",
        r"eliminate[sd]?",
        r"contradict",
        r"implicate[sd]?",
    ]
    if not any(re.search(p, text) for p in partition_patterns):
        return fail(
            "R2 predicted partition: state before running what each probe outcome "
            "(pass vs fail, or two explicit results) implies about which hypotheses "
            "survive"
        )

    # R3 — refute a partition after the observation.
    refute_patterns = [
        r"refute[sd]?",
        r"rules?\s+out",
        r"eliminate[sd]?",
        r"contradict(?:ed|s)?",
        r"discard(?:ed|s)?",
        r"not in (?:the )?(?:web server|job runner|first|second)",
        r"problem is (?:likely )?in",
        r"surviv(?:e|ing|es)",
        r"remaining (?:hypothes|cause|candidate|partition)",
    ]
    if not any(re.search(p, text) for p in refute_patterns):
        return fail(
            "R3 refute a partition: after the observation, say which hypothesis set "
            "the evidence refutes — do not merely restate both options"
        )

    # R4 — repeat bifurcation on the smaller space.
    repeat_patterns = [
        r"\b(?:repeat|again|second bifurc|next bifurc|bifurcate again)\b",
        r"smaller (?:section|space|partition|set|hypothesis)",
        r"until one cause",
        r"step\s*4",
        r"next (?:probe|checkpoint|split|bifurc)",
    ]
    if not any(re.search(p, text) for p in repeat_patterns):
        return fail(
            "R4 repeat: bifurcate again on the surviving partition (recursive "
            "practice — one split is rarely enough)"
        )

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
