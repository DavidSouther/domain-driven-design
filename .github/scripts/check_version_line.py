#!/usr/bin/env python3
"""check_version_line.py — keep ddd releases inside the 2026.09.x line.

This repository shares the ``ailly`` marketplace name and one CalVer sequence
with its successor (davidsouther/ailly).  Plugin caches update on version
inequality, so this repository must never carry a version that the successor
has used or will use.  Checks every version in the plugin manifests, the
marketplace manifest, and the local ``release/*`` tags.

Prints one reason line per violation to stdout and exits 1; prints nothing and
exits 0 when every version is acceptable.

Usage:
    python3 .github/scripts/check_version_line.py [--repo PATH]

Exit codes:
    0  every version is inside the allowed range
    1  at least one violation
"""

import argparse
import json
import subprocess
import sys
from pathlib import Path
from typing import Optional

LINE = "2026.09"
FIRST_RELEASE = f"{LINE}.3"
RESERVED = frozenset({f"{LINE}.2"})
CEILING = "2026.10.0"

MANIFEST_GLOBS = [
    "*/.claude-plugin/plugin.json",
    "*/.codex-plugin/plugin.json",
]
MARKETPLACE = ".claude-plugin/marketplace.json"
TAG_PREFIX = "release/"


def parse_version(value: str) -> tuple[int, ...]:
    """Parse a dotted numeric version into an integer tuple."""
    parts = value.split(".")
    if not all(p.isascii() and p.isdigit() for p in parts):
        raise ValueError(f"not a dotted numeric version: {value!r}")
    return tuple(int(p) for p in parts)


def violation(version: str) -> Optional[str]:
    """Return the reason a version is not allowed, or None when it is."""
    try:
        parsed = parse_version(version)
    except ValueError:
        return f"version {version!r} is not a dotted numeric version"
    if parsed in {parse_version(r) for r in RESERVED}:
        return f"version {version} is reserved for davidsouther/ailly"
    if parsed >= parse_version(CEILING):
        return (
            f"version {version} is at or above {CEILING}, "
            "which belongs to davidsouther/ailly"
        )
    return None


def _read_json(path: Path) -> dict:
    return json.loads(path.read_text())


def _manifest_versions(repo: Path) -> list[tuple[str, str]]:
    found = []
    paths = [p for pattern in MANIFEST_GLOBS for p in sorted(repo.glob(pattern))]
    for path in paths:
        version = _read_json(path).get("version")
        if version is not None:
            found.append((path.relative_to(repo).as_posix(), str(version)))

    marketplace = repo / MARKETPLACE
    if marketplace.exists():
        data = _read_json(marketplace)
        if data.get("version") is not None:
            found.append((MARKETPLACE, str(data["version"])))
        for entry in data.get("plugins", []):
            if entry.get("version") is not None:
                found.append(
                    (f"{MARKETPLACE} ({entry.get('name')})", str(entry["version"]))
                )
    return found


def _tag_versions(repo: Path) -> list[tuple[str, str]]:
    try:
        result = subprocess.run(
            ["git", "tag", "-l", f"{TAG_PREFIX}*"],
            cwd=repo,
            capture_output=True,
            text=True,
            check=True,
        )
    except (subprocess.CalledProcessError, FileNotFoundError):
        return []
    found = []
    for tag in result.stdout.split():
        version = tag.removeprefix(TAG_PREFIX)
        try:
            parse_version(version)
        except ValueError:
            continue
        found.append((tag, version))
    return found


def collect_versions(repo: Path) -> list[tuple[str, str]]:
    """Return (source, version) pairs for manifests and release tags."""
    return _manifest_versions(repo) + _tag_versions(repo)


def check(repo: Path) -> list[str]:
    """Return one reason line per violation."""
    lines = []
    for source, version in collect_versions(repo):
        reason = violation(version)
        if reason:
            lines.append(f"{source}: {reason}")
    return lines


def main(argv: Optional[list[str]] = None) -> int:
    parser = argparse.ArgumentParser(
        description="Fail when a version leaves the 2026.09.x line.",
    )
    _ = parser.add_argument(
        "--repo", default=".", help="Path to repository root (default: .)"
    )
    args = parser.parse_args(argv)
    lines = check(Path(args.repo).resolve())
    for line in lines:
        print(line)
    return 1 if lines else 0


if __name__ == "__main__":
    sys.exit(main())
