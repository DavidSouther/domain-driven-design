"""Fail when a plugin version leaves the 2026.09.x line.

davidsouther/ailly shares this repo's `ailly` marketplace name and CalVer
sequence, and owns 2026.09.2 and everything from 2026.10.0 on.
"""

import json
import sys
from pathlib import Path

root = Path(__file__).resolve().parents[2]
manifests = [root / ".claude-plugin/marketplace.json"]
manifests += root.glob("*/.c*-plugin/plugin.json")
bad = []
for path in manifests:
    data = json.loads(path.read_text())
    for entry in [data, *data.get("plugins", [])]:
        version = entry.get("version")
        if not version:
            continue
        if version == "2026.09.2" or tuple(map(int, version.split("."))) >= (2026, 10):
            bad.append(f"{path.relative_to(root)}: {entry['name']} {version}")
sys.exit("\n".join(bad) or None)
