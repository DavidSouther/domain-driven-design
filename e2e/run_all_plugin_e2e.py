#!/usr/bin/env python3

from __future__ import annotations

import argparse
import contextlib
import dataclasses
from datetime import datetime, timezone
import hashlib
import html
import json
import os
import re
import shutil
import subprocess
import sys
import uuid
from pathlib import Path
from typing import Callable, Iterable, NewType


REPO = Path(__file__).resolve().parents[1]
MODEL_RE = re.compile(r"^model:\s*(\S+)\s*$", re.MULTILINE)
NAME_RE = re.compile(r"^name:\s*(\S+)\s*$", re.MULTILINE)
CASE_RE = re.compile(r"^\s*-\s*name:\s*(\S+)\s*$")
MATRIX_AXIS_RE = re.compile(r"^\s{2}([a-zA-Z_][a-zA-Z0-9_-]*):\s*$")
MATRIX_VALUE_RE = re.compile(r"^\s{4}-\s*(\S+)\s*$")
PATH_VALUE_RE = re.compile(r"path:\s*(?:\"([^\"]+)\"|'([^']+)'|([^,}\s]+))")
TEXT_CONTAINS_RE = re.compile(r"type:\s*text_contains\b")
VALUE_RE = re.compile(r"value:\s*[\"']([^\"']+)[\"']")
RESOURCE_PATH_RE = re.compile(r"references/(?:patterns/)?([a-z][a-z0-9-]*(?:/[a-z][a-z0-9-]*)*)\.md")
SKILL_ID_RE = re.compile(r"\b([a-z][a-z0-9-]*):([a-z][a-z0-9-]*)\b")

DISCOVERY_PASS = "✅"
DISCOVERY_FAIL = "⛔️"
DISCOVERY_UNKNOWN = "⁇"
INVOCATION_WIN = "🥇"
INVOCATION_UNNEEDED = "🗡️"
INVOCATION_LOSS = "👎"
INVOCATION_NOISE = "💥"
INVOCATION_FAILURE = "⚠️"

INVOCATION_CHANGE_ICONS = {
    "Improved": INVOCATION_WIN,
    "UnchangedPass": INVOCATION_UNNEEDED,
    "Regressed": INVOCATION_LOSS,
    "UnchangedFail": INVOCATION_NOISE,
}


MODEL_FAMILIES: dict[str, tuple[str, ...]] = {
    "anthropic": (
        "claude-haiku-4-5",
        "claude-sonnet-4-6",
        "claude-sonnet-5",
        "claude-opus-4-8",
        "claude-fable-5",
    ),
    "openai": (
        "gpt-5.5",
        "gpt-5.4",
        "gpt-5.4-mini",
    ),
    "bedrock": (
        "bedrock:meta.llama3-3-70b-instruct-v1:0",
        "bedrock:meta.llama4-scout-17b-instruct-v1:0",
        "bedrock:mistral.mistral-large-3-675b-instruct",
        "bedrock:cohere.command-r-plus-v1:0",
    ),
}


@dataclasses.dataclass(frozen=True)
class Project:
    name: str
    path: Path
    static_ci: Path | None


@dataclasses.dataclass(frozen=True)
class Suite:
    name: str
    path: Path
    model: str | None
    axis: str | None
    cases: tuple[str, ...]
    prompt_paths: tuple[str, ...]
    prefix_paths: tuple[str, ...]


@dataclasses.dataclass
class ResourceCell:
    discovery_pass: bool | None = None
    invocation_icons: tuple[str, ...] = ()
    error: str | None = None


RunId = NewType("RunId", str)
ModelSlug = NewType("ModelSlug", str)


@dataclasses.dataclass(frozen=True)
class CommandRecord:
    sequence: int
    step: str
    args: tuple[str, ...]
    cwd: str
    started_at: str
    finished_at: str
    returncode: int
    stdout_path: str
    stderr_path: str


@dataclasses.dataclass(frozen=True)
class ArchiveSuiteRecord:
    status: str
    run_id: str | None
    input_paths: tuple[str, ...]
    run_paths: tuple[str, ...]
    report_paths: tuple[str, ...]
    comparison_paths: tuple[str, ...]
    command_records: tuple[CommandRecord, ...]


@dataclasses.dataclass(frozen=True)
class ArchiveModelRecord:
    slug: ModelSlug
    suites: dict[str, ArchiveSuiteRecord]


@dataclasses.dataclass(frozen=True)
class ArchivePluginRecord:
    path: str
    models: dict[str, ArchiveModelRecord]


@dataclasses.dataclass(frozen=True)
class ArchiveManifest:
    schema_version: int
    run_id: RunId
    created_at: str
    status: str
    plugins: dict[str, ArchivePluginRecord]
    models: tuple[str, ...]
    rendered: dict[str, str]
    failures: tuple[dict, ...]


@dataclasses.dataclass(frozen=True)
class ArchiveUnit:
    project: Project
    model: str
    model_slug: ModelSlug
    suite: Suite


@dataclasses.dataclass(frozen=True)
class EvalRunArchive:
    root: Path
    manifest: ArchiveManifest

    @classmethod
    def create(
        cls, repo: Path, run_id: RunId | None = None, created_at: str | None = None
    ) -> "EvalRunArchive":
        raise NotImplementedError("live archive creation is Step 4")

    @classmethod
    def open(cls, root: Path) -> "EvalRunArchive":
        return cls(root, parse_archive_manifest(root / "manifest.json"))

    def unit_root(self, project: Project, model_slug: ModelSlug) -> Path:
        return self.root / "plugins" / project.name / "models" / str(model_slug)

    def append_event(self, event_name: str, payload: dict) -> None:
        raise NotImplementedError("live archive events are Step 4")

    def write_manifest(self, manifest: ArchiveManifest) -> None:
        raise NotImplementedError("live archive manifest writes are Step 4")

    def begin_unit(self, unit: ArchiveUnit) -> None:
        raise NotImplementedError("live archive unit capture is Step 4")

    def record_command(
        self, unit: ArchiveUnit, step: str, result: subprocess.CompletedProcess[str]
    ) -> CommandRecord:
        raise NotImplementedError("live archive command capture is Step 4")

    def capture_inputs(self, unit: ArchiveUnit) -> tuple[str, ...]:
        raise NotImplementedError("live archive input capture is Step 4")

    def capture_run_dir(self, unit: ArchiveUnit, run_dir: Path) -> str:
        raise NotImplementedError("live archive run capture is Step 4")

    def capture_report(self, unit: ArchiveUnit, report_path: Path) -> str:
        raise NotImplementedError("live archive report capture is Step 4")

    def finish_unit(self, unit: ArchiveUnit, suite_record: ArchiveSuiteRecord) -> None:
        raise NotImplementedError("live archive unit completion is Step 4")

    def fail_unit(self, unit: ArchiveUnit, reason: str) -> None:
        raise NotImplementedError("live archive unit failure capture is Step 4")


def generate_run_id(
    now_utc: datetime | None = None,
    uuid_factory: Callable[[], uuid.UUID] = uuid.uuid4,
) -> RunId:
    instant = now_utc or datetime.now(timezone.utc)
    if instant.tzinfo is None:
        instant = instant.replace(tzinfo=timezone.utc)
    timestamp = instant.astimezone(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    return RunId(f"{timestamp}-{uuid_factory().hex[:8]}")


def model_slug(model: str, used_slugs: Iterable[str] = ()) -> ModelSlug:
    base = re.sub(r"[^a-z0-9]+", "-", model.lower()).strip("-") or "model"
    used = set(used_slugs)
    if base not in used:
        return ModelSlug(base)
    suffix = hashlib.sha1(model.encode("utf-8")).hexdigest()[:8]
    return ModelSlug(f"{base}-{suffix}")


def resolve_archive_path(repo: Path, archive_arg: str) -> Path:
    archive_path = Path(archive_arg)
    has_separator = "/" in archive_arg or (os.sep != "/" and os.sep in archive_arg)
    if archive_path.is_absolute() or has_separator:
        return archive_path
    return repo / "e2e" / "artifacts" / archive_arg


def command_record_from_json(data: dict) -> CommandRecord:
    return CommandRecord(
        sequence=int(data.get("sequence", 0)),
        step=str(data.get("step", "")),
        args=tuple(str(arg) for arg in data.get("args", ())),
        cwd=str(data.get("cwd", "")),
        started_at=str(data.get("started_at", "")),
        finished_at=str(data.get("finished_at", "")),
        returncode=int(data.get("returncode", 0)),
        stdout_path=str(data.get("stdout_path", "")),
        stderr_path=str(data.get("stderr_path", "")),
    )


def suite_record_from_json(data: dict) -> ArchiveSuiteRecord:
    return ArchiveSuiteRecord(
        status=str(data.get("status", "")),
        run_id=data.get("run_id"),
        input_paths=tuple(str(path) for path in data.get("input_paths", ())),
        run_paths=tuple(str(path) for path in data.get("run_paths", ())),
        report_paths=tuple(str(path) for path in data.get("report_paths", ())),
        comparison_paths=tuple(str(path) for path in data.get("comparison_paths", ())),
        command_records=tuple(
            command_record_from_json(record) for record in data.get("command_records", ())
        ),
    )


def model_record_from_json(data: dict) -> ArchiveModelRecord:
    suites = {
        suite_name: suite_record_from_json(suite_data)
        for suite_name, suite_data in data.get("suites", {}).items()
    }
    return ArchiveModelRecord(slug=ModelSlug(str(data.get("slug", ""))), suites=suites)


def plugin_record_from_json(data: dict) -> ArchivePluginRecord:
    models = {
        model_name: model_record_from_json(model_data)
        for model_name, model_data in data.get("models", {}).items()
    }
    return ArchivePluginRecord(path=str(data.get("path", "")), models=models)


def parse_archive_manifest(path: Path) -> ArchiveManifest:
    manifest_path = path / "manifest.json" if path.is_dir() else path
    data = json.loads(manifest_path.read_text(encoding="utf-8"))
    plugins = {
        plugin_name: plugin_record_from_json(plugin_data)
        for plugin_name, plugin_data in data.get("plugins", {}).items()
    }
    return ArchiveManifest(
        schema_version=int(data.get("schema_version", 0)),
        run_id=RunId(str(data.get("run_id", ""))),
        created_at=str(data.get("created_at", "")),
        status=str(data.get("status", "")),
        plugins=plugins,
        models=tuple(str(model) for model in data.get("models", ())),
        rendered={str(key): str(value) for key, value in data.get("rendered", {}).items()},
        failures=tuple(dict(failure) for failure in data.get("failures", ())),
    )


def fail(message: str) -> int:
    print(message, file=sys.stderr)
    return 1


def shell_env() -> dict[str, str]:
    env = os.environ.copy()
    env.setdefault("PYTHONUNBUFFERED", "1")
    return env


def ailly_command(args: argparse.Namespace) -> list[str]:
    if args.ailly_bin:
        return [args.ailly_bin]
    if os.environ.get("AILLY_BIN"):
        return [os.environ["AILLY_BIN"]]
    if os.environ.get("AILLY"):
        return [os.environ["AILLY"]]
    return ["ailly"]


def run_command(cmd: list[str], cwd: Path, continue_on_error: bool) -> subprocess.CompletedProcess[str]:
    print("+ " + " ".join(cmd))
    result = subprocess.run(
        cmd,
        cwd=cwd,
        env=shell_env(),
        text=True,
        capture_output=True,
    )
    if result.stdout:
        print(result.stdout, end="" if result.stdout.endswith("\n") else "\n")
    if result.stderr:
        print(result.stderr, end="" if result.stderr.endswith("\n") else "\n", file=sys.stderr)
    if result.returncode and not continue_on_error:
        raise subprocess.CalledProcessError(result.returncode, cmd, result.stdout, result.stderr)
    return result


def parse_matrix(text: str) -> tuple[str | None, tuple[str, ...]]:
    lines = text.splitlines()
    in_matrix = False
    axis: str | None = None
    values: list[str] = []
    for line in lines:
        if line.strip() == "matrix:":
            in_matrix = True
            continue
        if not in_matrix:
            continue
        if line and not line.startswith(" "):
            break
        axis_match = MATRIX_AXIS_RE.match(line)
        if axis_match:
            axis = axis_match.group(1)
            continue
        value_match = MATRIX_VALUE_RE.match(line)
        if axis and value_match:
            values.append(value_match.group(1))
    return axis, tuple(values)


def extract_path(line: str) -> str | None:
    match = PATH_VALUE_RE.search(line)
    if not match:
        return None
    return next(group for group in match.groups() if group)


def parse_prompt_paths(text: str) -> tuple[str, ...]:
    paths: list[str] = []
    in_conversation = False
    for line in text.splitlines():
        if line.strip() == "conversation:":
            in_conversation = True
            continue
        if not in_conversation:
            continue
        if line and not line.startswith(" "):
            break
        if "role:" in line and "path:" in line:
            path = extract_path(line)
            if path:
                paths.append(path)
    return tuple(paths)


def parse_prefix_paths(text: str) -> tuple[str, ...]:
    paths: list[str] = []
    in_prefix = False
    for line in text.splitlines():
        if line.strip() == "prefix:":
            in_prefix = True
            continue
        if not in_prefix:
            continue
        if line and not line.startswith(" "):
            break
        if "path:" in line:
            path = extract_path(line)
            if path:
                paths.append(path)
    return tuple(paths)


def parse_suite(path: Path) -> Suite:
    text = path.read_text(encoding="utf-8")
    name_match = NAME_RE.search(text)
    model_match = MODEL_RE.search(text)
    axis, matrix_cases = parse_matrix(text)
    cases = matrix_cases if matrix_cases else (path.stem,)
    return Suite(
        name=name_match.group(1) if name_match else path.stem,
        path=path,
        model=model_match.group(1) if model_match else None,
        axis=axis,
        cases=cases,
        prompt_paths=parse_prompt_paths(text),
        prefix_paths=parse_prefix_paths(text),
    )


def parse_eval_cases(path: Path) -> tuple[str, ...]:
    cases: list[str] = []
    for line in path.read_text(encoding="utf-8").splitlines():
        match = CASE_RE.match(line)
        if match:
            cases.append(match.group(1))
    return tuple(cases)


def parse_discovery_resources(path: Path, plugin: str) -> dict[str, set[str]]:
    resources: dict[str, set[str]] = {}
    current: str | None = None
    for line in path.read_text(encoding="utf-8").splitlines():
        case_match = CASE_RE.match(line)
        if case_match:
            current = case_match.group(1)
            continue
        if current is None or not TEXT_CONTAINS_RE.search(line):
            continue
        value_match = VALUE_RE.search(line)
        if not value_match:
            continue
        for resource in resources_from_assertion_value(plugin, value_match.group(1)):
            resources.setdefault(resource, set()).add(current)
    return resources


def resources_from_assertion_value(plugin: str, value: str) -> list[str]:
    resources: list[str] = []
    skill_match = SKILL_ID_RE.search(value)
    if skill_match:
        resources.append(f"{skill_match.group(1)}:{skill_match.group(2)}")
    path_match = RESOURCE_PATH_RE.search(value)
    if not path_match:
        return resources
    parts = path_match.group(1).split("/")
    if plugin == "developer":
        if parts[0] in {"phases", "abilities"}:
            parts = parts[1:]
        leaf = "-".join(parts)
        resources.append(f"developer:ailly {leaf}")
    elif plugin == "domain":
        leaf = "-".join(parts)
        resources.append(f"domain:using-domain {leaf}")
    elif plugin == "patterns":
        leaf = "-".join(parts)
        resources.append(f"patterns:using-patterns {leaf}")
    elif plugin == "research" and value.startswith("references/configuring/"):
        leaf = "-".join(parts)
        resources.append(f"research:using-research {leaf}")
    else:
        leaf = "-".join(parts)
        resources.append(f"{plugin}:{leaf}")
    return resources


def discover_projects(repo: Path) -> tuple[list[Project], list[Project]]:
    model_projects: list[Project] = []
    static_projects: list[Project] = []
    for ci in sorted(repo.glob("*/e2e/ci.sh")):
        project_dir = ci.parent
        if (project_dir / "assemblies").is_dir() and (project_dir / "evals").is_dir():
            model_projects.append(Project(project_dir.parent.name, project_dir, ci))
        else:
            static_projects.append(Project(project_dir.parent.name, project_dir, ci))
    return model_projects, static_projects


def suite_map(project: Project) -> dict[str, Suite]:
    return {
        parse_suite(path).name: parse_suite(path)
        for path in sorted((project.path / "assemblies").glob("*.yaml"))
    }


def eval_case_map(project: Project) -> dict[str, tuple[str, ...]]:
    return {
        path.stem: parse_eval_cases(path)
        for path in sorted((project.path / "evals").glob("*.yaml"))
    }


def baseline_for(suite_name: str, available: set[str]) -> str | None:
    if suite_name == "discovery" or suite_name.endswith("-baseline") or suite_name == "baseline":
        return None
    if suite_name == "invocation" and "baseline" in available:
        return "baseline"
    if suite_name.startswith("invocation-"):
        candidate = "baseline-" + suite_name.removeprefix("invocation-")
        return candidate if candidate in available else None
    candidate = f"{suite_name}-baseline"
    return candidate if candidate in available else None


def resource_name(project: Project, suite: Suite, case: str) -> str:
    if project.name == "developer":
        if suite.name == "invocation":
            return f"developer:{case}"
        if suite.axis is None:
            return f"developer:ailly {suite.name}"
        return f"developer:ailly {case}"
    if project.name == "domain":
        return f"domain:using-domain {case}"
    if project.name == "patterns":
        return f"patterns:using-patterns {case}"
    return f"{project.name}:{case}"


def project_resources(project: Project, suites: dict[str, Suite]) -> list[str]:
    resources: list[str] = []
    for suite in suites.values():
        if suite.name == "discovery" or suite.name.endswith("-baseline") or suite.name == "baseline":
            continue
        for case in suite.cases:
            resources.append(resource_name(project, suite, case))
    return sorted(dict.fromkeys(resources))


def validate_project(project: Project) -> list[str]:
    errors: list[str] = []
    suites = suite_map(project)
    eval_cases = eval_case_map(project)
    suite_names = set(suites)

    for suite in suites.values():
        if suite.name not in eval_cases:
            errors.append(f"{project.name}: missing eval suite for assembly {suite.name}")
            continue
        if suite.axis is not None:
            missing_eval_cases = set(suite.cases) - set(eval_cases[suite.name])
            extra_eval_cases = set(eval_cases[suite.name]) - set(suite.cases)
            if missing_eval_cases:
                errors.append(
                    f"{project.name}/{suite.name}: eval missing case(s): "
                    + ", ".join(sorted(missing_eval_cases))
                )
            if extra_eval_cases:
                errors.append(
                    f"{project.name}/{suite.name}: eval has case(s) not assembled: "
                    + ", ".join(sorted(extra_eval_cases))
                )
        cases_to_check = suite.cases if suite.axis is not None else ("",)
        for case in cases_to_check:
            for prompt in suite.prompt_paths:
                prompt_text = prompt
                if suite.axis is not None:
                    prompt_text = prompt_text.replace("{{ " + suite.axis + " }}", case)
                    prompt_text = prompt_text.replace("{{" + suite.axis + "}}", case)
                prompt_path = project.path / prompt_text
                if not prompt_path.is_file():
                    errors.append(
                        f"{project.name}/{suite.name}: missing prompt for {case}: "
                        f"{prompt_path.relative_to(REPO)}"
                    )

    for suite in suites.values():
        pair = baseline_for(suite.name, suite_names)
        if pair is None:
            continue
        if suite.axis is not None and tuple(suite.cases) != tuple(suites[pair].cases):
            errors.append(f"{project.name}: {pair} cases do not match {suite.name}")
    return errors


def prepare_project(project: Project, continue_on_error: bool) -> bool:
    commands: list[tuple[list[str], Path]] = []
    if (project.path / "vendor.py").is_file():
        commands.append(([sys.executable, str(project.path / "vendor.py")], REPO))
    vendor_sh = project.path / "evals" / "scripts" / "vendor.sh"
    disclosure_sh = project.path / "evals" / "scripts" / "gen_disclosure.sh"
    if vendor_sh.is_file():
        commands.append((["bash", str(vendor_sh)], REPO))
    if disclosure_sh.is_file():
        commands.append((["bash", str(disclosure_sh)], REPO))
    for cmd, cwd in commands:
        result = run_command(cmd, cwd, continue_on_error)
        if result.returncode:
            return False
    return True


@contextlib.contextmanager
def patched_models(project: Project, model: str | None):
    if model is None:
        yield
        return
    originals: dict[Path, str] = {}
    try:
        for path in sorted((project.path / "assemblies").glob("*.yaml")):
            text = path.read_text(encoding="utf-8")
            if not MODEL_RE.search(text):
                continue
            originals[path] = text
            path.write_text(MODEL_RE.sub(f"model: {model}", text, count=1), encoding="utf-8")
        yield
    finally:
        for path, text in originals.items():
            path.write_text(text, encoding="utf-8")


def clean_project_outputs(project: Project) -> None:
    shutil.rmtree(project.path / "runs", ignore_errors=True)
    shutil.rmtree(project.path / "evals" / "reports", ignore_errors=True)


def run_dir_for(project: Project, suite: str) -> Path:
    dirs = sorted((project.path / "runs").glob(f"*-{suite}"), key=lambda p: p.stat().st_mtime)
    if not dirs:
        raise FileNotFoundError(f"{project.name}: no run dir produced for {suite}")
    return dirs[-1]


def case_passes(case_report: dict) -> bool:
    for match in case_report.get("matches", []):
        for assertion in match.get("assertions", []):
            if assertion.get("outcome") != "pass":
                return False
    return bool(case_report.get("matches"))


def load_report(project: Project, run_id: str) -> dict:
    path = project.path / "evals" / "reports" / f"{run_id}.json"
    return json.loads(path.read_text(encoding="utf-8"))


def load_comparison(project: Project, run_id_a: str, run_id_b: str) -> dict:
    path = project.path / "evals" / "reports" / f"{run_id_a}-vs-{run_id_b}.json"
    return json.loads(path.read_text(encoding="utf-8"))


def initial_project_cells(
    project: Project, suites: dict[str, Suite]
) -> tuple[dict[str, ResourceCell], dict[str, set[str]]]:
    cells = {resource: ResourceCell() for resource in project_resources(project, suites)}
    discovery_resources = parse_discovery_resources(project.path / "evals" / "discovery.yaml", project.name)
    for resource in discovery_resources:
        cells.setdefault(resource, ResourceCell())
    return cells, discovery_resources


def invocation_icon_for_assertion(assertion: dict) -> str:
    change = assertion.get("change")
    if change in INVOCATION_CHANGE_ICONS:
        return INVOCATION_CHANGE_ICONS[change]

    arm_a = assertion.get("arm_a")
    arm_b = assertion.get("arm_b")
    if arm_a not in {"pass", "fail"} or arm_b not in {"pass", "fail"}:
        return INVOCATION_FAILURE
    if arm_a == "fail" and arm_b == "pass":
        return INVOCATION_WIN
    if arm_a == "pass" and arm_b == "pass":
        return INVOCATION_UNNEEDED
    if arm_a == "pass" and arm_b == "fail":
        return INVOCATION_LOSS
    return INVOCATION_NOISE


def comparison_invocation_icons(case: dict) -> tuple[str, ...]:
    return tuple(invocation_icon_for_assertion(assertion) for assertion in case.get("assertions", []))


def run_model_project(
    args: argparse.Namespace,
    project: Project,
    model: str | None,
    archive: EvalRunArchive | None = None,
) -> dict[str, ResourceCell]:
    suites = suite_map(project)
    cells, discovery_resources = initial_project_cells(project, suites)

    if args.dry_run:
        return cells

    if not prepare_project(project, args.continue_on_error):
        for cell in cells.values():
            cell.error = "setup"
        return cells

    with patched_models(project, model):
        run_dirs: dict[str, Path] = {}
        for suite_name in sorted(suites):
            result = run_command(
                ailly_command(args) + ["-p", str(project.path), "assemble", suite_name],
                REPO,
                args.continue_on_error,
            )
            if result.returncode:
                for cell in cells.values():
                    cell.error = f"assemble:{suite_name}"
                return cells
            run_dirs[suite_name] = run_dir_for(project, suite_name)

        for suite_name, run_dir in run_dirs.items():
            result = run_command(
                ailly_command(args) + ["-p", str(project.path), "run", str(run_dir)],
                REPO,
                args.continue_on_error,
            )
            if result.returncode:
                for cell in cells.values():
                    cell.error = f"run:{suite_name}"
                return cells

        for suite_name, run_dir in run_dirs.items():
            run_id = run_dir.name
            run_command(
                ailly_command(args) + ["-p", str(project.path), "eval", suite_name, "--over", str(run_dir)],
                REPO,
                continue_on_error=True,
            )
            if not (project.path / "evals" / "reports" / f"{run_id}.json").is_file():
                for cell in cells.values():
                    cell.error = f"eval:{suite_name}"
                return cells

        if "discovery" in run_dirs:
            discovery_id = run_dirs["discovery"].name
            run_command(ailly_command(args) + ["-p", str(project.path), "report", discovery_id], REPO, True)
            discovery_report = load_report(project, discovery_id)
            case_status = {
                case.get("name"): case_passes(case)
                for case in discovery_report.get("cases", [])
                if case.get("name")
            }
            for resource, cases in discovery_resources.items():
                if cases:
                    cells.setdefault(resource, ResourceCell()).discovery_pass = all(
                        case_status.get(case, False) for case in cases
                    )

        suite_names = set(suites)
        for suite_name, suite in suites.items():
            pair = baseline_for(suite_name, suite_names)
            if pair is None:
                continue
            run_id_a = run_dirs[pair].name
            run_id_b = run_dirs[suite_name].name
            run_command(
                ailly_command(args)
                + [
                    "-p",
                    str(project.path),
                    "report",
                    run_id_a,
                    run_id_b,
                    "--label-a",
                    pair,
                    "--label-b",
                    suite_name,
                ],
                REPO,
                True,
            )
            comparison = load_comparison(project, run_id_a, run_id_b)
            for case in comparison.get("cases", []):
                resource = resource_name(project, suite, case.get("case", ""))
                cells.setdefault(resource, ResourceCell()).invocation_icons = comparison_invocation_icons(case)

    return cells


def existing_models(projects: list[Project]) -> list[str]:
    models: list[str] = []
    for project in projects:
        for path in sorted((project.path / "evals" / "reports").glob("*.json")):
            data = json.loads(path.read_text(encoding="utf-8"))
            model = data.get("model")
            if data.get("suite") and model and model not in models:
                models.append(model)
    return models


def project_report_index(
    project: Project,
) -> tuple[dict[str, dict[str, dict]], dict[str, tuple[str, str]], list[dict]]:
    suite_reports: dict[str, dict[str, dict]] = {}
    run_index: dict[str, tuple[str, str]] = {}
    comparison_reports: list[dict] = []

    for path in sorted((project.path / "evals" / "reports").glob("*.json")):
        data = json.loads(path.read_text(encoding="utf-8"))
        suite = data.get("suite")
        model = data.get("model")
        run_id = data.get("run_id")
        if suite and model and run_id:
            run_index[run_id] = (model, suite)
            by_suite = suite_reports.setdefault(model, {})
            current = by_suite.get(suite)
            if current is None or str(run_id) > str(current.get("run_id", "")):
                by_suite[suite] = data
        elif data.get("arm_a") and data.get("arm_b"):
            comparison_reports.append(data)

    return suite_reports, run_index, comparison_reports


def comparison_arm_run_id(comparison: dict, arm: str) -> str:
    return str(comparison.get(arm, {}).get("run_id", ""))


def existing_comparisons_by_model_suite(
    suites: dict[str, Suite],
    run_index: dict[str, tuple[str, str]],
    comparison_reports: list[dict],
) -> dict[tuple[str, str], dict]:
    comparisons: dict[tuple[str, str], dict] = {}
    suite_names = set(suites)
    for comparison in comparison_reports:
        run_id_a = comparison_arm_run_id(comparison, "arm_a")
        run_id_b = comparison_arm_run_id(comparison, "arm_b")
        arm_a = run_index.get(run_id_a)
        arm_b = run_index.get(run_id_b)
        if arm_a is None or arm_b is None:
            continue
        model_a, suite_a = arm_a
        model_b, suite_b = arm_b
        if model_a != model_b or baseline_for(suite_b, suite_names) != suite_a:
            continue
        key = (model_b, suite_b)
        current = comparisons.get(key)
        if current is None or run_id_b > comparison_arm_run_id(current, "arm_b"):
            comparisons[key] = comparison
    return comparisons


def load_existing_project_matrix(
    project: Project, models: list[str]
) -> dict[str, dict[str, ResourceCell]]:
    suites = suite_map(project)
    suite_reports, run_index, comparison_reports = project_report_index(project)
    comparisons = existing_comparisons_by_model_suite(suites, run_index, comparison_reports)
    project_matrix: dict[str, dict[str, ResourceCell]] = {}

    for model in models:
        cells, discovery_resources = initial_project_cells(project, suites)
        discovery_report = suite_reports.get(model, {}).get("discovery")
        if discovery_report:
            case_status = {
                case.get("name"): case_passes(case)
                for case in discovery_report.get("cases", [])
                if case.get("name")
            }
            for resource, cases in discovery_resources.items():
                if cases:
                    cells.setdefault(resource, ResourceCell()).discovery_pass = all(
                        case_status.get(case, False) for case in cases
                    )

        for suite_name, suite in suites.items():
            if baseline_for(suite_name, set(suites)) is None:
                continue
            comparison = comparisons.get((model, suite_name))
            if comparison is None:
                continue
            for case in comparison.get("cases", []):
                resource = resource_name(project, suite, case.get("case", ""))
                cells.setdefault(resource, ResourceCell()).invocation_icons = comparison_invocation_icons(case)

        for resource, cell in cells.items():
            project_matrix.setdefault(resource, {})[model] = cell

    return project_matrix


def archive_models(
    manifest: ArchiveManifest,
    requested_plugins: set[str] | None = None,
) -> list[str]:
    selected_plugins = [
        plugin
        for plugin_name, plugin in manifest.plugins.items()
        if requested_plugins is None or plugin_name in requested_plugins
    ]
    models: list[str] = []
    for model in manifest.models:
        if model in models:
            continue
        if any(model in plugin.models for plugin in selected_plugins):
            models.append(model)
    for plugin in selected_plugins:
        for model in plugin.models:
            if model not in models:
                models.append(model)
    return models


def archive_model_record(
    plugin: ArchivePluginRecord,
    model: str,
) -> ArchiveModelRecord | None:
    if model in plugin.models:
        return plugin.models[model]
    for record in plugin.models.values():
        if str(record.slug) == model:
            return record
    return None


def archive_json(archive: EvalRunArchive, relative_path: str) -> dict | None:
    path = archive.root / relative_path
    if not path.is_file():
        return None
    return json.loads(path.read_text(encoding="utf-8"))


def mark_suite_error(
    cells: dict[str, ResourceCell],
    discovery_resources: dict[str, set[str]],
    project: Project,
    suite: Suite | None,
    message: str,
) -> None:
    if suite is None:
        for cell in cells.values():
            cell.error = message
        return
    if suite.name == "discovery":
        for resource in discovery_resources:
            cells.setdefault(resource, ResourceCell()).error = message
        return
    for case in suite.cases:
        resource = resource_name(project, suite, case)
        cells.setdefault(resource, ResourceCell()).error = message


def apply_archive_discovery_report(
    cells: dict[str, ResourceCell],
    discovery_resources: dict[str, set[str]],
    report: dict,
) -> None:
    case_status = {
        case.get("name"): case_passes(case)
        for case in report.get("cases", [])
        if case.get("name")
    }
    for resource, cases in discovery_resources.items():
        if cases:
            cells.setdefault(resource, ResourceCell()).discovery_pass = all(
                case_status.get(case, False) for case in cases
            )


def apply_archive_comparison_report(
    cells: dict[str, ResourceCell],
    project: Project,
    suite: Suite,
    comparison: dict,
) -> None:
    for case in comparison.get("cases", []):
        resource = resource_name(project, suite, case.get("case", ""))
        cells.setdefault(resource, ResourceCell()).invocation_icons = comparison_invocation_icons(case)


def archive_project_matrix(
    archive: EvalRunArchive,
    projects: list[Project],
    models: list[str],
) -> dict[str, dict[str, ResourceCell]]:
    project_by_name = {project.name: project for project in projects}
    project_matrix: dict[str, dict[str, ResourceCell]] = {}

    for plugin_name, plugin_record in archive.manifest.plugins.items():
        project = project_by_name.get(plugin_name)
        if project is None:
            continue
        suites = suite_map(project)
        for model in models:
            cells, discovery_resources = initial_project_cells(project, suites)
            model_record = archive_model_record(plugin_record, model)
            if model_record is not None:
                for suite_name, suite_record in model_record.suites.items():
                    if suite_record.status != "complete":
                        continue
                    suite = suites.get(suite_name)
                    for report_path in suite_record.report_paths:
                        report = archive_json(archive, report_path)
                        if report is None:
                            mark_suite_error(
                                cells,
                                discovery_resources,
                                project,
                                suite,
                                f"archive missing:{report_path}",
                            )
                            continue
                        if suite_name == "discovery":
                            apply_archive_discovery_report(cells, discovery_resources, report)
                    if suite is None or baseline_for(suite_name, set(suites)) is None:
                        continue
                    for comparison_path in suite_record.comparison_paths:
                        comparison = archive_json(archive, comparison_path)
                        if comparison is None:
                            mark_suite_error(
                                cells,
                                discovery_resources,
                                project,
                                suite,
                                f"archive missing:{comparison_path}",
                            )
                            continue
                        apply_archive_comparison_report(cells, project, suite, comparison)

            for resource, cell in cells.items():
                project_matrix.setdefault(resource, {})[model] = cell

    return project_matrix


def run_static_project(project: Project, args: argparse.Namespace) -> bool:
    if args.dry_run:
        return True
    assert project.static_ci is not None
    result = run_command(["bash", str(project.static_ci)], REPO, args.continue_on_error)
    return result.returncode == 0


def default_models(projects: list[Project]) -> list[str]:
    models: list[str] = []
    for project in projects:
        for suite in suite_map(project).values():
            if suite.model and suite.model not in models:
                models.append(suite.model)
    return models


def expand_model_args(requested: list[str], fallback: list[str]) -> list[str]:
    if not requested:
        return list(fallback)

    models: list[str] = []
    for item in requested:
        for model in MODEL_FAMILIES.get(item, (item,)):
            if model not in models:
                models.append(model)
    return models


def discovery_icon(cell: ResourceCell | None) -> str:
    if cell is None or cell.discovery_pass is None:
        return DISCOVERY_UNKNOWN
    return DISCOVERY_PASS if cell.discovery_pass else DISCOVERY_FAIL


def invocation_icon_text(cell: ResourceCell | None) -> str:
    if cell is None:
        return DISCOVERY_UNKNOWN * 3
    if cell.error:
        return INVOCATION_FAILURE
    if not cell.invocation_icons:
        return DISCOVERY_UNKNOWN * 3
    return "".join(cell.invocation_icons)


def report_title(cell: ResourceCell | None) -> str:
    if cell and cell.error:
        return f' title="{html.escape(cell.error, quote=True)}"'
    return ""


def report_styles() -> str:
    return """<style>
.e2e-report {
  margin: 0;
  max-width: 100%;
}
.e2e-report-scroll {
  max-width: 100%;
  overflow-x: auto;
}
.e2e-report table {
  border-collapse: separate;
  border-spacing: 0;
  min-width: max-content;
  white-space: nowrap;
  overflow-wrap: normal;
  word-break: keep-all;
}
.e2e-report th,
.e2e-report td {
  background: #fff;
  border: 1px solid #d0d7de;
  border-left: 0;
  border-top: 0;
  padding: 0.4rem 0.55rem;
  text-align: center;
  white-space: nowrap;
  overflow-wrap: normal;
  word-break: keep-all;
}
.e2e-report th {
  background: #f6f8fa;
  font-weight: 600;
}
.e2e-report thead tr:first-child th {
  position: sticky;
  top: 0;
  z-index: 4;
}
.e2e-report thead tr:nth-child(2) th {
  position: sticky;
  top: 2.25rem;
  z-index: 3;
}
.e2e-report .e2e-resource {
  left: 0;
  max-width: 28rem;
  position: sticky;
  text-align: left;
  z-index: 2;
}
.e2e-report thead .e2e-resource {
  z-index: 5;
}
.e2e-report tbody .e2e-resource {
  background: #fff;
  font-weight: 500;
}
.e2e-report .e2e-discovery,
.e2e-report .e2e-invocation {
  font-family: "Apple Color Emoji", "Segoe UI Emoji", "Noto Color Emoji", sans-serif;
  letter-spacing: 0;
}
.e2e-report figcaption,
.e2e-report .e2e-report-notes {
  margin-top: 0.75rem;
  white-space: nowrap;
}
</style>"""


def format_report(
    models: list[str],
    matrix: dict[str, dict[str, ResourceCell]],
    static_results: dict[str, bool],
    coverage_errors: list[str],
) -> str:
    lines: list[str] = []
    lines.append('<figure class="e2e-report">')
    lines.append(report_styles())
    lines.append('<div class="e2e-report-scroll">')
    lines.append("<table>")
    lines.append("<thead>")
    lines.append("<tr>")
    lines.append('<th class="e2e-resource" rowspan="2" scope="col">Resource</th>')
    for model in models:
        lines.append(
            f'<th class="e2e-model" colspan="2" scope="colgroup">{html.escape(model)}</th>'
        )
    lines.append("</tr>")
    lines.append("<tr>")
    for _ in models:
        lines.append('<th scope="col">Discover</th>')
        lines.append('<th scope="col">Invoke</th>')
    lines.append("</tr>")
    lines.append("</thead>")
    lines.append("<tbody>")
    for resource in sorted(matrix):
        lines.append("<tr>")
        lines.append(f'<th class="e2e-resource" scope="row">{html.escape(resource)}</th>')
        for model in models:
            cell = matrix[resource].get(model)
            title = report_title(cell)
            lines.append(f'<td class="e2e-discovery"{title}>{discovery_icon(cell)}</td>')
            lines.append(f'<td class="e2e-invocation"{title}>{invocation_icon_text(cell)}</td>')
        lines.append("</tr>")
    lines.append("</tbody>")
    lines.append("</table>")
    lines.append("</div>")

    lines.append(
        "<figcaption>"
        f"Discovery: {DISCOVERY_PASS} pass, {DISCOVERY_FAIL} fail, {DISCOVERY_UNKNOWN} unknown. "
        f"Invocation: {INVOCATION_WIN} win, {INVOCATION_UNNEEDED} unneeded, "
        f"{INVOCATION_LOSS} loss, {INVOCATION_NOISE} noise, {INVOCATION_FAILURE} failure."
        "</figcaption>"
    )

    if static_results:
        lines.append('<div class="e2e-report-notes"><strong>Static checks:</strong><ul>')
        for name, ok in sorted(static_results.items()):
            icon = DISCOVERY_PASS if ok else DISCOVERY_FAIL
            lines.append(f"<li>{html.escape(name)}: {icon}</li>")
        lines.append("</ul></div>")

    if coverage_errors:
        lines.append('<div class="e2e-report-notes"><strong>Coverage failures:</strong><ul>')
        for error in coverage_errors:
            lines.append(f"<li>{html.escape(error)}</li>")
        lines.append("</ul></div>")
    lines.append("</figure>")
    return "\n".join(lines) + "\n"


def parse_args(argv: list[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--ailly-bin")
    parser.add_argument(
        "--model",
        action="append",
        default=[],
        help="Model name or family: anthropic, openai, bedrock.",
    )
    parser.add_argument("--plugin", action="append", default=[])
    parser.add_argument("--report", type=Path)
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument(
        "--from-existing",
        action="store_true",
        help="Render saved eval reports without assembling, running, evaluating, or reporting.",
    )
    parser.add_argument(
        "--archive",
        help="Replay a durable e2e archive by run id or path when used with --from-existing.",
    )
    parser.add_argument("--fail-fast", dest="continue_on_error", action="store_false")
    parser.add_argument("--skip-static", action="store_true")
    parser.set_defaults(continue_on_error=True)
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    args = parse_args(sys.argv[1:] if argv is None else argv)
    model_projects, static_projects = discover_projects(REPO)
    if args.plugin:
        wanted = set(args.plugin)
        model_projects = [project for project in model_projects if project.name in wanted]
        static_projects = [project for project in static_projects if project.name in wanted]

    coverage_errors: list[str] = []
    for project in model_projects:
        coverage_errors.extend(validate_project(project))

    archive: EvalRunArchive | None = None
    if args.from_existing and args.archive:
        archive = EvalRunArchive.open(resolve_archive_path(REPO, args.archive))
        model_fallback = archive_models(archive.manifest, {project.name for project in model_projects})
    else:
        model_fallback = existing_models(model_projects) if args.from_existing else default_models(model_projects)
    models = expand_model_args(args.model, model_fallback)
    if not models:
        return fail("No model-driven plugin e2e projects found.")

    matrix: dict[str, dict[str, ResourceCell]] = {}
    if archive is not None:
        matrix = archive_project_matrix(archive, model_projects, models)
    elif args.from_existing:
        for project in model_projects:
            project_matrix = load_existing_project_matrix(project, models)
            for resource, per_model in project_matrix.items():
                matrix.setdefault(resource, {}).update(per_model)
    else:
        if not args.dry_run:
            for project in model_projects:
                clean_project_outputs(project)
        for model in models:
            for project in model_projects:
                project_cells = run_model_project(args, project, model)
                for resource, cell in project_cells.items():
                    matrix.setdefault(resource, {})[model] = cell

    static_results: dict[str, bool] = {}
    if not args.skip_static and not args.from_existing:
        for project in static_projects:
            static_results[project.name] = run_static_project(project, args)

    report = format_report(models, matrix, static_results, coverage_errors)
    print(report)
    if args.report:
        args.report.write_text(report, encoding="utf-8")

    any_error = any(cell.error for per_model in matrix.values() for cell in per_model.values())
    any_static_failure = any(not ok for ok in static_results.values())
    return 1 if coverage_errors or any_error or any_static_failure else 0


if __name__ == "__main__":
    sys.exit(main())
