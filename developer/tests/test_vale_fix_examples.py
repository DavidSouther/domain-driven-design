#!/usr/bin/env python3
"""Feature test: vale-fix.sh surfaces a worked example for a violated rule.

Per `.ailly/developer/2026-07-06-A-vale-examples/design.md`, when
`scripts/vale-fix.sh` builds a per-file fix prompt for Claude, it must
append a worked bad->good example for each *distinct* rule the file
violates (once per rule, not once per finding line), resolved from
`styles/config/examples/<Style>/<Rule>.examples.yml`. This directly
targets the observed `DDD.PassiveVoice` <-> `Google.We` livelock recorded
in `.ailly/prompts/vale_examples`: without a worked example, a fixer
session tends to bounce between the two rules forever.

This test never lets a real `claude` dispatch happen, regardless of how
(or whether) the dry-run hook is implemented: it shadows the `claude`
binary on `PATH` with a no-op stub for the whole run, so even a missing
or partially-wired `VALE_FIX_DRY_RUN` check cannot reach a live LLM call.
It then runs `vale-fix.sh` twice against the same probe file -- once with
`VALE_FIX_DRY_RUN=1` (expects the stub untouched, prompt printed to
stdout) and once without it set (expects the stub called exactly once,
confirming the new hook doesn't break the default dispatch path, e.g. via
an unguarded reference under the script's `set -u`).

This test exercises only the sidecar branch of the lookup order (the
probe's rule has no `swap`/`action` to auto-derive from). The
auto-derived and "nothing" branches, the LLM-generated tier, and
`styles/config/examples/Google/We.examples.yml` are part of this
design's Specification but are not covered by this one feature test.
"""

import os
import stat
import subprocess
import sys
import tempfile
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
VALE_FIX = REPO / "scripts" / "vale-fix.sh"
EXAMPLE_FILE = REPO / "styles" / "config" / "examples" / "DDD" / "PassiveVoice.examples.yml"

PROBE_MARKDOWN = """\
The bug was fixed by the on-call engineer.

The feature was tested by the QA team.
"""

EXPECTED_BAD = "This item is mentioned for parity with the sibling skills."
EXPECTED_GOOD = "The skill index mentions this item for parity with the sibling skills."
EXPECTED_NOTE = "Name the specific actor — not 'we' — to satisfy both active voice and Google.We."

CLAUDE_STUB = """#!/usr/bin/env bash
echo called >> "$CLAUDE_STUB_LOG"
exit 0
"""


def fail(reason: str) -> int:
    print(reason)
    return 1


def check_required_files() -> str | None:
    if not VALE_FIX.is_file():
        return f"missing {VALE_FIX.relative_to(REPO)}"
    if not EXAMPLE_FILE.is_file():
        return f"missing {EXAMPLE_FILE.relative_to(REPO)}"
    return None


def make_probe_file() -> Path:
    with tempfile.NamedTemporaryFile(
        mode="w", suffix=".md", dir=REPO, delete=False
    ) as tmp:
        tmp.write(PROBE_MARKDOWN)
        return Path(tmp.name)


def make_claude_stub(bin_dir: Path) -> None:
    stub = bin_dir / "claude"
    stub.write_text(CLAUDE_STUB, encoding="utf-8")
    stub.chmod(stub.stat().st_mode | stat.S_IEXEC | stat.S_IXGRP | stat.S_IXOTH)


def run_vale_fix(
    probe_path: Path, bin_dir: Path, log_path: Path, dry_run: bool
) -> subprocess.CompletedProcess:
    env = dict(os.environ)
    env["PATH"] = f"{bin_dir}:{env.get('PATH', '')}"
    env["CLAUDE_STUB_LOG"] = str(log_path)
    if dry_run:
        env["VALE_FIX_DRY_RUN"] = "1"
    else:
        env.pop("VALE_FIX_DRY_RUN", None)
    return subprocess.run(
        ["scripts/vale-fix.sh", probe_path.name],
        cwd=REPO,
        capture_output=True,
        text=True,
        timeout=60,
        env=env,
    )


def stub_call_count(log_path: Path) -> int:
    if not log_path.exists():
        return 0
    return log_path.read_text(encoding="utf-8").count("called")


def check_prompt_has_example_once(prompt: str) -> str | None:
    if "DDD.PassiveVoice" not in prompt:
        return f"prompt never mentions DDD.PassiveVoice:\n{prompt}"
    if "Worked example" not in prompt:
        return f"prompt has no 'Worked example' section:\n{prompt}"
    good_count = prompt.count(EXPECTED_GOOD)
    if good_count != 1:
        return (
            "expected the DDD.PassiveVoice example's good form to appear exactly "
            f"once (found {good_count}); the probe file trips the rule on two "
            f"lines, so the example must be deduplicated per rule, not per "
            f"line:\n{prompt}"
        )
    if EXPECTED_BAD not in prompt:
        return f"prompt is missing the DDD.PassiveVoice example's bad form:\n{prompt}"
    if EXPECTED_NOTE not in prompt:
        return f"prompt is missing the DDD.PassiveVoice example's note:\n{prompt}"
    return None


def main() -> int:
    required_failure = check_required_files()
    if required_failure:
        return fail(f"FAIL: {required_failure}")

    probe_path = make_probe_file()
    try:
        with tempfile.TemporaryDirectory() as workdir:
            bin_dir = Path(workdir) / "bin"
            bin_dir.mkdir()
            make_claude_stub(bin_dir)
            log_path = Path(workdir) / "claude.log"

            dry_run_result = run_vale_fix(probe_path, bin_dir, log_path, dry_run=True)
            if dry_run_result.returncode != 0:
                return fail(
                    f"FAIL: vale-fix.sh exited {dry_run_result.returncode} under "
                    f"VALE_FIX_DRY_RUN:\n{dry_run_result.stdout}\n{dry_run_result.stderr}"
                )
            dry_run_calls = stub_call_count(log_path)
            if dry_run_calls != 0:
                return fail(
                    f"FAIL: VALE_FIX_DRY_RUN=1 should print the prompt instead of "
                    f"dispatching, but the claude stub was called {dry_run_calls} time(s)"
                )
            content_failure = check_prompt_has_example_once(dry_run_result.stdout)
            if content_failure:
                return fail(f"FAIL: {content_failure}")

            log_path.unlink(missing_ok=True)
            normal_result = run_vale_fix(probe_path, bin_dir, log_path, dry_run=False)
            if normal_result.returncode != 0:
                return fail(
                    f"FAIL: vale-fix.sh exited {normal_result.returncode} in its "
                    f"default (non-dry-run) mode -- the new hook must not break "
                    f"the default dispatch path:\n{normal_result.stdout}\n{normal_result.stderr}"
                )
            normal_calls = stub_call_count(log_path)
            if normal_calls != 1:
                return fail(
                    "FAIL: expected the default (non-dry-run) path to dispatch to "
                    f"claude exactly once, was called {normal_calls} time(s)"
                )
    finally:
        probe_path.unlink(missing_ok=True)

    print("PASS: vale-fix.sh surfaces the DDD.PassiveVoice worked example exactly once")
    return 0


if __name__ == "__main__":
    sys.exit(main())
