#!/usr/bin/env python3
"""release.py — detect changed plugins, bump CalVer versions, update manifests.

Prints the new version string to stdout when changes are found; prints nothing
to stdout (and a notice to stderr) when there is nothing to release.  Git
commit, tag, and push are left to the caller (the CI workflow).

Usage:
    python3 .github/scripts/release.py [--repo PATH] [--date YYYY.MM]

Exit codes:
    0  success OR no changes detected (early-exit path)
    1  unexpected error or unknown flag
"""

import argparse
import json
import subprocess
import sys
from datetime import date as _date
from pathlib import Path
from typing import Optional

PLUGINS = ["developer", "general", "patterns", "domain", "research", "characters"]
MANIFEST_DIRS = [".claude-plugin", ".codex-plugin"]


def _run(args: list[str], *, cwd: Path, capture: bool = True) -> str:
    result = subprocess.run(
        args, cwd=cwd, capture_output=capture, text=True, check=True
    )
    return result.stdout.strip() if capture else ""


def find_last_tag(repo: Path) -> str:
    try:
        return _run(
            ["git", "describe", "--tags", "--match", "release/*", "--abbrev=0"],
            cwd=repo,
        )
    except subprocess.CalledProcessError:
        return _run(["git", "rev-list", "--max-parents=0", "HEAD"], cwd=repo)


def find_changed_plugins(repo: Path, since: str) -> list[str]:
    changed = []
    for plugin in PLUGINS:
        log = _run(["git", "log", f"{since}..HEAD", "--", f"{plugin}/"], cwd=repo)
        if log:
            changed.append(plugin)
    return changed


def compute_version(repo: Path, ym: str) -> str:
    raw = _run(["git", "tag", "-l", f"release/{ym}.*"], cwd=repo)
    micro = len([t for t in raw.splitlines() if t.strip()])
    return f"{ym}.{micro}"


def update_plugin_json(path: Path, version: str) -> None:
    data = json.loads(path.read_text())
    data["version"] = version
    path.write_text(json.dumps(data, indent=2) + "\n")


def update_plugin_manifests(repo: Path, plugin: str, version: str) -> list[Path]:
    updated = []
    for manifest_dir in MANIFEST_DIRS:
        path = repo / plugin / manifest_dir / "plugin.json"
        if path.exists():
            update_plugin_json(path, version)
            updated.append(path)

    if not updated:
        sys.exit(f"plugin {plugin!r} has no known plugin manifest")

    return updated


def update_marketplace_json(path: Path, plugin: str, version: str) -> None:
    data = json.loads(path.read_text())
    for entry in data.get("plugins", []):
        if entry.get("name") == plugin:
            entry["version"] = version
            break
    else:
        sys.exit(f"marketplace.json has no plugin entry named {plugin!r}")
    path.write_text(json.dumps(data, indent=2) + "\n")


def main(argv: Optional[list[str]] = None) -> int:
    parser = argparse.ArgumentParser(
        description="Release plugins with CalVer versioning.",
    )
    _ = parser.add_argument(
        "--repo", default=".", help="Path to repository root (default: .)"
    )
    _ = parser.add_argument(
        "--skip-push", action="store_true", help="Skip git push steps"
    )
    _ = parser.add_argument(
        "--skip-gh", action="store_true", help="Skip GitHub Release creation"
    )
    _ = parser.add_argument(
        "--date", help="Override release date as YYYY.MM (default: today)"
    )
    args = parser.parse_args(argv)

    repo = Path(args.repo).resolve()
    marketplace = repo / ".claude-plugin" / "marketplace.json"
    ym = args.date or _date.today().strftime("%Y.%m")

    last_tag = find_last_tag(repo)
    changed = find_changed_plugins(repo, last_tag)

    if not changed:
        print("No changes since last release, skipping.", file=sys.stderr)
        return 0

    version = compute_version(repo, ym)

    for plugin in changed:
        update_plugin_manifests(repo, plugin, version)
        update_marketplace_json(marketplace, plugin, version)

    print(version)

    return 0


if __name__ == "__main__":
    sys.exit(main())
