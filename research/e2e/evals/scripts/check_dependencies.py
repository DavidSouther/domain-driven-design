#!/usr/bin/env python3
"""Structural checker for the `dependencies` invocation case.

Rules trace to dependencies/SKILL.md "Output Format", "Ecosystem Config Files
Reference", and "Common Mistakes":
- R1 research-note path convention `docs/research/<dated-dir>/dependencies.md`.
- R2 a Sources section (the skill uses a `**Sources**` list).
- R3 cites at least one declared manifest (package.json, Cargo.toml,
  pyproject.toml, setup.py, requirements.txt, go.mod, pom.xml, build.gradle).
- R4 no lock file treated as a source (the "Reading lock files" mistake):
  package-lock.json, yarn.lock, pnpm-lock.yaml, Cargo.lock, go.sum,
  requirements.lock, pip.lock are resolved-deps and out of scope. Naming a lock
  file only to *exclude* it (the skill-correct behaviour) is not a violation;
  only a lock file cited *as a source* fails this rule.
"""

import re
import sys

from _md import candidate, fail

PATH = re.compile(r"docs/research/\d{4}-\d{2}-\d{2}-[\w-]+/dependencies\.md")
MANIFEST = re.compile(
    r"package\.json|Cargo\.toml|pyproject\.toml|setup\.py|requirements\.txt|"
    r"go\.mod|pom\.xml|build\.gradle",
    re.IGNORECASE,
)
LOCK = re.compile(
    r"package-lock\.json|yarn\.lock|pnpm-lock\.yaml|Cargo\.lock|go\.sum|"
    r"requirements\.lock|pip\.lock",
    re.IGNORECASE,
)
# Phrases that mark a lock-file mention as an explicit exclusion rather than a
# citation. A note that says "package-lock.json is out of scope" is following
# the skill, not violating it.
EXCLUSION = (
    "out of scope", "out-of-scope", "ignore", "not read", "do not read",
    "don't read", "exclude", "excluded", "resolved", "transitive", "skip",
    "never read", "not the declared", "rather than the lock",
)


def main() -> int:
    text = candidate()

    if not PATH.search(text):
        return fail(
            "R1 path convention: no `docs/research/<YYYY-MM-DD-A-topic>/dependencies.md` "
            "path; the skill writes findings to that dated research-note path"
        )

    if not re.search(r"(^|\n)\s*#{1,3}\s*Sources|\*\*Sources\*\*", text, re.IGNORECASE):
        return fail(
            "R2 note structure: no Sources section; the dependencies note lists every "
            "config file path and URL consulted under `**Sources**`"
        )

    if not MANIFEST.search(text):
        return fail(
            "R3 declared manifest: no declared-dependency manifest named (package.json, "
            "Cargo.toml, pyproject.toml, go.mod, …); the skill reads the main config"
        )

    for line in text.splitlines():
        m = LOCK.search(line)
        if m and not any(w in line.lower() for w in EXCLUSION):
            return fail(
                f"R4 lock file: `{m.group(0)}` cited as a source; lock files list "
                "resolved transitive deps and are out of scope for declared dependencies "
                "(mentioning a lock file only to exclude it is fine)"
            )

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
