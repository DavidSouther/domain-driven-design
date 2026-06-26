#!/usr/bin/env python3
"""Feature test: per-phase model selection in the Ailly developer skills.

The acceptance behavior is what a developer sees on entering each phase: the
skill announces the recommended model **for the active provider** and how to
switch with `/model`, then continues regardless. Behavior-level verification
(invoking a skill and grading the model's words) belongs to the out-of-scope,
single-model, nondeterministic e2e invocation harness. The runnable "done"
signal for this editorial change is a contract check on the source of truth:
the shared reference table plus the four phase skill bodies.

Provider neutrality is part of the contract. The recommended model differs by
provider (Anthropic / OpenAI / Open Source), so the verbatim model names and
their qualifiers live in the reference table, not baked into the announce lines.
Each announce line defers to the table and selects by the active provider; it
must NOT hardcode a single provider's model.

This is the design's one feature test. It runs end-to-end over the real files,
needs no model and no pytest, and exits 0 (all rules hold) or 1 with a single
reason line on stdout.
"""

import re
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
DEV = REPO / "developer"
REFERENCE = DEV / "skills" / "ailly" / "references" / "checks" / "model-per-phase.md"

# The four primary phases that get an announce-line recommendation. The verbatim
# Anthropic model AND its effort/thinking qualifier must appear in that phase's
# reference-table row (the source of truth). `qualifiers` is a list of alternative
# spellings; at least one must appear. The implementation qualifier (1M context)
# is what distinguishes the Planning and Implementation rows, which both name
# Sonnet 4.6.
PHASE_ROWS = {
    "Research": {"model": "Haiku 4.5", "qualifiers": ["thinking"]},
    "Design": {"model": "Opus 4.8", "qualifiers": ["max effort"]},
    "Planning": {"model": "Sonnet 4.6", "qualifiers": ["high effort"]},
    "Implementation": {"model": "Sonnet 4.6", "qualifiers": ["1m", "1M ctx", "1M context"]},
}

# Phase reference bodies whose announce lines must defer to the table by provider.
# Post-consolidation the phases are coordinator references, not standalone skills, so
# their announce lines live under skills/ailly/references/phases/<phase>.md.
PHASE_SKILLS = ["research", "design", "plan", "red-green-refactor"]
PHASE_REF_DIR = DEV / "skills" / "ailly" / "references" / "phases"

# Announce lines must not hardcode any single provider's model name.
HARDCODED_MODELS = ["Haiku 4.5", "Opus 4.8", "Sonnet 4.6", "o4-mini", "GPT-4.1", "Llama"]

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


def table_row(ref: str, phase: str) -> str:
    """Return the markdown table row whose first cell is `phase`, else ''."""
    for line in ref.splitlines():
        cells = [c.strip() for c in line.split("|")]
        # A data row looks like ['', 'Research', 'Haiku 4.5 (thinking)', ...].
        if len(cells) >= 3 and cells[1].lower() == phase.lower():
            return line
    return ""


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

    # R4 — the source of truth: each phase's reference-table row names the
    # Anthropic model and its qualifier verbatim.
    for phase, spec in PHASE_ROWS.items():
        row = table_row(ref, phase)
        if not row:
            return fail(f"R4 {phase}: no reference-table row found for the phase")
        low = row.lower()
        if spec["model"].lower() not in low:
            return fail(
                f"R4 {phase}: table row does not name the Anthropic model "
                f"({spec['model']})"
            )
        if not any(q.lower() in low for q in spec["qualifiers"]):
            return fail(
                f"R4 {phase}: table row does not carry the effort/thinking qualifier "
                f"verbatim (expected one of {spec['qualifiers']})"
            )

    # R5 — each phase announce line is provider-parametric: it defers to the table,
    # selects by the active provider, invites a `/model` switch, and does NOT
    # hardcode any single provider's model name.
    for skill in PHASE_SKILLS:
        body_path = PHASE_REF_DIR / f"{skill}.md"
        if not body_path.is_file():
            return fail(f"R5 {skill}: {body_path.relative_to(REPO)} not found")
        line = announce_line(body_path.read_text())
        if not line:
            return fail(f"R5 {skill}: no `Announce at start` line found")
        low = line.lower()
        if "provider" not in low:
            return fail(
                f"R5 {skill}: announce line is not provider-parametric (must select "
                "the model for the active provider, not assume one)"
            )
        if "model-per-phase" not in low:
            return fail(
                f"R5 {skill}: announce line does not point to the model-per-phase "
                "reference table"
            )
        if "/model" not in line:
            return fail(f"R5 {skill}: announce line does not invite a `/model` switch")
        hardcoded = [m for m in HARDCODED_MODELS if m.lower() in low]
        if hardcoded:
            return fail(
                f"R5 {skill}: announce line hardcodes provider-specific model name(s) "
                f"{hardcoded}; it must defer to the table by provider"
            )

    print("PASS: per-phase model selection contract holds")
    return 0


if __name__ == "__main__":
    sys.exit(main())
