#!/usr/bin/env python3
"""release.py — detect changed plugins, bump CalVer versions, update manifests.

Prints the new version string to stdout when changes are found; prints nothing
to stdout (and a notice to stderr) when there is nothing to release.  Git
commit, tag, and push are left to the caller.

Releases are pinned to the 2026.09 line (see check_version_line.py): the
version is 2026.09.N with N at least 3, because 2026.09.2 and everything at or
above 2026.10.0 belong to the successor repository (davidsouther/ailly).  By
default N is one more than the highest existing release/2026.09.* tag micro.

Usage:
    python3 .github/scripts/release.py [--repo PATH] [--version 2026.09.N]

Exit codes:
    0  success OR no changes detected (early-exit path)
    1  unexpected error or unknown flag
"""

import argparse
import json
import subprocess
import sys
from pathlib import Path
from typing import Optional

from check_version_line import (
    FIRST_RELEASE,
    LINE,
    RESERVED,
    TAG_PREFIX,
    parse_version,
    violation,
)

PLUGINS = ["developer", "general", "patterns", "domain", "research", "characters"]
MANIFEST_DIRS = [".claude-plugin", ".codex-plugin"]


def _calver(value: str) -> str:
    """Validate and return a CalVer version string YYYY.MM.MICRO."""
    parts = value.split(".")
    if len(parts) != 3:
        raise argparse.ArgumentTypeError(
            f"version must be YYYY.MM.MICRO (got {value!r})"
        )
    try:
        year, month, micro = (int(p) for p in parts)
        if not (2000 <= year <= 9999) or not (1 <= month <= 12):
            raise ValueError("invalid year or month")
    except ValueError:
        raise argparse.ArgumentTypeError(
            f"version must be YYYY.MM.MICRO with numeric parts (got {value!r})"
        )
    return value


def _release_version(value: str) -> str:
    """Validate a CalVer string and pin it to the allowed release line."""
    _calver(value)
    parsed = parse_version(value)
    reason = violation(value)
    if reason:
        raise argparse.ArgumentTypeError(reason)
    if parsed[:2] != parse_version(LINE) or parsed < parse_version(FIRST_RELEASE):
        raise argparse.ArgumentTypeError(
            f"version {value} must be {LINE}.N with N >= {FIRST_RELEASE.split('.')[-1]}"
            f" (first release is {FIRST_RELEASE})"
        )
    return value


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


def compute_version(repo: Path) -> str:
    """Return the next release on the pinned line, never below FIRST_RELEASE."""
    raw = _run(["git", "tag", "-l", f"{TAG_PREFIX}{LINE}.*"], cwd=repo)
    line = parse_version(LINE)
    first = parse_version(FIRST_RELEASE)
    reserved = {parse_version(r) for r in RESERVED}
    micros = []
    for tag in raw.split():
        try:
            parsed = parse_version(tag.removeprefix(TAG_PREFIX))
        except ValueError:
            continue
        if len(parsed) == 3 and parsed[:2] == line:
            micros.append(parsed[2])
    micro = max([first[2] - 1, *micros]) + 1
    while (*line, micro) in reserved:
        micro += 1
    return f"{LINE}.{micro}"


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
        "--version",
        type=_release_version,
        help=f"Override version; must be {LINE}.N, N >= {FIRST_RELEASE.split('.')[-1]}"
        " (default: next micro after the highest existing release tag)",
    )
    args = parser.parse_args(argv)

    repo = Path(args.repo).resolve()
    marketplace = repo / ".claude-plugin" / "marketplace.json"

    last_tag = find_last_tag(repo)
    changed = find_changed_plugins(repo, last_tag)

    if not changed:
        print("No changes since last release, skipping.", file=sys.stderr)
        return 0

    version = args.version or compute_version(repo)

    for plugin in changed:
        update_plugin_manifests(repo, plugin, version)
        update_marketplace_json(marketplace, plugin, version)

    print(version)

    return 0


if __name__ == "__main__":
    sys.exit(main())
