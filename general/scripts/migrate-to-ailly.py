#!/usr/bin/env python3
"""Migrate a legacy domain-driven-design install to the new ailly repository.

Usage:
    python3 migrate-to-ailly.py           # dry run: show what will change
    python3 migrate-to-ailly.py --apply   # apply the changes
    python3 migrate-to-ailly.py --notice  # output JSON for SessionStart hook
"""

import argparse
import json
import subprocess
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Optional

SUCCESSOR = "davidsouther/ailly"
LEGACY_NAMES = ("davidsouther/domain-driven-design", "davidsouther/ddd_skill")


@dataclass(frozen=True)
class Step:
    """One planned command."""

    argv: list[str]
    cwd: Optional[Path]
    mutating: bool = True

    def render(self) -> str:
        """Return "cd <cwd> && <argv>" when cwd is set."""
        ...


def is_legacy(source: str) -> bool:
    """Return True if source refers to the legacy repository (case-insensitive, any URL form)."""
    ...


def run_read(argv: list[str]) -> str:
    """Execute a read-only harness call; return "" when binary absent."""
    ...


def plan_claude() -> tuple[list[Step], list[str]]:
    """Return (steps, skip/report notes) for Claude Code."""
    ...


def plan_codex() -> tuple[list[Step], list[str]]:
    """Return (steps, skip/report notes) for Codex."""
    ...


def plan_pi() -> tuple[list[Step], list[str]]:
    """Return (steps, skip/report notes) for pi."""
    ...


def render_plan(steps: list[Step], notes: list[str]) -> str:
    """Return header + notes + one line per step."""
    ...


def apply_plan(steps: list[Step]) -> int:
    """Execute each Step in order; stop at first failure, return non-zero exit code."""
    ...


def notice_json(script_path: Path) -> str:
    """Return hook JSON, json.dumps-escaped."""
    ...


def main(argv: Optional[list[str]] = None) -> int:
    """Parse flags: --apply, --notice."""
    parser = argparse.ArgumentParser(
        description="Migrate Ailly plugins from legacy to successor repository."
    )
    group = parser.add_mutually_exclusive_group()
    group.add_argument("--apply", action="store_true", help="Apply the migration")
    group.add_argument(
        "--notice", action="store_true", help="Output JSON for SessionStart hook"
    )
    args = parser.parse_args(argv)

    if args.notice:
        print(notice_json(Path(__file__).resolve()))
        return 0

    steps, notes = [], []
    for plan in (plan_claude, plan_codex, plan_pi):
        s, n = plan()
        steps += s
        notes += n

    if args.apply:
        return apply_plan(steps)

    print(render_plan(steps, notes))
    return 0


if __name__ == "__main__":
    sys.exit(main())
