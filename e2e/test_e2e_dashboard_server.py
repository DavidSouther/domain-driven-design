#!/usr/bin/env python3

import importlib.util
import json
import sys
import tempfile
import unittest
from pathlib import Path


REPO = Path(__file__).resolve().parents[1]
SCRIPT = REPO / "e2e" / "serve_e2e_dashboard.py"


def load_server():
    sys.path.insert(0, str(SCRIPT.parent))
    spec = importlib.util.spec_from_file_location("serve_e2e_dashboard", SCRIPT)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


def write_fixture_project(repo: Path) -> Path:
    project = repo / "fixture" / "e2e"
    (project / "assemblies").mkdir(parents=True)
    (project / "evals" / "scripts").mkdir(parents=True)
    (project / "prompts" / "invocation").mkdir(parents=True)
    (project / "ci.sh").write_text("#!/usr/bin/env bash\nexit 0\n", encoding="utf-8")
    (project / "assemblies" / "discovery.yaml").write_text(
        "name: discovery\nmodel: model-a\n",
        encoding="utf-8",
    )
    (project / "assemblies" / "baseline.yaml").write_text(
        "name: baseline\nmodel: model-a\nmatrix:\n  skill:\n    - skill\n",
        encoding="utf-8",
    )
    (project / "assemblies" / "invocation.yaml").write_text(
        "name: invocation\nmodel: model-a\n"
        "matrix:\n"
        "  skill:\n"
        "    - skill\n"
        "conversation:\n"
        '  - { role: user, path: "prompts/invocation/{{ skill }}.md" }\n',
        encoding="utf-8",
    )
    (project / "evals" / "discovery.yaml").write_text(
        '- name: skill\n'
        '  assert:\n'
        '    - type: text_contains, value: "fixture:skill"\n',
        encoding="utf-8",
    )
    (project / "evals" / "invocation.yaml").write_text(
        "name: invocation\n"
        "cases:\n"
        "  - name: skill\n"
        "    assertions:\n"
        "      - { type: script, runtime: python, script: { path: evals/scripts/check_skill.py } }\n",
        encoding="utf-8",
    )
    (project / "evals" / "scripts" / "check_skill.py").write_text(
        "print('ok')\n",
        encoding="utf-8",
    )
    (project / "prompts" / "invocation" / "skill.md").write_text("Use fixture:skill\n", encoding="utf-8")
    return project


def write_fixture_archive(repo: Path) -> Path:
    archive_id = "20260710T000001Z-aaaa1111"
    archive = repo / "e2e" / "artifacts" / archive_id
    model_root = archive / "plugins" / "fixture" / "models" / "model-a"
    (model_root / "reports").mkdir(parents=True)
    (model_root / "commands").mkdir(parents=True)
    (model_root / "runs" / "run-baseline").mkdir(parents=True)
    (model_root / "runs" / "run-invocation").mkdir(parents=True)
    (model_root / "inputs" / "evals" / "scripts").mkdir(parents=True)
    (model_root / "inputs" / "prompts" / "invocation").mkdir(parents=True)
    (model_root / "commands" / "001-run.stdout.txt").write_text("ran\n", encoding="utf-8")
    (model_root / "commands" / "001-run.stderr.txt").write_text("", encoding="utf-8")
    (model_root / "runs" / "run-baseline" / "skill.yaml").write_text(
        "---\n"
        "role: user\n"
        "content: |\n"
        "  Use fixture:skill\n"
        "---\n"
        "role: assistant\n"
        "content: |\n"
        "  Baseline assistant response\n",
        encoding="utf-8",
    )
    (model_root / "runs" / "run-invocation" / "transcript.json").write_text("{}", encoding="utf-8")
    (model_root / "runs" / "run-invocation" / "skill.yaml").write_text(
        "---\n"
        "role: user\n"
        "content: |\n"
        "  Use fixture:skill\n"
        "---\n"
        "role: assistant\n"
        "content: |\n"
        "  Actual assistant response\n",
        encoding="utf-8",
    )
    (model_root / "inputs" / "evals" / "invocation.yaml").write_text(
        "cases:\n"
        "  - name: skill\n"
        "    assertions:\n"
        "      - { type: script, runtime: python, script: { path: evals/scripts/check_skill.py } }\n",
        encoding="utf-8",
    )
    (model_root / "inputs" / "evals" / "scripts" / "check_skill.py").write_text(
        "print('archived checker')\n",
        encoding="utf-8",
    )
    (model_root / "inputs" / "prompts" / "invocation" / "skill.md").write_text(
        "Use fixture:skill\n",
        encoding="utf-8",
    )
    (model_root / "reports" / "run-discovery.json").write_text(
        json.dumps(
            {
                "suite": "discovery",
                "model": "model-a",
                "run_id": "run-discovery",
                "cases": [{"name": "skill", "matches": [{"assertions": [{"outcome": "pass"}]}]}],
            }
        ),
        encoding="utf-8",
    )
    (model_root / "reports" / "run-invocation.json").write_text(
        json.dumps({"suite": "invocation", "model": "model-a", "run_id": "run-invocation", "cases": []}),
        encoding="utf-8",
    )
    (model_root / "reports" / "comparison.json").write_text(
        json.dumps(
            {
                "arm_a": {"run_id": "run-baseline"},
                "arm_b": {"run_id": "run-invocation"},
                "cases": [
                    {
                        "case": "skill",
                        "assertions": [
                            {
                                "class": "script",
                                "change": "UnchangedPass",
                                "arm_a": "pass",
                                "arm_b": "pass",
                                "reason": "script passed with the skill loaded",
                            },
                            {
                                "class": "judge",
                                "change": "Improved",
                                "arm_a": "fail",
                                "arm_b": "pass",
                                "reason": "judge accepted the invocation response",
                            },
                            {
                                "class": "tokens",
                                "change": "UnchangedPass",
                                "arm_a": "pass",
                                "arm_b": "pass",
                                "reason": "invocation stayed within the token budget",
                            }
                        ],
                    }
                ]
            }
        ),
        encoding="utf-8",
    )
    command = {
        "sequence": 1,
        "step": "run",
        "args": ["ailly", "run"],
        "cwd": str(repo),
        "started_at": "2026-07-10T00:00:00Z",
        "finished_at": "2026-07-10T00:00:01Z",
        "returncode": 0,
        "stdout_path": "plugins/fixture/models/model-a/commands/001-run.stdout.txt",
        "stderr_path": "plugins/fixture/models/model-a/commands/001-run.stderr.txt",
    }
    (archive / "manifest.json").write_text(
        json.dumps(
            {
                "schema_version": 1,
                "run_id": archive_id,
                "created_at": "2026-07-10T00:00:00Z",
                "source_snapshot": "snapshot-a",
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
                                        "run_id": "run-discovery",
                                        "input_paths": [],
                                        "run_paths": [],
                                        "report_paths": [
                                            "plugins/fixture/models/model-a/reports/run-discovery.json"
                                        ],
                                        "comparison_paths": [],
                                        "command_records": [],
                                    },
                                    "baseline": {
                                        "status": "complete",
                                        "run_id": "run-baseline",
                                        "input_paths": [],
                                        "run_paths": ["plugins/fixture/models/model-a/runs/run-baseline"],
                                        "report_paths": [],
                                        "comparison_paths": [],
                                        "command_records": [],
                                    },
                                    "invocation": {
                                        "status": "complete",
                                        "run_id": "run-invocation",
                                        "input_paths": [
                                            "plugins/fixture/models/model-a/inputs/evals/invocation.yaml",
                                            "plugins/fixture/models/model-a/inputs/evals/scripts/check_skill.py",
                                            "plugins/fixture/models/model-a/inputs/prompts/invocation/skill.md",
                                        ],
                                        "run_paths": ["plugins/fixture/models/model-a/runs/run-invocation"],
                                        "report_paths": [
                                            "plugins/fixture/models/model-a/reports/run-invocation.json"
                                        ],
                                        "comparison_paths": [
                                            "plugins/fixture/models/model-a/reports/comparison.json"
                                        ],
                                        "command_records": [command],
                                    },
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
    return archive


class E2EDashboardServerTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.server = load_server()

    def test_state_builds_tactical_rows_from_archive_group(self):
        with tempfile.TemporaryDirectory() as tmp:
            repo = Path(tmp)
            write_fixture_project(repo)
            write_fixture_archive(repo)

            state = self.server.build_state(repo, None)

            self.assertEqual(state["selected_group"], "snapshot-a")
            self.assertEqual(state["models"], ["model-a"])
            self.assertEqual(state["rows"][0]["resource"], "fixture:skill")
            self.assertEqual(state["rows"][0]["cells"]["model-a"]["discovery"], "✅")
            self.assertEqual(state["rows"][0]["cells"]["model-a"]["invocation"], "✅🥇💵")
            self.assertNotIn("spark", state["rows"][0]["summary"])
            self.assertNotIn("Signal Strip", self.server.APP_HTML)
            self.assertIn("statusBaubles", self.server.APP_HTML)
            self.assertIn("renderTranscripts", self.server.APP_HTML)
            self.assertIn("renderEvaluatorResults", self.server.APP_HTML)
            self.assertIn("💵", self.server.APP_HTML)
            self.assertIn("🔥", self.server.APP_HTML)

    def test_cell_detail_exposes_session_commands_and_evaluators(self):
        with tempfile.TemporaryDirectory() as tmp:
            repo = Path(tmp)
            write_fixture_project(repo)
            write_fixture_archive(repo)

            detail = self.server.build_cell_detail(
                repo,
                None,
                "snapshot-a",
                "fixture:skill",
                "model-a",
                "invocation",
            )
            evidence = detail["evidence"][0]

            self.assertEqual(evidence["cases"][0]["case"], "skill")
            self.assertEqual(evidence["commands"][0]["stdout"]["content"], "ran\n")
            self.assertEqual(
                [(arm["label"], arm["run_id"]) for arm in evidence["session_arms"]],
                [("baseline", "run-baseline"), ("invocation", "run-invocation")],
            )
            self.assertEqual(
                {
                    (file["arm"], file["path"])
                    for file in evidence["session_files"]
                },
                {
                    ("baseline", "plugins/fixture/models/model-a/runs/run-baseline/skill.yaml"),
                    ("invocation", "plugins/fixture/models/model-a/runs/run-invocation/skill.yaml"),
                },
            )
            transcripts = {transcript["arm"]: transcript for transcript in evidence["transcripts"]}
            self.assertEqual(
                transcripts["baseline"]["path"],
                "plugins/fixture/models/model-a/runs/run-baseline/skill.yaml",
            )
            self.assertEqual(
                transcripts["baseline"]["messages"][1]["content"],
                "Baseline assistant response",
            )
            self.assertEqual(
                transcripts["invocation"]["path"],
                "plugins/fixture/models/model-a/runs/run-invocation/skill.yaml",
            )
            self.assertEqual(transcripts["invocation"]["messages"][1]["role"], "assistant")
            self.assertEqual(transcripts["invocation"]["messages"][1]["content"], "Actual assistant response")
            self.assertEqual(evidence["evaluator_results"][0]["evaluator"], "script")
            self.assertEqual(evidence["evaluator_results"][0]["baseline"], "pass")
            self.assertEqual(evidence["evaluator_results"][0]["invocation"], "pass")
            self.assertEqual(evidence["evaluator_results"][0]["change"], "UnchangedPass")
            self.assertEqual(evidence["evaluator_results"][0]["icon"], "✅")
            self.assertEqual(evidence["evaluator_results"][1]["evaluator"], "judge")
            self.assertEqual(evidence["evaluator_results"][1]["baseline"], "fail")
            self.assertEqual(evidence["evaluator_results"][1]["invocation"], "pass")
            self.assertEqual(evidence["evaluator_results"][1]["change"], "Improved")
            self.assertEqual(evidence["evaluator_results"][1]["icon"], "🥇")
            self.assertEqual(evidence["evaluator_results"][2]["evaluator"], "tokens")
            self.assertEqual(evidence["evaluator_results"][2]["icon"], "💵")
            self.assertIn("archived checker", evidence["evaluators"][1]["preview"]["content"])

    def test_cell_detail_falls_back_to_checkout_transcript_when_archive_has_empty_assistant(self):
        with tempfile.TemporaryDirectory() as tmp:
            repo = Path(tmp)
            write_fixture_project(repo)
            write_fixture_archive(repo)
            archived = (
                repo
                / "e2e"
                / "artifacts"
                / "20260710T000001Z-aaaa1111"
                / "plugins"
                / "fixture"
                / "models"
                / "model-a"
                / "runs"
                / "run-invocation"
                / "skill.yaml"
            )
            archived.write_text(
                "---\n"
                "role: user\n"
                "content: |\n"
                "  Use fixture:skill\n"
                "---\n"
                "role: assistant\n",
                encoding="utf-8",
            )
            checkout = repo / "fixture" / "e2e" / "runs" / "run-invocation" / "skill.yaml"
            checkout.parent.mkdir(parents=True)
            checkout.write_text(
                "---\n"
                "role: user\n"
                "content: |\n"
                "  Use fixture:skill\n"
                "---\n"
                "role: assistant\n"
                "content: |\n"
                "  Recovered checkout response\n",
                encoding="utf-8",
            )

            detail = self.server.build_cell_detail(
                repo,
                None,
                "snapshot-a",
                "fixture:skill",
                "model-a",
                "invocation",
            )
            transcript = next(
                item for item in detail["evidence"][0]["transcripts"]
                if item["arm"] == "invocation"
            )

            self.assertEqual(transcript["source"], "checkout")
            self.assertEqual(transcript["messages"][1]["content"], "Recovered checkout response")


if __name__ == "__main__":
    unittest.main()
