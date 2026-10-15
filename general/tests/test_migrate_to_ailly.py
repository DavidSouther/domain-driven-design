#!/usr/bin/env python3
"""Unit tests for general/scripts/migrate-to-ailly.py.

The harness CLIs are never executed: each test replaces the script's
`run_read` and `shutil.which` with fakes that answer from fixtures. The
end-to-end contract (stub binaries on PATH, --apply call order) lives in the
root feature test e2e/evals/scripts/check_repo_moved_notice.py.

Run: python3 general/tests/test_migrate_to_ailly.py
"""

import importlib.util
import io
import json
import sys
import tempfile
import unittest
from contextlib import redirect_stdout
from pathlib import Path
from unittest import mock

SCRIPT = Path(__file__).resolve().parents[1] / "scripts" / "migrate-to-ailly.py"
_spec = importlib.util.spec_from_file_location("migrate_to_ailly", SCRIPT)
migrate = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(migrate)

LEGACY_SLUG = "davidsouther/domain-driven-design"


def claude_state(marketplace: dict, plugins: list) -> dict:
    return {
        "claude plugin marketplace list --json": json.dumps([marketplace]),
        "claude plugin list --json": json.dumps(plugins),
    }


def claude_entry(plugin_id: str, scope: str = "user", enabled: bool = True, project: str = "") -> dict:
    entry = {"id": plugin_id, "version": "2026.09.0", "scope": scope, "enabled": enabled}
    if project:
        entry["projectPath"] = project
    return entry


def codex_state(source: str, names: list, source_type: str = "git") -> dict:
    installed = [
        {
            "pluginId": f"{name}@ailly",
            "name": name,
            "marketplaceName": "ailly",
            "installed": True,
            "marketplaceSource": {"sourceType": source_type, "source": source},
        }
        for name in names
    ]
    return {"codex plugin list --json": json.dumps({"installed": installed, "available": []})}


def pi_state(text: str) -> dict:
    return {"pi list": text}


class Harnesses:
    """Fake read-only harness calls answered from one fixture map."""

    def __init__(self, outputs: dict, present=("claude", "codex", "pi")) -> None:
        self.outputs = outputs
        self.present = set(present)
        self.reads = []

    def run_read(self, argv):
        self.reads.append(argv)
        return self.outputs.get(" ".join(argv), "")

    def which(self, name):
        return f"/stub/bin/{name}" if name in self.present else None

    def __enter__(self):
        self._patches = [
            mock.patch.object(migrate, "run_read", self.run_read),
            mock.patch.object(migrate.shutil, "which", self.which),
        ]
        for patch in self._patches:
            patch.start()
        return self

    def __exit__(self, *exc):
        for patch in reversed(self._patches):
            patch.stop()


def rendered(steps) -> list:
    return [step.render() for step in steps]


class IsLegacyTest(unittest.TestCase):
    def test_accepts_every_legacy_url_form(self):
        # Arrange
        forms = [
            "davidsouther/domain-driven-design",
            "https://github.com/davidsouther/domain-driven-design.git",
            "https://github.com/DavidSouther/Domain-Driven-Design",
            "git@github.com:davidsouther/domain-driven-design.git",
            "git:github.com/davidsouther/domain-driven-design@v1",
            "https://github.com/davidsouther/ddd_skill",
            "git:github.com/davidsouther/ddd_skill",
        ]
        # Act
        results = {form: migrate.is_legacy(form) for form in forms}
        # Assert
        self.assertEqual({form: True for form in forms}, results)

    def test_rejects_other_repositories(self):
        # Arrange
        forms = [
            "davidsouther/ailly",
            "https://github.com/davidsouther/ailly.git",
            "notdavidsouther/domain-driven-design",
            "davidsouther/domain-driven-design-fork",
            "anthropics/claude-plugins-official",
            "",
        ]
        # Act
        results = {form: migrate.is_legacy(form) for form in forms}
        # Assert
        self.assertEqual({form: False for form in forms}, results)


class PlanClaudeTest(unittest.TestCase):
    def test_reinstalls_each_plugin_at_its_scope_and_redisables(self):
        # Arrange
        project = tempfile.mkdtemp()
        state = claude_state(
            {"name": "ailly", "source": "github", "repo": LEGACY_SLUG},
            [
                claude_entry("developer@ailly"),
                claude_entry("general@ailly", enabled=False),
                claude_entry("research@ailly", scope="project", project=project),
                claude_entry("code-review@claude-plugins-official"),
            ],
        )
        # Act
        with Harnesses(state):
            steps, _ = migrate.plan_claude()
        # Assert
        self.assertEqual(
            [
                "claude plugin marketplace remove ailly",
                "claude plugin marketplace add davidsouther/ailly",
                "claude plugin install developer@ailly --scope user",
                "claude plugin install general@ailly --scope user",
                "claude plugin disable general@ailly --scope user",
                f"cd {project} && claude plugin install research@ailly --scope project",
            ],
            rendered(steps),
        )
        self.assertEqual(Path(project), steps[-1].cwd)

    def test_ddd_skill_ssh_source_is_legacy(self):
        # Arrange
        state = claude_state(
            {"name": "ailly", "source": "git", "url": "git@github.com:DavidSouther/ddd_skill.git"},
            [claude_entry("developer@ailly")],
        )
        # Act
        with Harnesses(state):
            steps, _ = migrate.plan_claude()
        # Assert
        self.assertEqual("claude plugin marketplace remove ailly", steps[0].render())

    def test_local_path_marketplace_is_untouched_and_reported(self):
        # Arrange
        path = "/Users/someone/devel/davidsouther/domain-driven-design"
        state = claude_state(
            {"name": "ailly", "source": "directory", "path": path},
            [claude_entry("developer@ailly")],
        )
        # Act
        with Harnesses(state):
            steps, notes = migrate.plan_claude()
        # Assert
        self.assertEqual([], steps)
        self.assertTrue(any(path in note and "untouched" in note for note in notes), notes)

    def test_unrecognized_source_is_untouched_and_reported(self):
        # Arrange
        state = claude_state(
            {"name": "ailly", "source": "github", "repo": "someone-else/ailly-fork"},
            [claude_entry("developer@ailly")],
        )
        # Act
        with Harnesses(state):
            steps, notes = migrate.plan_claude()
        # Assert
        self.assertEqual([], steps)
        self.assertTrue(any("someone-else/ailly-fork" in note for note in notes), notes)

    def test_successor_marketplace_plans_nothing(self):
        # Arrange
        state = claude_state(
            {"name": "ailly", "source": "github", "repo": "davidsouther/ailly"},
            [claude_entry("developer@ailly")],
        )
        # Act
        with Harnesses(state):
            steps, notes = migrate.plan_claude()
        # Assert
        self.assertEqual([], steps)
        self.assertTrue(any("davidsouther/ailly" in note for note in notes), notes)

    def test_missing_project_path_skips_that_reinstall_and_reports_it(self):
        # Arrange
        gone = str(Path(tempfile.mkdtemp()) / "deleted-project")
        state = claude_state(
            {"name": "ailly", "source": "github", "repo": LEGACY_SLUG},
            [claude_entry("research@ailly", scope="local", project=gone)],
        )
        # Act
        with Harnesses(state):
            steps, notes = migrate.plan_claude()
        # Assert
        self.assertNotIn("research@ailly", " ".join(rendered(steps)))
        self.assertTrue(any(gone in note for note in notes), notes)

    def test_missing_cli_is_skipped_and_reported(self):
        # Arrange
        harnesses = Harnesses({}, present=())
        # Act
        with harnesses:
            steps, notes = migrate.plan_claude()
        # Assert
        self.assertEqual([], steps)
        self.assertEqual([], harnesses.reads)
        self.assertTrue(any("claude" in note and "PATH" in note for note in notes), notes)

    def test_unreadable_output_is_skipped_and_reported(self):
        # Arrange
        state = {"claude plugin marketplace list --json": "not json"}
        # Act
        with Harnesses(state):
            steps, notes = migrate.plan_claude()
        # Assert
        self.assertEqual([], steps)
        self.assertEqual(1, len(notes))


class PlanCodexTest(unittest.TestCase):
    def test_removes_then_readds_each_installed_plugin(self):
        # Arrange
        state = codex_state(f"https://github.com/{LEGACY_SLUG}.git", ["developer", "general"])
        # Act
        with Harnesses(state):
            steps, _ = migrate.plan_codex()
        # Assert
        self.assertEqual(
            [
                "codex plugin remove developer@ailly",
                "codex plugin remove general@ailly",
                "codex plugin marketplace remove ailly",
                "codex plugin marketplace add davidsouther/ailly",
                "codex plugin add developer@ailly",
                "codex plugin add general@ailly",
            ],
            rendered(steps),
        )

    def test_local_marketplace_is_untouched_and_reported(self):
        # Arrange
        state = codex_state("/Users/someone/devel/domain-driven-design", ["developer"], source_type="local")
        # Act
        with Harnesses(state):
            steps, notes = migrate.plan_codex()
        # Assert
        self.assertEqual([], steps)
        self.assertTrue(any("untouched" in note for note in notes), notes)


class PlanPiTest(unittest.TestCase):
    LISTING = (
        "User packages:\n"
        "  git:github.com/davidsouther/domain-driven-design (filtered)\n"
        "    /home/u/.pi/agent/git/github.com/davidsouther/domain-driven-design\n"
        "  npm:pi-unrelated-package\n"
        "    /home/u/.pi/agent/npm/pi-unrelated-package\n"
        "Project packages:\n"
        "  https://github.com/DavidSouther/ddd_skill\n"
        "    /work/.pi/git/github.com/davidsouther/ddd_skill\n"
    )

    def test_repoints_user_and_project_packages_only(self):
        # Arrange
        state = pi_state(self.LISTING)
        # Act
        with Harnesses(state):
            steps, _ = migrate.plan_pi()
        # Assert
        self.assertEqual(
            [
                "pi remove git:github.com/davidsouther/domain-driven-design",
                "pi install git:github.com/davidsouther/ailly",
                "pi remove https://github.com/DavidSouther/ddd_skill -l",
                "pi install git:github.com/davidsouther/ailly -l",
            ],
            rendered(steps),
        )

    def test_local_checkout_is_untouched_and_reported(self):
        # Arrange
        checkout = "../../devel/davidsouther/domain-driven-design/.worktrees/pi-first-class-tools"
        state = pi_state(f"User packages:\n  {checkout}\n")
        # Act
        with Harnesses(state):
            steps, notes = migrate.plan_pi()
        # Assert
        self.assertEqual([], steps)
        self.assertTrue(any(checkout in note and "untouched" in note for note in notes), notes)

    def test_unreadable_listing_is_skipped_and_reported(self):
        # Arrange
        state = pi_state("")
        # Act
        with Harnesses(state):
            steps, notes = migrate.plan_pi()
        # Assert
        self.assertEqual([], steps)
        self.assertTrue(any("could not read" in note for note in notes), notes)

    def test_successor_already_installed_is_not_reinstalled(self):
        # Arrange
        state = pi_state(
            "User packages:\n"
            "  git:github.com/davidsouther/ailly\n"
            "    /home/u/.pi/agent/git/github.com/davidsouther/ailly\n"
        )
        # Act
        with Harnesses(state):
            steps, notes = migrate.plan_pi()
        # Assert
        self.assertEqual([], steps)
        self.assertTrue(any("davidsouther/ailly" in note for note in notes), notes)


class DryRunTest(unittest.TestCase):
    def test_no_harness_on_path_prints_nothing_to_change_and_exits_zero(self):
        # Arrange
        out = io.StringIO()
        # Act
        with Harnesses({}, present=()), redirect_stdout(out):
            code = migrate.main([])
        # Assert
        self.assertEqual(0, code)
        self.assertIn("nothing needs changing", out.getvalue())

    def test_header_names_every_plugin_and_omits_command_text(self):
        # Arrange
        state = pi_state("User packages:\n  git:github.com/davidsouther/domain-driven-design\n")
        out = io.StringIO()
        # Act
        with Harnesses(state, present=("pi",)), redirect_stdout(out):
            migrate.main([])
        # Assert
        header = out.getvalue().split("\n\n", 1)[0]
        for plugin in ("patterns", "domain", "research", "characters", "davidsouther/ailly"):
            self.assertIn(plugin, header)
        self.assertNotIn("pi remove", header)


def recorder(log: Path, code: int = 0) -> list:
    """argv for a command that appends its cwd to log and exits with code."""
    script = f"import os, sys; open({str(log)!r}, 'a').write(os.getcwd() + '\\n'); sys.exit({code})"
    return [sys.executable, "-c", script]


class ApplyTest(unittest.TestCase):
    def test_runs_every_step_in_order_from_its_cwd(self):
        # Arrange
        root = Path(tempfile.mkdtemp()).resolve()
        log = root / "log"
        steps = [migrate.Step(recorder(log), root), migrate.Step(recorder(log), Path("/"))]
        out = io.StringIO()
        # Act
        with redirect_stdout(out):
            code = migrate.apply_plan(steps)
        # Assert
        self.assertEqual(0, code)
        self.assertEqual([str(root), "/"], log.read_text().splitlines())
        self.assertIn("restart", out.getvalue().lower())

    def test_failure_stops_and_lists_the_commands_not_run(self):
        # Arrange
        root = Path(tempfile.mkdtemp()).resolve()
        log = root / "log"
        last = migrate.Step(["echo", "never-runs"], None)
        steps = [migrate.Step(recorder(log), root), migrate.Step(recorder(log, code=1), root), last]
        out = io.StringIO()
        # Act
        with redirect_stdout(out):
            code = migrate.apply_plan(steps)
        # Assert
        self.assertNotEqual(0, code)
        self.assertEqual(2, len(log.read_text().splitlines()))
        failed, not_run = out.getvalue().split("Not run:", 1)
        self.assertIn(steps[1].render(), failed)
        self.assertIn(last.render(), not_run)

    def test_missing_project_directory_is_a_failure_not_a_crash(self):
        # Arrange
        gone = Path(tempfile.mkdtemp()) / "deleted"
        out = io.StringIO()
        # Act
        with redirect_stdout(out):
            code = migrate.apply_plan([migrate.Step(["true"], gone)])
        # Assert
        self.assertNotEqual(0, code)

    def test_apply_with_nothing_planned_exits_zero(self):
        # Arrange
        out = io.StringIO()
        # Act
        with Harnesses({}, present=()), redirect_stdout(out):
            code = migrate.main(["--apply"])
        # Assert
        self.assertEqual(0, code)
        self.assertIn("nothing needs changing", out.getvalue())


class NoticeTest(unittest.TestCase):
    def test_notice_is_one_json_object_for_session_start(self):
        # Arrange
        path = Path('/tmp/odd "dir" \\ name/migrate-to-ailly.py')
        # Act
        notice = json.loads(migrate.notice_json(path))
        # Assert
        context = notice["hookSpecificOutput"]["additionalContext"]
        self.assertEqual("SessionStart", notice["hookSpecificOutput"]["hookEventName"])
        self.assertIn("davidsouther/ailly", notice["systemMessage"])
        self.assertIn("davidsouther/ailly", context)
        self.assertIn(str(path), context)
        self.assertIn("--apply", context)

    def test_notice_flag_makes_no_harness_call(self):
        # Arrange
        harnesses = Harnesses({})
        out = io.StringIO()
        # Act
        with harnesses, redirect_stdout(out):
            code = migrate.main(["--notice"])
        # Assert
        self.assertEqual(0, code)
        self.assertEqual([], harnesses.reads)
        self.assertIn(str(SCRIPT), json.loads(out.getvalue())["hookSpecificOutput"]["additionalContext"])


class HookTest(unittest.TestCase):
    HOOKS = SCRIPT.parents[1] / "hooks" / "hooks.json"

    def test_session_start_runs_the_notice_only_on_startup(self):
        # Arrange
        config = json.loads(self.HOOKS.read_text(encoding="utf-8"))
        # Act
        groups = config["hooks"]["SessionStart"]
        # Assert
        self.assertEqual(["SessionStart"], list(config["hooks"]))
        self.assertEqual(1, len(groups))
        self.assertEqual("startup", groups[0]["matcher"])
        (hook,) = groups[0]["hooks"]
        self.assertEqual("command", hook["type"])
        self.assertIn('"${CLAUDE_PLUGIN_ROOT}/scripts/migrate-to-ailly.py" --notice', hook["command"])
        self.assertLessEqual(hook["timeout"], 10)


if __name__ == "__main__":
    sys.exit(0 if unittest.main(exit=False).result.wasSuccessful() else 1)
