#!/usr/bin/env python3
"""Structural checker for `general:review` invocation cases.

The artifact is a review of a PR diff that carries concerns in more than one
domain (code correctness and comment longevity). Each rule traces to the
parallel reviewer fan-out the review skill describes: route applicable
reviewers, fan out findings per lens, converge (verify + dedup + severity-rank),
then a separate fix pass. On the first violated rule it prints a single-line
reason to stdout and exits 1; if every rule holds it exits 0. stderr is left
untouched so the runner records a genuine Fail, not an Errored checker.

Rules:
- R1 base rubric: names >= 2 of the four canonical criteria (correctness,
     completeness, clarity, conciseness) — the always-on base reviewer.
- R2 fan-out: surfaces >= 2 distinct review lenses, i.e. a comment/longevity
     lens in addition to the base correctness lens (the artifact warrants both).
- R3 convergence: shows a verify-against-artifact step AND a severity ranking,
     not a flat unverified list.
- R4 issue grounded in this diff: flags >= 1 concrete issue tied to this diff.
- R5 no inline edits: evaluation stays separate from editing (no `git apply`,
     no ```suggestion fence).
"""

import re
import sys

from _checker_utils import fail, read_candidate

CRITERIA = ("correctness", "completeness", "clarity", "conciseness")

# A comment/longevity lens, distinct from the base correctness criteria.
COMMENT_LENS = (
    "comment",
    "docstring",
    "docblock",
    "doc string",
    "longevity",
    "enumerat",  # "enumerates current callers"
    "call site",
    "callers",
)

VERIFY_TERMS = ("verif", "confirm", "trace", "against the", "check the code", "grounded")
RANK_TERMS = ("severity", "priorit", "ranked", "rank by", "high/medium", "high / medium", "critical", "blocking")
DEDUP_TERMS = ("dedup", "duplicate", "de-dup", "merge", "overlap", "collaps")

ISSUE_TERMS = (
    "missing",
    "removed",
    "unrelated",
    "scope",
    "breaking",
    "rename",
    "renamed",
    "no test",
    "default",
    "required",
    "positional",
    "regress",
)
DIFF_REFS = ("is_admin", "format_timestamp", "fmt_ts", "user(", "/users", "test_", "fast path", "utc")


def main() -> int:
    src = read_candidate()
    low = src.lower()

    named = [c for c in CRITERIA if c in low]
    if len(named) < 2:
        return fail(
            f"R1 base rubric: named {len(named)} of correctness/completeness/clarity/"
            "conciseness, expected >= 2 (the always-on base reviewer's criteria)"
        )

    if not any(term in low for term in COMMENT_LENS):
        return fail(
            "R2 fan-out: no comment/longevity lens distinct from the base "
            "correctness lens (the artifact's docstring enumerates callers and "
            "warrants a second reviewer)"
        )

    has_verify = any(t in low for t in VERIFY_TERMS)
    has_rank = any(t in low for t in RANK_TERMS)
    has_dedup = any(t in low for t in DEDUP_TERMS)
    if not (has_verify and has_rank and has_dedup):
        return fail(
            "R3 convergence: missing a convergence stage "
            f"(verify={has_verify}, severity-rank={has_rank}, dedup={has_dedup}); "
            "findings must be verified against the artifact, deduplicated, and "
            "severity-ranked, not handed forward as a flat list"
        )

    if not any(term in low for term in ISSUE_TERMS):
        return fail(
            "R4 issue: no concrete issue flagged (scope creep / removed test / "
            "breaking change / stale comment)"
        )
    if not any(ref in low for ref in DIFF_REFS):
        return fail(
            "R4 issue: issues are not grounded in this diff (no reference to "
            "is_admin / format_timestamp / User / tests / the fast-path comment)"
        )

    if "git apply" in low or re.search(r"```+\s*suggestion", low):
        return fail(
            "R5 no inline edits: the review produced edits (a suggestion/patch); "
            "evaluation and editing must happen in separate agents"
        )

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
