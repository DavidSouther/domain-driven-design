#!/usr/bin/env bash
# Refresh the vendored skill context under general/e2e/context/.
#
# Ailly's project-rooted virtual filesystem clamps `..` at the project root, so
# the assembly prefix can only name files *under* general/e2e/. This script
# copies the live coding-agent AGENTS.md and the candidate SKILL.md files into
# context/ before each run, so the eval always scores the current skill text
# (the "live paths" intent) while keeping every prefix path inside the project.
#
# It only reads from ../skills and ../../e2e; the source skill files are never
# modified. context/ is git-ignored and regenerated, so the skill text lives in
# exactly one committed place (general/skills/).

set -euo pipefail

project_dir="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"   # general/e2e
repo_root="$(cd "${project_dir}/../.." && pwd)"                     # repo clone root
skills_src="${project_dir}/../skills"                              # general/skills
ctx="${project_dir}/context"

rm -rf "${ctx}"
mkdir -p "${ctx}/skills"

# Shared coding-agent constitution (repo-root e2e/AGENTS.md).
cp "${repo_root}/e2e/AGENTS.md" "${ctx}/AGENTS.md"

# using-general is the bootstrap routing skill; the other five are the
# discovery candidates and the four invocation targets (conversation is a
# discovery foil only).
skills=(using-general conversation review writing-skills writing-paired-skills writing-pattern-skills)
for name in "${skills[@]}"; do
  src="${skills_src}/${name}/SKILL.md"
  [[ -f "${src}" ]] || { echo "vendor: missing ${src}" >&2; exit 1; }
  mkdir -p "${ctx}/skills/${name}"
  cp "${src}" "${ctx}/skills/${name}/SKILL.md"
done

echo "vendor: refreshed ${ctx} (AGENTS.md + ${#skills[@]} skills)"
