"""Unit tests for release.py — each function in isolation with mocked subprocess."""

import contextlib
import io
import json
import subprocess
import tempfile
import unittest
from pathlib import Path
from unittest.mock import MagicMock, call, patch

import release as _r


def _make_proc(stdout: str = "") -> MagicMock:
    m = MagicMock()
    m.stdout = stdout
    m.returncode = 0
    return m


REPO = Path("/fake/repo")


class TestFindLastTag(unittest.TestCase):
    def test_returns_most_recent_release_tag(self) -> None:
        with patch(
            "release.subprocess.run", return_value=_make_proc("release/1.0.0")
        ) as mock:
            result = _r.find_last_tag(REPO)

        self.assertEqual(result, "release/1.0.0")
        mock.assert_called_once_with(
            ["git", "describe", "--tags", "--match", "release/*", "--abbrev=0"],
            cwd=REPO,
            capture_output=True,
            text=True,
            check=True,
        )

    def test_falls_back_to_initial_commit_when_no_tags(self) -> None:
        initial = "abc1234"
        with patch("release.subprocess.run") as mock:
            mock.side_effect = [
                subprocess.CalledProcessError(128, "git"),
                _make_proc(initial),
            ]
            result = _r.find_last_tag(REPO)

        self.assertEqual(result, initial)
        self.assertEqual(
            mock.call_args_list[1],
            call(
                ["git", "rev-list", "--max-parents=0", "HEAD"],
                cwd=REPO,
                capture_output=True,
                text=True,
                check=True,
            ),
        )


class TestFindChangedPlugins(unittest.TestCase):
    def test_returns_plugins_with_commits(self) -> None:
        def side_effect(args: list[str], **_: object) -> MagicMock:
            plugin = args[4].rstrip("/")
            return _make_proc(
                "some commit" if plugin in ("developer", "patterns") else ""
            )

        with patch("release.subprocess.run", side_effect=side_effect):
            result = _r.find_changed_plugins(REPO, "release/0.0.0")

        self.assertEqual(result, ["developer", "patterns"])

    def test_returns_empty_when_nothing_changed(self) -> None:
        with patch("release.subprocess.run", return_value=_make_proc("")):
            result = _r.find_changed_plugins(REPO, "release/0.0.0")

        self.assertEqual(result, [])


class TestComputeVersion(unittest.TestCase):
    def _compute(self, tags: str) -> str:
        with patch("release.subprocess.run", return_value=_make_proc(tags)) as mock:
            result = _r.compute_version(REPO)
        mock.assert_called_once_with(
            ["git", "tag", "-l", "release/2026.09.*"],
            cwd=REPO,
            capture_output=True,
            text=True,
            check=True,
        )
        return result

    def test_starts_at_first_release_when_no_prior_tags(self) -> None:
        self.assertEqual(self._compute(""), "2026.09.3")

    def test_skips_reserved_successor_version_after_historical_tags(self) -> None:
        existing = "release/2026.09.0\nrelease/2026.09.1\n"
        self.assertEqual(self._compute(existing), "2026.09.3")

    def test_never_returns_reserved_version(self) -> None:
        existing = "release/2026.09.0\nrelease/2026.09.1\nrelease/2026.09.2\n"
        self.assertEqual(self._compute(existing), "2026.09.3")

    def test_increments_past_highest_existing_micro(self) -> None:
        existing = "release/2026.09.0\nrelease/2026.09.1\nrelease/2026.09.3\n"
        self.assertEqual(self._compute(existing), "2026.09.4")

    def test_compares_micro_numerically(self) -> None:
        existing = "release/2026.09.9\nrelease/2026.09.10\n"
        self.assertEqual(self._compute(existing), "2026.09.11")

    def test_ignores_gaps_and_unparseable_tags(self) -> None:
        existing = "release/2026.09.7\nrelease/2026.09.x\n"
        self.assertEqual(self._compute(existing), "2026.09.8")


class TestUpdatePluginJson(unittest.TestCase):
    def setUp(self) -> None:
        self._tmpdir = tempfile.TemporaryDirectory()
        self.tmp = Path(self._tmpdir.name)

    def tearDown(self) -> None:
        self._tmpdir.cleanup()

    def test_writes_new_version(self) -> None:
        path = self.tmp / "plugin.json"
        path.write_text(
            json.dumps({"name": "developer", "version": "0.0.0"}, indent=2) + "\n"
        )

        _r.update_plugin_json(path, "2026.06.0")

        data = json.loads(path.read_text())
        self.assertEqual(data["version"], "2026.06.0")
        self.assertEqual(data["name"], "developer")


class TestUpdatePluginManifests(unittest.TestCase):
    def setUp(self) -> None:
        self._tmpdir = tempfile.TemporaryDirectory()
        self.tmp = Path(self._tmpdir.name)

    def tearDown(self) -> None:
        self._tmpdir.cleanup()

    def _write_manifest(self, plugin: str, manifest_dir: str, version: str) -> Path:
        path = self.tmp / plugin / manifest_dir / "plugin.json"
        path.parent.mkdir(parents=True)
        path.write_text(
            json.dumps({"name": plugin, "version": version}, indent=2) + "\n"
        )
        return path

    def test_updates_claude_and_codex_manifests_when_both_exist(self) -> None:
        claude = self._write_manifest("developer", ".claude-plugin", "0.0.0")
        codex = self._write_manifest("developer", ".codex-plugin", "0.0.0")

        updated = _r.update_plugin_manifests(self.tmp, "developer", "2026.06.0")

        self.assertEqual(updated, [claude, codex])
        self.assertEqual(json.loads(claude.read_text())["version"], "2026.06.0")
        self.assertEqual(json.loads(codex.read_text())["version"], "2026.06.0")

    def test_updates_existing_manifest_when_codex_mirror_is_absent(self) -> None:
        claude = self._write_manifest("characters", ".claude-plugin", "0.0.0")

        updated = _r.update_plugin_manifests(self.tmp, "characters", "2026.06.0")

        self.assertEqual(updated, [claude])
        self.assertEqual(json.loads(claude.read_text())["version"], "2026.06.0")


class TestUpdateMarketplaceJson(unittest.TestCase):
    def setUp(self) -> None:
        self._tmpdir = tempfile.TemporaryDirectory()
        self.tmp = Path(self._tmpdir.name)

    def tearDown(self) -> None:
        self._tmpdir.cleanup()

    def _write(self, filename: str, plugins: list[dict[str, str]]) -> Path:
        path = self.tmp / filename
        path.write_text(json.dumps({"plugins": plugins}, indent=2) + "\n")
        return path

    def test_updates_matching_plugin(self) -> None:
        path = self._write(
            "marketplace.json", [{"name": "developer", "version": "0.0.0"}]
        )

        _r.update_marketplace_json(path, "developer", "2026.06.0")

        data = json.loads(path.read_text())
        self.assertEqual(data["plugins"][0]["version"], "2026.06.0")

    def test_exits_when_plugin_not_found(self) -> None:
        path = self._write("marketplace.json", [{"name": "other", "version": "0.0.0"}])

        with self.assertRaises(SystemExit):
            _r.update_marketplace_json(path, "developer", "2026.06.0")


class TestVersionOverride(unittest.TestCase):
    def setUp(self) -> None:
        self._tmpdir = tempfile.TemporaryDirectory()
        self.tmp = Path(self._tmpdir.name)

    def tearDown(self) -> None:
        self._tmpdir.cleanup()

    def _setup_repo(self) -> tuple[Path, Path]:
        """Create a temporary repo with minimal manifests."""
        repo = self.tmp / "repo"
        repo.mkdir()

        # Initialize git repo
        _r._run(["git", "init"], cwd=repo)
        _r._run(["git", "config", "user.email", "test@example.com"], cwd=repo)
        _r._run(["git", "config", "user.name", "Test User"], cwd=repo)

        # Create developer plugin with manifests
        dev_dir = repo / "developer"
        dev_dir.mkdir()
        for manifest_dir in _r.MANIFEST_DIRS:
            path = dev_dir / manifest_dir / "plugin.json"
            path.parent.mkdir(parents=True)
            path.write_text(
                json.dumps({"name": "developer", "version": "0.0.0"}, indent=2) + "\n"
            )

        # Create marketplace.json
        marketplace = repo / ".claude-plugin" / "marketplace.json"
        marketplace.parent.mkdir(parents=True)
        marketplace.write_text(
            json.dumps({"plugins": [{"name": "developer", "version": "0.0.0"}]}, indent=2)
            + "\n"
        )

        # Create initial commit
        _r._run(["git", "add", "."], cwd=repo)
        _r._run(["git", "commit", "-m", "initial"], cwd=repo)

        return repo, marketplace

    def test_version_override_replaces_computed_version(self) -> None:
        repo, marketplace = self._setup_repo()

        with patch("release.find_changed_plugins", return_value=["developer"]):
            result = _r.main(["--repo", str(repo), "--version", "2026.09.3"])

        self.assertEqual(result, 0)

        # Check that the version was set to the override
        dev_manifest = repo / "developer" / ".claude-plugin" / "plugin.json"
        data = json.loads(dev_manifest.read_text())
        self.assertEqual(data["version"], "2026.09.3")

        marketplace_data = json.loads(marketplace.read_text())
        self.assertEqual(marketplace_data["plugins"][0]["version"], "2026.09.3")

    def test_date_flag_is_not_accepted(self) -> None:
        """The release line is pinned, so there is no --date override."""
        repo, _ = self._setup_repo()

        with self.assertRaises(SystemExit):
            _r.main(["--repo", str(repo), "--date", "2026.09"])

    def test_version_outside_line_is_rejected_with_reason(self) -> None:
        repo, _ = self._setup_repo()
        cases = {
            "2026.10.0": "davidsouther/ailly",
            "2026.11.4": "davidsouther/ailly",
            "2027.09.3": "davidsouther/ailly",
            "2026.08.2": "2026.09",
            "2026.09.0": "2026.09.3",
            "2026.09.1": "2026.09.3",
            "2026.09.2": "reserved",
        }
        for version, expected in cases.items():
            with self.subTest(version=version):
                stderr = io.StringIO()
                with contextlib.redirect_stderr(stderr):
                    with self.assertRaises(SystemExit) as ctx:
                        _r.main(["--repo", str(repo), "--version", version])
                self.assertEqual(ctx.exception.code, 2)
                self.assertIn(version, stderr.getvalue())
                self.assertIn(expected, stderr.getvalue())

    def test_version_at_or_after_first_release_is_accepted(self) -> None:
        repo, _ = self._setup_repo()

        for version in ("2026.09.3", "2026.09.12"):
            with self.subTest(version=version):
                with patch("release.find_changed_plugins", return_value=["developer"]):
                    self.assertEqual(
                        _r.main(["--repo", str(repo), "--version", version]), 0
                    )

    def test_version_format_validation(self) -> None:
        """Test that malformed versions are rejected."""
        repo, _ = self._setup_repo()

        # Missing micro version
        with self.assertRaises(SystemExit):
            _r.main(["--repo", str(repo), "--version", "2026.09"])

        # Non-numeric parts
        with self.assertRaises(SystemExit):
            _r.main(["--repo", str(repo), "--version", "abc"])

    def test_no_version_override_uses_computed_version(self) -> None:
        """Test that computed version is used when no override is provided."""
        repo, marketplace = self._setup_repo()

        with patch("release.find_changed_plugins", return_value=["developer"]):
            with patch("release.compute_version", return_value="2026.09.4"):
                result = _r.main(["--repo", str(repo)])

        self.assertEqual(result, 0)

        dev_manifest = repo / "developer" / ".claude-plugin" / "plugin.json"
        data = json.loads(dev_manifest.read_text())
        self.assertEqual(data["version"], "2026.09.4")
