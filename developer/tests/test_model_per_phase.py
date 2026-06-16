#!/usr/bin/env python3
"""Feature test: per-phase model selection in the Ailly developer skills.

The acceptance behavior is what a developer sees on entering each phase: the
skill announces the recommended model for the active provider and how to switch
with `/model`, then continues regardless. Behavior-level verification (invoking
a skill and grading the model's words) belongs to the out-of-scope, single-model,
nondeterministic e2e invocation harness. The runnable "done" signal for this
editorial change is a contract check on the source of truth: the four phase
skill bodies plus the shared reference file.

This is the design's one feature test. It runs end-to-end over the real files,
needs no model and no pytest, and exits 0 (all rules hold) or 1 with a single
reason line on stdout. It starts RED: today no phase skill names a model and
`developer/references/model-per-phase.md` does not exist.
"""

import re
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
DEV = REPO / "developer"
REFERENCE = DEV / "references" / "model-per-phase.md"

# The four primary phases that get an announce-line recommendation. Each must
# name the Anthropic model AND its effort/thinking qualifier verbatim (per the
# design's "qualifiers carried verbatim" contract). `qualifiers` is a list of
# alternative spellings; at least one must appear. The implementation qualifier
# (1M context) is what distinguishes the plan and implementation announce lines,
# which both otherwise name Sonnet 4.6.
PHASE_SKILLS = {
    "research": {"model": "Haiku 4.5", "qualifiers": ["thinking"]},
    "design": {"model": "Opus 4.8", "qualifiers": ["max effort"]},
    "plan": {"model": "Sonnet 4.6", "qualifiers": ["high effort"]},
    "red-green-refactor": {"model": "Sonnet 4.6", "qualifiers": ["1m", "1M ctx", "1M context"]},
}

# Rows and columns the reference table must carry.
TABLE_PHASES = ["Research", "Design", "Planning", "Implementation", "Cleanup"]
TABLE_PROVIDERS = ["Anthropic", "OpenAI", "Open Source"]

ANNOUNCE = re.compile(r"\*\*Announce at start:\*\*.*", re.IGNORECASE)


def fail(reason: str) -> int:
    print(reason)
    return 1


def announce_line(text: str) -> str:
    m = ANNOUNCE.search(text)
    return m.group(0) if m else ""


def main() -> int:
    # R1 — the shared reference file exists.
    if not REFERENCE.is_file():
        return fail(
            f"R1 reference required: {REFERENCE.relative_to(REPO)} does not exist; "
            "it must hold the phase x provider table and the /model switch protocol"
        )
    ref = REFERENCE.read_text()

    # R2 — the reference carries every phase row and provider column.
    missing_rows = [p for p in TABLE_PHASES if p.lower() not in ref.lower()]
    if missing_rows:
        return fail(
            "R2 reference table rows: missing phase row(s) " + ", ".join(missing_rows)
        )
    missing_cols = [p for p in TABLE_PROVIDERS if p.lower() not in ref.lower()]
    if missing_cols:
        return fail(
            "R2 reference table columns: missing provider column(s) "
            + ", ".join(missing_cols)
        )

    # R3 — the reference documents the /model switch protocol.
    if "/model" not in ref:
        return fail(
            "R3 switch protocol: reference does not mention the `/model` command"
        )

    # R4 — each phase skill's announce line carries the recommended model, its
    # qualifier verbatim, the /model switch path, and a pointer to the reference.
    for skill, spec in PHASE_SKILLS.items():
        model = spec["model"]
        qualifiers = spec["qualifiers"]
        body_path = DEV / "skills" / skill / "SKILL.md"
        if not body_path.is_file():
            return fail(f"R4 {skill}: {body_path.relative_to(REPO)} not found")
        line = announce_line(body_path.read_text())
        if not line:
            return fail(f"R4 {skill}: no `Announce at start` line found")
        low = line.lower()
        if model.lower() not in low:
            return fail(
                f"R4 {skill}: announce line does not name the recommended model "
                f"({model})"
            )
        if not any(q.lower() in low for q in qualifiers):
            return fail(
                f"R4 {skill}: announce line does not carry the effort/thinking "
                f"qualifier verbatim (expected one of {qualifiers})"
            )
        if "/model" not in line:
            return fail(
                f"R4 {skill}: announce line does not invite a `/model` switch"
            )
        if "model-per-phase" not in line:
            return fail(
                f"R4 {skill}: announce line does not point to the "
                "model-per-phase reference"
            )

    print("PASS: per-phase model selection contract holds")
    return 0


if __name__ == "__main__":
    sys.exit(main())
