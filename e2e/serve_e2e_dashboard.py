#!/usr/bin/env python3

from __future__ import annotations

import argparse
import dataclasses
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
import json
import mimetypes
import os
from pathlib import Path
import re
import sys
from typing import Iterable
from urllib.parse import parse_qs, unquote, urlparse

import run_all_plugin_e2e as runner


REPO = Path(__file__).resolve().parents[1]
TEXT_PREVIEW_LIMIT = 80_000
FILE_LIST_LIMIT = 160
TRANSCRIPT_FILE_LIMIT = 120
TRANSCRIPT_CONTENT_LIMIT = 80_000


@dataclasses.dataclass(frozen=True)
class AppConfig:
    repo: Path
    archive: str | None
    plugins: tuple[str, ...]
    models: tuple[str, ...]


class AppError(Exception):
    status: int

    def __init__(self, message: str, status: int = 400):
        super().__init__(message)
        self.status = status


def resolve_archive_location(repo: Path, archive_arg: str | None) -> Path:
    if not archive_arg:
        return repo / "e2e" / "artifacts"
    archive_path = Path(archive_arg)
    if archive_path.is_absolute():
        return archive_path
    if "/" in archive_arg or (os.sep != "/" and os.sep in archive_arg):
        return repo / archive_path
    return repo / "e2e" / "artifacts" / archive_arg


def load_archive_roots(repo: Path, archive_arg: str | None) -> tuple[Path, ...]:
    return runner.archive_roots(resolve_archive_location(repo, archive_arg))


def open_archives(repo: Path, archive_arg: str | None) -> tuple[runner.EvalRunArchive, ...]:
    return tuple(runner.EvalRunArchive.open(root) for root in load_archive_roots(repo, archive_arg))


def archive_group_key(archive: runner.EvalRunArchive) -> str:
    return archive.manifest.source_snapshot or f"archive:{archive.manifest.run_id}"


def archive_groups(archives: Iterable[runner.EvalRunArchive]) -> list[dict]:
    groups: dict[str, dict] = {}
    for archive in archives:
        key = archive_group_key(archive)
        group = groups.setdefault(
            key,
            {
                "key": key,
                "source_snapshot": archive.manifest.source_snapshot,
                "archives": [],
                "models": [],
                "statuses": {},
                "failures": 0,
                "created_at": archive.manifest.created_at,
            },
        )
        group["archives"].append(str(archive.manifest.run_id))
        group["failures"] += len(archive.manifest.failures)
        group["statuses"][archive.manifest.status] = group["statuses"].get(archive.manifest.status, 0) + 1
        group["created_at"] = max(group["created_at"], archive.manifest.created_at)
        for model in archive.manifest.models:
            if model not in group["models"]:
                group["models"].append(model)
    return sorted(groups.values(), key=lambda group: group["created_at"], reverse=True)


def select_archives(
    repo: Path,
    archive_arg: str | None,
    source_snapshot: str | None,
) -> tuple[runner.EvalRunArchive, ...]:
    archives = open_archives(repo, archive_arg)
    if not archives:
        return ()
    groups = archive_groups(archives)
    selected = source_snapshot
    if selected is None:
        selected = groups[0]["key"]
    return tuple(
        sorted(
            (archive for archive in archives if archive_group_key(archive) == selected),
            key=runner.archive_sort_key,
        )
    )


def selected_projects(repo: Path, plugins: Iterable[str]) -> list[runner.Project]:
    model_projects, _ = runner.discover_projects(repo)
    wanted = set(plugins)
    if wanted:
        model_projects = [project for project in model_projects if project.name in wanted]
    return model_projects


def icon_counts(icons: Iterable[str]) -> dict[str, int]:
    counts = {
        runner.DISCOVERY_PASS: 0,
        runner.DISCOVERY_FAIL: 0,
        runner.INVOCATION_WIN: 0,
        runner.INVOCATION_UNNEEDED: 0,
        runner.INVOCATION_LOSS: 0,
        runner.INVOCATION_NOISE: 0,
        runner.INVOCATION_FAILURE: 0,
        runner.INVOCATION_TOKEN_SAVINGS: 0,
        runner.INVOCATION_TOKEN_BURN: 0,
        runner.DISCOVERY_UNKNOWN: 0,
    }
    for icon in icons:
        counts[icon] = counts.get(icon, 0) + 1
    return counts


def cell_to_json(cell: runner.ResourceCell | None) -> dict:
    invocation_icons = list(cell.invocation_icons) if cell and cell.invocation_icons else []
    evidence = [
        dataclasses.asdict(item)
        for item in (cell.evidence if cell else ())
    ]
    return {
        "discovery": runner.discovery_icon(cell),
        "invocation": runner.invocation_icon_text(cell),
        "invocation_icons": invocation_icons,
        "counts": icon_counts(invocation_icons),
        "error": cell.error if cell else None,
        "evidence_count": len(evidence),
        "evidence": evidence,
    }


def row_summary(cells: dict[str, dict]) -> dict:
    discovery = {runner.DISCOVERY_PASS: 0, runner.DISCOVERY_FAIL: 0, runner.DISCOVERY_UNKNOWN: 0}
    invocation: list[str] = []
    errors = 0
    for cell in cells.values():
        discovery[cell["discovery"]] = discovery.get(cell["discovery"], 0) + 1
        invocation.extend(cell["invocation_icons"])
        if cell["error"]:
            errors += 1
    return {
        "discovery": discovery,
        "invocation": icon_counts(invocation),
        "errors": errors,
    }


def build_state(
    repo: Path,
    archive_arg: str | None = None,
    source_snapshot: str | None = None,
    plugins: Iterable[str] = (),
    models: Iterable[str] = (),
) -> dict:
    all_archives = open_archives(repo, archive_arg)
    groups = archive_groups(all_archives)
    selected_key = source_snapshot or (groups[0]["key"] if groups else None)
    archives = select_archives(repo, archive_arg, selected_key)
    projects = selected_projects(repo, plugins)
    wanted_plugins = {project.name for project in projects}
    model_names = runner.expand_model_args(
        list(models),
        runner.archive_group_models(archives, wanted_plugins),
    )
    matrix = runner.archive_group_matrix(archives, projects, model_names) if archives else {}

    rows = []
    for resource in sorted(matrix):
        cells = {
            model: cell_to_json(matrix[resource].get(model))
            for model in model_names
        }
        rows.append(
            {
                "resource": resource,
                "plugin": resource.split(":", 1)[0],
                "summary": row_summary(cells),
                "cells": cells,
            }
        )

    failures = [
        {"archive": str(archive.manifest.run_id), **failure}
        for archive in archives
        for failure in archive.manifest.failures
    ]
    return {
        "archive_root": str(resolve_archive_location(repo, archive_arg)),
        "selected_group": selected_key,
        "groups": groups,
        "archives": [
            {
                "id": str(archive.manifest.run_id),
                "created_at": archive.manifest.created_at,
                "status": archive.manifest.status,
                "source_snapshot": archive.manifest.source_snapshot,
                "failures": len(archive.manifest.failures),
            }
            for archive in archives
        ],
        "models": model_names,
        "rows": rows,
        "failures": failures,
    }


def archive_by_id(archives: Iterable[runner.EvalRunArchive], archive_id: str) -> runner.EvalRunArchive:
    for archive in archives:
        if str(archive.manifest.run_id) == archive_id:
            return archive
    raise AppError(f"Unknown archive: {archive_id}", 404)


def safe_archive_path(archive: runner.EvalRunArchive, relative_path: str) -> Path:
    target = (archive.root / relative_path).resolve()
    root = archive.root.resolve()
    try:
        target.relative_to(root)
    except ValueError as error:
        raise AppError("Path is outside the archive", 400) from error
    return target


def read_text_preview(path: Path, limit: int = TEXT_PREVIEW_LIMIT) -> dict:
    if not path.is_file():
        return {"exists": False, "path": str(path), "content": "", "truncated": False}
    content = path.read_bytes()
    truncated = len(content) > limit
    text = content[:limit].decode("utf-8", errors="replace")
    return {
        "exists": True,
        "path": str(path),
        "content": text,
        "truncated": truncated,
        "size": len(content),
        "mime": mimetypes.guess_type(path.name)[0] or "text/plain",
    }


def read_archive_json(archive: runner.EvalRunArchive, relative_path: str) -> dict:
    path = safe_archive_path(archive, relative_path)
    if not path.is_file():
        return {}
    return json.loads(path.read_text(encoding="utf-8"))


def project_for_resource(projects: list[runner.Project], resource: str) -> runner.Project | None:
    plugin = resource.split(":", 1)[0]
    for project in projects:
        if project.name == plugin:
            return project
    return None


def selected_cases(
    report: dict,
    resource: str,
    project: runner.Project | None,
    suite: runner.Suite | None,
    kind: str,
) -> list[dict]:
    cases = report.get("cases", [])
    if project is None:
        return list(cases)
    if kind == "discovery":
        discovery_path = project.path / "evals" / "discovery.yaml"
        if not discovery_path.is_file():
            return list(cases)
        discovery_resources = runner.parse_discovery_resources(discovery_path, project.name)
        names = discovery_resources.get(resource)
        if not names:
            return list(cases)
        return [case for case in cases if case.get("name") in names]
    if suite is None:
        return list(cases)
    return [
        case
        for case in cases
        if runner.resource_name(project, suite, str(case.get("case", ""))) == resource
    ]


def archive_file_list(
    archive: runner.EvalRunArchive,
    roots: Iterable[str],
    limit: int = FILE_LIST_LIMIT,
    case_stems: set[str] | None = None,
) -> list[dict]:
    files: list[dict] = []
    archive_root = archive.root.resolve()
    stems = case_stems or set()
    for root_path in roots:
        base = safe_archive_path(archive, root_path)
        if base.is_file():
            if stems and base.stem not in stems:
                continue
            files.append({"path": root_path, "size": base.stat().st_size})
            continue
        if not base.is_dir():
            continue
        for child in sorted(path for path in base.rglob("*") if path.is_file()):
            if stems and child.stem not in stems:
                continue
            files.append(
                {
                    "path": child.relative_to(archive_root).as_posix(),
                    "size": child.stat().st_size,
                }
            )
            if len(files) >= limit:
                return files
    return files


def model_run_root(
    archive: runner.EvalRunArchive,
    plugin: str,
    model_record: runner.ArchiveModelRecord | None,
) -> str | None:
    if model_record is None:
        return None
    return f"plugins/{plugin}/models/{model_record.slug}/runs"


def archived_run_path_for_id(
    archive: runner.EvalRunArchive,
    plugin: str,
    model_record: runner.ArchiveModelRecord | None,
    run_id: object,
) -> str | None:
    if not run_id:
        return None
    root = model_run_root(archive, plugin, model_record)
    if root is None:
        return None
    relative = f"{root}/{run_id}"
    if safe_archive_path(archive, relative).exists():
        return relative
    return None


def archived_report_path_for_id(
    archive: runner.EvalRunArchive,
    plugin: str,
    model_record: runner.ArchiveModelRecord | None,
    run_id: object,
) -> str | None:
    if not run_id or model_record is None:
        return None
    relative = f"plugins/{plugin}/models/{model_record.slug}/reports/{run_id}.json"
    if safe_archive_path(archive, relative).is_file():
        return relative
    return None


def comparison_arm_run_paths(
    archive: runner.EvalRunArchive,
    plugin: str,
    model_record: runner.ArchiveModelRecord | None,
    report: dict,
    suite_record: runner.ArchiveSuiteRecord,
    suite_name: str,
    evidence_kind: str,
) -> list[dict]:
    if evidence_kind != "invocation":
        return [
            {
                "label": "session",
                "run_id": suite_record.run_id or "",
                "paths": list(suite_record.run_paths),
            }
        ]
    arms: list[dict] = []
    for key, label in (("arm_a", "baseline"), ("arm_b", "invocation")):
        run_id = comparison_arm_run_id(report, key)
        path = archived_run_path_for_id(archive, plugin, model_record, run_id)
        if path is None and key == "arm_a":
            fallback = baseline_suite_record(model_record, suite_name)
            paths = list(fallback.run_paths) if fallback is not None else []
            run_id = run_id or (fallback.run_id if fallback is not None else None)
        elif path is None and key == "arm_b":
            paths = list(suite_record.run_paths)
            run_id = run_id or suite_record.run_id
        elif path is None:
            paths = []
        else:
            paths = [path]
        arms.append({"label": label, "run_id": run_id or "", "paths": paths})
    return arms


def comparison_arm_report_paths(
    archive: runner.EvalRunArchive,
    plugin: str,
    model_record: runner.ArchiveModelRecord | None,
    report: dict,
    suite_record: runner.ArchiveSuiteRecord,
    suite_name: str,
    evidence_kind: str,
) -> dict[str, str]:
    if evidence_kind != "invocation":
        return {}
    paths: dict[str, str] = {}
    baseline_record = baseline_suite_record(model_record, suite_name)
    arm_specs = (
        ("arm_a", "baseline", baseline_record),
        ("arm_b", "invocation", suite_record),
    )
    for key, label, record in arm_specs:
        if record is None:
            continue
        run_id = comparison_arm_run_id(report, key) or record.run_id
        path = report_path_for_run_id(record, run_id)
        if path is None:
            path = archived_report_path_for_id(archive, plugin, model_record, run_id)
        if path is not None:
            paths[label] = path
    return paths


def report_path_for_run_id(
    suite_record: runner.ArchiveSuiteRecord,
    run_id: str | None,
) -> str | None:
    report_paths = list(suite_record.report_paths)
    if run_id:
        for path in report_paths:
            if Path(path).stem == run_id:
                return path
        for path in report_paths:
            if run_id in Path(path).stem:
                return path
    if len(report_paths) == 1:
        return report_paths[0]
    return None


def comparison_arm_run_id(report: dict, key: str) -> str | None:
    arm = report.get(key)
    if not isinstance(arm, dict):
        return None
    run_id = arm.get("run_id")
    return str(run_id) if run_id else None


def baseline_suite_record(
    model_record: runner.ArchiveModelRecord | None,
    suite_name: str,
) -> runner.ArchiveSuiteRecord | None:
    if model_record is None:
        return None
    baseline_name = runner.baseline_for(suite_name, set(model_record.suites))
    if baseline_name is None:
        return None
    return model_record.suites.get(baseline_name)


def file_list_for_session_arms(
    archive: runner.EvalRunArchive,
    arms: list[dict],
    case_stems: set[str],
) -> list[dict]:
    files: list[dict] = []
    remaining = FILE_LIST_LIMIT
    for arm in arms:
        if remaining <= 0:
            break
        arm_files = archive_file_list(archive, arm["paths"], limit=remaining, case_stems=case_stems)
        for file in arm_files:
            file["arm"] = arm["label"]
            file["run_id"] = arm.get("run_id") or ""
        files.extend(arm_files)
        remaining -= len(arm_files)
    return files


def transcripts_for_session_arms(
    archive: runner.EvalRunArchive,
    arms: list[dict],
    case_stems: set[str],
    project: runner.Project | None,
) -> list[dict]:
    transcripts: list[dict] = []
    remaining = TRANSCRIPT_FILE_LIMIT
    for arm in arms:
        if remaining <= 0:
            break
        arm_transcripts = session_transcripts(
            archive,
            arm["paths"],
            limit=remaining,
            case_stems=case_stems,
            project=project,
        )
        for transcript in arm_transcripts:
            transcript["arm"] = arm["label"]
            transcript["run_id"] = arm.get("run_id") or ""
        transcripts.extend(arm_transcripts)
        remaining -= len(arm_transcripts)
    return transcripts


def parse_inline_scalar(value: str) -> str:
    value = value.strip()
    if not value:
        return ""
    if value.startswith('"') and value.endswith('"'):
        try:
            parsed = json.loads(value)
        except json.JSONDecodeError:
            return value[1:-1]
        return parsed if isinstance(parsed, str) else str(parsed)
    if value.startswith("'") and value.endswith("'"):
        return value[1:-1].replace("''", "'")
    return value


def yaml_documents(text: str) -> list[list[str]]:
    documents: list[list[str]] = []
    current: list[str] = []
    for line in text.splitlines():
        if line.strip() == "---":
            if current:
                documents.append(current)
            current = []
            continue
        current.append(line)
    if current:
        documents.append(current)
    return documents


def top_level_scalar(lines: list[str], key: str) -> str | None:
    prefix = f"{key}:"
    for line in lines:
        if line.startswith(prefix):
            return parse_inline_scalar(line[len(prefix) :])
    return None


def dedent_yaml_block(lines: list[str]) -> str:
    indents = [
        len(line) - len(line.lstrip(" "))
        for line in lines
        if line.strip()
    ]
    indent = min(indents) if indents else 0
    return "\n".join(line[indent:] if len(line) >= indent else "" for line in lines)


def top_level_content(lines: list[str]) -> str:
    for index, line in enumerate(lines):
        if not line.startswith("content:"):
            continue
        value = line[len("content:") :].strip()
        if value in {"|", "|-", "|+", ">", ">-", ">+"}:
            block: list[str] = []
            for block_line in lines[index + 1 :]:
                if re.match(r"^[A-Za-z0-9_-]+:", block_line):
                    break
                block.append(block_line)
            return dedent_yaml_block(block)
        return parse_inline_scalar(value)
    return ""


def trim_transcript_content(content: str) -> tuple[str, bool]:
    if len(content) <= TRANSCRIPT_CONTENT_LIMIT:
        return content, False
    return content[:TRANSCRIPT_CONTENT_LIMIT], True


def parse_run_transcript(path: Path) -> list[dict]:
    messages: list[dict] = []
    for document in yaml_documents(path.read_text(encoding="utf-8", errors="replace")):
        role = top_level_scalar(document, "role")
        if role not in {"user", "assistant"}:
            continue
        content, truncated = trim_transcript_content(top_level_content(document))
        messages.append(
            {
                "role": role,
                "content": content,
                "chars": len(content),
                "truncated": truncated,
                "empty": content == "",
            }
        )
    return messages


def session_transcripts(
    archive: runner.EvalRunArchive,
    roots: Iterable[str],
    limit: int = TRANSCRIPT_FILE_LIMIT,
    case_stems: set[str] | None = None,
    project: runner.Project | None = None,
) -> list[dict]:
    transcripts: list[dict] = []
    archive_root = archive.root.resolve()
    stems = case_stems or set()
    for root_path in roots:
        base = safe_archive_path(archive, root_path)
        candidates: list[Path]
        if base.is_file():
            if stems and base.stem not in stems:
                continue
            candidates = [base]
        elif base.is_dir():
            candidates = sorted(
                path
                for path in base.rglob("*")
                if path.is_file()
                and path.suffix in {".yaml", ".yml"}
                and (not stems or path.stem in stems)
            )
        else:
            continue
        for path in candidates:
            if path.suffix not in {".yaml", ".yml"}:
                continue
            messages = parse_run_transcript(path)
            if not messages:
                continue
            source = "archive"
            source_path = path.relative_to(archive_root).as_posix()
            fallback_path = checkout_transcript_path(project, base, path)
            if transcript_needs_fallback(messages) and fallback_path is not None:
                fallback_messages = parse_run_transcript(fallback_path)
                if transcript_has_assistant_content(fallback_messages):
                    messages = fallback_messages
                    source = "checkout"
                    source_path = display_path(fallback_path)
            assistant_messages = [message for message in messages if message["role"] == "assistant"]
            transcripts.append(
                {
                    "path": path.relative_to(archive_root).as_posix(),
                    "source": source,
                    "source_path": source_path,
                    "messages": messages,
                    "message_count": len(messages),
                    "assistant_count": len(assistant_messages),
                    "assistant_empty": sum(1 for message in assistant_messages if message["empty"]),
                }
            )
            if len(transcripts) >= limit:
                return transcripts
    return transcripts


def transcript_needs_fallback(messages: list[dict]) -> bool:
    return any(message["role"] == "assistant" for message in messages) and not transcript_has_assistant_content(messages)


def transcript_has_assistant_content(messages: list[dict]) -> bool:
    return any(
        message["role"] == "assistant" and message["content"].strip()
        for message in messages
    )


def display_path(path: Path) -> str:
    try:
        return path.relative_to(REPO).as_posix()
    except ValueError:
        return path.as_posix()


def checkout_transcript_path(
    project: runner.Project | None,
    archive_run_root: Path,
    archive_transcript: Path,
) -> Path | None:
    if project is None or not archive_run_root.is_dir():
        return None
    try:
        relative = archive_transcript.relative_to(archive_run_root)
    except ValueError:
        return None
    candidate = project.path / "runs" / archive_run_root.name / relative
    return candidate if candidate.is_file() else None


def command_to_json(archive: runner.EvalRunArchive, command: runner.CommandRecord) -> dict:
    return {
        "sequence": command.sequence,
        "step": command.step,
        "args": list(command.args),
        "returncode": command.returncode,
        "started_at": command.started_at,
        "finished_at": command.finished_at,
        "stdout_path": command.stdout_path,
        "stderr_path": command.stderr_path,
        "stdout": read_text_preview(safe_archive_path(archive, command.stdout_path), 24_000),
        "stderr": read_text_preview(safe_archive_path(archive, command.stderr_path), 24_000),
    }


def evaluator_files(
    repo: Path,
    archive: runner.EvalRunArchive,
    project: runner.Project | None,
    suite_record: runner.ArchiveSuiteRecord,
) -> list[dict]:
    files: list[dict] = []
    eval_inputs = [path for path in suite_record.input_paths if "/inputs/evals/" in path]
    for relative_path in eval_inputs:
        path = safe_archive_path(archive, relative_path)
        files.append(
            {
                "source": "archive",
                "path": relative_path,
                "preview": read_text_preview(path),
            }
        )
        if "/inputs/evals/scripts/" in relative_path:
            continue
        for script_path in runner.parse_eval_script_paths(path) if path.is_file() else ():
            archived_script = script_input_path_for_eval(relative_path, script_path)
            if archived_script and (archive.root / archived_script).is_file():
                files.append(
                    {
                        "source": "archive",
                        "path": archived_script,
                        "preview": read_text_preview(safe_archive_path(archive, archived_script)),
                    }
                )
            elif project is not None:
                repo_script = project.path / script_path
                files.append(
                    {
                        "source": "checkout",
                        "path": repo_script.relative_to(repo).as_posix(),
                        "preview": read_text_preview(repo_script),
                    }
                )
    return files


def script_input_path_for_eval(eval_input_path: str, script_path: str) -> str | None:
    marker = "/inputs/evals/"
    if marker not in eval_input_path:
        return None
    prefix = eval_input_path.split(marker, 1)[0] + "/inputs/"
    return prefix + script_path


def evaluator_results(
    cases: Iterable[dict],
    arm_details: dict[str, dict[tuple[str, str], list[dict]]] | None = None,
) -> list[dict]:
    results: list[dict] = []
    attempt = 1
    detail_cursors: dict[tuple[str, str, str], int] = {}
    for case in cases:
        case_name = str(case.get("case") or case.get("name") or "case")
        for assertion in case.get("assertions", ()):
            result = evaluator_assertion_result(case_name, assertion, attempt)
            enrich_evaluator_result(result, arm_details, detail_cursors)
            results.append(result)
            attempt += 1
        for match in case.get("matches", ()):
            conversation = str(match.get("conversation") or "")
            for assertion in match.get("assertions", ()):
                result = evaluator_assertion_result(case_name, assertion, attempt)
                if conversation:
                    result["conversation"] = conversation
                enrich_evaluator_result(result, arm_details, detail_cursors)
                results.append(result)
                attempt += 1
    return results


def evaluator_assertion_result(case_name: str, assertion: dict, attempt: int) -> dict:
    result = {
        "attempt": attempt,
        "case": case_name,
        "evaluator": str(assertion.get("class") or assertion.get("type") or assertion.get("name") or "assertion"),
        "outcome": string_or_empty(assertion.get("outcome") or assertion.get("status")),
        "baseline": string_or_empty(assertion.get("arm_a")),
        "invocation": string_or_empty(assertion.get("arm_b")),
        "change": string_or_empty(assertion.get("change")),
        "reason": string_or_empty(assertion.get("reason")),
    }
    result["icon"] = evaluator_result_icon(result)
    return result


def enrich_evaluator_result(
    result: dict,
    arm_details: dict[str, dict[tuple[str, str], list[dict]]] | None,
    detail_cursors: dict[tuple[str, str, str], int],
) -> None:
    if not arm_details:
        return
    key = (result["case"], result["evaluator"])
    for arm_label, details_by_key in arm_details.items():
        matches = details_by_key.get(key, [])
        cursor_key = (arm_label, key[0], key[1])
        cursor = detail_cursors.get(cursor_key, 0)
        if cursor >= len(matches):
            continue
        detail = matches[cursor]
        detail_cursors[cursor_key] = cursor + 1
        for field in ("outcome", "reason", "conversation", "report_path"):
            value = detail.get(field)
            if value:
                result[f"{arm_label}_{field}"] = value


def evaluator_detail_index(cases: Iterable[dict], report_path: str) -> dict[tuple[str, str], list[dict]]:
    details: dict[tuple[str, str], list[dict]] = {}
    for case in cases:
        case_name = str(case.get("case") or case.get("name") or "case")
        for assertion in case.get("assertions", ()):
            add_evaluator_detail(details, case_name, assertion, report_path, "")
        for match in case.get("matches", ()):
            conversation = str(match.get("conversation") or "")
            for assertion in match.get("assertions", ()):
                add_evaluator_detail(details, case_name, assertion, report_path, conversation)
    return details


def add_evaluator_detail(
    details: dict[tuple[str, str], list[dict]],
    case_name: str,
    assertion: dict,
    report_path: str,
    conversation: str,
) -> None:
    evaluator = str(assertion.get("class") or assertion.get("type") or assertion.get("name") or "assertion")
    key = (case_name, evaluator)
    details.setdefault(key, []).append(
        {
            "outcome": string_or_empty(assertion.get("outcome") or assertion.get("status")),
            "reason": string_or_empty(assertion.get("reason")),
            "conversation": conversation,
            "report_path": report_path,
        }
    )


def evaluator_arm_details(
    archive: runner.EvalRunArchive,
    arm_report_paths: dict[str, str],
) -> dict[str, dict[tuple[str, str], list[dict]]]:
    details: dict[str, dict[tuple[str, str], list[dict]]] = {}
    for arm_label, report_path in arm_report_paths.items():
        report = read_archive_json(archive, report_path)
        details[arm_label] = evaluator_detail_index(report.get("cases", ()), report_path)
    return details


def evaluator_result_icon(result: dict) -> str:
    return runner.invocation_icon_for_assertion(
        {
            "class": result.get("evaluator"),
            "outcome": result.get("outcome"),
            "arm_a": result.get("baseline"),
            "arm_b": result.get("invocation"),
            "change": result.get("change"),
        }
    )


def string_or_empty(value: object) -> str:
    return "" if value is None else str(value)


def case_transcript_stems(cases: Iterable[dict]) -> set[str]:
    stems: set[str] = set()
    for case in cases:
        for key in ("case", "name"):
            add_case_stem(stems, case.get(key))
        for match in case.get("matches", ()):
            add_case_stem(stems, match.get("conversation"))
    return stems


def add_case_stem(stems: set[str], value: object) -> None:
    if value is None:
        return
    text = str(value).strip()
    if not text:
        return
    stems.add(Path(text).stem)


def evidence_detail(
    repo: Path,
    archives: tuple[runner.EvalRunArchive, ...],
    projects: list[runner.Project],
    resource: str,
    model: str,
    evidence: runner.CellEvidence,
) -> dict:
    archive = archive_by_id(archives, evidence.archive_id)
    plugin = resource.split(":", 1)[0]
    project = project_for_resource(projects, resource)
    suites = runner.suite_map(project) if project is not None else {}
    suite = suites.get(evidence.suite)
    plugin_record = archive.manifest.plugins.get(plugin)
    model_record = runner.archive_model_record(plugin_record, model) if plugin_record else None
    suite_record = model_record.suites.get(evidence.suite) if model_record else None
    report = read_archive_json(archive, evidence.path)
    cases = selected_cases(report, resource, project, suite, evidence.kind)
    transcript_stems = case_transcript_stems(cases)
    detail = {
        "archive": str(archive.manifest.run_id),
        "archive_status": archive.manifest.status,
        "kind": evidence.kind,
        "suite": evidence.suite,
        "report_path": evidence.path,
        "report": report,
        "cases": cases,
        "evaluator_results": evaluator_results(cases),
        "suite_record": None,
        "session_arms": [],
        "commands": [],
        "session_files": [],
        "transcripts": [],
        "inputs": [],
        "evaluators": [],
    }
    if suite_record is None:
        return detail
    detail["suite_record"] = {
        "status": suite_record.status,
        "run_id": suite_record.run_id,
        "input_paths": list(suite_record.input_paths),
        "run_paths": list(suite_record.run_paths),
        "report_paths": list(suite_record.report_paths),
        "comparison_paths": list(suite_record.comparison_paths),
    }
    session_arms = comparison_arm_run_paths(
        archive,
        plugin,
        model_record,
        report,
        suite_record,
        evidence.suite,
        evidence.kind,
    )
    detail["session_arms"] = session_arms
    arm_report_paths = comparison_arm_report_paths(
        archive,
        plugin,
        model_record,
        report,
        suite_record,
        evidence.suite,
        evidence.kind,
    )
    detail["evaluator_results"] = evaluator_results(cases, evaluator_arm_details(archive, arm_report_paths))
    detail["commands"] = [command_to_json(archive, command) for command in suite_record.command_records]
    detail["session_files"] = file_list_for_session_arms(archive, session_arms, transcript_stems)
    detail["transcripts"] = transcripts_for_session_arms(
        archive,
        session_arms,
        transcript_stems,
        project=project,
    )
    detail["inputs"] = [
        {
            "path": path,
            "preview": read_text_preview(safe_archive_path(archive, path), 16_000),
        }
        for path in suite_record.input_paths
        if "/inputs/prompts/" in path or path.endswith("/AGENTS.md") or "/inputs/context/" in path
    ][:40]
    detail["evaluators"] = evaluator_files(repo, archive, project, suite_record)
    return detail


def build_cell_detail(
    repo: Path,
    archive_arg: str | None,
    source_snapshot: str | None,
    resource: str,
    model: str,
    kind: str | None = None,
    plugins: Iterable[str] = (),
    models: Iterable[str] = (),
) -> dict:
    archives = select_archives(repo, archive_arg, source_snapshot)
    projects = selected_projects(repo, plugins)
    model_names = runner.expand_model_args(
        list(models),
        runner.archive_group_models(archives, {project.name for project in projects}),
    )
    if model not in model_names:
        model_names.append(model)
    matrix = runner.archive_group_matrix(archives, projects, model_names) if archives else {}
    cell = matrix.get(resource, {}).get(model)
    evidence = list(cell.evidence if cell else ())
    if kind:
        evidence = [item for item in evidence if item.kind == kind]
    return {
        "resource": resource,
        "model": model,
        "kind": kind,
        "cell": cell_to_json(cell),
        "evidence": [
            evidence_detail(repo, archives, projects, resource, model, item)
            for item in evidence
        ],
    }


def query_value(query: dict[str, list[str]], name: str, fallback: str | None = None) -> str | None:
    values = query.get(name)
    if not values:
        return fallback
    return values[-1] or fallback


def query_list(query: dict[str, list[str]], name: str, fallback: Iterable[str] = ()) -> tuple[str, ...]:
    values = query.get(name)
    if not values:
        return tuple(fallback)
    result: list[str] = []
    for value in values:
        result.extend(item for item in value.split(",") if item)
    return tuple(result)


class DashboardHandler(BaseHTTPRequestHandler):
    config: AppConfig

    def log_message(self, format: str, *args) -> None:
        print("%s - %s" % (self.address_string(), format % args), file=sys.stderr)

    def do_GET(self) -> None:
        try:
            parsed = urlparse(self.path)
            if parsed.path == "/":
                self.respond_html(APP_HTML)
            elif parsed.path == "/api/state":
                self.respond_json(self.handle_state(parse_qs(parsed.query)))
            elif parsed.path == "/api/cell":
                self.respond_json(self.handle_cell(parse_qs(parsed.query)))
            elif parsed.path == "/api/file":
                self.respond_json(self.handle_file(parse_qs(parsed.query)))
            else:
                self.respond_json({"error": "Not found"}, 404)
        except AppError as error:
            self.respond_json({"error": str(error)}, error.status)
        except Exception as error:  # pragma: no cover - defensive server boundary
            self.respond_json({"error": str(error)}, 500)

    def archive_arg(self, query: dict[str, list[str]]) -> str | None:
        return query_value(query, "archive", self.config.archive)

    def source_snapshot(self, query: dict[str, list[str]]) -> str | None:
        return query_value(query, "source_snapshot")

    def plugins(self, query: dict[str, list[str]]) -> tuple[str, ...]:
        return query_list(query, "plugin", self.config.plugins)

    def models(self, query: dict[str, list[str]]) -> tuple[str, ...]:
        return query_list(query, "model", self.config.models)

    def handle_state(self, query: dict[str, list[str]]) -> dict:
        return build_state(
            self.config.repo,
            self.archive_arg(query),
            self.source_snapshot(query),
            self.plugins(query),
            self.models(query),
        )

    def handle_cell(self, query: dict[str, list[str]]) -> dict:
        resource = query_value(query, "resource")
        model = query_value(query, "model")
        if resource is None or model is None:
            raise AppError("resource and model are required")
        return build_cell_detail(
            self.config.repo,
            self.archive_arg(query),
            self.source_snapshot(query),
            unquote(resource),
            unquote(model),
            query_value(query, "kind"),
            self.plugins(query),
            self.models(query),
        )

    def handle_file(self, query: dict[str, list[str]]) -> dict:
        archive_id = query_value(query, "archive_id")
        relative_path = query_value(query, "path")
        if archive_id is None or relative_path is None:
            raise AppError("archive_id and path are required")
        archives = open_archives(self.config.repo, self.archive_arg(query))
        archive = archive_by_id(archives, archive_id)
        path = safe_archive_path(archive, unquote(relative_path))
        return read_text_preview(path, 400_000)

    def respond_html(self, content: str) -> None:
        body = content.encode("utf-8")
        self.send_response(200)
        self.send_header("Content-Type", "text/html; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def respond_json(self, payload: dict, status: int = 200) -> None:
        body = json.dumps(payload, ensure_ascii=False).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)


APP_HTML = r"""<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Tactical E2E Dashboard</title>
<style>
:root {
  --bg: #f5f6f7;
  --panel: #ffffff;
  --ink: #20242a;
  --muted: #667085;
  --line: #d7dce2;
  --soft: #eef1f4;
  --win: #dff5e7;
  --cut: #ece8ff;
  --loss: #ffe5e1;
  --noise: #fff0c2;
  --fail: #ffe0ea;
  --money: #ddf7f1;
  --burn: #ffe7d5;
  --unknown: #edf0f2;
}
* { box-sizing: border-box; }
body {
  background: var(--bg);
  color: var(--ink);
  font: 14px/1.45 ui-sans-serif, system-ui, -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif;
  margin: 0;
}
button, select {
  font: inherit;
}
.app {
  display: grid;
  grid-template-rows: auto 1fr;
  min-height: 100vh;
}
.topbar {
  align-items: center;
  background: var(--panel);
  border-bottom: 1px solid var(--line);
  display: grid;
  gap: 12px;
  grid-template-columns: 1fr auto;
  padding: 12px 16px;
}
.title {
  display: flex;
  flex-wrap: wrap;
  gap: 8px 14px;
  min-width: 0;
}
.title h1 {
  font-size: 18px;
  margin: 0;
}
.meta {
  color: var(--muted);
  font-size: 12px;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}
.controls {
  align-items: center;
  display: flex;
  gap: 8px;
}
.controls select,
.controls button {
  background: #fff;
  border: 1px solid var(--line);
  border-radius: 6px;
  color: var(--ink);
  min-height: 32px;
  padding: 5px 8px;
}
.layout {
  display: grid;
  gap: 12px;
  grid-template-columns: minmax(0, 1fr) minmax(360px, 34vw);
  padding: 12px;
}
.dashboard,
.detail {
  background: var(--panel);
  border: 1px solid var(--line);
  border-radius: 8px;
  min-width: 0;
}
.dashboard {
  overflow: hidden;
}
.summary {
  border-bottom: 1px solid var(--line);
  display: grid;
  gap: 10px;
  grid-template-columns: repeat(5, minmax(0, 1fr));
  padding: 10px;
}
.metric {
  background: var(--soft);
  border-radius: 6px;
  padding: 8px;
}
.metric strong {
  display: block;
  font-size: 18px;
}
.metric span {
  color: var(--muted);
  font-size: 12px;
}
.table-scroll {
  max-height: calc(100vh - 168px);
  overflow: auto;
}
table {
  border-collapse: separate;
  border-spacing: 0;
  min-width: max-content;
  width: 100%;
}
th, td {
  border-bottom: 1px solid var(--line);
  border-right: 1px solid var(--line);
  padding: 8px 10px;
  text-align: center;
  white-space: nowrap;
}
thead th {
  background: #fafbfc;
  position: sticky;
  top: 0;
  z-index: 4;
}
thead tr:nth-child(2) th {
  top: 36px;
  z-index: 3;
}
.resource-col {
  background: #fff;
  left: 0;
  max-width: 320px;
  min-width: 260px;
  position: sticky;
  text-align: left;
  z-index: 5;
}
thead .resource-col {
  background: #fafbfc;
  z-index: 6;
}
.resource-name {
  font-weight: 650;
}
.plugin {
  color: var(--muted);
  display: block;
  font-size: 12px;
  margin-top: 2px;
}
.chip {
  align-items: center;
  border: 1px solid transparent;
  border-radius: 999px;
  display: inline-flex;
  font-family: "Apple Color Emoji", "Segoe UI Emoji", "Noto Color Emoji", sans-serif;
  height: 24px;
  justify-content: center;
  min-width: 24px;
  padding: 0 5px;
}
.chip.win { background: var(--win); }
.chip.cut { background: var(--cut); }
.chip.loss { background: var(--loss); }
.chip.noise { background: var(--noise); }
.chip.fail { background: var(--fail); }
.chip.money { background: var(--money); }
.chip.burn { background: var(--burn); }
.chip.unknown { background: var(--unknown); color: var(--muted); }
.cell-button {
  background: transparent;
  border: 0;
  border-radius: 6px;
  cursor: pointer;
  display: inline-flex;
  gap: 3px;
  justify-content: center;
  font-family: "Apple Color Emoji", "Segoe UI Emoji", "Noto Color Emoji", sans-serif;
  letter-spacing: 0;
  min-width: 52px;
  padding: 5px 8px;
}
.cell-button:hover,
.cell-button.active {
  background: #eef6ff;
  outline: 1px solid #9cc7f0;
}
.detail {
  display: grid;
  grid-template-rows: auto auto 1fr;
  max-height: calc(100vh - 88px);
  min-height: 520px;
  overflow: hidden;
}
.detail-head {
  border-bottom: 1px solid var(--line);
  padding: 12px;
}
.detail-head h2 {
  font-size: 16px;
  margin: 0 0 4px;
}
.tabs {
  border-bottom: 1px solid var(--line);
  display: flex;
  gap: 4px;
  padding: 8px;
}
.tabs button {
  background: transparent;
  border: 1px solid transparent;
  border-radius: 6px;
  cursor: pointer;
  padding: 6px 9px;
}
.tabs button.active {
  background: var(--soft);
  border-color: var(--line);
}
.detail-body {
  overflow: auto;
  padding: 12px;
}
.section {
  display: grid;
  gap: 10px;
}
.evidence {
  border: 1px solid var(--line);
  border-radius: 8px;
  overflow: hidden;
}
.evidence h3 {
  background: #fafbfc;
  border-bottom: 1px solid var(--line);
  font-size: 13px;
  margin: 0;
  padding: 8px 10px;
}
.evidence-content {
  display: grid;
  gap: 10px;
  padding: 10px;
}
.kv {
  color: var(--muted);
  display: grid;
  gap: 4px;
  grid-template-columns: 90px minmax(0, 1fr);
  overflow-wrap: anywhere;
}
.case {
  background: #fafbfc;
  border: 1px solid var(--line);
  border-radius: 6px;
  padding: 8px;
}
.case-title {
  font-weight: 650;
  margin-bottom: 6px;
}
.transcript {
  background: #fbfcfd;
  border: 1px solid var(--line);
  border-radius: 6px;
  display: grid;
  gap: 8px;
  padding: 8px;
}
.session-arm {
  display: grid;
  gap: 8px;
}
.session-arm + .session-arm {
  border-top: 1px solid var(--line);
  margin-top: 10px;
  padding-top: 10px;
}
.session-arm h4 {
  color: var(--muted);
  font-size: 12px;
  letter-spacing: .02em;
  margin: 0;
  text-transform: uppercase;
}
.session-arm.compact {
  gap: 4px;
  padding: 8px;
}
.transcript-head {
  align-items: center;
  color: var(--muted);
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
  justify-content: space-between;
}
.message {
  border: 1px solid var(--line);
  border-radius: 6px;
  overflow: hidden;
}
.message-role {
  background: #f0f3f6;
  color: var(--muted);
  font-size: 12px;
  font-weight: 700;
  letter-spacing: .02em;
  padding: 6px 8px;
  text-transform: uppercase;
}
.message.assistant {
  border-color: #8ab6de;
}
.message.assistant .message-role {
  background: #e8f3ff;
  color: #184d79;
}
.message.empty pre {
  color: #f8bcc6;
}
.evaluator-results {
  border: 1px solid var(--line);
  border-radius: 6px;
  overflow: hidden;
}
.result-entry {
  border: 0;
  border-radius: 0;
  border-top: 1px solid var(--line);
  overflow: visible;
}
.result-entry > summary.result-row {
  background: #fff;
  border-top: 0;
  cursor: pointer;
  list-style: none;
}
.result-entry > summary.result-row::-webkit-details-marker {
  display: none;
}
.result-row {
  align-items: center;
  border-top: 1px solid var(--line);
  display: grid;
  gap: 8px;
  grid-template-columns: minmax(62px, .45fr) minmax(120px, 1.2fr) minmax(84px, .7fr) minmax(80px, .6fr) minmax(80px, .6fr) minmax(120px, 1fr);
  padding: 7px 8px;
}
.result-row:first-child {
  border-top: 0;
}
.result-head {
  align-items: center;
  background: #fafbfc;
  color: var(--muted);
  font-size: 12px;
  font-weight: 700;
  text-transform: uppercase;
}
.status-pill {
  border-radius: 999px;
  display: inline-flex;
  font-size: 12px;
  font-weight: 700;
  justify-content: center;
  min-width: 54px;
  padding: 3px 8px;
}
.status-pill.pass { background: var(--win); color: #1f6b3a; }
.status-pill.fail { background: var(--loss); color: #8a2c21; }
.status-pill.warn { background: var(--noise); color: #735500; }
.status-pill.unknown { background: var(--unknown); color: var(--muted); }
.result-expansion {
  background: #fbfcfd;
  border-top: 1px solid var(--line);
  display: grid;
  gap: 10px;
  padding: 10px 12px 12px;
}
.reason-change {
  color: var(--muted);
  font-size: 12px;
  font-weight: 700;
}
.comparison-reason {
  background: #fff;
  border: 1px solid var(--line);
  border-radius: 6px;
  color: var(--muted);
  display: grid;
  gap: 4px;
  padding: 8px;
}
.comparison-reason strong,
.reason-title {
  font-size: 12px;
  font-weight: 700;
}
.reason-columns {
  display: grid;
  gap: 10px;
  grid-template-columns: repeat(2, minmax(0, 1fr));
}
.reason-panel {
  background: #fff;
  border: 1px solid var(--line);
  border-radius: 6px;
  display: grid;
  gap: 8px;
  min-width: 0;
  padding: 8px;
}
.reason-path {
  color: var(--muted);
  font-size: 12px;
  overflow-wrap: anywhere;
}
.reason-panel pre {
  font-size: 12px;
  max-height: 360px;
}
.reason-warning {
  background: var(--noise);
  border-radius: 6px;
  color: #735500;
  font-size: 12px;
  font-weight: 700;
  padding: 6px 8px;
}
.reason-empty {
  color: var(--muted);
  font-size: 12px;
  padding: 8px 0;
}
pre {
  background: #111418;
  border-radius: 6px;
  color: #eef2f6;
  margin: 0;
  max-height: 320px;
  overflow: auto;
  padding: 10px;
  white-space: pre-wrap;
}
details {
  border: 1px solid var(--line);
  border-radius: 6px;
  overflow: hidden;
}
summary {
  background: #fafbfc;
  cursor: pointer;
  padding: 8px;
}
.empty {
  color: var(--muted);
  padding: 18px;
}
@media (max-width: 1050px) {
  .layout {
    grid-template-columns: 1fr;
  }
  .detail {
    max-height: none;
  }
  .reason-columns {
    grid-template-columns: 1fr;
  }
}
</style>
</head>
<body>
<div class="app">
  <header class="topbar">
    <div class="title">
      <h1>Tactical E2E Dashboard</h1>
      <div class="meta" id="archiveMeta"></div>
    </div>
    <div class="controls">
      <select id="groupSelect" aria-label="Source snapshot"></select>
      <button id="reloadButton" type="button">Refresh</button>
    </div>
  </header>
  <main class="layout">
    <section class="dashboard">
      <div class="summary" id="summary"></div>
      <div class="table-scroll" id="tableMount"></div>
    </section>
    <aside class="detail" id="detailPane"></aside>
  </main>
</div>
<script>
const ICON_CLASS = {
  "✅": "win",
  "⛔️": "loss",
  "🥇": "win",
  "🗡️": "cut",
  "👎": "loss",
  "💥": "noise",
  "⚠️": "fail",
  "💵": "money",
  "🔥": "burn",
  "⁇": "unknown"
};
const KNOWN_ICONS = ["⛔️", "✅", "🥇", "🗡️", "👎", "💥", "⚠️", "💵", "🔥", "⁇"];
let state = null;
let selected = null;
let activeTab = "reports";

function params(extra = {}) {
  const url = new URL(window.location.href);
  const query = new URLSearchParams(url.search);
  for (const [key, value] of Object.entries(extra)) {
    if (value === undefined || value === null || value === "") query.delete(key);
    else query.set(key, value);
  }
  return query;
}

async function fetchJSON(path, query) {
  const response = await fetch(path + "?" + query.toString());
  const payload = await response.json();
  if (!response.ok) throw new Error(payload.error || response.statusText);
  return payload;
}

function escapeHTML(value) {
  return String(value ?? "")
    .replaceAll("&", "&amp;")
    .replaceAll("<", "&lt;")
    .replaceAll(">", "&gt;")
    .replaceAll('"', "&quot;");
}

function statusBaubles(text) {
  const icons = [];
  let index = 0;
  while (index < text.length) {
    const icon = KNOWN_ICONS.find(candidate => text.startsWith(candidate, index));
    if (icon) {
      icons.push(icon);
      index += icon.length;
    } else {
      icons.push(text[index]);
      index += 1;
    }
  }
  return icons.map(icon => `<span class="chip ${ICON_CLASS[icon] || "unknown"}">${escapeHTML(icon)}</span>`).join("");
}

function shortSnapshot(value) {
  if (!value) return "legacy archive";
  if (value.startsWith("archive:")) return value.slice("archive:".length);
  return value.length > 22 ? value.slice(0, 12) + "…" + value.slice(-8) : value;
}

function renderSummary() {
  const rows = state.rows || [];
  const failures = state.failures || [];
  const cells = rows.flatMap(row => Object.values(row.cells));
  const wins = cells.reduce((sum, cell) => sum + (cell.counts["🥇"] || 0), 0);
  const losses = cells.reduce((sum, cell) => sum + (cell.counts["👎"] || 0), 0);
  const noise = cells.reduce((sum, cell) => sum + (cell.counts["💥"] || 0), 0);
  const unneeded = cells.reduce((sum, cell) => sum + (cell.counts["🗡️"] || 0), 0);
  document.getElementById("summary").innerHTML = [
    metric(rows.length, "resources"),
    metric(state.models.length, "models"),
    metric(wins, "wins"),
    metric(losses, "losses"),
    metric(failures.length || noise + unneeded, failures.length ? "run failures" : "noise / unneeded")
  ].join("");
}

function metric(value, label) {
  return `<div class="metric"><strong>${escapeHTML(value)}</strong><span>${escapeHTML(label)}</span></div>`;
}

function renderGroups() {
  const select = document.getElementById("groupSelect");
  select.innerHTML = "";
  for (const group of state.groups) {
    const option = document.createElement("option");
    option.value = group.key;
    option.selected = group.key === state.selected_group;
    option.textContent = `${shortSnapshot(group.key)} · ${group.archives.length} archive${group.archives.length === 1 ? "" : "s"}`;
    select.append(option);
  }
  select.disabled = state.groups.length <= 1;
  document.getElementById("archiveMeta").textContent =
    `${state.archive_root} · ${state.archives.map(archive => archive.id).join(", ") || "no archives"}`;
}

function renderTable() {
  if (!state.rows.length) {
    document.getElementById("tableMount").innerHTML = `<div class="empty">No archive results.</div>`;
    return;
  }
  const headModels = state.models.map(model => `<th colspan="2">${escapeHTML(model)}</th>`).join("");
  const subHead = state.models.map(() => `<th>Discover</th><th>Invoke</th>`).join("");
  const body = state.rows.map(row => {
    const cells = state.models.map(model => {
      const cell = row.cells[model];
      return `
        <td>${cellButton(row.resource, model, "discovery", cell.discovery)}</td>
        <td>${cellButton(row.resource, model, "invocation", cell.invocation)}</td>`;
    }).join("");
    return `<tr>
      <th class="resource-col"><span class="resource-name">${escapeHTML(row.resource)}</span><span class="plugin">${escapeHTML(row.plugin)}</span></th>
      ${cells}
    </tr>`;
  }).join("");
  document.getElementById("tableMount").innerHTML = `
    <table>
      <thead>
        <tr><th class="resource-col" rowspan="2">Resource</th>${headModels}</tr>
        <tr>${subHead}</tr>
      </thead>
      <tbody>${body}</tbody>
    </table>`;
}

function cellButton(resource, model, kind, label) {
  const active = selected && selected.resource === resource && selected.model === model && selected.kind === kind;
  return `<button class="cell-button ${active ? "active" : ""}" type="button"
    data-resource="${escapeHTML(resource)}"
    data-model="${escapeHTML(model)}"
    data-kind="${escapeHTML(kind)}">${statusBaubles(label)}</button>`;
}

async function selectCell(resource, model, kind) {
  selected = { resource, model, kind };
  renderTable();
  const detail = await fetchJSON("/api/cell", params({
    source_snapshot: state.selected_group,
    resource,
    model,
    kind
  }));
  renderDetail(detail);
}

function renderDetail(detail) {
  const pane = document.getElementById("detailPane");
  const tabs = ["reports", "session", "evaluators", "summary"];
  pane.innerHTML = `
    <div class="detail-head">
      <h2>${escapeHTML(detail.resource)}</h2>
      <div class="meta">${escapeHTML(detail.model)} · ${escapeHTML(detail.kind || "cell")} · ${escapeHTML(detail.cell.invocation || "")}</div>
    </div>
    <div class="tabs">${tabs.map(tab => `<button type="button" data-tab="${tab}" class="${activeTab === tab ? "active" : ""}">${tab[0].toUpperCase() + tab.slice(1)}</button>`).join("")}</div>
    <div class="detail-body">${renderTab(detail)}</div>`;
}

function renderTab(detail) {
  if (!detail.evidence.length) return `<div class="empty">No archived evidence for this cell.</div>`;
  if (activeTab === "session") return renderSession(detail);
  if (activeTab === "evaluators") return renderEvaluators(detail);
  if (activeTab === "summary") return renderDetailSummary(detail);
  return renderReports(detail);
}

function renderReports(detail) {
  return `<div class="section">${detail.evidence.map(item => `
    <article class="evidence">
      <h3>${escapeHTML(item.archive)} · ${escapeHTML(item.suite)} · ${escapeHTML(item.report_path)}</h3>
      <div class="evidence-content">
        ${item.cases.length ? item.cases.map(renderCase).join("") : `<pre>${escapeHTML(JSON.stringify(item.report, null, 2))}</pre>`}
      </div>
    </article>`).join("")}</div>`;
}

function renderCase(testCase) {
  const title = testCase.case || testCase.name || "case";
  const assertions = testCase.assertions || [];
  const matches = testCase.matches || [];
  return `<div class="case">
    <div class="case-title">${escapeHTML(title)}</div>
    ${assertions.length ? `<pre>${escapeHTML(JSON.stringify(assertions, null, 2))}</pre>` : ""}
    ${matches.length ? `<pre>${escapeHTML(JSON.stringify(matches, null, 2))}</pre>` : ""}
  </div>`;
}

function renderSession(detail) {
  return `<div class="section">${detail.evidence.map(item => `
    <article class="evidence">
      <h3>${escapeHTML(item.archive)} · ${escapeHTML(item.suite)}</h3>
      <div class="evidence-content">
        ${renderKV("run", item.suite_record?.run_id || "")}
        ${renderKV("status", item.suite_record?.status || item.archive_status)}
        ${item.session_arms?.length ? renderKV("session arms", item.session_arms.map(arm => arm.run_id ? `${arm.label}: ${arm.run_id}` : arm.label).join(" · ")) : ""}
        ${renderTranscripts(item)}
        ${item.commands.map(renderCommand).join("")}
        ${renderSessionFiles(item)}
        ${item.inputs.map(renderPreview).join("")}
      </div>
    </article>`).join("")}</div>`;
}

function renderTranscripts(item) {
  const transcripts = item.transcripts || [];
  if (!transcripts.length) return `<div class="empty">No archived transcript messages.</div>`;
  return groupByArm(transcripts, item.session_arms).map(group => `
    <section class="session-arm">
      <h4>${escapeHTML(titleCase(group.label))}${group.runId ? ` · ${escapeHTML(group.runId)}` : ""}</h4>
      ${group.items.map(transcript => {
    const empty = transcript.assistant_empty ? ` · ${transcript.assistant_empty} empty assistant` : "";
    const source = transcript.source && transcript.source !== "archive" ? ` · ${transcript.source}` : "";
    return `<details open>
      <summary>Transcript · ${escapeHTML(transcript.path)} · ${escapeHTML(transcript.assistant_count)} assistant${empty}${source}</summary>
      <div class="transcript">
        <div class="transcript-head">
          <span>${escapeHTML(transcript.message_count)} messages</span>
          <span>${escapeHTML(transcript.source_path || transcript.path)}</span>
        </div>
        ${transcript.messages.map(renderTranscriptMessage).join("")}
      </div>
    </details>`;
      }).join("")}
    </section>
  `).join("");
}

function renderSessionFiles(item) {
  const files = item.session_files || [];
  if (!files.length) return "";
  return `<details open><summary>Session files</summary>${groupByArm(files, item.session_arms).map(group => `
    <section class="session-arm compact">
      <h4>${escapeHTML(titleCase(group.label))}${group.runId ? ` · ${escapeHTML(group.runId)}` : ""}</h4>
      <pre>${escapeHTML(group.items.map(file => `${file.path} (${file.size} bytes)`).join("\n"))}</pre>
    </section>
  `).join("")}</details>`;
}

function groupByArm(items, arms = []) {
  const preferred = (arms || []).map(arm => arm.label).filter(Boolean);
  const labels = [...preferred, ...items.map(item => item.arm || "session")];
  return [...new Set(labels)].map(label => {
    const groupItems = items.filter(item => (item.arm || "session") === label);
    if (!groupItems.length) return null;
    return {
      label,
      runId: groupItems.find(item => item.run_id)?.run_id || "",
      items: groupItems
    };
  }).filter(Boolean);
}

function titleCase(value) {
  const text = String(value || "session");
  return text.charAt(0).toUpperCase() + text.slice(1);
}

function renderTranscriptMessage(message) {
  const empty = message.empty ? " empty" : "";
  const content = message.empty
    ? (message.role === "assistant" ? "(empty assistant response)" : `(empty ${message.role} message)`)
    : message.content;
  const truncated = message.truncated ? "\n\n[truncated]" : "";
  return `<div class="message ${escapeHTML(message.role)}${empty}">
    <div class="message-role">${escapeHTML(message.role)} · ${escapeHTML(message.chars)} chars</div>
    <pre>${escapeHTML(content + truncated)}</pre>
  </div>`;
}

function renderCommand(command) {
  return `<details>
    <summary>${escapeHTML(command.sequence)} · ${escapeHTML(command.step)} · exit ${escapeHTML(command.returncode)}</summary>
    <div class="evidence-content">
      <pre>${escapeHTML(command.args.join(" "))}</pre>
      ${command.stdout.content ? `<pre>${escapeHTML(command.stdout.content)}</pre>` : ""}
      ${command.stderr.content ? `<pre>${escapeHTML(command.stderr.content)}</pre>` : ""}
    </div>
  </details>`;
}

function renderEvaluators(detail) {
  return `<div class="section">${detail.evidence.map(item => `
    <article class="evidence">
      <h3>${escapeHTML(item.archive)} · ${escapeHTML(item.suite)}</h3>
      <div class="evidence-content">
        ${renderEvaluatorResults(item)}
        ${item.evaluators.length ? item.evaluators.map(renderPreview).join("") : `<div class="empty">No evaluator files captured.</div>`}
      </div>
    </article>`).join("")}</div>`;
}

function renderEvaluatorResults(item) {
  const results = item.evaluator_results || [];
  if (!results.length) return `<div class="empty">No evaluator outcomes in this report.</div>`;
  const comparison = results.some(result => result.baseline || result.invocation);
  return `<div class="evaluator-results">
    <div class="result-row result-head">
      <span>Run</span>
      <span>Case</span>
      <span>Evaluator</span>
      <span>${comparison ? "Baseline" : "Trace"}</span>
      <span>${comparison ? "Invocation" : "Outcome"}</span>
      <span>${comparison ? "Change / Output" : "Reason"}</span>
    </div>
    ${results.map(result => renderEvaluatorResult(result, comparison)).join("")}
  </div>`;
}

function renderEvaluatorResult(result, comparison) {
  const runOutcome = comparison ? result.invocation : result.outcome;
  const trace = comparison ? result.baseline : result.conversation;
  const expansion = renderEvaluatorExpansion(result, comparison);
  const change = comparison ? result.change || (expansion ? "details" : result.reason) : result.reason;
  const cells = `
    <span>${statusBaubles(result.icon || "⁇")}</span>
    <span>${escapeHTML(result.case)}</span>
    <span>${escapeHTML(result.evaluator)}</span>
    <span>${comparison ? renderOutcome(trace) : escapeHTML(trace || "—")}</span>
    <span>${renderOutcome(runOutcome)}</span>
    <span class="reason-change">${escapeHTML(change || "—")}</span>`;
  if (!expansion) return `<div class="result-row">${cells}</div>`;
  return `<details open class="result-entry">
    <summary class="result-row">${cells}</summary>
    ${expansion}
  </details>`;
}

function renderEvaluatorExpansion(result, comparison) {
  if (!comparison) {
    if (!result.reason) return "";
    return `<div class="result-expansion">${renderOutputPanel("Reason", result.reason, result.report_path)}</div>`;
  }
  const parts = [];
  if (result.reason) {
    parts.push(`<div class="comparison-reason">
      <strong>Comparison reason${result.report_path ? ` · ${escapeHTML(result.report_path)}` : ""}</strong>
      <span>${escapeHTML(result.reason)}</span>
    </div>`);
  }
  const evaluator = String(result.evaluator || "evaluator").toLowerCase();
  const noun = evaluator === "judge" ? "judge output" : `${evaluator} output`;
  if (result.baseline_reason || result.invocation_reason) {
    parts.push(`<div class="reason-columns">
      ${renderOutputPanel(`Baseline ${noun}`, result.baseline_reason, result.baseline_report_path, result.baseline_outcome || result.baseline)}
      ${renderOutputPanel(`Invocation ${noun}`, result.invocation_reason, result.invocation_report_path, result.invocation_outcome || result.invocation)}
    </div>`);
  }
  return parts.length ? `<div class="result-expansion">${parts.join("")}</div>` : "";
}

function renderOutputPanel(label, reason, path, outcome = "") {
  return `<section class="reason-panel">
    <div class="reason-title">${escapeHTML(label)}</div>
    ${path ? `<div class="reason-path">${escapeHTML(path)}</div>` : ""}
    ${reason && reasonLikelyTruncated(reason) ? `<div class="reason-warning">Stored reason appears truncated at 200 characters.</div>` : ""}
    ${reason ? `<pre>${escapeHTML(reason)}</pre>` : `<div class="reason-empty">${escapeHTML(missingReasonMessage(label, outcome))}</div>`}
  </section>`;
}

function reasonLikelyTruncated(reason) {
  const text = String(reason || "").trimEnd();
  return text.length === 200 && !/[.!?)]$/.test(text);
}

function missingReasonMessage(label, outcome) {
  const subject = String(label || "Evaluator output")
    .replace(/^(Baseline|Invocation)\s+/, "")
    .replace(/\s+output$/, "");
  const title = subject.charAt(0).toUpperCase() + subject.slice(1);
  const status = String(outcome || "").toLowerCase();
  if (["pass", "passed"].includes(status)) return `${title} passed; no reason recorded.`;
  if (["fail", "failed"].includes(status)) return `${title} failed; no reason recorded.`;
  if (status) return `${title} ${status}; no reason recorded.`;
  return "No reason recorded.";
}

function renderOutcome(value) {
  if (!value) return `<span class="status-pill unknown">—</span>`;
  return `<span class="status-pill ${statusClass(value)}">${escapeHTML(value)}</span>`;
}

function statusClass(value) {
  const normalized = String(value || "").toLowerCase();
  if (["pass", "passed", "unchangedpass", "improved"].includes(normalized)) return "pass";
  if (["fail", "failed", "regressed", "unchangedfail"].includes(normalized)) return "fail";
  if (["deferred", "malformed", "errored", "error"].includes(normalized)) return "warn";
  return "unknown";
}

function renderDetailSummary(detail) {
  return `<div class="section">${detail.evidence.map(item => `
    <article class="evidence">
      <h3>${escapeHTML(item.archive)} · ${escapeHTML(item.kind)}</h3>
      <div class="evidence-content">
        ${renderKV("suite", item.suite)}
        ${renderKV("report", item.report_path)}
        ${renderKV("cases", item.cases.length)}
        ${renderKV("commands", item.commands.length)}
        ${renderKV("files", item.session_files.length)}
        ${renderKV("transcripts", (item.transcripts || []).length)}
        ${renderKV("assistant turns", (item.transcripts || []).reduce((sum, transcript) => sum + transcript.assistant_count, 0))}
        ${renderKV("evaluator outcomes", (item.evaluator_results || []).length)}
      </div>
    </article>`).join("")}</div>`;
}

function renderKV(key, value) {
  return `<div class="kv"><strong>${escapeHTML(key)}</strong><span>${escapeHTML(value)}</span></div>`;
}

function renderPreview(file) {
  const preview = file.preview || file;
  const source = file.source ? `${file.source} · ` : "";
  return `<details>
    <summary>${escapeHTML(source + file.path)}</summary>
    <pre>${escapeHTML(preview.content || "")}</pre>
  </details>`;
}

async function load() {
  const query = params();
  state = await fetchJSON("/api/state", query);
  renderGroups();
  renderSummary();
  renderTable();
  document.getElementById("detailPane").innerHTML = `
    <div class="detail-head"><h2>Archive</h2><div class="meta">${escapeHTML(shortSnapshot(state.selected_group || ""))}</div></div>
    <div class="tabs"><button class="active" type="button">Summary</button></div>
    <div class="detail-body">${renderArchiveSummary()}</div>`;
}

function renderArchiveSummary() {
  return `<div class="section">${state.archives.map(archive => `
    <article class="evidence">
      <h3>${escapeHTML(archive.id)}</h3>
      <div class="evidence-content">
        ${renderKV("created", archive.created_at)}
        ${renderKV("status", archive.status)}
        ${renderKV("failures", archive.failures)}
      </div>
    </article>`).join("")}</div>`;
}

document.addEventListener("click", event => {
  const cell = event.target.closest(".cell-button");
  if (cell) selectCell(cell.dataset.resource, cell.dataset.model, cell.dataset.kind);
  const tab = event.target.closest("[data-tab]");
  if (tab) {
    activeTab = tab.dataset.tab;
    if (selected) selectCell(selected.resource, selected.model, selected.kind);
  }
});

document.getElementById("groupSelect").addEventListener("change", event => {
  const url = new URL(window.location.href);
  url.searchParams.set("source_snapshot", event.target.value);
  window.history.replaceState(null, "", url);
  selected = null;
  load();
});
document.getElementById("reloadButton").addEventListener("click", load);
load().catch(error => {
  document.getElementById("tableMount").innerHTML = `<div class="empty">${escapeHTML(error.message)}</div>`;
});
</script>
</body>
</html>
"""


def parse_args(argv: list[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--archive", help="Archive id, archive path, or archive root directory.")
    parser.add_argument("--host", default="127.0.0.1")
    parser.add_argument("--port", type=int, default=8765)
    parser.add_argument("--plugin", action="append", default=[])
    parser.add_argument("--model", action="append", default=[])
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    args = parse_args(sys.argv[1:] if argv is None else argv)
    config = AppConfig(
        repo=REPO,
        archive=args.archive,
        plugins=tuple(args.plugin),
        models=tuple(args.model),
    )

    class ConfiguredHandler(DashboardHandler):
        pass

    ConfiguredHandler.config = config
    server = ThreadingHTTPServer((args.host, args.port), ConfiguredHandler)
    print(f"Serving E2E archive dashboard at http://{args.host}:{args.port}/", flush=True)
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        return 0
    finally:
        server.server_close()
    return 0


if __name__ == "__main__":
    sys.exit(main())
