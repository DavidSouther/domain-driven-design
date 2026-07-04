#!/usr/bin/env python3
"""Feature test: soft-block Fable 5 in the Ailly phase-entry model check.

The primary user story (design.md, "User Journey and Metrics"): a developer
running `developer:ailly` on a harness currently reporting `claude-fable-5`
as the active model triggers the coordinator's phase-entry Model check. The
check names Fable 5 as soft-blocked with a reason (it applies stored
feedback too literally, missing the intent behind a rule) and an un-block
condition (quality parity with Sonnet/Opus-tier judgment on that same
point), recommends switching via `/model`, and continues the loop either
way -- this is a check, not a gate. When the coordinator dispatches a phase
subagent, the soft-blocked model is not silently inherited; dispatch
prefers the phase table's recommended alias instead.

This test is a contract check on the two source-of-truth files (mirroring
`test_subagent_model_mandate.py`'s shape), not a live-model integration
test: `general/skills/dispatching-agents/model-selection.md` (the soft-block
list itself) and `developer/skills/ailly/SKILL.md` (the Model check bullet
that consults it and the dispatch behavior that must not inherit it
silently). It needs no model and no pytest, and exits 0 (all rules hold) or
1 with a single reason line on stdout.

It starts RED: today neither file mentions `claude-fable-5`, "Fable", or any
soft-block concept at all.
"""

import re
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
MODEL_SELECTION = REPO / "general" / "skills" / "dispatching-agents" / "model-selection.md"
AILLY = REPO / "developer" / "skills" / "ailly" / "SKILL.md"

# Names identifying the soft-blocked model. Either form is acceptable in
# prose; both must appear somewhere for the block to be discoverable by a
# developer scanning either the model name or its common nickname.
BLOCKED_MODEL_NAMES = ["claude-fable-5", "fable"]

# Dated version strings that must NOT appear in the soft-block wording --
# the file's own alias rule (and the sibling `test_subagent_model_mandate.py`
# T2 staleness check) forbids hardcoding a dated recommendation. The
# soft-block flag must recommend switching via bare alias instead.
STALE_MODEL_NAMES = ["sonnet 4.6", "opus 4.8", "haiku 4.5"]


def fail(reason: str) -> int:
    print(reason)
    return 1


def section(text: str, heading_re: str) -> str:
    """Return the body of the `##` section whose heading matches, up to the
    next `##` heading (case-insensitive), or "" if not found."""
    m = re.search(rf"(?ims)^##\s+{heading_re}\s*$(.*?)(?=^##\s+|\Z)", text)
    return m.group(1) if m else ""


def main() -> int:
    # T1 - model-selection.md exists and carries a distinct soft-block
    # section naming the blocked model by its identifier and its nickname.
    if not MODEL_SELECTION.is_file():
        return fail(f"T1 {MODEL_SELECTION} not found")
    ms_text = MODEL_SELECTION.read_text()
    ms_low = ms_text.lower()

    soft_block_section = section(ms_text, r"Soft-?Blocked Models?")
    if not soft_block_section:
        return fail(
            "T1 soft-block section: no `## Soft-Blocked Model(s)` heading "
            f"found in {MODEL_SELECTION.relative_to(REPO)}"
        )
    sb_low = soft_block_section.lower()
    missing_names = [n for n in BLOCKED_MODEL_NAMES if n not in sb_low]
    if missing_names:
        return fail(
            "T1 blocked-model identity: the Soft-Blocked Models section "
            f"does not name {missing_names}"
        )

    # T2 - the section states a reason (literal rule-following / missed
    # intent) and an un-block condition (quality parity), not just the name.
    reason_terms = ["literal", "intent", "judgment", "judgement"]
    if not any(t in sb_low for t in reason_terms):
        return fail(
            "T2 reason: the Soft-Blocked Models section does not explain "
            "why Fable 5 is blocked (expected language about literal "
            "rule-following vs. intent/judgment)"
        )
    parity_terms = ["parity", "quality parity", "comparable"]
    if not any(t in sb_low for t in parity_terms):
        return fail(
            "T2 un-block condition: the Soft-Blocked Models section does "
            "not state the condition for lifting the block (expected "
            "parity/comparable-quality language)"
        )

    # T3 - the flag recommends a switch, but only via bare alias, never a
    # dated pinned version -- this must never trip the sibling mandate
    # test's staleness check.
    if not any(t in sb_low for t in ("sonnet", "opus")):
        return fail(
            "T3 switch recommendation: the Soft-Blocked Models section does "
            "not recommend switching to `sonnet` or `opus`"
        )
    stale_hits = [s for s in STALE_MODEL_NAMES if s in sb_low]
    if stale_hits:
        return fail(
            "T3 alias-only: the Soft-Blocked Models section hardcodes a "
            f"dated version string {stale_hits}; it must use bare aliases "
            "only (sonnet/opus), matching this file's own alias rule"
        )

    # T4 - the coordinator's Model check bullet (ailly/SKILL.md) names the
    # soft block and keeps the existing check-not-gate language.
    if not AILLY.is_file():
        return fail(f"T4 {AILLY} not found")
    ailly_text = AILLY.read_text()
    ailly_low = ailly_text.lower()
    m = re.search(r"(?im)^-\s+\*\*model check\.\*\*.*$", ailly_text)
    if not m:
        return fail(
            f"T4 Model check bullet: no `**Model check.**` bullet found in "
            f"{AILLY.relative_to(REPO)}"
        )
    model_check_bullet = m.group(0)
    mc_low = model_check_bullet.lower()
    if "soft" not in mc_low or "block" not in mc_low:
        return fail(
            "T4 soft-block reference: the Model check bullet does not "
            "mention a soft block at all"
        )
    if "fable" not in mc_low:
        return fail(
            "T4 named model: the Model check bullet does not name Fable "
            "specifically when describing the soft block"
        )
    if "check, not a gate" not in mc_low and "check not a gate" not in mc_low:
        return fail(
            "T4 check-not-gate: the Model check bullet no longer states "
            "this remains a check, not a gate"
        )

    # T5 - dispatch does not silently inherit a soft-blocked model; it
    # prefers the phase table's recommended alias instead.
    inherit_terms = ["not inherit", "does not inherit", "not silently inherit"]
    prefer_terms = ["prefer", "recommended model", "recommended alias"]
    if not any(t in mc_low for t in inherit_terms) or not any(
        t in mc_low for t in prefer_terms
    ):
        return fail(
            "T5 no-silent-inheritance: the Model check bullet does not "
            "state that a dispatched phase subagent avoids silently "
            "inheriting a soft-blocked model in favor of the phase's "
            "recommended model/alias"
        )

    print("PASS: Fable 5 soft-block contract holds")
    return 0


if __name__ == "__main__":
    sys.exit(main())
