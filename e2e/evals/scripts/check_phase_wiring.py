#!/usr/bin/env python3
"""T9 - phase wiring for the two gates that carry a feature test forward: the
Design and Plan phase references must each name intent review at their
draft-gate / "After the ..." step, so the mechanism is reachable from those
phases.
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from _checker_utils import fail, read, REPO, DESIGN_PHASE, PLAN_PHASE  # noqa: E402


def main() -> int:
    for label, path in (("design", DESIGN_PHASE), ("plan", PLAN_PHASE)):
        if not path.is_file():
            return fail(f"T9 {path.relative_to(REPO)} not found")
        low = read(path).lower()
        if "intent review" not in low and "intent-review" not in low:
            return fail(
                f"T9 {label} phase wiring: {path.relative_to(REPO)} must name "
                "intent review at its draft gate so the mechanism is reachable "
                f"from the {label} phase"
            )
    return 0


if __name__ == "__main__":
    sys.exit(main())
