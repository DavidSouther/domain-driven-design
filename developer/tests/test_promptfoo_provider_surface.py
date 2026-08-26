#!/usr/bin/env python3
"""Step 0 contract: Promptfoo provider surface imports and parses inputs."""

from __future__ import annotations

import importlib.util
import json
import os
import re
import sys
import tempfile
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
PILOT = REPO / "developer" / "e2e" / "promptfoo" / "invocation-phases"
SERVICE = PILOT / "service.py"
PROVIDER = PILOT / "provider.py"
ASSERTIONS = PILOT / "assertions.py"
_MISSING = object()


def fail(reason: str) -> int:
    print(reason)
    return 1


def load_module(name: str, path: Path):
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"Unable to load {path}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


def without_env(name: str):
    previous = os.environ.get(name, _MISSING)
    if previous is _MISSING:
        return _MISSING
    del os.environ[name]
    return previous


def restore_env(name: str, value) -> None:
    if value is _MISSING:
        os.environ.pop(name, None)
        return
    if value is None:
        os.environ.pop(name, None)
    else:
        os.environ[name] = value


def main() -> int:
    if not SERVICE.is_file():
        return fail(f"surface: {SERVICE.relative_to(REPO)} does not exist")
    if not PROVIDER.is_file():
        return fail(f"surface: {PROVIDER.relative_to(REPO)} does not exist")
    if not ASSERTIONS.is_file():
        return fail(f"surface: {ASSERTIONS.relative_to(REPO)} does not exist")

    service = load_module("promptfoo_invocation_service_test", SERVICE)

    env_name = "AILLY_PROMPTFOO_BASELINE_RUN_DIR"
    previous = os.environ.get(env_name)
    os.environ[env_name] = "/tmp/ailly-promptfoo-baseline-does-not-need-to-exist"
    try:
        artifact_input = service.resolve_artifact_input("baseline", "research")
    except Exception as exc:
        return fail(f"happy path: resolving artifact input failed: {exc}")
    finally:
        restore_env(env_name, previous)

    if artifact_input.arm is not service.Arm.BASELINE:
        return fail("happy path: arm did not parse to Arm.BASELINE")
    if artifact_input.phase is not service.Phase.RESEARCH:
        return fail("happy path: phase did not parse to Phase.RESEARCH")
    if artifact_input.run_dir != Path(
        "/tmp/ailly-promptfoo-baseline-does-not-need-to-exist"
    ):
        return fail("happy path: run_dir was not carried as a Path value")

    try:
        service.parse_phase("unknown")
    except service.ArtifactInputError:
        pass
    else:
        return fail("edge: unknown phase string must be rejected at the boundary")

    try:
        service.parse_arm("control")
    except service.ArtifactInputError:
        pass
    else:
        return fail("edge: unknown arm string must be rejected at the boundary")

    previous = without_env(env_name)
    try:
        service.resolve_artifact_input("baseline", "research")
    except service.ArtifactInputError:
        pass
    else:
        return fail("edge: missing baseline run-dir env must raise ArtifactInputError")
    finally:
        restore_env(env_name, previous)

    sys.modules.pop("service", None)
    provider = load_module("promptfoo_invocation_provider_test", PROVIDER)
    previous = without_env(env_name)
    try:
        response = provider.call_api(
            "",
            {},
            {"vars": {"arm": "baseline", "phase": "research"}},
        )
    finally:
        restore_env(env_name, previous)

    if "output" not in response or "error" not in response:
        return fail("adapter: missing run-dir must become a Promptfoo-readable mapping")
    if "AILLY_PROMPTFOO_BASELINE_RUN_DIR" not in response["output"]:
        return fail("adapter: error output must name the missing artifact env var")

    with tempfile.TemporaryDirectory() as tmp:
        run_dir = Path(tmp)
        artifact = run_dir / "research.json"
        artifact.write_text(
            json.dumps(
                {
                    "conversation": [
                        {"role": "system", "content": "Use the developer profile."},
                        {"role": "user", "content": "Research promptfoo."},
                        {"role": "assistant", "content": "Research draft."},
                    ],
                    "providerOutput": {"raw": "kept"},
                }
            ),
            encoding="utf-8",
        )
        result = service.read_artifact_result(
            service.ArtifactInput(
                arm=service.Arm.BASELINE,
                run_dir=run_dir,
                phase=service.Phase.RESEARCH,
            )
        )

    if result.output != "Research draft.":
        return fail("artifact: final assistant output was not preserved")
    if result.provider_output.get("raw") != "kept":
        return fail("artifact: providerOutput metadata was not preserved")
    if [turn.role for turn in result.conversation] != ["system", "user", "assistant"]:
        return fail("artifact: conversation turn order was not preserved")

    better = service.ProviderResult(
        phase_name=service.Phase.RESEARCH,
        arm_name=service.Arm.INVOCATION,
        output="Improved research draft.",
        provider_output={},
        conversation=(),
    )
    comparison = service.compare_phase_results(result, better)
    if comparison.improved <= 0 or comparison.regressed != 0:
        return fail("comparison: improved > 0 and regressed == 0 was not represented")

    assertions = load_module("promptfoo_invocation_assertions_test", ASSERTIONS)
    research_output = (
        "*Draft 2026-07-02*\n\n"
        "## Topic and Intent\n\n"
        "## Search/Expand\n\n"
        "## Falsification/Refine\n\n"
        "## Scope\n\n"
        "## Resolved Decisions\n\n"
        "## Sources\n"
    )
    assertion_result = assertions.check_phase_output(
        research_output,
        {"vars": {"expected_checker": "evals/scripts/check_research.py"}},
    )
    if assertion_result.get("pass") is not True:
        return fail(
            "assertion adapter: expected checker did not pass: "
            + str(assertion_result.get("reason"))
        )

    imported_text = SERVICE.read_text(encoding="utf-8") + "\n" + PROVIDER.read_text(
        encoding="utf-8"
    ) + "\n" + ASSERTIONS.read_text(encoding="utf-8")
    phase_value = r"(research|design|plan|red-green-refactor|cleanup)"
    if re.search(
        rf"(?m)^\s*(?:-\s*)?phase:\s*['\"]?{phase_value}['\"]?\s*$",
        imported_text,
    ):
        return fail("edge: provider imports must not contain literal YAML phase fields")
    if re.search(rf"['\"]phase['\"]\s*:\s*['\"]{phase_value}['\"]", imported_text):
        return fail("edge: provider imports must not contain literal JSON phase fields")

    print("PASS: Promptfoo provider Step 0 surface holds")
    return 0


if __name__ == "__main__":
    sys.exit(main())
