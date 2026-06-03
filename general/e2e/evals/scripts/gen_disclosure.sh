#!/usr/bin/env bash
# Regenerate disclosure.md from the live skill frontmatter.
#
# The discovery axis selects from a routing table; that table is the verbatim
# `description:` frontmatter of every candidate skill, exactly as it ships.
# Building it from the live ../skills/<name>/SKILL.md keeps the thing under test
# identical to the thing that ships: a description edit takes effect on the next
# run. Banners match the patterns-eval disclosure format (`==> name/SKILL.md <==`).

set -euo pipefail

project_dir="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"   # general/e2e
skills_dir="$(cd "${project_dir}/../skills" && pwd)"
out="${project_dir}/disclosure.md"

# The five candidates the discovery cases route among. using-general is the
# bootstrap routing skill (loaded separately) and is not a discovery target.
candidates=(conversation review writing-paired-skills writing-pattern-skills writing-skills)

: > "${out}"
for name in "${candidates[@]}"; do
  skill="${skills_dir}/${name}/SKILL.md"
  if [[ ! -f "${skill}" ]]; then
    echo "gen_disclosure: missing ${skill}" >&2
    exit 1
  fi
  printf '==> %s/SKILL.md <==\n' "${name}" >> "${out}"
  # Print the frontmatter: the first `---` fence through the next `---` fence.
  awk '
    /^---[[:space:]]*$/ { count++; print; if (count == 2) exit; next }
    count == 1          { print }
  ' "${skill}" >> "${out}"
  printf '\n' >> "${out}"
done

echo "gen_disclosure: wrote ${out} (${#candidates[@]} skills)"
