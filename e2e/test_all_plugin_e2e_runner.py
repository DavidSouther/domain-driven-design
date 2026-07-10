#!/usr/bin/env python3

import importlib.util
import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path
from types import SimpleNamespace


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


def comparison_report(case_name, assertions):
    return {
        "cases": [
            {
                "case": case_name,
                "assertions": assertions,
            }
        ]
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

    def test_source_snapshot_ignores_generated_archive_outputs(self):
        with tempfile.TemporaryDirectory() as tmp:
            repo = Path(tmp)
            subprocess.run(["git", "init"], cwd=repo, check=True, capture_output=True)
            (repo / "source.txt").write_text("source\n", encoding="utf-8")
            subprocess.run(["git", "add", "source.txt"], cwd=repo, check=True, capture_output=True)
            subprocess.run(
                [
                    "git",
                    "-c",
                    "user.name=Test",
                    "-c",
                    "user.email=test@example.com",
                    "commit",
                    "-m",
                    "initial",
                ],
                cwd=repo,
                check=True,
                capture_output=True,
            )
            clean_snapshot = self.runner.current_source_snapshot(repo)

            archive = repo / "e2e" / "artifacts" / "20260709T000001Z-aaaa1111"
            archive.mkdir(parents=True)
            (archive / "manifest.json").write_text("{}", encoding="utf-8")
            (repo / "e2e-dashboard.html").write_text("<html></html>\n", encoding="utf-8")

            self.assertEqual(self.runner.current_source_snapshot(repo), clean_snapshot)

            (repo / "source.txt").write_text("changed\n", encoding="utf-8")

            self.assertNotEqual(self.runner.current_source_snapshot(repo), clean_snapshot)

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

    def test_related_archives_consolidate_same_source_snapshot(self):
        with tempfile.TemporaryDirectory() as tmp:
            repo = Path(tmp)
            project = repo / "fixture" / "e2e"
            artifacts = repo / "e2e" / "artifacts"

            (project / "assemblies").mkdir(parents=True)
            (project / "evals").mkdir(parents=True)
            (project / "ci.sh").write_text("#!/usr/bin/env bash\nexit 0\n", encoding="utf-8")
            (project / "assemblies" / "discovery.yaml").write_text(
                "name: discovery\nmodel: model-a\n",
                encoding="utf-8",
            )
            for suite_name in ("baseline", "invocation"):
                (project / "assemblies" / f"{suite_name}.yaml").write_text(
                    f"name: {suite_name}\n"
                    "model: model-a\n"
                    "matrix:\n"
                    "  skill:\n"
                    "    - skill\n",
                    encoding="utf-8",
                )
            (project / "evals" / "discovery.yaml").write_text(
                '- name: skill\n'
                '  assert:\n'
                '    - type: text_contains, value: "fixture:skill"\n',
                encoding="utf-8",
            )

            def write_archive(
                archive_id,
                created_at,
                snapshot,
                comparison_assertions,
                include_discovery=False,
            ):
                archive = artifacts / archive_id
                reports = archive / "plugins" / "fixture" / "models" / "model-a" / "reports"
                reports.mkdir(parents=True)
                suites = {
                    "invocation": {
                        "status": "complete",
                        "run_id": f"{archive_id}-invocation",
                        "input_paths": [],
                        "run_paths": [],
                        "report_paths": [],
                        "comparison_paths": [
                            f"plugins/fixture/models/model-a/reports/{archive_id}-comparison.json"
                        ],
                        "command_records": [],
                    }
                }
                (reports / f"{archive_id}-comparison.json").write_text(
                    json.dumps(comparison_report("skill", comparison_assertions)),
                    encoding="utf-8",
                )
                if include_discovery:
                    suites["discovery"] = {
                        "status": "complete",
                        "run_id": f"{archive_id}-discovery",
                        "input_paths": [],
                        "run_paths": [],
                        "report_paths": [
                            f"plugins/fixture/models/model-a/reports/{archive_id}-discovery.json"
                        ],
                        "comparison_paths": [],
                        "command_records": [],
                    }
                    (reports / f"{archive_id}-discovery.json").write_text(
                        json.dumps(
                            {
                                "suite": "discovery",
                                "model": "model-a",
                                "run_id": f"{archive_id}-discovery",
                                "cases": [
                                    {
                                        "name": "skill",
                                        "matches": [
                                            {"assertions": [{"outcome": "pass"}]},
                                        ],
                                    },
                                ],
                            }
                        ),
                        encoding="utf-8",
                    )
                (archive / "manifest.json").write_text(
                    json.dumps(
                        {
                            "schema_version": 1,
                            "run_id": archive_id,
                            "created_at": created_at,
                            "source_snapshot": snapshot,
                            "status": "complete",
                            "plugins": {
                                "fixture": {
                                    "path": "fixture/e2e",
                                    "models": {
                                        "model-a": {
                                            "slug": "model-a",
                                            "suites": suites,
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

            write_archive(
                "20260709T000001Z-aaaa1111",
                "2026-07-09T00:00:01Z",
                "snapshot-a",
                [{"class": "judge", "arm_a": "fail", "arm_b": "pass"}],
                include_discovery=True,
            )
            write_archive(
                "20260709T000002Z-bbbb2222",
                "2026-07-09T00:00:02Z",
                "snapshot-a",
                [{"class": "judge", "arm_a": "pass", "arm_b": "fail"}],
            )
            write_archive(
                "20260709T000003Z-cccc3333",
                "2026-07-09T00:00:03Z",
                "snapshot-b",
                [{"class": "judge", "arm_a": "fail", "arm_b": "fail"}],
            )

            archives = self.runner.related_archives_from_arg(
                repo,
                "20260709T000001Z-aaaa1111",
            )
            models = self.runner.archive_group_models(archives, {"fixture"})
            matrix = self.runner.archive_group_matrix(
                archives,
                [self.runner.Project("fixture", project, project / "ci.sh")],
                models,
            )
            cell = matrix["fixture:skill"]["model-a"]

            self.assertEqual(
                [str(archive.manifest.run_id) for archive in archives],
                ["20260709T000001Z-aaaa1111", "20260709T000002Z-bbbb2222"],
            )
            self.assertEqual(models, ["model-a"])
            self.assertIs(cell.discovery_pass, True)
            self.assertEqual(cell.invocation_icons, ("⁇", "🥇", "⁇", "⁇", "👎", "⁇"))
            self.assertEqual(
                [evidence.archive_id for evidence in self.runner.cell_evidence(cell, "invocation")],
                ["20260709T000001Z-aaaa1111", "20260709T000002Z-bbbb2222"],
            )

    def test_live_archive_capture_writes_manifest_events_command_streams_and_reports(self):
        with tempfile.TemporaryDirectory() as tmp:
            repo = Path(tmp)
            project = repo / "fixture" / "e2e"
            run_id = "20260709-model-a-discovery"

            (project / "assemblies").mkdir(parents=True)
            (project / "evals" / "reports").mkdir(parents=True)
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
            report = project / "evals" / "reports" / f"{run_id}.json"
            report.write_text(json.dumps(discovery_report("model-a", run_id)), encoding="utf-8")
            archive = self.runner.EvalRunArchive.create(
                repo,
                self.runner.RunId("20260709T000000Z-1234abcd"),
                "2026-07-09T00:00:00Z",
            )
            suite = self.runner.parse_suite(project / "assemblies" / "discovery.yaml")
            unit = self.runner.ArchiveUnit(
                self.runner.Project("fixture", project, project / "ci.sh"),
                "model-a",
                self.runner.ModelSlug("model-a"),
                suite,
            )
            command_result = subprocess.CompletedProcess(
                args=("ailly", "eval", "discovery"),
                returncode=0,
                stdout="ok\n",
                stderr="",
            )

            archive.begin_unit(unit)
            input_paths = archive.capture_inputs(unit)
            command = archive.record_command(unit, "eval", command_result)
            report_path = archive.capture_report(unit, report)
            archive.finish_unit(
                unit,
                self.runner.ArchiveSuiteRecord(
                    status="complete",
                    run_id=run_id,
                    input_paths=input_paths,
                    run_paths=(),
                    report_paths=(report_path,),
                    comparison_paths=(),
                    command_records=(command,),
                ),
            )
            archive.finish_run("complete")

            reloaded = self.runner.EvalRunArchive.open(archive.root)
            suite_record = reloaded.manifest.plugins["fixture"].models["model-a"].suites["discovery"]
            events = (archive.root / "events.jsonl").read_text(encoding="utf-8")

            self.assertEqual(reloaded.manifest.status, "complete")
            self.assertEqual(suite_record.status, "complete")
            self.assertEqual(suite_record.report_paths, (report_path,))
            self.assertEqual(suite_record.command_records[0].stdout_path, command.stdout_path)
            self.assertEqual((archive.root / command.stdout_path).read_text(encoding="utf-8"), "ok\n")
            self.assertIn("unit_finished", events)
            self.assertIn("run_finished", events)

    def test_live_archive_captures_run_directory_after_model_responses_are_written(self):
        with tempfile.TemporaryDirectory() as tmp:
            repo = Path(tmp)
            project_path = repo / "fixture" / "e2e"
            (project_path / "assemblies").mkdir(parents=True)
            (project_path / "evals" / "scripts").mkdir(parents=True)
            (project_path / "ci.sh").write_text("#!/usr/bin/env bash\nexit 0\n", encoding="utf-8")
            (project_path / "assemblies" / "discovery.yaml").write_text(
                "name: discovery\nmodel: model-a\n",
                encoding="utf-8",
            )
            (project_path / "assemblies" / "baseline.yaml").write_text(
                "name: baseline\nmodel: model-a\nmatrix:\n  skill:\n    - skill\n",
                encoding="utf-8",
            )
            (project_path / "assemblies" / "invocation.yaml").write_text(
                "name: invocation\nmodel: model-a\nmatrix:\n  skill:\n    - skill\n",
                encoding="utf-8",
            )
            (project_path / "evals" / "discovery.yaml").write_text(
                '- name: fixture-skill\n'
                '  assert:\n'
                '    - type: text_contains, value: "fixture:skill"\n',
                encoding="utf-8",
            )
            for suite in ("baseline", "invocation"):
                (project_path / "evals" / f"{suite}.yaml").write_text(
                    "cases:\n"
                    "  - name: skill\n"
                    "    assertions:\n"
                    "      - { type: script, runtime: python, script: { path: evals/scripts/check_skill.py } }\n",
                    encoding="utf-8",
                )
            (project_path / "evals" / "scripts" / "check_skill.py").write_text(
                "print('ok')\n",
                encoding="utf-8",
            )

            original_repo = self.runner.REPO
            original_run_command = self.runner.run_command

            def fake_run_command(cmd, cwd, continue_on_error):
                if "assemble" in cmd:
                    suite = cmd[-1]
                    run_dir = project_path / "runs" / f"run-{suite}"
                    run_dir.mkdir(parents=True, exist_ok=True)
                    case = "fixture-skill" if suite == "discovery" else "skill"
                    (run_dir / f"{case}.yaml").write_text(
                        "---\n"
                        "role: user\n"
                        "content: |\n"
                        "  prompt\n"
                        "---\n"
                        "role: assistant\n",
                        encoding="utf-8",
                    )
                elif "run" in cmd:
                    run_dir = Path(cmd[-1])
                    for transcript in run_dir.glob("*.yaml"):
                        transcript.write_text(
                            transcript.read_text(encoding="utf-8")
                            + "content: |\n"
                            + f"  filled response for {transcript.stem}\n",
                            encoding="utf-8",
                        )
                elif "eval" in cmd:
                    suite = cmd[cmd.index("eval") + 1]
                    run_dir = Path(cmd[-1])
                    reports = project_path / "evals" / "reports"
                    reports.mkdir(parents=True, exist_ok=True)
                    case = "fixture-skill" if suite == "discovery" else "skill"
                    (reports / f"{run_dir.name}.json").write_text(
                        json.dumps(
                            {
                                "suite": suite,
                                "model": "model-a",
                                "run_id": run_dir.name,
                                "cases": [
                                    {
                                        "name": case,
                                        "matches": [{"assertions": [{"outcome": "pass"}]}],
                                    }
                                ],
                            }
                        ),
                        encoding="utf-8",
                    )
                elif "report" in cmd and "--label-a" in cmd:
                    report_index = cmd.index("report")
                    run_id_a = cmd[report_index + 1]
                    run_id_b = cmd[report_index + 2]
                    reports = project_path / "evals" / "reports"
                    reports.mkdir(parents=True, exist_ok=True)
                    (reports / f"{run_id_a}-vs-{run_id_b}.json").write_text(
                        json.dumps(
                            {
                                "cases": [
                                    {
                                        "case": "skill",
                                        "assertions": [
                                            {"class": "script", "arm_a": "fail", "arm_b": "pass"}
                                        ],
                                    }
                                ]
                            }
                        ),
                        encoding="utf-8",
                    )
                return subprocess.CompletedProcess(cmd, 0, "ok\n", "")

            archive = self.runner.EvalRunArchive.create_at(
                repo / "e2e" / "artifacts" / "archive",
                self.runner.RunId("archive"),
                "2026-07-10T00:00:00Z",
                "snapshot",
            )
            project = self.runner.Project("fixture", project_path, project_path / "ci.sh")
            args = SimpleNamespace(dry_run=False, continue_on_error=False, ailly_bin="ailly")

            try:
                self.runner.REPO = repo
                self.runner.run_command = fake_run_command
                self.runner.run_model_project(args, project, "model-a", archive)
            finally:
                self.runner.REPO = original_repo
                self.runner.run_command = original_run_command

            reloaded = self.runner.EvalRunArchive.open(archive.root)
            suite_record = reloaded.manifest.plugins["fixture"].models["model-a"].suites["invocation"]
            archived_run = archive.root / suite_record.run_paths[0] / "skill.yaml"

            self.assertIn("filled response for skill", archived_run.read_text(encoding="utf-8"))

    def test_invocation_icons_categorize_comparison_assertions(self):
        self.assertEqual(
            self.runner.comparison_invocation_icons(
                {
                    "assertions": [
                        {"class": "script", "arm_a": "fail", "arm_b": "pass"},
                        {"class": "judge", "change": "Improved"},
                        {"class": "tokens", "arm_b": "pass"},
                    ]
                }
            ),
            ("✅", "🥇", "💵"),
        )
        self.assertEqual(
            self.runner.comparison_invocation_icons(
                {
                    "assertions": [
                        {"class": "static", "arm_b": "fail"},
                        {"class": "judge", "change": "Regressed"},
                        {"class": "tokens", "arm_b": "fail"},
                    ]
                }
            ),
            ("⛔️", "👎", "🔥"),
        )
        self.assertEqual(
            self.runner.comparison_invocation_icons(
                {
                    "assertions": [
                        {"class": "judge", "change": "UnchangedFail"},
                    ]
                }
            ),
            ("⁇", "💥", "⁇"),
        )
        self.assertEqual(
            self.runner.comparison_invocation_icons(
                {"assertions": [{"class": "unexpected", "arm_b": "pass"}]}
            ),
            ("⁇", "⁇", "⁇"),
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
        self.assertIn("<th>Ailly Good</th><th>Bad</th>", report)
        self.assertIn("position: sticky;", report)
        self.assertNotRegex(report, r">\s*-?\d+%</td>")

    def test_report_cells_with_archive_evidence_open_drilldown(self):
        evidence = self.runner.CellEvidence(
            kind="invocation",
            archive_id="20260709T000001Z-aaaa1111",
            suite="invocation",
            path="plugins/fixture/models/model-a/reports/comparison.json",
            href="file:///tmp/archive/comparison.json",
        )
        cell = self.runner.ResourceCell(
            discovery_pass=True,
            invocation_icons=("🥇",),
            evidence=(evidence,),
        )

        report = self.runner.format_report(["model-a"], {"fixture:skill": {"model-a": cell}}, {}, [])

        self.assertIn('data-e2e-detail="e2e-detail-fixture-skill-model-a-invocation"', report)
        self.assertIn("Report drilldown", report)
        self.assertIn("file:///tmp/archive/comparison.json", report)
        self.assertIn("plugins/fixture/models/model-a/reports/comparison.json", report)


if __name__ == "__main__":
    unittest.main()
