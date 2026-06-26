#!/usr/bin/env python3
"""Feature test: Claude and Codex plugin packaging stay mirrored.

The skill source of truth is `*/skills/*/SKILL.md`, but this repository ships
packaging adapters for Claude Code and Codex. The five portable skill plugins
must have both `.claude-plugin/plugin.json` and `.codex-plugin/plugin.json`, and
their release versions must match. The Claude-only `characters` output-style
package is intentionally excluded from the Codex mirror set.
"""

import json
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
PORTABLE_PLUGINS = ["developer", "domain", "general", "patterns", "research"]


def fail(reason: str) -> int:
    print(reason)
    return 1


def read_json(path: Path) -> dict[str, object]:
    return json.loads(path.read_text(encoding="utf-8"))


def main() -> int:
    for plugin in PORTABLE_PLUGINS:
        claude = REPO / plugin / ".claude-plugin" / "plugin.json"
        codex = REPO / plugin / ".codex-plugin" / "plugin.json"
        if not claude.is_file():
            return fail(f"R1 missing Claude manifest: {claude.relative_to(REPO)}")
        if not codex.is_file():
            return fail(f"R1 missing Codex mirror: {codex.relative_to(REPO)}")

        claude_data = read_json(claude)
        codex_data = read_json(codex)
        if claude_data.get("name") != codex_data.get("name"):
            return fail(f"R2 manifest names differ for {plugin}")
        if claude_data.get("version") != codex_data.get("version"):
            return fail(f"R2 manifest versions differ for {plugin}")
        if codex_data.get("skills") != "./skills/":
            return fail(f"R3 Codex mirror for {plugin} must point at ./skills/")

    if (REPO / "characters" / ".codex-plugin" / "plugin.json").exists():
        return fail("R4 characters is a Claude output-style package; do not add a Codex mirror")

    marketplace = REPO / ".agents" / "plugins" / "marketplace.json"
    if not marketplace.is_file():
        return fail("R5 missing Codex repo marketplace: .agents/plugins/marketplace.json")

    data = read_json(marketplace)
    entries = {entry.get("name"): entry for entry in data.get("plugins", [])}
    for plugin in PORTABLE_PLUGINS:
        entry = entries.get(plugin)
        if not isinstance(entry, dict):
            return fail(f"R5 Codex marketplace missing plugin entry: {plugin}")
        source = entry.get("source")
        if not isinstance(source, dict) or source.get("source") != "local":
            return fail(f"R5 Codex marketplace entry for {plugin} must be local")
        path = source.get("path")
        if not isinstance(path, str):
            return fail(f"R5 Codex marketplace entry for {plugin} has no path")
        plugin_root = (marketplace.parent / path).resolve()
        if plugin_root != (REPO / plugin).resolve():
            return fail(f"R5 Codex marketplace path for {plugin} resolves to {plugin_root}")
        if not (plugin_root / ".codex-plugin" / "plugin.json").is_file():
            return fail(f"R5 Codex marketplace path for {plugin} does not contain a mirror")

    print("PASS: plugin packaging mirrors contract holds")
    return 0


if __name__ == "__main__":
    sys.exit(main())
