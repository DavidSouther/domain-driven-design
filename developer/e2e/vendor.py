#!/usr/bin/env python3
"""Vendor live harness inputs into ./context/.

Skill bodies are referenced via `kind: external` in the assemblies
(../skills/<name>/SKILL.md), so only the shared AGENTS.md and the generated
disclosure table are copied in here.

Re-run before every assemble so the SCORED text is always current HEAD.
ci.sh calls this first; run it by hand after editing any skill if you want
to assemble manually.

context/ is committed (a fresh checkout can assemble without running this),
and re-vendored here so a stale committed copy is never what gets scored.
"""

import os
import shutil
import sys
from pathlib import Path


def frontmatter(path: Path) -> dict:
    text = path.read_text(encoding="utf-8")
    if not text.startswith("---"):
        return {}
    end = text.find("\n---", 3)
    if end == -1:
        return {}
    fields: dict = {}
    for line in text[3:end].splitlines():
        if ":" not in line:
            continue
        key, _, value = line.partition(":")
        key = key.strip()
        value = value.strip()
        if len(value) >= 2 and value[0] == value[-1] and value[0] in "\"'":
            value = value[1:-1]
        if key in ("name", "description"):
            fields[key] = value
    return fields


def main() -> None:
    script_dir = Path(__file__).resolve().parent
    repo_root = (script_dir / "../..").resolve()
    skills_dir = repo_root / "developer" / "skills"
    agents_src = repo_root / "e2e" / "AGENTS.md"
    ctx = script_dir / "context"

    if not agents_src.is_file():
        print(f"FAIL: shared AGENTS.md not found at {agents_src}", file=sys.stderr)
        sys.exit(1)
    if not skills_dir.is_dir():
        print(f"FAIL: skills dir not found at {skills_dir}", file=sys.stderr)
        sys.exit(1)

    shutil.rmtree(ctx, ignore_errors=True)
    (ctx / "skills").mkdir(parents=True)
    shutil.copy(agents_src, ctx / "AGENTS.md")

    entries = []
    for name in sorted(os.listdir(skills_dir)):
        skill = skills_dir / name / "SKILL.md"
        if not skill.is_file():
            continue
        fm = frontmatter(skill)
        if "name" in fm and "description" in fm:
            desc = fm["description"].rstrip(".")
            entries.append(f"- `developer:{fm['name']}` — {desc}.")

    lines = [
        "# Available developer skills",
        "",
        "These are the skills you can invoke. Each line is one skill's identifier "
        "and the `description:` from its frontmatter — the same routing surface a "
        "coding agent presents. Select the one whose description fits the situation.",
        "",
        *entries,
    ]
    (ctx / "skills" / "disclosure.md").write_text(
        "\n".join(lines) + "\n", encoding="utf-8"
    )

    print(f"OK: vendored AGENTS.md and disclosure.md into {ctx.relative_to(repo_root)}")


if __name__ == "__main__":
    main()
