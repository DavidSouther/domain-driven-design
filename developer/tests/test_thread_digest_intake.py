#!/usr/bin/env python3
"""Feature test: thread-digest reference + Ailly tracker intake routed through it.

Guards against scoping a tracker-origin task from title/body alone when a
later comment reframes its scope (see issue #37, and design.md's Purpose for
the full motivating narrative). This test is the executable form of
design.md's Specification; see design.md for the full rationale behind each
file touched below.

This is a source-level contract check on the affected reference/skill prose,
matching the existing pattern in `test_status_transition_and_subissue_linking.py`.
It needs no model and no pytest; it exits 0 when every rule holds, or 1 with a
single reason line on stdout. It starts RED; run it to see the failing
assertion.
"""

import re
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]

THREAD_DIGEST = REPO / "research" / "references" / "thread-digest.md"
USING_RESEARCH_SKILL = REPO / "research" / "skills" / "using-research" / "SKILL.md"
INTERNAL_CONFIG = (
    REPO
    / "research"
    / "skills"
    / "using-research"
    / "references"
    / "configuring"
    / "internal.md"
)
PUBLIC_CONFIG = (
    REPO
    / "research"
    / "skills"
    / "using-research"
    / "references"
    / "configuring"
    / "public.md"
)
PM_CONFIGURING = (
    REPO
    / "developer"
    / "skills"
    / "ailly"
    / "references"
    / "abilities"
    / "program-management"
    / "configuring.md"
)
PM_USING = (
    REPO
    / "developer"
    / "skills"
    / "ailly"
    / "references"
    / "abilities"
    / "program-management"
    / "using.md"
)
RESEARCH_PHASE = REPO / "developer" / "skills" / "ailly" / "references" / "phases" / "research.md"


def fail(reason: str) -> int:
    print(reason)
    return 1


def section(text: str, heading: str) -> str:
    """Return the body of a `## heading` section, up to the next `##`, or ""
    if the heading is not found."""
    m = re.search(rf"(?im)^##\s+{re.escape(heading)}\s*$", text)
    if not m:
        return ""
    rest = text[m.end():]
    nxt = re.search(r"(?m)^##\s+", rest)
    return rest[: nxt.start()] if nxt else rest


def window(text: str, needle: str, radius: int = 400) -> str:
    """Return `radius` chars on either side of the first case-insensitive
    match of `needle` in `text`, or "" if `needle` is not found. Used to
    check that two phrases appear near each other -- i.e. as part of the
    same new rule -- rather than merely somewhere in the whole file."""
    m = re.search(re.escape(needle), text, re.IGNORECASE)
    if not m:
        return ""
    return text[max(0, m.start() - radius): m.end() + radius]


def read(path: Path) -> str | None:
    return path.read_text(encoding="utf-8") if path.is_file() else None


def main() -> int:
    # T1 - names the three passes
    digest_text = read(THREAD_DIGEST)
    if digest_text is None:
        return fail(f"T1 {THREAD_DIGEST} not found")
    digest_low = digest_text.lower()
    for term in ("fetch", "organize", "refine"):
        if term not in digest_low:
            return fail(f"T1 thread-digest.md must name the '{term}' pass")

    # T2 - the gate is source-type classification, not a comment-count
    # threshold: conversational media always digest, static documents don't.
    if "conversational" not in digest_low:
        return fail(
            "T2 thread-digest.md must gate digestion on conversational-medium "
            "classification, not a comment count"
        )
    if re.search(r"threshold of \d+|(?<!no )\d+\+? comments? (trigger|threshold)", digest_low):
        return fail(
            "T2 thread-digest.md must not gate digestion on a fixed numeric "
            "comment-count threshold"
        )

    # T3 - the "no signal, drop it" outcome is an auditable note, not silent.
    if "no signal" not in digest_low:
        return fail("T3 thread-digest.md must name the 'no signal' outcome")
    if "drop" not in digest_low:
        return fail("T3 thread-digest.md must name dropping a no-signal thread")
    if "silent" not in digest_low:
        return fail(
            "T3 thread-digest.md must contrast the recorded note against a "
            "silent/undocumented drop"
        )

    # T4 - fetched content is framed as data to analyze, not instructions to
    # execute (the untrusted-content boundary).
    if "instruction" not in digest_low:
        return fail(
            "T4 thread-digest.md must state fetched thread content is data, "
            "not instructions, for the organize/refine passes"
        )

    # T5 - cite thread-digest.md alongside the jeopardy.md/falsify.md precedent
    using_research_text = read(USING_RESEARCH_SKILL)
    if using_research_text is None:
        return fail(f"T5 {USING_RESEARCH_SKILL} not found")
    if "thread-digest.md" not in using_research_text:
        return fail("T5 using-research/SKILL.md must cite research/references/thread-digest.md")

    # T6 - internal.md Composes With
    internal_text = read(INTERNAL_CONFIG)
    if internal_text is None:
        return fail(f"T6 {INTERNAL_CONFIG} not found")
    internal_composes = section(internal_text, "Composes With")
    if "thread-digest.md" not in internal_composes:
        return fail(
            "T6 configuring/internal.md's Composes With section must cite "
            "research/references/thread-digest.md"
        )

    # T7 - public.md Composes With
    public_text = read(PUBLIC_CONFIG)
    if public_text is None:
        return fail(f"T7 {PUBLIC_CONFIG} not found")
    public_composes = section(public_text, "Composes With")
    if "thread-digest.md" not in public_composes:
        return fail(
            "T7 configuring/public.md's Composes With section must cite "
            "research/references/thread-digest.md"
        )

    # T8 - "Select next task" row widened to body + comments
    pm_configuring_text = read(PM_CONFIGURING)
    if pm_configuring_text is None:
        return fail(f"T8 {PM_CONFIGURING} not found")
    row_match = re.search(
        r"(?im)^\|\s*Select next task\s*\|.*\|\s*$", pm_configuring_text
    )
    if not row_match:
        return fail("T8 configuring.md must have a 'Select next task' capability row")
    row_low = row_match.group(0).lower()
    if "body" not in row_low:
        return fail("T8 'Select next task' row must return 'body'")
    if "comments" not in row_low:
        return fail("T8 'Select next task' row must return 'comments'")

    # T9 - using.md's new read rule: full-thread fetch, check-with-degrade
    # (not-available -> warn and proceed) posture. Both checks are scoped to
    # a window around "full thread" so a pre-existing, unrelated use of
    # "not-available" elsewhere in the file (e.g. the Capability Routing
    # JSON example) cannot satisfy this by accident.
    pm_using_text = read(PM_USING)
    if pm_using_text is None:
        return fail(f"T9 {PM_USING} not found")
    fetch_rule = window(pm_using_text, "full thread") or window(pm_using_text, "full-thread")
    if not fetch_rule:
        return fail(
            "T9 using.md must add a rule mandating a full-thread fetch on "
            "task selection"
        )
    fetch_rule_low = fetch_rule.lower()
    if "thread-digest" not in fetch_rule_low:
        return fail("T9 the full-thread-fetch rule must cite thread-digest")
    if "not-available" not in fetch_rule_low and "not available" not in fetch_rule_low:
        return fail(
            "T9 the full-thread-fetch rule must address the tracker's "
            "Not-Available result (check-with-degrade, not a hard gate)"
        )

    # T10 - research.md's tracker-origin step (full thread -> thread-digest)
    # and its note-only reframe flag, recorded in Resolved Decisions. The
    # Resolved Decisions check is scoped to a window around "reframe" so the
    # pre-existing, unrelated "Resolved Decisions" heading listed in the
    # "research.md Sections" bullet cannot satisfy this by accident.
    research_phase_text = read(RESEARCH_PHASE)
    if research_phase_text is None:
        return fail(f"T10 {RESEARCH_PHASE} not found")
    research_phase_low = research_phase_text.lower()
    if "tracker" not in research_phase_low or "thread-digest" not in research_phase_low:
        return fail(
            "T10 research.md phase reference must add a tracker-origin step "
            "routing the full thread through thread-digest"
        )
    reframe_note = window(research_phase_text, "reframe") or window(research_phase_text, "reframing")
    if not reframe_note:
        return fail(
            "T10 research.md phase reference must extend its review pass to "
            "flag a comment that reframes the original scoping"
        )
    if "resolved decisions" not in reframe_note.lower():
        return fail(
            "T10 the reframe flag must be recorded as a research.md Resolved "
            "Decisions note, not a halt"
        )

    print("PASS: thread-digest reference and tracker-intake routing hold")
    return 0


if __name__ == "__main__":
    sys.exit(main())
