"""Provider service for the Promptfoo invocation-phases pilot."""

from __future__ import annotations

from collections.abc import Mapping as MappingABC
from dataclasses import dataclass
import json
import os
from pathlib import Path
import re
try:
    from enum import StrEnum
except ImportError:
    from enum import Enum

    class StrEnum(str, Enum):
        def __str__(self) -> str:
            return self.value

from typing import Any, Literal, Mapping, Sequence


class Phase(StrEnum):
    RESEARCH = "research"
    DESIGN = "design"
    PLAN = "plan"
    RED_GREEN_REFACTOR = "red-green-refactor"
    CLEANUP = "cleanup"


class Arm(StrEnum):
    BASELINE = "baseline"
    INVOCATION = "invocation"


@dataclass(frozen=True)
class ArtifactInput:
    arm: Arm
    run_dir: Path
    phase: Phase


@dataclass(frozen=True)
class ConversationTurn:
    role: Literal["system", "user", "assistant"]
    content: str


@dataclass(frozen=True)
class ProviderResult:
    phase_name: Phase
    arm_name: Arm
    output: str
    provider_output: Mapping[str, Any]
    conversation: Sequence[ConversationTurn]


@dataclass(frozen=True)
class ComparisonEvidence:
    improved: int
    regressed: int
    inspectable_fields: tuple[str, ...]


class ArtifactInputError(Exception):
    pass


class PromptfooReadableError(Exception):
    pass


RUN_DIR_ENV = {
    Arm.BASELINE: "AILLY_PROMPTFOO_BASELINE_RUN_DIR",
    Arm.INVOCATION: "AILLY_PROMPTFOO_INVOCATION_RUN_DIR",
}


def _expected_values(enum_type: type[StrEnum]) -> str:
    return ", ".join(item.value for item in enum_type)


def _parse_enum(raw: str, enum_type: type[StrEnum], label: str) -> StrEnum:
    if not isinstance(raw, str) or not raw.strip():
        raise ArtifactInputError(f"Missing {label} value")
    value = raw.strip()
    try:
        return enum_type(value)
    except ValueError as exc:
        expected = _expected_values(enum_type)
        raise ArtifactInputError(
            f"Unknown {label} {value!r}; expected one of: {expected}"
        ) from exc


def parse_phase(raw: str) -> Phase:
    return _parse_enum(raw, Phase, "phase")


def parse_arm(raw: str) -> Arm:
    return _parse_enum(raw, Arm, "arm")


def resolve_artifact_input(raw_arm: str, raw_phase: str) -> ArtifactInput:
    arm = parse_arm(raw_arm)
    phase = parse_phase(raw_phase)
    env_name = RUN_DIR_ENV[arm]
    raw_run_dir = os.environ.get(env_name)
    if not raw_run_dir:
        raise ArtifactInputError(f"Missing required artifact env var {env_name}")
    return ArtifactInput(arm=arm, run_dir=Path(raw_run_dir).expanduser(), phase=phase)


def read_artifact_result(artifact_input: ArtifactInput) -> ProviderResult:
    path = _find_artifact_path(artifact_input)
    text = path.read_text(encoding="utf-8")
    if path.suffix == ".json":
        return _read_json_artifact(artifact_input, path, text)
    return _read_conversation_artifact(artifact_input, path, text)


def build_promptfoo_response(result: ProviderResult) -> Mapping[str, Any]:
    conversation = [
        {"role": turn.role, "content": turn.content} for turn in result.conversation
    ]
    return {
        "output": result.output,
        "providerOutput": result.provider_output,
        "metadata": {
            "phaseName": result.phase_name.value,
            "armName": result.arm_name.value,
            "conversation": conversation,
        },
    }


def compare_phase_results(
    baseline: ProviderResult,
    invocation: ProviderResult,
) -> ComparisonEvidence:
    baseline_has_output = bool(baseline.output.strip())
    invocation_has_output = bool(invocation.output.strip())
    improved = 1 if invocation_has_output and invocation.output != baseline.output else 0
    regressed = 1 if baseline_has_output and not invocation_has_output else 0
    return ComparisonEvidence(
        improved=improved,
        regressed=regressed,
        inspectable_fields=(
            "results.stats",
            "response.output",
            "score",
            "gradingResult.reason",
            "error",
            "providerOutput",
        ),
    )


def _find_artifact_path(artifact_input: ArtifactInput) -> Path:
    run_dir = artifact_input.run_dir
    if not run_dir.is_dir():
        raise ArtifactInputError(f"Artifact run dir does not exist: {run_dir}")

    phase = artifact_input.phase.value
    direct_names = (
        f"{phase}.json",
        f"{phase}.yaml",
        f"{phase}.yml",
        f"{artifact_input.arm.value}.{phase}.json",
        f"{artifact_input.arm.value}.{phase}.yaml",
        f"{artifact_input.arm.value}.{phase}.yml",
    )
    for name in direct_names:
        candidate = run_dir / name
        if candidate.is_file():
            return candidate

    matches = sorted(
        path
        for suffix in ("*.json", "*.yaml", "*.yml")
        for path in run_dir.glob(suffix)
        if phase in path.stem
    )
    if matches:
        return matches[0]

    raise ArtifactInputError(
        f"No artifact file for phase {phase!r} in run dir {run_dir}"
    )


def _read_json_artifact(
    artifact_input: ArtifactInput,
    path: Path,
    text: str,
) -> ProviderResult:
    try:
        data = json.loads(text)
    except json.JSONDecodeError as exc:
        raise ArtifactInputError(f"Invalid JSON artifact {path}: {exc}") from exc
    if not isinstance(data, MappingABC):
        raise ArtifactInputError(f"JSON artifact {path} must be an object")

    turns = _turns_from_json_value(
        data.get("conversation") or data.get("messages") or data.get("turns")
    )
    output = _last_assistant_output(turns, path)
    provider_output = data.get("providerOutput")
    if not isinstance(provider_output, MappingABC):
        provider_output = {
            "artifactPath": str(path),
            "artifactFormat": "json",
        }
    return ProviderResult(
        phase_name=artifact_input.phase,
        arm_name=artifact_input.arm,
        output=output,
        provider_output=dict(provider_output),
        conversation=tuple(turns),
    )


def _read_conversation_artifact(
    artifact_input: ArtifactInput,
    path: Path,
    text: str,
) -> ProviderResult:
    turns = _turns_from_yamlish_text(text)
    output = _last_assistant_output(turns, path)
    return ProviderResult(
        phase_name=artifact_input.phase,
        arm_name=artifact_input.arm,
        output=output,
        provider_output={
            "artifactPath": str(path),
            "artifactFormat": path.suffix.lstrip(".") or "text",
        },
        conversation=tuple(turns),
    )


def _turns_from_json_value(raw_turns: Any) -> list[ConversationTurn]:
    if not isinstance(raw_turns, list):
        raise ArtifactInputError(
            "Artifact must contain conversation, messages, or turns as a list"
        )
    turns: list[ConversationTurn] = []
    for index, item in enumerate(raw_turns):
        if not isinstance(item, MappingABC):
            raise ArtifactInputError(f"Conversation turn {index} must be an object")
        turns.append(_turn_from_mapping(item, index))
    return turns


def _turn_from_mapping(item: MappingABC[str, Any], index: int) -> ConversationTurn:
    role = item.get("role")
    content = item.get("content", item.get("body", item.get("text", "")))
    if role not in {"system", "user", "assistant"}:
        raise ArtifactInputError(f"Conversation turn {index} has unknown role {role!r}")
    if not isinstance(content, str):
        raise ArtifactInputError(f"Conversation turn {index} content must be text")
    return ConversationTurn(role=role, content=content)


def _turns_from_yamlish_text(text: str) -> list[ConversationTurn]:
    turns: list[ConversationTurn] = []
    for index, doc in enumerate(re.split(r"(?m)^---\s*$", text)):
        role_match = re.search(r"(?m)^role:\s*(system|user|assistant)\s*$", doc)
        if not role_match:
            continue
        content = _extract_yamlish_content(doc)
        turns.append(ConversationTurn(role=role_match.group(1), content=content))
    if not turns:
        raise ArtifactInputError("Artifact contains no role-ordered conversation turns")
    return turns


def _extract_yamlish_content(doc: str) -> str:
    lines = doc.splitlines()
    for index, line in enumerate(lines):
        if not re.match(r"^(body|content):", line):
            continue
        _, _, inline = line.partition(":")
        if inline.strip() and inline.strip() != "|":
            return inline.strip().strip('"')
        block: list[str] = []
        for body_line in lines[index + 1 :]:
            if body_line.startswith(("  ", "\t")):
                block.append(body_line[2:] if body_line.startswith("  ") else body_line[1:])
            elif block:
                break
        return "\n".join(block).strip()
    return ""


def _last_assistant_output(turns: Sequence[ConversationTurn], path: Path) -> str:
    for turn in reversed(turns):
        if turn.role == "assistant":
            if not turn.content.strip():
                raise ArtifactInputError(f"Assistant turn is unfilled in {path}")
            return turn.content
    raise ArtifactInputError(f"No assistant output found in {path}")


def _lookup_promptfoo_value(
    options: Mapping[str, Any],
    context: Mapping[str, Any],
    key: str,
) -> Any:
    vars_value = context.get("vars")
    if isinstance(vars_value, MappingABC) and key in vars_value:
        return vars_value[key]
    if key in context:
        return context[key]

    option_vars = options.get("vars")
    if isinstance(option_vars, MappingABC) and key in option_vars:
        return option_vars[key]
    if key in options:
        return options[key]

    raise ArtifactInputError(f"Missing Promptfoo {key} value")


def _coerce_text(value: Any, label: str) -> str:
    if not isinstance(value, str) or not value.strip():
        raise ArtifactInputError(f"Promptfoo {label} value must be a non-empty string")
    return value


def _readable_error(exc: Exception) -> Mapping[str, Any]:
    return {
        "output": f"ERROR: {exc}",
        "error": str(exc),
        "providerOutput": {
            "errorType": exc.__class__.__name__,
        },
    }


def call_api(
    prompt: str,
    options: Mapping[str, Any],
    context: Mapping[str, Any],
) -> Mapping[str, Any]:
    try:
        raw_arm = _coerce_text(
            _lookup_promptfoo_value(options, context, "arm"),
            "arm",
        )
        raw_phase = _coerce_text(
            _lookup_promptfoo_value(options, context, "phase"),
            "phase",
        )
        artifact_input = resolve_artifact_input(raw_arm, raw_phase)
        result = read_artifact_result(artifact_input)
        return build_promptfoo_response(result)
    except (ArtifactInputError, PromptfooReadableError) as exc:
        return _readable_error(exc)
