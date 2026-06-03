#!/usr/bin/env python3
"""Structural checker for the `domain:arrow-of-maturity` invocation case.

Rules, each tracing to the arrow-of-maturity SKILL.md "Output" / "Stages":
- R1 current stage: the assessment states which stage the codebase is at
       (Output part 1, "Current stage").
- R2 signal: the assessment names the signal/friction that justifies advancing
       or staying (Output part 2, "Signal").
- R3 next step: the assessment gives a next concrete step (Output part 3, "Next
       concrete step").
- R4 stage taxonomy: the assessment is framed in the Arrow's stage vocabulary —
       a stage code (Stage 1, 2a, 2b, 2c, 3) or a distinctive stage name
       (straight-through handler, extracted repository, event-sourced). Generic
       architecture words alone (domain model, repository, aggregate) do not
       satisfy this; the staged framing is the skill's distinguishing output.

No `[DRAFT]` rule: the arrow assessment is advisory output, not a `docs/ddd/`
artifact, so the skill does not mark it DRAFT.
"""

import re

from _checker_utils import decoded_artifacts, fail, read_candidate

STAGE_TAXONOMY = re.compile(
    r"\bstage\s*[0-3][abc]?\b"          # "Stage 1", "Stage 2a"
    r"|\b2[abc]\b"                       # bare substage codes 2a/2b/2c
    r"|straight[-\s]through"             # Stage 1 name
    r"|extracted\s+repository"           # Stage 2b name
    r"|event[-\s]sourc",                 # Stage 3 name (event-sourced/sourcing)
    re.IGNORECASE,
)


def main() -> int:
    text = decoded_artifacts(read_candidate())
    lowered = text.lower()

    # R1 — current stage stated.
    if "current stage" not in lowered and not re.search(
        r"\b(currently|today|right now)\b.{0,40}\bstage\b", lowered, re.DOTALL
    ):
        return fail(
            "R1 current stage: the assessment does not state which stage the "
            "codebase is currently at"
        )

    # R2 — signal / friction justifying the move.
    if not re.search(r"\b(signal|friction|trigger|justif)", lowered):
        return fail(
            "R2 signal: the assessment does not name the signal or friction that "
            "justifies advancing (or staying)"
        )

    # R3 — next concrete step.
    if re.search(r"\bnext\b.{0,40}\b(step|move|change|action)\b", lowered, re.DOTALL) is None \
       and re.search(r"^\s*#+.*\bnext\b", text, re.IGNORECASE | re.MULTILINE) is None:
        return fail(
            "R3 next step: the assessment does not give a next concrete step"
        )

    # R4 — Arrow stage taxonomy.
    if STAGE_TAXONOMY.search(text) is None:
        return fail(
            "R4 stage taxonomy: the assessment is not framed in the Arrow's stage "
            "vocabulary (a stage code like 2a/2b, or a stage name like "
            "straight-through handler / extracted repository / event-sourced)"
        )

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
