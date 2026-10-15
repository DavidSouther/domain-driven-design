"""Tests for check_version_line.py — versions outside the 2026.09.x line fail."""

import contextlib
import io
import json
import subprocess
import tempfile
import unittest
from pathlib import Path

import check_version_line as _c


def _git(args: list[str], *, cwd: Path) -> None:
    _ = subprocess.run(["git"] + args, cwd=cwd, check=True, capture_output=True)


class TestParseVersion(unittest.TestCase):
    def test_parses_to_integer_tuple(self) -> None:
        self.assertEqual(_c.parse_version("2026.09.3"), (2026, 9, 3))

    def test_compares_numerically_not_lexically(self) -> None:
        self.assertGreater(
            _c.parse_version("2026.09.10"), _c.parse_version("2026.09.9")
        )

    def test_rejects_non_numeric(self) -> None:
        with self.assertRaises(ValueError):
            _c.parse_version("2026.09.x")


class TestViolation(unittest.TestCase):
    def test_accepts_versions_in_the_line(self) -> None:
        for version in ("2026.09.0", "2026.09.1", "2026.09.3", "2026.09.40"):
            self.assertIsNone(_c.violation(version), version)

    def test_accepts_older_historical_versions(self) -> None:
        for version in ("2026.08.2", "2026.06.8"):
            self.assertIsNone(_c.violation(version), version)

    def test_rejects_reserved_successor_version(self) -> None:
        reason = _c.violation("2026.09.2")
        assert reason is not None
        self.assertIn("2026.09.2", reason)
        self.assertIn("reserved", reason)

    def test_rejects_ceiling_and_above(self) -> None:
        for version in ("2026.10.0", "2026.10.1", "2026.11.0", "2027.01.0"):
            reason = _c.violation(version)
            assert reason is not None, version
            self.assertIn(version, reason)
            self.assertIn(_c.CEILING, reason)

    def test_rejects_unparseable_version(self) -> None:
        reason = _c.violation("latest")
        assert reason is not None
        self.assertIn("latest", reason)

    def test_rejects_wrong_part_count(self) -> None:
        for version in ("2026.09.2.1", "2026.09"):
            reason = _c.violation(version)
            assert reason is not None, version
            self.assertIn("YYYY.MM.MICRO", reason)


class RepoFixture(unittest.TestCase):
    def setUp(self) -> None:
        self._tmpdir = tempfile.TemporaryDirectory()
        self.repo = Path(self._tmpdir.name) / "repo"
        self.repo.mkdir()
        _git(["init", "-b", "main"], cwd=self.repo)
        _git(["config", "user.name", "Test"], cwd=self.repo)
        _git(["config", "user.email", "test@example.com"], cwd=self.repo)
        self.write_plugin("developer", "2026.09.3")
        self.write_plugin("general", "2026.09.3")
        self.write_plugin("patterns", "2026.08.2", codex=False)
        self.write_marketplace(
            {"developer": "2026.09.3", "general": "2026.09.3", "patterns": "2026.08.2"}
        )
        _git(["add", "."], cwd=self.repo)
        _git(["commit", "-m", "init", "--no-gpg-sign"], cwd=self.repo)

    def tearDown(self) -> None:
        self._tmpdir.cleanup()

    def write_plugin(self, plugin: str, version: str, *, codex: bool = True) -> None:
        dirs = [".claude-plugin"] + ([".codex-plugin"] if codex else [])
        for manifest_dir in dirs:
            path = self.repo / plugin / manifest_dir / "plugin.json"
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text(
                json.dumps({"name": plugin, "version": version}, indent=2) + "\n"
            )

    def write_marketplace(self, versions: dict[str, str]) -> None:
        path = self.repo / ".claude-plugin" / "marketplace.json"
        path.parent.mkdir(parents=True, exist_ok=True)
        plugins = [{"name": n, "version": v} for n, v in versions.items()]
        path.write_text(
            json.dumps({"name": "ailly", "plugins": plugins}, indent=2) + "\n"
        )

    def tag(self, name: str) -> None:
        _git(["tag", "-a", name, "-m", "tag", "--no-sign"], cwd=self.repo)

    def run_main(self, argv: list[str]) -> tuple[int, str]:
        stdout = io.StringIO()
        with contextlib.redirect_stdout(stdout):
            result = _c.main(argv)
        return result, stdout.getvalue()


class TestCheck(RepoFixture):
    def test_clean_repo_passes_silently(self) -> None:
        self.tag("release/2026.09.0")
        self.tag("release/2026.09.1")
        result, out = self.run_main(["--repo", str(self.repo)])

        self.assertEqual(result, 0)
        self.assertEqual(out, "")

    def test_claude_manifest_at_ceiling_fails(self) -> None:
        path = self.repo / "developer" / ".claude-plugin" / "plugin.json"
        path.write_text(json.dumps({"name": "developer", "version": "2026.10.0"}))

        result, out = self.run_main(["--repo", str(self.repo)])

        self.assertEqual(result, 1)
        lines = out.splitlines()
        self.assertEqual(len(lines), 1)
        self.assertIn("developer/.claude-plugin/plugin.json", lines[0])
        self.assertIn("2026.10.0", lines[0])

    def test_codex_manifest_reserved_version_fails(self) -> None:
        path = self.repo / "general" / ".codex-plugin" / "plugin.json"
        path.write_text(json.dumps({"name": "general", "version": "2026.09.2"}))

        result, out = self.run_main(["--repo", str(self.repo)])

        self.assertEqual(result, 1)
        lines = out.splitlines()
        self.assertEqual(len(lines), 1)
        self.assertIn("general/.codex-plugin/plugin.json", lines[0])
        self.assertIn("reserved", lines[0])

    def test_marketplace_entry_above_ceiling_fails(self) -> None:
        self.write_marketplace(
            {"developer": "2026.09.3", "general": "2026.11.0", "patterns": "2026.08.2"}
        )

        result, out = self.run_main(["--repo", str(self.repo)])

        self.assertEqual(result, 1)
        lines = out.splitlines()
        self.assertEqual(len(lines), 1)
        self.assertIn(".claude-plugin/marketplace.json", lines[0])
        self.assertIn("general", lines[0])
        self.assertIn("2026.11.0", lines[0])

    def test_marketplace_entry_without_version_is_ignored(self) -> None:
        path = self.repo / ".claude-plugin" / "marketplace.json"
        path.write_text(json.dumps({"plugins": [{"name": "developer"}]}))

        result, out = self.run_main(["--repo", str(self.repo)])

        self.assertEqual((result, out), (0, ""))

    def test_release_tag_in_future_line_fails(self) -> None:
        self.tag("release/2026.10.0")

        result, out = self.run_main(["--repo", str(self.repo)])

        self.assertEqual(result, 1)
        self.assertEqual(len(out.splitlines()), 1)
        self.assertIn("release/2026.10.0", out)

    def test_release_tag_with_reserved_version_fails(self) -> None:
        self.tag("release/2026.09.2")

        result, out = self.run_main(["--repo", str(self.repo)])

        self.assertEqual(result, 1)
        self.assertIn("release/2026.09.2", out)
        self.assertIn("reserved", out)

    def test_unrelated_tags_are_ignored(self) -> None:
        self.tag("v2026.10.0")
        self.tag("release/notes")

        result, out = self.run_main(["--repo", str(self.repo)])

        self.assertEqual((result, out), (0, ""))

    def test_one_line_per_violation(self) -> None:
        (self.repo / "developer" / ".claude-plugin" / "plugin.json").write_text(
            json.dumps({"version": "2026.10.0"})
        )
        (self.repo / "developer" / ".codex-plugin" / "plugin.json").write_text(
            json.dumps({"version": "2026.09.2"})
        )
        self.tag("release/2026.12.0")

        result, out = self.run_main(["--repo", str(self.repo)])

        self.assertEqual(result, 1)
        self.assertEqual(len(out.splitlines()), 3)

    def test_non_git_directory_checks_manifests_only(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "developer" / ".claude-plugin" / "plugin.json"
            path.parent.mkdir(parents=True)
            path.write_text(json.dumps({"version": "2026.10.0"}))

            result, out = self.run_main(["--repo", tmp])

        self.assertEqual(result, 1)
        self.assertIn("2026.10.0", out)


if __name__ == "__main__":
    unittest.main()
