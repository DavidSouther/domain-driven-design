"""Unit tests for release.py — each function in isolation with mocked subprocess."""

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
    def test_micro_is_zero_when_no_prior_tags(self) -> None:
        with patch("release.subprocess.run", return_value=_make_proc("")):
            self.assertEqual(_r.compute_version(REPO, "2026.06"), "2026.06.0")

    def test_micro_increments_with_existing_tags(self) -> None:
        existing = "release/2026.06.0\nrelease/2026.06.1\n"
        with patch("release.subprocess.run", return_value=_make_proc(existing)):
            self.assertEqual(_r.compute_version(REPO, "2026.06"), "2026.06.2")


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

    def test_version_and_date_mutually_exclusive(self) -> None:
        """Test that --version and --date cannot be used together."""
        repo, _ = self._setup_repo()

        with self.assertRaises(SystemExit):
            _r.main(["--repo", str(repo), "--version", "2026.09.3", "--date", "2026.09"])

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
            with patch("release.compute_version", return_value="2026.10.0"):
                result = _r.main(["--repo", str(repo)])

        self.assertEqual(result, 0)

        dev_manifest = repo / "developer" / ".claude-plugin" / "plugin.json"
        data = json.loads(dev_manifest.read_text())
        self.assertEqual(data["version"], "2026.10.0")
