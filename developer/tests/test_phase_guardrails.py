#!/usr/bin/env python3
"""Feature test: phase-entry guardrails in the Ailly developer coordinator.

Two complementary phase-boundary disciplines share one acceptance behavior: at a
phase boundary the coordinator checks before proceeding and escalates to the human
rather than silently working around a problem.

- force-model-per-phase: the model check is *active* — detect the running model,
  compare it to the phase's recommended model, and flag a mismatch explicitly,
  while preserving the deliberate no-gate guarantee (the loop never stalls).
- fail-if-no-tools: when a declared project tool fails, be adamant (do not silently
  substitute another tool); first try local remediation via `developer:initialize`
  (e.g. `mise trust` / `npm install`), then escalate to the user with what failed,
  a suggested remediation, and why it is correct; retry after remediation/permission.

Like test_model_per_phase.py this is a contract check on the source of truth (the
reference files plus the coordinator skill body). It needs no model and no pytest,
and exits 0 (all rules hold) or 1 with a single reason line on stdout. It starts RED:
today developer/references/tool-failure.md does not exist and ailly/SKILL.md has no
Phase-Entry Checks section.
"""

import re
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
DEV = REPO / "developer"
TOOL_REF = DEV / "references" / "tool-failure.md"
MODEL_REF = DEV / "references" / "model-per-phase.md"
AILLY = DEV / "skills" / "ailly" / "SKILL.md"


def fail(reason: str) -> int:
    print(reason)
    return 1


def section(text: str, heading_re: str) -> str:
    """Return the body of the section whose `##` heading matches, up to the next `##`."""
    m = re.search(rf"(?im)^##\s+{heading_re}\s*$", text)
    if not m:
        return ""
    rest = text[m.end():]
    nxt = re.search(r"(?m)^##\s+", rest)
    return rest[: nxt.start()] if nxt else rest


def main() -> int:
    # G1 — the tool-failure reference exists.
    if not TOOL_REF.is_file():
        return fail(
            f"G1 reference required: {TOOL_REF.relative_to(REPO)} does not exist; "
            "it must hold the declared-tool failure escalation discipline"
        )
    tool = TOOL_REF.read_text()
    tool_low = tool.lower()

    # G2 — the tool-failure reference documents the escalation sequence:
    # check initialize for a local fix (naming mise/npm), escalate to the user,
    # and retry after remediation.
    if "initialize" not in tool_low:
        return fail(
            "G2 local remediation: tool-failure reference must direct a check of "
            "`developer:initialize` for a local fix before escalating"
        )
    if not any(t in tool_low for t in ("mise", "npm", "install")):
        return fail(
            "G2 local remediation: tool-failure reference must name a concrete local "
            "fix (e.g. `mise trust` / `npm install`)"
        )
    if not any(t in tool_low for t in ("escalat", "ask the user", "the user")):
        return fail(
            "G2 escalation: tool-failure reference must escalate back to the user "
            "with what failed and a suggested remediation"
        )
    if "retry" not in tool_low and "retries" not in tool_low:
        return fail(
            "G2 retry: tool-failure reference must retry after the user remediates "
            "or grants permission"
        )

    # G3 — be adamant / do not silently substitute another tool.
    adamant = any(t in tool_low for t in ("adamant", "do not silently", "stop"))
    no_swap = any(
        t in tool_low for t in ("substitut", "work around", "another tool", "swap")
    )
    if not (adamant and no_swap):
        return fail(
            "G3 be-adamant rule: tool-failure reference must say to stop / be adamant "
            "and not silently substitute another tool"
        )

    # G4 — the coordinator has a Phase-Entry Checks section pointing to tool-failure.
    if not AILLY.is_file():
        return fail(f"G4 {AILLY.relative_to(REPO)} not found")
    ailly = AILLY.read_text()
    checks = section(ailly, r"Phase-Entry Checks")
    if not checks:
        return fail(
            "G4 coordinator: ailly/SKILL.md must have a `## Phase-Entry Checks` section"
        )
    if "tool-failure" not in checks:
        return fail(
            "G4 coordinator: the Phase-Entry Checks section must point to "
            "developer/references/tool-failure.md"
        )

    # G5 — the model reference documents an active phase-entry check (compare the
    # running model to the recommendation, flag a mismatch) AND preserves no-gate.
    if not MODEL_REF.is_file():
        return fail(f"G5 {MODEL_REF.relative_to(REPO)} not found")
    model = MODEL_REF.read_text()
    model_low = model.lower()
    if "phase-entry check" not in model_low and "phase entry check" not in model_low:
        return fail(
            "G5 active check: model-per-phase reference must document a `Phase-entry "
            "check` that compares the running model to the recommendation"
        )
    if "mismatch" not in model_low:
        return fail(
            "G5 mismatch: the phase-entry check must flag a mismatch between the "
            "running model and the recommended one explicitly"
        )
    if not any(t in model_low for t in ("no gate", "never stall", "does not stall")):
        return fail(
            "G5 no-gate: the model reference must preserve the no-gate guarantee "
            "(the loop never stalls waiting for a switch)"
        )
    # G5b — the reference documents the harness-first / announce-fallback chain:
    # switch the model directly when the harness allows, else fall back to the
    # announce line + `/model`.
    if "fallback" not in model_low or "harness" not in model_low:
        return fail(
            "G5 fallback chain: the model reference must document switching the model "
            "directly when the harness allows, with the announce line as the fallback"
        )

    # G6 — the Phase-Entry Checks section also points to the model reference.
    if "model-per-phase" not in checks:
        return fail(
            "G6 coordinator: the Phase-Entry Checks section must point to "
            "developer/references/model-per-phase.md"
        )

    # G7 — each phase announce line carries the fallback phrasing: switch when the
    # harness allows, else `/model`. (test_model_per_phase.py covers the model name,
    # qualifier, and reference pointer; here we lock the harness-first/fallback shape.)
    announce_re = re.compile(r"\*\*Announce at start:\*\*.*", re.IGNORECASE)
    for skill in ("research", "design", "plan", "red-green-refactor"):
        body = (DEV / "skills" / skill / "SKILL.md").read_text()
        m = announce_re.search(body)
        line = m.group(0).lower() if m else ""
        if "harness" not in line:
            return fail(
                f"G7 {skill}: announce line must name the harness-switch path "
                "(switch when the harness allows) before the `/model` fallback"
            )
        if "fallback" not in line:
            return fail(
                f"G7 {skill}: announce line must mark `/model` as the fallback path"
            )

    print("PASS: phase-entry guardrails contract holds")
    return 0


if __name__ == "__main__":
    sys.exit(main())
