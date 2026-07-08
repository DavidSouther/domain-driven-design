#!/usr/bin/env python3
"""Feature test: the SWE-bench runner turns instances into official predictions.jsonl.

Given a local instances file and a fake ``claude`` on ``PATH`` that edits the
checked-out repo and prints a JSON envelope, the ``run`` subcommand must, for each
instance: clone the repo, check out ``base_commit`` into an isolated working
directory, invoke ``claude -p`` inside that checkout, capture the working-tree diff
as ``model_patch``, append one official-format record (``instance_id``,
``model_name_or_path``, ``model_patch``) to ``predictions.jsonl``, and record the
run's ``session_id`` / ``total_cost_usd`` to a metadata sidecar.

This proves the harness plumbing with no live Anthropic API call and no network:
the fake ``claude`` supplies a canned edit plus a canned JSON envelope. The real
end-to-end benchmark run is the *same* ``main()`` invocation with the real
``claude`` on ``PATH`` and no ``--repo-base`` override -- the only differences are
which ``claude`` resolves first and where repos are cloned from.

Mirrors the repo's `.github/scripts/tests/test_release_feature.py` style (a
`unittest.TestCase` over a live git fixture in a temp dir). Stays red until
`swebench_runner/runner.py` exists.
"""

import json
import os
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import runner as _r  # noqa: E402

# A fake `claude` CLI: stands in for a real developer:ailly long-loop run by
# editing the checkout to fix the bug, then printing the JSON envelope that
# `--output-format json` would produce. It ignores its flags on purpose.
FAKE_CLAUDE = """#!/usr/bin/env python3
import json
from pathlib import Path

calc = Path("calc.py")
calc.write_text(calc.read_text().replace("a - b", "a + b"))
print(json.dumps({
    "type": "result",
    "subtype": "success",
    "session_id": "fake-session-abc123",
    "total_cost_usd": 0.0,
    "result": "Fixed subtraction bug in calc.add",
}))
"""


def _git(args: list[str], *, cwd: Path) -> None:
    subprocess.run(["git", *args], cwd=cwd, check=True, capture_output=True)


class PredictionsPlumbingTest(unittest.TestCase):
    def setUp(self) -> None:
        self._tmp = tempfile.TemporaryDirectory()
        self.tmp = Path(self._tmp.name)

        # 1. Upstream fixture repo standing in for a SWE-bench instance's repo.
        repo = self.tmp / "repos" / "fixture" / "demo"
        repo.mkdir(parents=True)
        _git(["init", "-b", "main"], cwd=repo)
        _git(["config", "user.name", "Fix"], cwd=repo)
        _git(["config", "user.email", "fix@example.com"], cwd=repo)
        (repo / "calc.py").write_text("def add(a, b):\n    return a - b  # BUG\n")
        _git(["add", "."], cwd=repo)
        _git(["commit", "-m", "init", "--no-gpg-sign"], cwd=repo)
        base = subprocess.run(
            ["git", "rev-parse", "HEAD"],
            cwd=repo,
            check=True,
            capture_output=True,
            text=True,
        ).stdout.strip()

        # 2. Instances file: one SWE-bench-shaped record, no gold patch / test names.
        self.instances = self.tmp / "instances.jsonl"
        self.instances.write_text(
            json.dumps(
                {
                    "instance_id": "fixture__demo-1",
                    "repo": "fixture/demo",
                    "base_commit": base,
                    "problem_statement": (
                        "calc.add subtracts instead of adding; it should return a + b."
                    ),
                }
            )
            + "\n"
        )

        # 3. Fake `claude` first on PATH -> deterministic, no live API call.
        bindir = self.tmp / "bin"
        bindir.mkdir()
        fake = bindir / "claude"
        fake.write_text(FAKE_CLAUDE)
        fake.chmod(0o755)
        self.fake_path = f"{bindir}{os.pathsep}{os.environ['PATH']}"

        self.out = self.tmp / "predictions.jsonl"
        self.meta = self.tmp / "run_metadata.jsonl"

    def tearDown(self) -> None:
        self._tmp.cleanup()

    def test_produces_official_predictions_record(self) -> None:
        prev_path = os.environ["PATH"]
        os.environ["PATH"] = self.fake_path
        try:
            rc = _r.main(
                [
                    "run",
                    "--instances", str(self.instances),
                    # Injection seam: clone from the local fixture, not GitHub.
                    "--repo-base", str(self.tmp / "repos" / "{repo}"),
                    "--workdir", str(self.tmp / "work"),
                    "--out", str(self.out),
                    "--metadata-out", str(self.meta),
                    "--model-name", "claude-ailly-longloop",
                ]
            )
        finally:
            os.environ["PATH"] = prev_path

        self.assertEqual(rc, 0)

        # Exactly one official-format predictions record.
        lines = self.out.read_text().splitlines()
        self.assertEqual(len(lines), 1)
        record = json.loads(lines[0])
        self.assertEqual(
            set(record), {"instance_id", "model_name_or_path", "model_patch"}
        )
        self.assertEqual(record["instance_id"], "fixture__demo-1")
        self.assertEqual(record["model_name_or_path"], "claude-ailly-longloop")

        # model_patch is the unified diff of the fake claude's edit.
        patch = record["model_patch"]
        self.assertIn("calc.py", patch)
        self.assertIn("-    return a - b", patch)
        self.assertIn("+    return a + b", patch)

        # Session metadata sidecar captures spend/session per instance.
        meta = json.loads(self.meta.read_text().splitlines()[0])
        self.assertEqual(meta["instance_id"], "fixture__demo-1")
        self.assertEqual(meta["session_id"], "fake-session-abc123")
        self.assertIn("total_cost_usd", meta)


if __name__ == "__main__":
    unittest.main()
