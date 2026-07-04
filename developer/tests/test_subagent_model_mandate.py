#!/usr/bin/env python3
"""Feature test: subagent model mandate for Ailly's developer subagent dispatch.

The primary user story (design.md, "User Journey and Metrics"): a developer
running `developer:ailly` on any supported harness enters or resumes a phase.
The coordinator dispatches it (and any sub-step the phase body describes)
through that harness's subagent mechanism, consulting one general-purpose,
complexity-dimension-organized reference (not an Ailly-only, phase-keyed
table). Every such dispatch follows mandate-with-announce: if the harness's
dispatch call exposes a way to set the model, it sets it (an alias, not a
dated version); either way, it announces the model chosen. This holds
uniformly across harnesses — the rule degrades to announce-only wherever no
mechanism is confirmed, with no per-harness special case required. The
guidance itself keeps one dated "principle -> example" table, stamped so it
reads as a snapshot rather than a durable contract, and `DEVELOPMENT.md`
carries a matching maintenance nudge.

This test deliberately does not touch `test_model_per_phase.py` or
`test_phase_guardrails.py`. Both encode the pre-issue contract and are slated
for retirement, not in-place edits (design.md Specification item 10) — that
retirement is Plan-phase work, sequenced separately from this new test.

Like those two, this is a contract check on the source of truth: the
general-purpose reference, the coordinator skill body, and `DEVELOPMENT.md`.
It needs no model and no pytest, and exits 0 (all rules hold) or 1 with a
single reason line on stdout. It starts RED: today no file under `general/`
carries this guidance, `ailly/SKILL.md`'s Phase Isolation section does not
mention setting or announcing a model or dispatching within a phase, and
`DEVELOPMENT.md` has no maintenance nudge.
"""

import re
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
DEV = REPO / "developer"
GENERAL = REPO / "general"
AILLY = DEV / "skills" / "ailly" / "SKILL.md"
DEVELOPMENT = REPO / "DEVELOPMENT.md"

# The dated version pins the pre-issue table hardcoded. New guidance must not
# repeat them as its durable recommendation.
STALE_MODEL_NAMES = ["Haiku 4.5", "Opus 4.8", "Sonnet 4.6"]

# The complexity-dimension axes research surfaced; the guidance must key on
# at least one of these rather than organizing solely by Ailly phase name.
COMPLEXITY_TERMS = [
    "complexity dimension",
    "reasoning depth",
    "constraint",
    "domain specificity",
    "generation-vs-evaluation",
    "generation vs evaluation",
    "generation/evaluation",
]


def fail(reason: str) -> int:
    print(reason)
    return 1


def find_general_model_guidance():
    """Return (path, text) of the first general/**/*.md file that reads like
    subagent model-selection guidance, else (None, "")."""
    if not GENERAL.is_dir():
        return None, ""
    for path in sorted(GENERAL.rglob("*.md")):
        text = path.read_text()
        low = text.lower()
        if "model" not in low or "alias" not in low:
            continue
        if any(t in low for t in ("subagent", "dispatch", "select", "selection")):
            return path, text
    return None, ""


def section(text: str, heading_re: str) -> str:
    """Return the body of the `##` section whose heading matches, up to the
    next `##` heading (case-insensitive), or "" if not found."""
    m = re.search(rf"(?ims)^##\s+{heading_re}\s*$(.*?)(?=^##\s+|\Z)", text)
    return m.group(1) if m else ""


def main() -> int:
    # T1 - a general/ home for subagent model-selection guidance exists,
    # using alias language, and organizes by complexity dimension rather than
    # solely by Ailly phase name.
    path, text = find_general_model_guidance()
    if not path:
        return fail(
            "T1 general home: no file under general/ carries subagent "
            "model-selection guidance (expected alias language plus a "
            "subagent/dispatch/selection keyword)"
        )
    low = text.lower()
    if not any(t in low for t in COMPLEXITY_TERMS):
        return fail(
            f"T1 organization: {path.relative_to(REPO)} does not organize by "
            "any complexity-dimension term (e.g. 'reasoning depth', "
            "'constraint', 'domain specificity', 'generation-vs-evaluation'); "
            "the guidance must key on complexity dimension, not phase name alone"
        )

    # T2 - the guidance does not hardcode a stale, dated model version name
    # as its durable recommendation.
    stale = [m for m in STALE_MODEL_NAMES if m.lower() in low]
    if stale:
        return fail(
            f"T2 staleness: {path.relative_to(REPO)} still hardcodes dated "
            f"model version name(s) {stale}"
        )

    # T3 - the guidance keeps exactly one dated example table, stamped so a
    # reader knows it is a snapshot (resolves table-vs-principle).
    if "2026-07-03" not in text and "as of" not in low:
        return fail(
            f"T3 dated example: {path.relative_to(REPO)} does not carry a "
            "visibly dated ('as of ...') example table"
        )

    # T4 - DEVELOPMENT.md carries a maintenance nudge for that dated table.
    if not DEVELOPMENT.is_file():
        return fail(f"T4 {DEVELOPMENT.relative_to(REPO)} not found")
    development_low = DEVELOPMENT.read_text().lower()
    if not any(t in development_low for t in ("model", "example table")) or not any(
        t in development_low for t in ("periodic", "check whether", "review")
    ):
        return fail(
            f"T4 maintenance nudge: {DEVELOPMENT.relative_to(REPO)} does not "
            "prompt periodic review of the dated model-selection example table"
        )

    # T5 - the coordinator's Phase Isolation section documents mandate-with-
    # announce: setting the model when the mechanism exists, AND announcing
    # the choice either way (not silent mandate, not announce-only).
    if not AILLY.is_file():
        return fail(f"T5 {AILLY.relative_to(REPO)} not found")
    ailly = AILLY.read_text()
    isolation = section(ailly, "Phase Isolation")
    if not isolation:
        return fail(
            f"T5 coordinator: no `## Phase Isolation` section found in "
            f"{AILLY.relative_to(REPO)}"
        )
    iso_low = isolation.lower()
    if "model" not in iso_low:
        return fail(
            "T5 mandate: the Phase Isolation section does not mention the "
            "subagent's model at all"
        )
    mandates = any(
        t in iso_low
        for t in ("set the model", "sets the model", "mandate", "model=", "model parameter", "model argument")
    )
    announces = "announce" in iso_low
    if not (mandates and announces):
        return fail(
            "T5 mandate-with-announce: the Phase Isolation section must both "
            "document actively setting the subagent's model where the "
            "mechanism exists AND announcing the choice, not one alone"
        )

    # T6 - the mandate is unconditional: the general home must be loaded on
    # every dispatch, not situationally.
    if not any(t in iso_low for t in ("unconditional", "every dispatch", "every subagent dispatch")):
        return fail(
            "T6 unconditional load: the Phase Isolation section does not "
            "state that the general model-selection reference is loaded on "
            "every subagent dispatch, unconditionally"
        )

    # T7 - the mandate reaches sub-steps described within a phase's own body,
    # not only the phase's single top-level dispatch.
    if not any(t in iso_low for t in ("within a phase", "within the phase", "sub-step", "inside a phase")):
        return fail(
            "T7 within-phase mandate: the Phase Isolation section does not "
            "extend the subagent mandate to sub-steps described inside a "
            "phase's own body, only to the phase's top-level dispatch"
        )

    print("PASS: subagent model mandate contract holds")
    return 0


if __name__ == "__main__":
    sys.exit(main())
