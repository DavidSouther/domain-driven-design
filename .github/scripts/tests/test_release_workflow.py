"""Workflow contract tests for the nightly release job."""

from pathlib import Path
import unittest


WORKFLOW = Path(__file__).resolve().parents[2] / "workflows" / "nightly-release.yml"


class ReleaseWorkflowTests(unittest.TestCase):
    def setUp(self) -> None:
        self.text = WORKFLOW.read_text(encoding="utf-8")

    def _position(self, needle: str) -> int:
        position = self.text.find(needle)
        self.assertNotEqual(position, -1, f"missing workflow text: {needle}")
        return position

    def test_no_change_path_gates_release_only_steps(self) -> None:
        self.assertIn("VERSION=$(python3 .github/scripts/release.py)", self.text)
        self.assertIn("echo \"release_needed=false\" >> \"${GITHUB_OUTPUT}\"", self.text)

        for step in (
            "Configure SSH signing",
            "Generate changelog",
            "Commit release changes to main",
            "Create release tag",
            "Publish GitHub Release",
        ):
            start = self._position(f"- name: {step}")
            end = self.text.find("\n      - name:", start + 1)
            block = self.text[start:] if end == -1 else self.text[start:end]
            self.assertIn("if: steps.release.outputs.release_needed == 'true'", block)

    def test_changelog_lands_on_main_before_release_tag(self) -> None:
        prepare = self._position("- name: Prepare release versions")
        changelog = self._position("- name: Generate changelog")
        commit = self._position("- name: Commit release changes to main")
        push_main = self._position("git push origin main")
        tag = self._position("- name: Create release tag")
        publish = self._position("- name: Publish GitHub Release")

        self.assertLess(prepare, changelog)
        self.assertLess(changelog, commit)
        self.assertLess(commit, push_main)
        self.assertLess(push_main, tag)
        self.assertLess(tag, publish)

    def test_github_release_uses_the_created_tag_and_changelog(self) -> None:
        self.assertIn('gh release create "release/${VERSION}"', self.text)
        self.assertIn("--notes-file CHANGELOG.md", self.text)
        self.assertIn("--verify-tag", self.text)


if __name__ == "__main__":
    unittest.main()
