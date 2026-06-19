"""Feature test: full release cycle in a real git fixture."""

import contextlib
import io
import json
import subprocess
import tempfile
import unittest
from pathlib import Path

import release as _r


def _git(args: list[str], *, cwd: Path) -> None:
    _ = subprocess.run(["git"] + args, cwd=cwd, check=True, capture_output=True)


class ReleaseFeatureTests(unittest.TestCase):
    def setUp(self) -> None:
        self._tmpdir = tempfile.TemporaryDirectory()
        r = Path(self._tmpdir.name) / "repo"
        r.mkdir()

        _git(["init", "-b", "main"], cwd=r)
        _git(["config", "user.name", "Test"], cwd=r)
        _git(["config", "user.email", "test@example.com"], cwd=r)

        mp = r / ".claude-plugin"
        mp.mkdir()
        (mp / "marketplace.json").write_text(
            json.dumps(
                {
                    "name": "test",
                    "plugins": [
                        {
                            "name": "developer",
                            "version": "0.0.0",
                            "source": "./developer",
                        },
                    ],
                },
                indent=2,
            )
            + "\n"
        )

        dev_plugin = r / "developer" / ".claude-plugin"
        dev_plugin.mkdir(parents=True)
        (dev_plugin / "plugin.json").write_text(
            json.dumps({"name": "developer", "version": "0.0.0"}, indent=2) + "\n"
        )

        _git(["add", "."], cwd=r)
        _git(["commit", "-m", "init", "--no-gpg-sign"], cwd=r)

        (r / "developer" / "SKILL.md").write_text("# skill\n")
        _git(["add", "."], cwd=r)
        _git(["commit", "-m", "feat: add skill", "--no-gpg-sign"], cwd=r)

        self.repo = r

    def tearDown(self) -> None:
        self._tmpdir.cleanup()

    def _run_main(self, argv: list[str]) -> tuple[int, str, str]:
        stdout, stderr = io.StringIO(), io.StringIO()
        with contextlib.redirect_stdout(stdout), contextlib.redirect_stderr(stderr):
            result = _r.main(argv)
        return result, stdout.getvalue(), stderr.getvalue()

    def test_full_release_cycle(self) -> None:
        result, out, _ = self._run_main(["--repo", str(self.repo), "--date", "2026.06"])

        self.assertEqual(result, 0)
        self.assertEqual(out.strip(), "2026.06.0")

        plugin_data = json.loads(
            (self.repo / "developer" / ".claude-plugin" / "plugin.json").read_text()
        )
        self.assertEqual(plugin_data["version"], "2026.06.0")

        mp_data = json.loads(
            (self.repo / ".claude-plugin" / "marketplace.json").read_text()
        )
        dev_entry = next(p for p in mp_data["plugins"] if p["name"] == "developer")
        self.assertEqual(dev_entry["version"], "2026.06.0")

    def test_no_changes_prints_nothing(self) -> None:
        subprocess.run(
            ["git", "tag", "-a", "release/2026.05.0", "-m", "prev", "--no-sign"],
            cwd=self.repo,
            check=True,
        )

        result, out, err = self._run_main(
            ["--repo", str(self.repo), "--date", "2026.06"]
        )

        self.assertEqual(result, 0)
        self.assertEqual(out, "")
        self.assertIn("No changes", err)
