#!/usr/bin/env python3

import json
import importlib.util
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


class E2EArchiveDurabilityTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.runner = load_runner()

    def test_archive_from_existing_renders_reports_after_scratch_cleanup(self):
        with tempfile.TemporaryDirectory() as tmp:
            repo = Path(tmp)
            project = repo / "fixture" / "e2e"
            reports = project / "evals" / "reports"
            archive_id = "20260709T000000Z-1234abcd"
            archive = repo / "e2e" / "artifacts" / archive_id
            run_a = "20260709-model-a-discovery"
            run_b = "20260709-model-b-discovery"
            report_a = discovery_report("model-a", run_a)
            report_b = discovery_report("model-b", run_b)

            (project / "assemblies").mkdir(parents=True)
            (project / "evals").mkdir(parents=True)
            (project / "runs" / f"{run_a}-discovery").mkdir(parents=True)
            reports.mkdir(parents=True)
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
            (reports / f"{run_a}.json").write_text(json.dumps(report_a), encoding="utf-8")

            for model, run_id, report in (("model-a", run_a, report_a), ("model-b", run_b, report_b)):
                model_root = archive / "plugins" / "fixture" / "models" / model
                (model_root / "inputs" / "assemblies").mkdir(parents=True, exist_ok=True)
                (model_root / "inputs" / "evals").mkdir(parents=True, exist_ok=True)
                (model_root / "reports").mkdir(parents=True, exist_ok=True)
                (model_root / "runs" / f"{run_id}-discovery").mkdir(parents=True, exist_ok=True)
                (model_root / "commands").mkdir(parents=True, exist_ok=True)
                (model_root / "inputs" / "assemblies" / "discovery.yaml").write_text(
                    "name: discovery\nmodel: " + model + "\n",
                    encoding="utf-8",
                )
                (model_root / "inputs" / "evals" / "discovery.yaml").write_text(
                    '- name: fixture-skill\n'
                    '  assert:\n'
                    '    - type: text_contains, value: "fixture:skill"\n',
                    encoding="utf-8",
                )
                (model_root / "reports" / f"{run_id}.json").write_text(
                    json.dumps(report),
                    encoding="utf-8",
                )

            archive.mkdir(parents=True, exist_ok=True)
            (archive / "events.jsonl").write_text("", encoding="utf-8")
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
                                                "run_id": run_a,
                                                "input_paths": [
                                                    "plugins/fixture/models/model-a/inputs/assemblies/discovery.yaml",
                                                    "plugins/fixture/models/model-a/inputs/evals/discovery.yaml",
                                                ],
                                                "run_paths": [
                                                    f"plugins/fixture/models/model-a/runs/{run_a}-discovery"
                                                ],
                                                "report_paths": [
                                                    f"plugins/fixture/models/model-a/reports/{run_a}.json"
                                                ],
                                                "comparison_paths": [],
                                                "command_records": [],
                                            }
                                        },
                                    },
                                    "model-b": {
                                        "slug": "model-b",
                                        "suites": {
                                            "discovery": {
                                                "status": "complete",
                                                "run_id": run_b,
                                                "input_paths": [
                                                    "plugins/fixture/models/model-b/inputs/assemblies/discovery.yaml",
                                                    "plugins/fixture/models/model-b/inputs/evals/discovery.yaml",
                                                ],
                                                "run_paths": [
                                                    f"plugins/fixture/models/model-b/runs/{run_b}-discovery"
                                                ],
                                                "report_paths": [
                                                    f"plugins/fixture/models/model-b/reports/{run_b}.json"
                                                ],
                                                "comparison_paths": [],
                                                "command_records": [],
                                            }
                                        },
                                    },
                                },
                            }
                        },
                        "models": ["model-a", "model-b"],
                        "rendered": {},
                        "failures": [],
                    }
                ),
                encoding="utf-8",
            )

            original_repo = self.runner.REPO
            self.runner.REPO = repo
            self.runner.clean_project_outputs(
                self.runner.Project("fixture", project, project / "ci.sh")
            )
            (project / "runs" / f"{run_b}-discovery").mkdir(parents=True)
            reports.mkdir(parents=True)
            (reports / f"{run_b}.json").write_text(json.dumps(report_b), encoding="utf-8")
            output = repo / "rendered.md"

            try:
                exit_code = self.runner.main(
                    [
                        "--plugin",
                        "fixture",
                        "--from-existing",
                        "--archive",
                        archive_id,
                        "--report",
                        str(output),
                        "--skip-static",
                    ]
                )
            finally:
                self.runner.REPO = original_repo

            report = output.read_text(encoding="utf-8")
            self.assertEqual(exit_code, 0)
            self.assertIn(">model-a</th>", report)
            self.assertIn(">model-b</th>", report)
            self.assertIn(">fixture:skill</th>", report)


if __name__ == "__main__":
    unittest.main()
