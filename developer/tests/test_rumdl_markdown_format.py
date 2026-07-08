#!/usr/bin/env python3
"""Feature test: rumdl enforces One-Sentence-Per-Line (OSPL) Markdown wrapping.

Per `.ailly/developer/2026-07-07-A-vale-markdown-format/design.md`, adding
consistent Markdown prose-wrapping requires:

- `.rumdl.toml` at the repo root, scoping `rumdl` to the `MD013` rule only
  (`[global] enable = ["MD013"]`) with `reflow-mode = "sentence-per-line"`
  and a generous `line-length` (so the tool's OSPL reflow is never
  constrained by a tight width cap -- see the open, unresolved
  `rvben/rumdl#111` upstream issue the design cites for why that composition
  is not assumed to just work);
- `scripts/rumdl-check.sh`, a pure lint pass mirroring `vale-check.sh`'s
  shape (`REPO_ROOT`-relative `cd`, optional `$1` path argument), exiting
  non-zero when a file isn't OSPL-wrapped;
- `scripts/rumdl-fix.sh`, a mechanical rewrite-in-place mirroring the same
  invocation shape, with no LLM dispatch (unlike `vale-fix.sh`) because
  `rumdl`'s fix for `MD013` is fully deterministic.

This test exercises the end-to-end round trip that defines "done" for this
feature: a probe file with a multi-sentence single-line paragraph fails
`rumdl-check.sh`, passes through `rumdl-fix.sh` to become one-sentence-per-
line, and then passes `rumdl-check.sh` cleanly. It runs both scripts for
real (no stubbing) since `rumdl-fix.sh` has no LLM dispatch to guard against
the way `vale-fix.sh`'s test must. When the `rumdl` binary is not on PATH,
the test reports that verification was skipped rather than failing for an
unrelated environment reason.
"""

import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
RUMDL_TOML = REPO / ".rumdl.toml"
RUMDL_CHECK = REPO / "scripts" / "rumdl-check.sh"
RUMDL_FIX = REPO / "scripts" / "rumdl-fix.sh"

PROBE_MARKDOWN = """\
This is the first sentence. This is the second sentence. This is the third sentence.
"""

EXPECTED_LINES_AFTER_FIX = [
    "This is the first sentence.",
    "This is the second sentence.",
    "This is the third sentence.",
]


def fail(reason: str) -> int:
    print(reason)
    return 1


def check_required_files() -> str | None:
    if not RUMDL_TOML.is_file():
        return f"missing {RUMDL_TOML.relative_to(REPO)}"
    if not RUMDL_CHECK.is_file():
        return f"missing {RUMDL_CHECK.relative_to(REPO)}"
    if not RUMDL_FIX.is_file():
        return f"missing {RUMDL_FIX.relative_to(REPO)}"
    return None


def make_probe_file() -> Path:
    with tempfile.NamedTemporaryFile(
        mode="w", suffix=".md", dir=REPO, delete=False
    ) as tmp:
        tmp.write(PROBE_MARKDOWN)
        return Path(tmp.name)


def run_check(rel_path: str) -> subprocess.CompletedProcess:
    return subprocess.run(
        [str(RUMDL_CHECK), rel_path],
        cwd=REPO,
        capture_output=True,
        text=True,
        timeout=30,
    )


def run_fix(rel_path: str) -> subprocess.CompletedProcess:
    return subprocess.run(
        [str(RUMDL_FIX), rel_path],
        cwd=REPO,
        capture_output=True,
        text=True,
        timeout=30,
    )


def main() -> int:
    required_failure = check_required_files()
    if required_failure:
        return fail(f"FAIL: {required_failure}")

    if not shutil.which("rumdl"):
        print(
            "PASS: rumdl markdown format static contract holds "
            "('rumdl' not on PATH, dynamic round-trip check skipped)"
        )
        return 0

    probe_path = make_probe_file()
    rel_path = probe_path.name
    try:
        dirty_result = run_check(rel_path)
        if dirty_result.returncode == 0:
            return fail(
                "FAIL: scripts/rumdl-check.sh reported the multi-sentence "
                "probe file as clean before any fix ran -- OSPL is not being "
                f"enforced:\n{dirty_result.stdout}\n{dirty_result.stderr}"
            )

        fix_result = run_fix(rel_path)
        if fix_result.returncode != 0:
            return fail(
                f"FAIL: scripts/rumdl-fix.sh exited {fix_result.returncode} "
                f"fixing the probe file:\n{fix_result.stdout}\n{fix_result.stderr}"
            )

        fixed_lines = probe_path.read_text(encoding="utf-8").splitlines()
        if fixed_lines != EXPECTED_LINES_AFTER_FIX:
            return fail(
                "FAIL: after scripts/rumdl-fix.sh, the probe file is not "
                f"one-sentence-per-line. Expected {EXPECTED_LINES_AFTER_FIX!r}, "
                f"got {fixed_lines!r}"
            )

        clean_result = run_check(rel_path)
        if clean_result.returncode != 0:
            return fail(
                "FAIL: scripts/rumdl-check.sh still reports the probe file as "
                f"dirty after scripts/rumdl-fix.sh ran:\n{clean_result.stdout}\n"
                f"{clean_result.stderr}"
            )
    finally:
        probe_path.unlink(missing_ok=True)

    print("PASS: rumdl-check.sh/rumdl-fix.sh enforce OSPL end-to-end")
    return 0


if __name__ == "__main__":
    sys.exit(main())
