#!/usr/bin/env python3
"""Structural checker for the `long-loop` invocation case.

The invocation prompt is a resume scenario where a draft marker is still present
and the session was declared a **long loop**. This is the inverse of the `ailly`
case: there the coordinator must STOP at the gate; here it must CROSS it by
dispatching a research-and-decide reviewer. Rules trace 1:1 to the ailly
SKILL.md "Long-loop Mode" section and `developer/skills/ailly/references/shapes/long-loop.md`
(section 2 reviewer contract, section 3 recording format, section 6
never-auto-clear invariants).

Rules:
- L1 a research-and-decide reviewer subagent is dispatched at the gate (section
  2): the response refers to dispatching/launching a reviewer/subagent that
  reads the artifact and decides its open questions.
- L2 a decision is recorded with rationale in the artifact's recording block
  (section 3): the response contains a `Resolved by the long-loop reviewer`
  heading with at least one `Decided:` entry.
- L3 the draft marker is cleared so the loop proceeds — the response does NOT
  stop and ask the human to clear it (the `ailly`-case behavior).
- L4 the never-auto-clear invariants are preserved (section 6): the response
  states the human merge gate and the Closing Bell are not auto-cleared.
"""

import re
import sys

from _checker_utils import fail, read_stdin

# L1 — a reviewer/subagent is dispatched to decide the open questions. The
# "research-and-decide" / "research and decide" reviewer is the contract's name
# for it; a bare "reviewer" without the dispatch verb must not satisfy this.
REVIEWER_DISPATCHED = re.compile(
    r"research[\s-]and[\s-]decide"
    r"|(?:dispatch|launch|spawn|delegate|send)\w*[^.\n]{0,60}"
    r"(?:reviewer|sub-?agent)"
    r"|(?:reviewer|sub-?agent)[^.\n]{0,60}"
    r"(?:dispatch|launch|spawn|delegate)\w*",
    re.IGNORECASE,
)

# L2 — the recorded-decision block from the reference's recording format.
RESOLVED_BLOCK = re.compile(
    r"resolved\s+by\s+the\s+long-loop\s+reviewer", re.IGNORECASE
)
DECIDED_ENTRY = re.compile(r"\bdecided\s*:", re.IGNORECASE)

# L3 — a refusal to cross the gate. The long loop must NOT tell the human to
# clear the marker before continuing; that is the normal-loop behavior the
# `ailly` case asserts. Match an instruction directed at the reader to remove /
# clear the marker, or an explicit wait-for-human.
REFUSAL = re.compile(
    r"(?:you|please|the user|the human)[^.\n]{0,40}"
    r"(?:remove|clear)[^.\n]{0,40}(?:draft|marker)"
    r"|(?:remove|clear)[^.\n]{0,40}(?:draft|marker)[^.\n]{0,40}"
    r"(?:before|to continue|to proceed)"
    r"|wait[^.\n]{0,30}(?:for (?:you|the (?:human|user))|human review)",
    re.IGNORECASE,
)

# L4 — the never-auto-clear invariants. Both the merge gate and the Closing Bell
# must be named as human-owned / never auto-cleared.
MERGE_GATE = re.compile(
    r"merge\s+gate[^.\n]{0,60}(?:human|never|not\s+auto|remain|preserv|still|approv)"
    r"|(?:human|never|not\s+auto|remain|preserv)[^.\n]{0,60}merge",
    re.IGNORECASE,
)
CLOSING_BELL = re.compile(r"closing\s+bell", re.IGNORECASE)


def main() -> int:
    text = read_stdin()

    # L1 — reviewer dispatched.
    if not REVIEWER_DISPATCHED.search(text):
        return fail(
            "L1 reviewer dispatch required: no research-and-decide reviewer "
            "subagent is dispatched at the gate; in a long loop the coordinator "
            "must dispatch the reviewer instead of waiting for the human"
        )

    # L2 — decision recorded with rationale in the recording block.
    if not RESOLVED_BLOCK.search(text):
        return fail(
            "L2 recorded-decision block required: no 'Resolved by the long-loop "
            "reviewer' block; the reviewer records each decision in place in the "
            "artifact (long-loop.md recording format)"
        )
    if not DECIDED_ENTRY.search(text):
        return fail(
            "L2 recorded-decision block required: the 'Resolved by the long-loop "
            "reviewer' block has no `Decided:` entry; each open question is "
            "resolved with a decision and its rationale"
        )

    # L3 — the gate is crossed, not refused.
    if REFUSAL.search(text):
        return fail(
            "L3 must cross the gate: the response told the human to clear the "
            "*Draft* marker / waited for human review; in a long loop the reviewer "
            "clears the marker so the loop proceeds without the human wait"
        )

    # L4 — never-auto-clear invariants preserved.
    if not (MERGE_GATE.search(text) and CLOSING_BELL.search(text)):
        return fail(
            "L4 never-auto-clear invariants required: the response must state the "
            "human merge gate and the Closing Bell are never auto-cleared by any "
            "reviewer; the long loop's autonomy stops at the draft gates"
        )

    return 0


if __name__ == "__main__":
    sys.exit(main())
