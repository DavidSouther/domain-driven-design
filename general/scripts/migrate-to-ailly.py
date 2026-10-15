#!/usr/bin/env python3
"""Repoint a legacy Ailly install at davidsouther/ailly.

Ailly moved from davidsouther/domain-driven-design to davidsouther/ailly.
This script finds Claude Code, Codex, and pi installs that still come from the
legacy repository and plans the commands that repoint each one.

Usage:
    python3 migrate-to-ailly.py           # dry run: print the plan, change nothing
    python3 migrate-to-ailly.py --apply   # run the plan in order
    python3 migrate-to-ailly.py --notice  # print the SessionStart hook JSON

Python 3 standard library only. Every harness read happens before the first
command runs, and the whole plan is held in memory: removing the Claude Code
marketplace deletes the cached plugin directory that holds this file.
"""

import argparse
import json
import re
import shlex
import shutil
import subprocess
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Optional

SUCCESSOR = "davidsouther/ailly"
LEGACY_NAMES = ("davidsouther/domain-driven-design", "davidsouther/ddd_skill")
MARKETPLACE = "ailly"
PI_SUCCESSOR = f"git:github.com/{SUCCESSOR}"
READ_TIMEOUT = 60

HEADER = (
    f"Ailly moved from {LEGACY_NAMES[0]} to {SUCCESSOR}. On each repointed harness,"
    f" every @{MARKETPLACE} plugin, including patterns, domain, research, and"
    f" characters, moves to {SUCCESSOR} and receives that repository's versions."
)


def _repo_pattern(slugs: tuple) -> "re.Pattern[str]":
    names = "|".join(re.escape(slug) for slug in slugs)
    return re.compile(rf"(?:^|[/:])(?:{names})(?:\.git)?(?:[/@#?]|$)", re.IGNORECASE)


_LEGACY = _repo_pattern(LEGACY_NAMES)
_SUCCESSOR = _repo_pattern((SUCCESSOR,))


@dataclass(frozen=True)
class Step:
    """One planned command, run exactly as rendered."""

    argv: list[str]
    cwd: Optional[Path]
    mutating: bool = True

    def render(self) -> str:
        """Return the shell form, prefixed with "cd <cwd> && " when cwd is set."""
        command = shlex.join(self.argv)
        if self.cwd is None:
            return command
        return f"cd {shlex.quote(str(self.cwd))} && {command}"


def is_legacy(source: str) -> bool:
    """Return True when source names a legacy repository (case-insensitive, any URL form)."""
    return bool(_LEGACY.search(source.strip()))


def is_successor(source: str) -> bool:
    """Return True when source names davidsouther/ailly (case-insensitive, any URL form)."""
    return bool(_SUCCESSOR.search(source.strip()))


def is_local(source: str) -> bool:
    """Return True when source is a filesystem path rather than a repository."""
    return source.strip().startswith(("/", ".", "~", "file:"))


def run_read(argv: list[str]) -> str:
    """Run a read-only harness command; return "" when it is absent or fails."""
    try:
        result = subprocess.run(argv, capture_output=True, text=True, timeout=READ_TIMEOUT)
    except (OSError, subprocess.TimeoutExpired):
        return ""
    return result.stdout if result.returncode == 0 else ""


def _classify(harness: str, source: str, local: bool) -> tuple[str, Optional[str]]:
    """Return ("legacy" | "skip", note) for one harness's Ailly source."""
    if local or is_local(source):
        return "skip", f"{harness}: Ailly comes from the local path {source}; left untouched."
    if is_legacy(source):
        return "legacy", None
    if is_successor(source):
        return "skip", f"{harness}: Ailly already comes from {SUCCESSOR}; nothing to change."
    return "skip", f"{harness}: Ailly comes from the unrecognized source {source}; left untouched."


def _read_json(harness: str, argv: list[str]) -> tuple[object, Optional[str]]:
    """Return (parsed JSON, None), or (None, note) when the output is unreadable."""
    try:
        return json.loads(run_read(argv)), None
    except ValueError:
        return None, f"{harness}: could not read `{shlex.join(argv)}`; skipped."


def _absent(harness: str, binary: str) -> Optional[str]:
    if shutil.which(binary):
        return None
    return f"{harness}: `{binary}` is not on PATH; skipped."


def plan_claude() -> tuple[list[Step], list[str]]:
    """Return (steps, notes) for Claude Code."""
    harness = "Claude Code"
    absent = _absent(harness, "claude")
    if absent:
        return [], [absent]
    marketplaces, note = _read_json(harness, ["claude", "plugin", "marketplace", "list", "--json"])
    if note:
        return [], [note]
    plugins, note = _read_json(harness, ["claude", "plugin", "list", "--json"])
    if note:
        return [], [note]

    if not isinstance(marketplaces, list) or not isinstance(plugins, list):
        return [], [f"{harness}: unexpected `claude plugin` JSON shape; skipped."]
    entry = next((m for m in marketplaces if isinstance(m, dict) and m.get("name") == MARKETPLACE), None)
    if entry is None:
        return [], [f"{harness}: no `{MARKETPLACE}` marketplace is configured; nothing to change."]
    source = str(entry.get("repo") or entry.get("url") or entry.get("path") or entry.get("source") or "")
    local = "path" in entry or entry.get("source") in ("directory", "file")
    kind, note = _classify(harness, source, local)
    if kind != "legacy":
        return [], [note]

    steps = [
        Step(["claude", "plugin", "marketplace", "remove", MARKETPLACE], None),
        Step(["claude", "plugin", "marketplace", "add", SUCCESSOR], None),
    ]
    notes = []
    for plugin in plugins:
        if not isinstance(plugin, dict):
            continue
        plugin_id = str(plugin.get("id", ""))
        if not plugin_id.endswith(f"@{MARKETPLACE}"):
            continue
        scope = str(plugin.get("scope", "user"))
        cwd = None
        if scope in ("project", "local"):
            cwd = Path(str(plugin.get("projectPath", "")))
            if not plugin.get("projectPath") or not cwd.is_dir():
                notes.append(
                    f"{harness}: {plugin_id} ({scope} scope) belongs to the missing project"
                    f" {plugin.get('projectPath', '')}; not reinstalled."
                )
                continue
        elif scope != "user":
            notes.append(f"{harness}: {plugin_id} has {scope} scope; not reinstalled.")
            continue
        steps.append(Step(["claude", "plugin", "install", plugin_id, "--scope", scope], cwd))
        if plugin.get("enabled") is False:
            steps.append(Step(["claude", "plugin", "disable", plugin_id, "--scope", scope], cwd))
    notes.insert(0, f"{harness}: the `{MARKETPLACE}` marketplace comes from {source}; repointing it.")
    return steps, notes


def plan_codex() -> tuple[list[Step], list[str]]:
    """Return (steps, notes) for Codex."""
    harness = "Codex"
    absent = _absent(harness, "codex")
    if absent:
        return [], [absent]
    listing, note = _read_json(harness, ["codex", "plugin", "list", "--json"])
    if note:
        return [], [note]
    if not isinstance(listing, dict):
        return [], [f"{harness}: unexpected `codex plugin list` JSON shape; skipped."]

    entries = [
        e
        for key in ("installed", "available")
        for e in listing.get(key, [])
        if isinstance(e, dict) and e.get("marketplaceName") == MARKETPLACE
    ]
    if not entries:
        return [], [f"{harness}: no `{MARKETPLACE}` marketplace is configured; nothing to change."]
    marketplace = entries[0].get("marketplaceSource") or {}
    source = str(marketplace.get("source", ""))
    kind, note = _classify(harness, source, marketplace.get("sourceType") == "local")
    if kind != "legacy":
        return [], [note]

    installed = [
        str(e.get("pluginId") or f"{e.get('name')}@{MARKETPLACE}")
        for e in listing.get("installed", [])
        if isinstance(e, dict) and e.get("marketplaceName") == MARKETPLACE and e.get("installed", True)
    ]
    steps = [Step(["codex", "plugin", "remove", plugin_id], None) for plugin_id in installed]
    steps += [
        Step(["codex", "plugin", "marketplace", "remove", MARKETPLACE], None),
        Step(["codex", "plugin", "marketplace", "add", SUCCESSOR], None),
    ]
    steps += [Step(["codex", "plugin", "add", plugin_id], None) for plugin_id in installed]
    return steps, [f"{harness}: the `{MARKETPLACE}` marketplace comes from {source}; repointing it."]


def _pi_packages(listing: str) -> dict[str, list[str]]:
    """Parse `pi list` into {"user": [...], "project": [...]} source lists."""
    sections = {"User packages:": "user", "Project packages:": "project"}
    packages: dict[str, list[str]] = {"user": [], "project": []}
    current = None
    for line in listing.splitlines():
        if line.strip() in sections and not line.startswith(" "):
            current = sections[line.strip()]
        elif not line.startswith(" "):
            current = None
        elif current and line.startswith("  ") and not line.startswith("   "):
            packages[current].append(line.strip().removesuffix(" (filtered)"))
    return packages


def plan_pi() -> tuple[list[Step], list[str]]:
    """Return (steps, notes) for pi."""
    harness = "pi"
    absent = _absent(harness, "pi")
    if absent:
        return [], [absent]
    listing = run_read(["pi", "list"])
    if not listing.strip():
        return [], [f"{harness}: could not read `pi list`; skipped."]
    packages = _pi_packages(listing)

    steps, notes = [], []
    for scope, sources in packages.items():
        flag = ["-l"] if scope == "project" else []
        has_successor = any(is_successor(s) and not is_local(s) for s in sources)
        for source in sources:
            if is_local(source):
                last = source.rstrip("/").rsplit("/", 1)[-1].lower()
                if is_legacy(source) or is_successor(source) or last in ("domain-driven-design", "ailly"):
                    notes.append(f"{harness}: the {scope} package {source} is a local path; left untouched.")
            elif is_legacy(source):
                steps.append(Step(["pi", "remove", source] + flag, None))
                if not has_successor:
                    steps.append(Step(["pi", "install", PI_SUCCESSOR] + flag, None))
                    has_successor = True
                notes.append(f"{harness}: the {scope} package {source} is legacy; repointing it.")
            elif is_successor(source):
                notes.append(f"{harness}: the {scope} package already comes from {SUCCESSOR}; nothing to change.")
    if not steps and not notes:
        notes.append(f"{harness}: no Ailly package is installed; nothing to change.")
    return steps, notes


def plan_all() -> tuple[list[Step], list[str]]:
    """Read every harness and return the combined (steps, notes)."""
    steps: list[Step] = []
    notes: list[str] = []
    for plan in (plan_claude, plan_codex, plan_pi):
        harness_steps, harness_notes = plan()
        steps += harness_steps
        notes += harness_notes
    return steps, notes


def render_plan(steps: list[Step], notes: list[str]) -> str:
    """Return the header, the notes, and one rendered command per line."""
    lines = [HEADER, ""] + notes + [""]
    if not steps:
        lines.append("No commands planned: nothing needs changing.")
    else:
        lines.append("This dry run changed nothing. With --apply, this script runs these commands in order:")
        lines += [f"  {step.render()}" for step in steps]
    return "\n".join(lines)


def apply_plan(steps: list[Step]) -> int:
    """Execute each Step in order; stop at first failure, return non-zero exit code."""
    ...


def notice_json(script_path: Path) -> str:
    """Return hook JSON, json.dumps-escaped."""
    ...


def main(argv: Optional[list[str]] = None) -> int:
    """Parse flags: --apply, --notice."""
    parser = argparse.ArgumentParser(
        description="Migrate Ailly plugins from legacy to successor repository."
    )
    group = parser.add_mutually_exclusive_group()
    group.add_argument("--apply", action="store_true", help="Apply the migration")
    group.add_argument(
        "--notice", action="store_true", help="Output JSON for SessionStart hook"
    )
    args = parser.parse_args(argv)

    if args.notice:
        print(notice_json(Path(__file__).resolve()))
        return 0

    steps, notes = plan_all()

    if args.apply:
        return apply_plan(steps)

    print(render_plan(steps, notes))
    return 0


if __name__ == "__main__":
    sys.exit(main())
