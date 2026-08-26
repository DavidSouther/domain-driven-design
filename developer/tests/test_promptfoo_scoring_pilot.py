#!/usr/bin/env python3
"""Feature test: Promptfoo scoring pilot for developer invocation phases.

Acceptance behavior: the repo has one Promptfoo pilot config that represents the
developer `invocation-phases` eval as a five-case baseline-vs-invocation suite.
It also preserves role-ordered multi-turn conversation evidence. The test stays
source-level and deterministic: no live model, no Promptfoo install, no pytest
dependency. It exits 0 when the contract holds or 1 with one clear reason.
"""

from __future__ import annotations

import re
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
CONFIG = (
    REPO
    / "developer"
    / "e2e"
    / "promptfoo"
    / "invocation-phases"
    / "promptfooconfig.yaml"
)
SOURCE_EVAL = REPO / "developer" / "e2e" / "evals" / "invocation-phases.yaml"
SOURCE_ASSEMBLY = REPO / "developer" / "e2e" / "assemblies" / "invocation-phases.yaml"
BASELINE_EVAL = REPO / "developer" / "e2e" / "evals" / "baseline-phases.yaml"
BASELINE_ASSEMBLY = REPO / "developer" / "e2e" / "assemblies" / "baseline-phases.yaml"
PHASES = ["research", "design", "plan", "red-green-refactor", "cleanup"]
PROMPTFOO_SCHEMA_COMMENT = (
    "# yaml-language-server: $schema=https://promptfoo.dev/config-schema.json"
)
TOKEN_BUDGETS = {
    "research": "7000",
    "design": "7000",
    "plan": "6000",
    "red-green-refactor": "7000",
    "cleanup": "5000",
}
TOP_LEVEL_ORDER = [
    "description",
    "env",
    "prompts",
    "providers",
    "defaultTest",
    "scenarios",
    "tests",
]
REQUIRED_TRANSCRIPT_TERMS = ["conversation", "messages", "role", "turns"]
MIN_ROLE_COUNTS = {"system": 1, "user": 2, "assistant": 2}


def fail(reason: str) -> int:
    print(reason)
    return 1


def rel(path: Path) -> str:
    return str(path.relative_to(REPO))


def read(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def top_level_keys(text: str) -> list[str]:
    keys: list[str] = []
    for line in text.splitlines():
        m = re.match(r"^([A-Za-z][A-Za-z0-9_-]*):(?:\s|$)", line)
        if m:
            keys.append(m.group(1))
    return keys


def ordered_subset(keys: list[str], expected: list[str]) -> bool:
    positions = []
    for key in expected:
        try:
            positions.append(keys.index(key))
        except ValueError:
            return False
    return positions == sorted(positions)


def file_refs(text: str) -> list[Path]:
    refs: list[Path] = []
    base = CONFIG.parent
    for raw in re.findall(r"file://([^\s,'\"]+)", text):
        if "{{" in raw:
            continue
        refs.append((base / raw).resolve())
    return refs


def phase_mentions(text: str, phase: str) -> int:
    return len(
        re.findall(
            rf"(?<![A-Za-z0-9_-]){re.escape(phase)}(?![A-Za-z0-9_-])",
            text,
        )
    )


def declared_phases(text: str) -> list[str]:
    phases: list[str] = []
    yaml_phase_re = (
        r"(?m)^\s*(?:-\s*)?phase:\s*['\"]?([A-Za-z][A-Za-z0-9_-]*)['\"]?\s*$"
    )
    for match in re.finditer(yaml_phase_re, text):
        phases.append(match.group(1))
    json_phase_re = (
        r"['\"]phase['\"]\s*:\s*['\"]([A-Za-z][A-Za-z0-9_-]*)['\"]"
    )
    for match in re.finditer(json_phase_re, text):
        phases.append(match.group(1))
    return phases


def token_budget_visible(text: str, phase: str, budget: str) -> bool:
    phase_at = text.find(phase)
    budget_at = text.find(budget, phase_at if phase_at >= 0 else 0)
    return phase_at >= 0 and budget_at >= 0


def combined_config_and_imports(config_text: str) -> str:
    parts = [config_text]
    for ref in file_refs(config_text):
        # Prompts/tests/providers/assertion files are part of the pilot contract
        # once the config exists. Missing imports are reported before structural
        # checks so later failures stay actionable.
        if not ref.is_file():
            raise FileNotFoundError(rel(ref))
        if ref.suffix in {".yaml", ".yml", ".md", ".txt", ".py", ".js"}:
            parts.append(read(ref))
    return "\n".join(parts)


def main() -> int:
    if not CONFIG.is_file():
        return fail(
            f"P1 Promptfoo pilot config required: {rel(CONFIG)} does not exist"
        )

    config = read(CONFIG)
    keys = top_level_keys(config)

    if not config.lstrip().startswith(PROMPTFOO_SCHEMA_COMMENT):
        return fail(
            "P2 schema comment: config must start with a Promptfoo YAML schema comment"
        )
    if not ordered_subset(keys, TOP_LEVEL_ORDER):
        return fail(
            "P2 field order: config must order top-level fields as "
            + ", ".join(TOP_LEVEL_ORDER)
        )
    description = re.search(r"(?m)^description:\s*(.+)$", config)
    if not description or "invocation-phases" not in description.group(1):
        return fail(
            "P2 description: config description must name the invocation-phases pilot"
        )

    for path in (SOURCE_EVAL, SOURCE_ASSEMBLY, BASELINE_EVAL, BASELINE_ASSEMBLY):
        if rel(path) not in config:
            return fail(
                "P3 source traceability: config must reference "
                f"{rel(path)}"
            )

    if "{{env." not in config:
        return fail(
            "P4 env placeholders: config must use {{env.VAR}} placeholders for provider secrets"
        )
    artifact_envs = (
        "AILLY_PROMPTFOO_BASELINE_RUN_DIR",
        "AILLY_PROMPTFOO_INVOCATION_RUN_DIR",
    )
    for name in artifact_envs:
        if name not in config:
            return fail(
                f"P4 artifact inputs: config must require {{{{env.{name}}}}}"
            )
    secret_re = r"(?i)(api[_-]?key|token):\s*['\"]?(sk-|ghp_|github_pat_|xoxb-)"
    if re.search(secret_re, config):
        return fail("P4 no secrets: config appears to contain a committed secret value")
    if "file://" not in config:
        return fail("P4 file imports: config must use file:// prompts/tests imports")
    if "file://provider.py" not in config and "file://./provider.py" not in config:
        return fail(
            "P4 local provider: config must use a local provider.py adapter to score existing artifacts"
        )

    try:
        combined = combined_config_and_imports(config)
    except FileNotFoundError as exc:
        return fail(f"P4 file imports: referenced file does not exist: {exc}")

    for phase in PHASES:
        if phase_mentions(combined, phase) < 2:
            return fail(
                f"P5 phase matrix: Promptfoo pilot must include phase {phase!r}"
            )
        checker = f"evals/scripts/check_{phase.replace('-', '_')}.py"
        if checker not in combined:
            return fail(
                f"P6 python checker: phase {phase!r} must reuse {checker}"
            )
        if not token_budget_visible(combined, phase, TOKEN_BUDGETS[phase]):
            return fail(
                f"P6 token budget: phase {phase!r} must preserve "
                f"output budget {TOKEN_BUDGETS[phase]}"
            )
    declared = declared_phases(combined)
    if sorted(declared) != sorted(PHASES):
        return fail(
            "P5 phase matrix: Promptfoo pilot must declare exactly the five phases "
            f"{PHASES}, found {declared}"
        )

    if (
        len(re.findall(r"(?m)^\s*-\s*type:\s*python\s*$", combined))
        < len(PHASES)
    ):
        return fail(
            "P6 Promptfoo assertions: each phase must include a type: python assertion"
        )
    if (
        len(re.findall(r"(?m)^\s*-\s*type:\s*llm-rubric\s*$", combined))
        < len(PHASES)
    ):
        return fail(
            "P6 Promptfoo assertions: each phase must include a type: llm-rubric assertion"
        )
    if "type: script" in combined or "type: judge" in combined:
        return fail(
            "P6 Promptfoo assertions: pilot must use Promptfoo-native python and llm-rubric, not Ailly script/judge types"
        )

    for token in ("baseline", "invocation", "providerOutput", "response.output"):
        if token not in combined:
            return fail(
                f"P7 comparison evidence: config/tests must preserve {token!r}"
            )
    gate = combined.replace(" ", "")
    if "improved>0" not in gate or "regressed==0" not in gate:
        return fail(
            "P7 release gate: config/tests must document improved > 0 and regressed == 0"
        )
    for token in ("results.stats", "score", "gradingResult.reason", "error"):
        if token not in combined:
            return fail(
                f"P8 result inspection: config/tests must call out {token}"
            )
    for token in REQUIRED_TRANSCRIPT_TERMS:
        if token not in combined:
            return fail(
                f"P8 multi-turn transcript: config/tests must preserve {token!r}"
            )
    for role, minimum in MIN_ROLE_COUNTS.items():
        role_re = (
            rf"(?m)(role:\s*['\"]?{role}['\"]?"
            rf"|['\"]role['\"]\s*:\s*['\"]{role}['\"])"
        )
        if len(re.findall(role_re, combined)) < minimum:
            return fail(
                "P8 multi-turn transcript: config/tests must include at least "
                f"{minimum} {role!r} role turn(s)"
            )

    validate_cmd = (
        "npx promptfoo@latest validate config -c "
        "developer/e2e/promptfoo/invocation-phases/promptfooconfig.yaml"
    )
    eval_cmd = (
        "npx promptfoo@latest eval -c "
        "developer/e2e/promptfoo/invocation-phases/promptfooconfig.yaml "
        "-o /tmp/eval-results.json --no-cache --no-share"
    )
    if validate_cmd not in combined:
        return fail("P9 manual validation: config must document the validate command")
    if eval_cmd not in combined:
        return fail("P9 manual eval: config must document the eval command")
    for name in artifact_envs:
        if name not in combined:
            return fail(f"P9 manual eval: config must document `{name}`")

    print("PASS: Promptfoo invocation-phases pilot contract holds")
    return 0


if __name__ == "__main__":
    sys.exit(main())
