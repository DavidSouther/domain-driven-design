"""Unit tests for runner.py -- each function in isolation, per plan.md's steps."""

import json
import os
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import runner as _r  # noqa: E402


def _write_jsonl(path: Path, records: list[dict]) -> Path:
    path.write_text("\n".join(json.dumps(r) for r in records) + "\n")
    return path


def _git(args: list[str], *, cwd: Path) -> None:
    subprocess.run(["git", *args], cwd=cwd, check=True, capture_output=True)


class TestMainArgparse(unittest.TestCase):
    def test_cli_rejects_missing_instances(self) -> None:
        with self.assertRaises(SystemExit):
            _r.main(
                [
                    "run",
                    "--out",
                    "x",
                    "--metadata-out",
                    "y",
                    "--workdir",
                    "w",
                    "--model-name",
                    "m",
                ]
            )

    def test_cli_accepts_full_flag_set_and_dispatches(self) -> None:
        # An empty instances file makes `run()`'s per-instance loop a no-op, so
        # this exercises real argparse-to-run() dispatch (Step 1's original
        # intent) without needing a git checkout or a `claude` on PATH -- those
        # are covered by the feature test and the narrower unit tests below.
        with tempfile.TemporaryDirectory() as tmp:
            tmp_path = Path(tmp)
            instances = tmp_path / "i.jsonl"
            instances.write_text("")

            rc = _r.main(
                [
                    "run",
                    "--instances",
                    str(instances),
                    "--repo-base",
                    "t",
                    "--workdir",
                    str(tmp_path / "w"),
                    "--out",
                    str(tmp_path / "o.jsonl"),
                    "--metadata-out",
                    str(tmp_path / "m.jsonl"),
                    "--model-name",
                    "n",
                ]
            )
        self.assertEqual(rc, 0)

    def test_unknown_subcommand_is_an_argparse_error(self) -> None:
        with self.assertRaises(SystemExit):
            _r.main(["bogus"])


class TestParseInstances(unittest.TestCase):
    def setUp(self) -> None:
        self._tmpdir = tempfile.TemporaryDirectory()
        self.tmp = Path(self._tmpdir.name)

    def tearDown(self) -> None:
        self._tmpdir.cleanup()

    def test_parses_a_two_instance_fixture(self) -> None:
        path = _write_jsonl(
            self.tmp / "instances.jsonl",
            [
                {
                    "instance_id": "a",
                    "repo": "o/a",
                    "base_commit": "abc",
                    "problem_statement": "...",
                },
                {
                    "instance_id": "b",
                    "repo": "o/b",
                    "base_commit": "def",
                    "problem_statement": "...",
                },
            ],
        )

        instances = _r.parse_instances(path)

        self.assertEqual(len(instances), 2)
        self.assertEqual(instances[0], _r.Instance("a", "o/a", "abc", "..."))
        self.assertEqual(instances[1], _r.Instance("b", "o/b", "def", "..."))

    def test_skips_blank_lines(self) -> None:
        path = self.tmp / "instances.jsonl"
        path.write_text(
            "\n"
            + json.dumps(
                {
                    "instance_id": "a",
                    "repo": "o/a",
                    "base_commit": "abc",
                    "problem_statement": "...",
                }
            )
            + "\n   \n"
        )

        instances = _r.parse_instances(path)

        self.assertEqual(len(instances), 1)

    def test_missing_field_raises_with_line_number_and_field_name(self) -> None:
        path = self.tmp / "instances.jsonl"
        path.write_text(
            json.dumps({"instance_id": "a", "repo": "o/a", "problem_statement": "..."})
            + "\n"
        )

        with self.assertRaises(ValueError) as ctx:
            _r.parse_instances(path)

        self.assertIn("1", str(ctx.exception))
        self.assertIn("base_commit", str(ctx.exception))

    def test_malformed_json_raises_with_line_number(self) -> None:
        path = self.tmp / "instances.jsonl"
        path.write_text("{not json}\n")

        with self.assertRaises(ValueError) as ctx:
            _r.parse_instances(path)

        self.assertIn("1", str(ctx.exception))


class TestCheckoutInstance(unittest.TestCase):
    def setUp(self) -> None:
        self._tmpdir = tempfile.TemporaryDirectory()
        self.tmp = Path(self._tmpdir.name)

    def tearDown(self) -> None:
        self._tmpdir.cleanup()

    def _init_fixture_repo(self) -> tuple[Path, str]:
        repo = self.tmp / "repos" / "demo"
        repo.mkdir(parents=True)
        _git(["init", "-b", "main"], cwd=repo)
        _git(["config", "user.name", "Fix"], cwd=repo)
        _git(["config", "user.email", "fix@example.com"], cwd=repo)
        (repo / "calc.py").write_text("def add(a, b):\n    return a - b\n")
        _git(["add", "."], cwd=repo)
        _git(["commit", "-m", "init", "--no-gpg-sign"], cwd=repo)
        base = subprocess.run(
            ["git", "rev-parse", "HEAD"],
            cwd=repo,
            check=True,
            capture_output=True,
            text=True,
        ).stdout.strip()
        return repo, base

    def test_checks_out_base_commit_into_isolated_workdir(self) -> None:
        repo, base = self._init_fixture_repo()
        instance = _r.Instance("x", "demo", base, "...")

        checkout = _r.checkout_instance(
            instance, repo_base=str(repo.parent / "{repo}"), workdir=self.tmp / "work"
        )

        self.assertTrue((checkout / "calc.py").exists())
        head = subprocess.run(
            ["git", "rev-parse", "HEAD"],
            cwd=checkout,
            check=True,
            capture_output=True,
            text=True,
        ).stdout.strip()
        self.assertEqual(head, base)

    def test_nonexistent_repo_base_raises_called_process_error(self) -> None:
        instance = _r.Instance("x", "nope", "abc", "...")
        with self.assertRaises(subprocess.CalledProcessError):
            _r.checkout_instance(
                instance,
                repo_base=str(self.tmp / "repos" / "{repo}"),
                workdir=self.tmp / "work",
            )

    def test_nonexistent_base_commit_raises_called_process_error(self) -> None:
        repo, _base = self._init_fixture_repo()
        instance = _r.Instance("x", "demo", "0" * 40, "...")
        with self.assertRaises(subprocess.CalledProcessError):
            _r.checkout_instance(
                instance,
                repo_base=str(repo.parent / "{repo}"),
                workdir=self.tmp / "work",
            )


class TestBuildPrompt(unittest.TestCase):
    def test_declares_long_loop_mode_and_embeds_issue_text(self) -> None:
        prompt = _r.build_prompt("calc.add subtracts instead of adding.")

        self.assertIn("long loop", prompt)
        self.assertIn("to completion", prompt)
        self.assertIn("calc.add subtracts instead of adding.", prompt)


class TestInvokeClaude(unittest.TestCase):
    def setUp(self) -> None:
        self._tmpdir = tempfile.TemporaryDirectory()
        self.tmp = Path(self._tmpdir.name)
        self.checkout = self.tmp / "checkout"
        self.checkout.mkdir()

    def tearDown(self) -> None:
        self._tmpdir.cleanup()

    def _write_fake_claude(self, script: str) -> Path:
        bindir = self.tmp / "bin"
        bindir.mkdir(exist_ok=True)
        fake = bindir / "claude"
        fake.write_text(script)
        fake.chmod(0o755)
        return bindir

    def test_captures_session_id_and_total_cost_usd(self) -> None:
        bindir = self._write_fake_claude(
            "#!/usr/bin/env python3\n"
            "import json\n"
            "print(json.dumps({'session_id': 's1', 'total_cost_usd': 0.5}))\n"
        )
        prev = os.environ["PATH"]
        os.environ["PATH"] = f"{bindir}{os.pathsep}{prev}"
        try:
            result = _r.invoke_claude(self.checkout, "prompt text", max_turns=5)
        finally:
            os.environ["PATH"] = prev

        self.assertEqual(result.returncode, 0)
        self.assertEqual(result.session_id, "s1")
        self.assertEqual(result.total_cost_usd, 0.5)
        self.assertIsNone(result.error)

    def test_nonzero_exit_folds_into_error_not_raised(self) -> None:
        bindir = self._write_fake_claude(
            "#!/usr/bin/env python3\nimport sys\nsys.exit(3)\n"
        )
        prev = os.environ["PATH"]
        os.environ["PATH"] = f"{bindir}{os.pathsep}{prev}"
        try:
            result = _r.invoke_claude(self.checkout, "prompt text")
        finally:
            os.environ["PATH"] = prev

        self.assertIsNotNone(result.error)
        assert result.error is not None
        self.assertIn("3", result.error)
        self.assertIsNone(result.session_id)

    def test_unparseable_stdout_folds_into_error_not_raised(self) -> None:
        bindir = self._write_fake_claude("#!/usr/bin/env python3\nprint('not json')\n")
        prev = os.environ["PATH"]
        os.environ["PATH"] = f"{bindir}{os.pathsep}{prev}"
        try:
            result = _r.invoke_claude(self.checkout, "prompt text")
        finally:
            os.environ["PATH"] = prev

        self.assertIsNotNone(result.error)
        self.assertIsNone(result.session_id)
        self.assertIsNone(result.total_cost_usd)

    def test_claude_not_found_folds_into_error_not_raised(self) -> None:
        prev = os.environ["PATH"]
        os.environ["PATH"] = str(self.tmp / "empty-bin")
        try:
            result = _r.invoke_claude(self.checkout, "prompt text")
        finally:
            os.environ["PATH"] = prev

        self.assertIsNotNone(result.error)


class TestCapturePatch(unittest.TestCase):
    def setUp(self) -> None:
        self._tmpdir = tempfile.TemporaryDirectory()
        self.tmp = Path(self._tmpdir.name)
        self.checkout = self.tmp / "repo"
        self.checkout.mkdir()
        _git(["init", "-b", "main"], cwd=self.checkout)
        _git(["config", "user.name", "Fix"], cwd=self.checkout)
        _git(["config", "user.email", "fix@example.com"], cwd=self.checkout)
        (self.checkout / "calc.py").write_text(
            "def add(a, b):\n    return a - b\n"
        )
        _git(["add", "."], cwd=self.checkout)
        _git(["commit", "-m", "init", "--no-gpg-sign"], cwd=self.checkout)

    def tearDown(self) -> None:
        self._tmpdir.cleanup()

    def test_captures_unified_diff_of_working_tree_edit(self) -> None:
        (self.checkout / "calc.py").write_text(
            "def add(a, b):\n    return a + b\n"
        )

        patch = _r.capture_patch(self.checkout)

        self.assertIn("calc.py", patch)
        self.assertIn("-    return a - b", patch)
        self.assertIn("+    return a + b", patch)

    def test_no_changes_returns_empty_string(self) -> None:
        patch = _r.capture_patch(self.checkout)

        self.assertEqual(patch, "")

    def test_untracked_file_is_included(self) -> None:
        (self.checkout / "new_file.py").write_text("x = 1\n")

        patch = _r.capture_patch(self.checkout)

        self.assertIn("new_file.py", patch)


class TestAppendJsonl(unittest.TestCase):
    def setUp(self) -> None:
        self._tmpdir = tempfile.TemporaryDirectory()
        self.tmp = Path(self._tmpdir.name)

    def tearDown(self) -> None:
        self._tmpdir.cleanup()

    def test_appends_one_line_per_call(self) -> None:
        path = self.tmp / "out.jsonl"

        _r.append_jsonl(path, {"a": 1})
        _r.append_jsonl(path, {"a": 2})

        self.assertEqual(
            path.read_text().splitlines(), ['{"a": 1}', '{"a": 2}']
        )


class TestRunFailureModes(unittest.TestCase):
    def setUp(self) -> None:
        self._tmpdir = tempfile.TemporaryDirectory()
        self.tmp = Path(self._tmpdir.name)

    def tearDown(self) -> None:
        self._tmpdir.cleanup()

    def test_checkout_failure_for_one_instance_still_yields_a_record_and_continues(
        self,
    ) -> None:
        # First instance points at a repo_base with no matching fixture repo on
        # disk, so checkout_instance fails with CalledProcessError; the second
        # instance has nothing usable to checkout either but is used purely to
        # prove the batch reaches instance 2 rather than aborting after 1.
        instances = _write_jsonl(
            self.tmp / "instances.jsonl",
            [
                {
                    "instance_id": "bad-1",
                    "repo": "does/not-exist",
                    "base_commit": "deadbeef",
                    "problem_statement": "...",
                },
                {
                    "instance_id": "bad-2",
                    "repo": "also/not-exist",
                    "base_commit": "deadbeef",
                    "problem_statement": "...",
                },
            ],
        )
        out = self.tmp / "predictions.jsonl"
        meta = self.tmp / "run_metadata.jsonl"
        args = _r.build_parser().parse_args(
            [
                "run",
                "--instances",
                str(instances),
                "--repo-base",
                str(self.tmp / "repos" / "{repo}"),
                "--workdir",
                str(self.tmp / "work"),
                "--out",
                str(out),
                "--metadata-out",
                str(meta),
                "--model-name",
                "n",
            ]
        )

        rc = _r.run(args)

        self.assertEqual(rc, 0)
        lines = out.read_text().splitlines()
        self.assertEqual(len(lines), 2)
        self.assertEqual(json.loads(lines[0])["model_patch"], "")
        self.assertEqual(json.loads(lines[1])["instance_id"], "bad-2")

        meta_lines = meta.read_text().splitlines()
        self.assertEqual(len(meta_lines), 2)
        self.assertIn("error", json.loads(meta_lines[0]))

    def test_grade_is_reachable_and_does_not_crash(self) -> None:
        args = _r.build_parser().parse_args(["grade"])

        rc = _r.grade(args)

        self.assertIsInstance(rc, int)
        self.assertNotEqual(rc, 0)


if __name__ == "__main__":
    unittest.main()
