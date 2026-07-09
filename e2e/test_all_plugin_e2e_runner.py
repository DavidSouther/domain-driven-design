#!/usr/bin/env python3

import importlib.util
import json
import sys
import tempfile
import unittest
from pathlib import Path


REPO = Path(__file__).resolve().parents[1]
SCRIPT = REPO / "e2e" / "run_all_plugin_e2e.py"


def load_runner():
    spec = importlib.util.spec_from_file_location("run_all_plugin_e2e", SCRIPT)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


def discovery_report(model, run_id):
    return {
        "suite": "discovery",
        "model": model,
        "run_id": run_id,
        "cases": [
            {
                "name": "fixture-skill",
                "matches": [
                    {
                        "assertions": [
                            {"outcome": "pass"},
                        ],
                    },
                ],
            },
        ],
    }


class AllPluginE2ERunnerTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.runner = load_runner()

    def test_discovers_model_and_static_plugin_projects(self):
        model_projects, static_projects = self.runner.discover_projects(REPO)

        self.assertEqual(
            [project.name for project in model_projects],
            ["developer", "domain", "general", "patterns", "research"],
        )
        self.assertEqual([project.name for project in static_projects], ["characters"])

    def test_validates_current_e2e_entry_coverage(self):
        model_projects, _ = self.runner.discover_projects(REPO)
        errors = [
            error
            for project in model_projects
            for error in self.runner.validate_project(project)
        ]

        self.assertEqual(errors, [])

    def test_resource_inventory_names_consolidated_resources(self):
        model_projects, _ = self.runner.discover_projects(REPO)
        projects = {project.name: project for project in model_projects}

        developer = self.runner.project_resources(
            projects["developer"], self.runner.suite_map(projects["developer"])
        )
        patterns = self.runner.project_resources(
            projects["patterns"], self.runner.suite_map(projects["patterns"])
        )

        self.assertIn("developer:ailly research", developer)
        self.assertIn("developer:ailly cleanup", developer)
        self.assertIn("patterns:using-patterns newtype", patterns)

    def test_model_args_fall_back_to_discovered_models(self):
        self.assertEqual(
            self.runner.expand_model_args([], ["claude-sonnet-4-6"]),
            ["claude-sonnet-4-6"],
        )

    def test_model_args_expand_anthropic_family(self):
        self.assertEqual(
            self.runner.expand_model_args(["anthropic"], []),
            [
                "claude-haiku-4-5",
                "claude-sonnet-4-6",
                "claude-sonnet-5",
                "claude-opus-4-8",
                "claude-fable-5",
            ],
        )

    def test_model_args_expand_mixed_families_and_model_names_once(self):
        self.assertEqual(
            self.runner.expand_model_args(["openai", "gpt-5.4", "bedrock", "noop"], []),
            [
                "gpt-5.5",
                "gpt-5.4",
                "gpt-5.4-mini",
                "bedrock:meta.llama3-3-70b-instruct-v1:0",
                "bedrock:meta.llama4-scout-17b-instruct-v1:0",
                "bedrock:mistral.mistral-large-3-675b-instruct",
                "bedrock:cohere.command-r-plus-v1:0",
                "noop",
            ],
        )

    def test_bare_archive_id_resolves_under_repo_artifacts_and_loads_manifest(self):
        with tempfile.TemporaryDirectory() as tmp:
            repo = Path(tmp)
            archive_id = "20260709T000000Z-1234abcd"
            archive = repo / "e2e" / "artifacts" / archive_id
            archive.mkdir(parents=True)
            (archive / "manifest.json").write_text(
                json.dumps(
                    {
                        "schema_version": 1,
                        "run_id": archive_id,
                        "created_at": "2026-07-09T00:00:00Z",
                        "status": "complete",
                        "plugins": {},
                        "models": ["model-a", "model-b"],
                        "rendered": {},
                        "failures": [],
                    }
                ),
                encoding="utf-8",
            )

            archive_path = self.runner.resolve_archive_path(repo, archive_id)
            manifest = self.runner.parse_archive_manifest(archive_path / "manifest.json")

            self.assertEqual(archive_path, archive)
            self.assertEqual(manifest.models, ("model-a", "model-b"))

    def test_archive_project_matrix_includes_archived_model_report(self):
        with tempfile.TemporaryDirectory() as tmp:
            repo = Path(tmp)
            project = repo / "fixture" / "e2e"
            archive_id = "20260709T000000Z-1234abcd"
            run_id = "20260709-model-a-discovery"
            archive = repo / "e2e" / "artifacts" / archive_id
            report_path = "plugins/fixture/models/model-a/reports/20260709-model-a-discovery.json"

            (project / "assemblies").mkdir(parents=True)
            (project / "evals").mkdir(parents=True)
            (project / "ci.sh").write_text("#!/usr/bin/env bash\nexit 0\n", encoding="utf-8")
            (project / "assemblies" / "discovery.yaml").write_text(
                "name: discovery\nmodel: model-a\n",
                encoding="utf-8",
            )
            (project / "evals" / "discovery.yaml").write_text(
                '- name: fixture-skill\n'
                '  assert:\n'
                '    - type: text_contains, value: "fixture:skill"\n',
                encoding="utf-8",
            )
            (archive / "plugins" / "fixture" / "models" / "model-a" / "reports").mkdir(
                parents=True
            )
            (archive / report_path).write_text(
                json.dumps(discovery_report("model-a", run_id)),
                encoding="utf-8",
            )
            (archive / "manifest.json").write_text(
                json.dumps(
                    {
                        "schema_version": 1,
                        "run_id": archive_id,
                        "created_at": "2026-07-09T00:00:00Z",
                        "status": "complete",
                        "plugins": {
                            "fixture": {
                                "path": "fixture/e2e",
                                "models": {
                                    "model-a": {
                                        "slug": "model-a",
                                        "suites": {
                                            "discovery": {
                                                "status": "complete",
                                                "run_id": run_id,
                                                "input_paths": [],
                                                "run_paths": [],
                                                "report_paths": [report_path],
                                                "comparison_paths": [],
                                                "command_records": [],
                                            }
                                        },
                                    }
                                },
                            }
                        },
                        "models": ["model-a"],
                        "rendered": {},
                        "failures": [],
                    }
                ),
                encoding="utf-8",
            )

            matrix = self.runner.archive_project_matrix(
                self.runner.EvalRunArchive.open(archive),
                [self.runner.Project("fixture", project, project / "ci.sh")],
                ["model-a"],
            )

            self.assertIs(matrix["fixture:skill"]["model-a"].discovery_pass, True)

    def test_invocation_icons_categorize_comparison_assertions(self):
        self.assertEqual(
            self.runner.comparison_invocation_icons(
                {
                    "assertions": [
                        {"change": "Improved"},
                        {"change": "UnchangedPass"},
                        {"change": "Regressed"},
                        {"change": "UnchangedFail"},
                        {"arm_a": "error", "arm_b": "pass"},
                    ]
                }
            ),
            ("🥇", "🗡️", "👎", "💥", "⚠️"),
        )

    def test_report_splits_discovery_and_invocation_cells_as_html(self):
        cell = self.runner.ResourceCell(discovery_pass=False, invocation_icons=("🥇", "🗡️", "👎"))
        ok_cell = self.runner.ResourceCell(discovery_pass=True, invocation_icons=("💥", "⚠️", "🥇"))
        matrix = {
            "developer:ailly research": {"haiku": cell},
            "developer:ailly cleanup": {"haiku": ok_cell},
        }

        report = self.runner.format_report(["haiku"], matrix, {}, [])

        self.assertIn('<figure class="e2e-report">', report)
        self.assertIn('<th class="e2e-model" colspan="2" scope="colgroup">haiku</th>', report)
        self.assertIn('<th scope="col">Discover</th>', report)
        self.assertIn('<th scope="col">Invoke</th>', report)
        self.assertIn(
            '<td class="e2e-discovery">⛔️</td>\n<td class="e2e-invocation">🥇🗡️👎</td>',
            report,
        )
        self.assertIn(
            '<td class="e2e-discovery">✅</td>\n<td class="e2e-invocation">💥⚠️🥇</td>',
            report,
        )
        self.assertIn("position: sticky;", report)
        self.assertNotRegex(report, r">\s*-?\d+%</td>")


if __name__ == "__main__":
    unittest.main()
