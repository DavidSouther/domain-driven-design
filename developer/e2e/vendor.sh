#!/usr/bin/env bash
# Vendor live harness inputs into ./context/ so ailly's project-rooted VFS can
# read them. ailly jails every prefix path to the project root: a `../`-escaping
# path is normalised away and fails to resolve, so the shared AGENTS.md (at the
# repo root) and the skill bodies (under developer/skills/) must be copied in.
#
# Re-run before every assemble so the SCORED text is always current HEAD — this
# is what keeps a vended harness honest as a regression suite. ci.sh calls this
# first; run it by hand after editing any skill if you want to assemble manually.
#
# `context/` is committed (a fresh checkout can assemble without running this),
# and re-vended here so a stale committed copy is never what gets scored.

set -euo pipefail

project_dir="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
repo_root="$(cd "${project_dir}/../.." && pwd)"
skills_dir="${repo_root}/developer/skills"
agents_src="${repo_root}/e2e/AGENTS.md"
ctx="${project_dir}/context"

if [[ ! -f "${agents_src}" ]]; then
  echo "FAIL: shared AGENTS.md not found at ${agents_src}" >&2
  exit 1
fi
if [[ ! -d "${skills_dir}" ]]; then
  echo "FAIL: skills dir not found at ${skills_dir}" >&2
  exit 1
fi

rm -rf "${ctx}"
mkdir -p "${ctx}/skills"
cp "${agents_src}" "${ctx}/AGENTS.md"

for d in "${skills_dir}"/*/; do
  name="$(basename "${d}")"
  if [[ -f "${d}SKILL.md" ]]; then
    mkdir -p "${ctx}/skills/${name}"
    cp "${d}SKILL.md" "${ctx}/skills/${name}/SKILL.md"
  fi
done

# Generate the discovery routing surface from the live frontmatter, so a
# `description:` edit shows up in the disclosure table the model selects from.
python3 - "${skills_dir}" > "${ctx}/skills/disclosure.md" <<'PY'
import os
import sys

skills_dir = sys.argv[1]


def frontmatter(path):
    with open(path, encoding="utf-8") as fh:
        text = fh.read()
    if not text.startswith("---"):
        return {}
    end = text.find("\n---", 3)
    if end == -1:
        return {}
    block = text[3:end]
    fields = {}
    for line in block.splitlines():
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


entries = []
for name in sorted(os.listdir(skills_dir)):
    skill = os.path.join(skills_dir, name, "SKILL.md")
    if not os.path.isfile(skill):
        continue
    fm = frontmatter(skill)
    if "name" in fm and "description" in fm:
        desc = fm["description"].rstrip(".")
        entries.append(f"- `developer:{fm['name']}` — {desc}.")

print("# Available developer skills")
print()
print(
    "These are the skills you can invoke. Each line is one skill's identifier "
    "and the `description:` from its frontmatter — the same routing surface a "
    "coding agent presents. Select the one whose description fits the situation."
)
print()
print("\n".join(entries))
PY

echo "OK: vendored AGENTS.md, $(find "${ctx}/skills" -maxdepth 1 -mindepth 1 -type d | wc -l | tr -d ' ') skills, and disclosure.md into ${ctx#"${repo_root}/"}"
