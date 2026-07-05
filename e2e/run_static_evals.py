#!/usr/bin/env python3
"""Driver for root e2e/'s STATIC suites (no model call).

Every plugin's `<plugin>/e2e/ci.sh` delegates real YAML parsing and
assertion dispatch entirely to the external `ailly` binary: `ailly assemble`
builds a model conversation, `ailly run` fills it, and `ailly eval` scores
it against `judge`/`text_contains`/`text_not_contains`/`script`/`tokens`
assertions. Per `research/e2e/README.md`, `run`, `eval`, and `report` all
call a live model -- there is no subcommand in that pipeline that stays
model-free past `assemble`. A suite that must never call a model (like this
repository's own reference-architecture feature tests) therefore cannot be
scored by delegating to `ailly` at all; it needs its own driver.

This script is that driver. It intentionally reuses only the parts of the
existing convention that don't require a model:

- The `evals/<suite>.yaml` file shape (`name`, `cases`, each case an
  `assertions` list of flow-mappings) -- restricted here to `type: script`
  assertions, since a static suite has no transcript for `text_contains`/
  `judge`/`tokens` to score.
- The `evals/scripts/check_*.py` checker layout and the exact stdout-
  reason/exit-code contract used by every plugin's checkers (0 + silent =
  pass; 1 + one reason line on stdout = fail; a checker must never write to
  stderr, matching every other plugin's `_checker_utils.py` doc comment).

No third-party YAML parser is used because none exists anywhere in this
repo's e2e tooling (confirmed: PyYAML is not installed, and no existing
checker or ci.sh imports it) -- every existing `ci.sh` already hand-parses
a restricted subset of YAML for its own purposes (see each plugin's
`assert_filled()` awk state machine). This driver does the same, in Python,
for the restricted subset of the schema it actually needs.
"""

import re
import subprocess
import sys
from pathlib import Path

E2E = Path(__file__).resolve().parent
REPO = E2E.parent

CASE_RE = re.compile(r"^\s*-\s*name:\s*(\S+)\s*$")
SCRIPT_PATH_RE = re.compile(r"type:\s*script.*?path:\s*([^\s},]+)")


def parse_suite(path: Path) -> list[dict]:
    """Hand-parse the restricted static-suite subset of the eval schema:
    a top-level `cases:` list, each case a `name:` followed by one or more
    `- { type: script, ..., script: { path: ... } }` assertion lines.
    """
    cases: list[dict] = []
    current: dict | None = None
    for line in path.read_text(encoding="utf-8").splitlines():
        case_match = CASE_RE.match(line)
        if case_match:
            current = {"name": case_match.group(1), "scripts": []}
            cases.append(current)
            continue
        if current is not None and "type: script" in line:
            script_match = SCRIPT_PATH_RE.search(line)
            if script_match:
                current["scripts"].append(script_match.group(1))
    return cases


def run_case(case: dict) -> tuple[bool, str]:
    if not case["scripts"]:
        return False, "malformed: no `type: script` assertion found for this case"
    for rel_path in case["scripts"]:
        script_path = E2E / rel_path
        if not script_path.is_file():
            return False, f"errored: checker script not found at {rel_path}"
        result = subprocess.run(
            [sys.executable, str(script_path)],
            input="",
            capture_output=True,
            text=True,
        )
        if result.stderr.strip():
            return False, (
                "errored: checker wrote to stderr (should never happen): "
                f"{result.stderr.strip()[:200]}"
            )
        if result.returncode == 0:
            continue
        reason = result.stdout.strip() or (
            f"malformed: checker exited {result.returncode} with no reason on stdout"
        )
        return False, reason
    return True, ""


def main() -> int:
    evals_dir = E2E / "evals"
    suite_paths = sorted(evals_dir.glob("*.yaml"))
    if not suite_paths:
        print("No static suites found under e2e/evals/")
        return 0

    failures: list[str] = []
    total = 0
    for suite_path in suite_paths:
        suite_name = suite_path.stem
        for case in parse_suite(suite_path):
            total += 1
            ok, reason = run_case(case)
            status = "PASS" if ok else "FAIL"
            line = f"[{status}] {suite_name}::{case['name']}"
            if reason:
                line += f" -- {reason}"
            print(line)
            if not ok:
                failures.append(f"{suite_name}::{case['name']}")

    passed = total - len(failures)
    print(f"\n{passed}/{total} static-suite cases passed")
    return 1 if failures else 0


if __name__ == "__main__":
    sys.exit(main())
