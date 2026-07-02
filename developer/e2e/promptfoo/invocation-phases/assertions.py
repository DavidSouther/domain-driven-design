"""Promptfoo assertion adapters for the invocation-phases pilot."""

from __future__ import annotations

from pathlib import Path
import subprocess
from typing import Any


REPO = Path(__file__).resolve().parents[4]


def check_phase_output(output: str, context: dict[str, Any]) -> dict[str, Any]:
    vars_ = context.get("vars", {})
    checker = vars_.get("expected_checker")
    if not isinstance(checker, str) or not checker:
        return {
            "pass": False,
            "score": 0,
            "reason": "Missing expected_checker test variable",
        }

    checker_path = (REPO / "developer" / "e2e" / checker).resolve()
    if not checker_path.is_file():
        return {
            "pass": False,
            "score": 0,
            "reason": f"Checker does not exist: {checker}",
        }

    result = subprocess.run(
        ["python3", str(checker_path)],
        input=output,
        text=True,
        capture_output=True,
        check=False,
    )
    if result.returncode == 0:
        return {
            "pass": True,
            "score": 1,
            "reason": f"{checker} passed",
        }

    reason = result.stdout.strip() or result.stderr.strip() or "checker failed"
    return {
        "pass": False,
        "score": 0,
        "reason": reason,
    }
