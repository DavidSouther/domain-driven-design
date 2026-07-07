#!/usr/bin/env python3
"""Structural checker for the `code-mode` invocation case.

The invocation prompt asks for Code Mode explicitly, on a small standalone
script (find every TODO, dispatch a capped, restricted headless session per
file to resolve them) with one genuinely ambiguous term ("resolve them" --
auto-fix vs. triage/report). Rules trace 1:1 to
`developer/skills/ailly/references/shapes/code-mode.md`'s specification:
the cursory `research:public` tool check, the single combined planning doc
(no separate research.md/design.md/plan.md, no three-gate ceremony), the
no-feature-test run-it-once build, reusing `intent-review.md` for the
ambiguous term, and the spawned-session guidance (bare-alias model,
`--allowedTools` restriction, headless `--print`/`-p` dispatch, a
concurrency cap).

Rules:
- C1 a cursory off-the-shelf tool check runs before any script is written:
  the response names a `research:public`-style check and an existing tool
  (e.g. grep/ripgrep) that already finds TODOs.
- C2 planning collapses into one combined document, not the standard
  three-artifact, three-gate ceremony (research.md + design.md + plan.md
  with three separate stop-and-wait gates).
- C3 the build step is run-it-once-and-inspect, not TDD: no feature test /
  red-green-refactor loop for this script.
- C4 the genuinely ambiguous term ("resolve them") is raised through
  `intent-review.md` or an explicit clarifying question, not silently
  guessed or refused outright.
- C5 spawned-session guidance is correct: a bare-alias model (`haiku`, not
  the dated `haiku-4.5` the prompt used verbatim), `--allowedTools`
  restriction, headless `--print`/`-p` dispatch, and a concurrency cap
  (`xargs -P N` or a semaphore) matching the prompt's cap of 5.
"""

import re
import sys

from _checker_utils import fail, read_stdin

# C1 -- cursory tool check via research:public, naming an existing tool.
TOOL_CHECK = re.compile(
    r"research:public|off-the-shelf", re.IGNORECASE
)
EXISTING_TOOL = re.compile(r"\b(?:grep|ripgrep|rg)\b", re.IGNORECASE)

# C2 -- must NOT run the standard three-artifact, three-gate ceremony. Flag
# the naive/baseline behavior: separate research.md + design.md + plan.md
# each with its own stop-and-wait gate, or an explicit "three draft gates"
# framing. A negation cue shortly before the match (e.g. "instead of
# separate research.md, design.md, and plan.md ...") means the response is
# describing what it is NOT doing, so that phrasing must not trip the flag.
FULL_CEREMONY = re.compile(
    r"research\.md.{0,200}design\.md.{0,200}plan\.md"
    r"|design\.md.{0,200}plan\.md.{0,200}research\.md"
    r"|three\s+(?:separate\s+)?(?:draft\s+)?gates"
    r"|three\s+stop-and-wait",
    re.IGNORECASE | re.DOTALL,
)
NEGATION_CUE = re.compile(
    r"instead of|rather than|not\s+\w+\s+separate|no\s+separate|without|"
    r"collapses?|avoids?|skips?|isn't|is not",
    re.IGNORECASE,
)


def full_ceremony_described(text: str) -> bool:
    for match in FULL_CEREMONY.finditer(text):
        window = text[max(0, match.start() - 80) : match.start()]
        if not NEGATION_CUE.search(window):
            return True
    return False
COMBINED_DOC = re.compile(
    r"combined\s+(?:planning\s+)?doc|single\s+(?:planning\s+)?doc|one\s+(?:short\s+)?doc",
    re.IGNORECASE,
)

# C3 -- no feature test / TDD; run once and inspect.
NO_FEATURE_TEST = re.compile(r"no\s+feature\s+test", re.IGNORECASE)
RUN_ONCE = re.compile(r"run\s+it\s+once", re.IGNORECASE)

# C4 -- the ambiguous term is raised, not silently resolved or refused.
INTENT_REVIEW = re.compile(r"intent-review\.md", re.IGNORECASE)
CLARIFYING_QUESTION = re.compile(
    r"resolve\b[^.\n]{0,80}\?"
    r"|clarif\w+[^.\n]{0,80}(?:resolve|auto-fix|triage|report)"
    r"|(?:auto-fix|autofix)[^.\n]{0,40}\bor\b[^.\n]{0,40}(?:triage|report)",
    re.IGNORECASE,
)

# C5 -- spawned-session guidance.
BARE_ALIAS = re.compile(r"\bhaiku\b(?!-4\.5)", re.IGNORECASE)
ALLOWED_TOOLS = re.compile(r"--allowedtools", re.IGNORECASE)
HEADLESS_DISPATCH = re.compile(r"--print|(?<![a-z-])-p(?![a-z-])", re.IGNORECASE)
CONCURRENCY_CAP = re.compile(r"xargs\s+-p|semaphore", re.IGNORECASE)


def main() -> int:
    text = read_stdin()
    lowered = text.lower()

    # C1 -- cursory tool check.
    if not TOOL_CHECK.search(text):
        return fail(
            "C1 cursory tool check required: no research:public / "
            "off-the-shelf check is described before writing the script"
        )
    if not EXISTING_TOOL.search(text):
        return fail(
            "C1 cursory tool check required: no existing tool (e.g. grep/"
            "ripgrep) is named as the off-the-shelf fit for finding TODOs"
        )

    # C2 -- combined doc, not the full three-artifact ceremony.
    if full_ceremony_described(text):
        return fail(
            "C2 must not run the standard ceremony: the response describes "
            "separate research.md/design.md/plan.md artifacts or three "
            "stop-and-wait gates; Code Mode collapses these into one doc"
        )
    if not COMBINED_DOC.search(text):
        return fail(
            "C2 combined planning doc required: no mention of a single/"
            "combined planning document replacing research.md+design.md+"
            "plan.md"
        )

    # C3 -- no feature test, run-it-once build.
    if not NO_FEATURE_TEST.search(text):
        return fail(
            "C3 no-feature-test build required: response does not state "
            "that this script gets no feature test / TDD loop"
        )
    if not RUN_ONCE.search(text):
        return fail(
            "C3 run-it-once build required: response does not describe "
            "running the script once and inspecting its output"
        )

    # C4 -- the ambiguous term is raised, not silently resolved.
    if not (INTENT_REVIEW.search(text) or CLARIFYING_QUESTION.search(text)):
        return fail(
            "C4 ambiguity handling required: 'resolve them' is genuinely "
            "ambiguous (auto-fix vs. triage/report) and the response neither "
            "points at intent-review.md nor raises an explicit clarifying "
            "question about it"
        )

    # C5 -- spawned-session guidance.
    if not BARE_ALIAS.search(text):
        return fail(
            "C5 bare-alias model guidance required: response must normalize "
            "the prompt's verbatim 'haiku-4.5' to the bare alias 'haiku'"
        )
    if "--allowedtools" not in lowered:
        return fail(
            "C5 --allowedTools restriction required: response does not "
            "describe restricting the spawned session's tool access"
        )
    if not HEADLESS_DISPATCH.search(text):
        return fail(
            "C5 headless dispatch required: response does not describe "
            "`claude --print` / `-p` for the spawned sessions"
        )
    if not CONCURRENCY_CAP.search(text):
        return fail(
            "C5 concurrency cap required: response does not cap outstanding "
            "sessions with `xargs -P N` or a counting semaphore"
        )

    return 0


if __name__ == "__main__":
    sys.exit(main())
