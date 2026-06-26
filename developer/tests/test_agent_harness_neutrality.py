#!/usr/bin/env python3
"""Feature test: Ailly is framed as an agent-ecosystem skill package.

The acceptance behavior is a source-level contract:

- the README presents Claude Code as one marketplace adapter, while naming Codex
  and Gemini as supported harness mappings;
- `developer:ailly` owns the shared harness contract and points at per-harness
  references, including Claude, Codex, and Gemini;
- Claude-specific packaging details stay in the Claude adapter or manifest files,
  not duplicated through the coordinator and phase references;
- Gemini records subagent support and does not carry the stale single-session
  fallback assumption.

It needs no model and no pytest. It exits 0 (all rules hold) or 1 with a single
reason line on stdout.
"""

import json
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
DEV = REPO / "developer"
AILLY = DEV / "skills" / "ailly" / "SKILL.md"
AGENTS = DEV / "skills" / "ailly" / "references" / "agents"
PHASES = DEV / "skills" / "ailly" / "references" / "phases"
README = REPO / "README.md"


def fail(reason: str) -> int:
    print(reason)
    return 1


def read(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def manifest_description(path: Path) -> str:
    return json.loads(read(path))["description"]


def main() -> int:
    readme = read(README)
    readme_low = readme.lower()

    if "agent skills collection" not in readme_low:
        return fail("R1 README must frame the repo as an agent skills collection")
    for term in ("Claude Code Marketplace", "Other Agent Harnesses", "Codex", "Gemini"):
        if term not in readme:
            return fail(f"R1 README missing harness framing term: {term}")
    if ".claude-plugin/` and `.codex-plugin/` manifests are packaging metadata only" not in readme:
        return fail(
            "R1 README must say .claude-plugin and .codex-plugin manifests are packaging metadata only"
        )

    ailly = read(AILLY)
    ailly_low = ailly.lower()
    if "## Agent Harness Compatibility" not in ailly:
        return fail("R2 coordinator must have an Agent Harness Compatibility section")
    for adapter in ("claude.md", "codex.md", "copilot.md", "gemini.md"):
        if f"references/agents/{adapter}" not in ailly:
            return fail(f"R2 coordinator must point at references/agents/{adapter}")
        if not (AGENTS / adapter).is_file():
            return fail(f"R2 missing harness adapter file: {adapter}")
    forbidden_ailly = [
        "non-claude",
        "claude's tool names",
        "skills use claude code tool names",
        "phase subagent isolation",
    ]
    for phrase in forbidden_ailly:
        if phrase in ailly_low:
            return fail(f"R2 coordinator still carries Claude/subagent-only wording: {phrase}")

    claude = read(AGENTS / "claude.md").lower()
    if ".claude-plugin" not in claude or "not a separate behavioral source of truth" not in claude:
        return fail(
            "R3 Claude adapter must centralize .claude-plugin as packaging metadata"
        )

    for adapter in ("codex.md", "copilot.md", "gemini.md"):
        text = read(AGENTS / adapter).lower()
        if "skills use claude code tool names" in text:
            return fail(f"R3 {adapter} duplicates the old Claude-first preamble")
        if "claude's tool names" in text:
            return fail(f"R3 {adapter} should map from Ailly vocabulary, not Claude's")

    gemini = read(AGENTS / "gemini.md").lower()
    if "no equivalent to subagent dispatch" in gemini or "single-session fallback" in gemini:
        return fail("R4 Gemini adapter still carries the stale no-subagent fallback")
    if "read only the selected" not in gemini:
        return fail("R4 Gemini subagent dispatch must preserve one-reference phase isolation")

    for phase in ("research", "design", "plan", "red-green-refactor", "cleanup"):
        text = read(PHASES / f"{phase}.md").lower()
        if "isolated phase subagent" in text:
            return fail(f"R5 {phase} phase header still assumes subagents only")
        if "skill tool" in text or "claude skill" in text:
            return fail(f"R5 {phase} phase still hardcodes a Claude-specific skill loader")

    for path in (
        REPO / "general" / ".claude-plugin" / "plugin.json",
        REPO / "research" / ".claude-plugin" / "plugin.json",
        REPO / "domain" / ".claude-plugin" / "plugin.json",
    ):
        desc = manifest_description(path).lower()
        if "for claude code" in desc:
            return fail(
                f"R6 manifest description repeats Claude Code as identity: {path.relative_to(REPO)}"
            )

    print("PASS: agent harness neutrality contract holds")
    return 0


if __name__ == "__main__":
    sys.exit(main())
