"""Shared helpers for root e2e/'s STATIC-suite checkers.

Contract (matches every plugin's e2e checker convention, e.g.
`patterns/e2e/evals/scripts/_checker_utils.py`): a checker exits 0 with no
output on success, or exits 1 with EXACTLY ONE reason line written to
stdout on failure. Never write to stderr and never exit with any other
code -- doing either converts a normal Fail into an Errored (broken-
checker) outcome in the report, per the same contract documented in every
plugin's `_checker_utils.py`.

Unlike the model-driven plugin checkers (which read an assistant's
transcript from stdin), a static-suite checker has no transcript -- there
is no model call anywhere in this suite. It reads the repository's own
reference-architecture files directly from disk instead.
"""

from pathlib import Path

# check_*.py lives at e2e/evals/scripts/check_*.py, so the repo root is
# three levels up: scripts -> evals -> e2e -> repo root.
REPO = Path(__file__).resolve().parents[3]

AILLY_DIR = REPO / "developer" / "skills" / "ailly"
INTENT_REVIEW = AILLY_DIR / "references" / "abilities" / "intent-review.md"
SKILL = AILLY_DIR / "SKILL.md"
DESIGN_PHASE = AILLY_DIR / "references" / "phases" / "design.md"
PLAN_PHASE = AILLY_DIR / "references" / "phases" / "plan.md"
RESEARCH_PHASE = AILLY_DIR / "references" / "phases" / "research.md"
GENERAL_REVIEW = REPO / "general" / "skills" / "review" / "SKILL.md"
C3_REVIEW = REPO / "general" / "skills" / "c3-review" / "SKILL.md"

# The four question categories; they must survive into the ability's text
# unchanged.
CATEGORIES = [
    "Research gap",
    "Design assumption",
    "Plan scope",
    "Implementation surprise",
]


def fail(reason: str) -> int:
    print(reason)
    return 1


def read(path: Path) -> str:
    return path.read_text(encoding="utf-8")
