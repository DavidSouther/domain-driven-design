#!/usr/bin/env python3
"""Feature test: Vale.sh prose linting is wired into the repository.

Per `.ailly/prompts/vale.md` (the user-specified rule spec) and
`.ailly/developer/2026-07-05-A-vale/design.md`, adopting Vale requires:

- `.vale.ini` at the repo root, syncing Google/Joblint and enabling the DDD
  custom style (all of `styles/DDD/` loaded via `BasedOnStyles`);
- a vocab directory at `styles/config/vocabularies/DDD/` (required because
  `.vale.ini` declares `Vocab = DDD`);
- 12 rule files under `styles/DDD/` (the source spec's "Parentheticals" rule
  file held two YAML documents, one per rule; Vale keys a rule's ID off its
  *filename*, not an internal `name:` field, so multi-document files only
  ever register their first rule -- the second was split into its own file,
  `LongParenthetical.yml`, during build once this was discovered);
- a GitHub Actions workflow at `.github/workflows/vale.yml`;
- local-execution instructions appended to `DEVELOPMENT.md`.

When the `vale` binary is on PATH, this test runs it for real against a probe
file with one known trigger phrase per custom rule and asserts every rule ID
fires. This is deliberately not a structural-only check: an earlier version
of this test only inspected YAML shape and stayed green while the rules were
silently non-functional (missing `extends:` keys, an RE2-incompatible regex,
an unusable `Rules =` .vale.ini directive, a missing vocab directory, and a
message-formatting bug). Running the real tool is the only way this class of
bug gets caught. When `vale` is not on PATH, the test falls back to the
original structural sanity checks and reports that full verification was
skipped.
"""

import re
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
VALE_INI = REPO / ".vale.ini"
STYLES_DDD = REPO / "styles" / "DDD"
VOCAB_DDD = REPO / "styles" / "config" / "vocabularies" / "DDD"
WORKFLOW = REPO / ".github" / "workflows" / "vale.yml"
DEVELOPMENT_MD = REPO / "DEVELOPMENT.md"

# Filename -> the rule's Vale ID uses the filename stem, not the internal
# `name:` field (Google's own bundled styles follow the same convention).
RULE_FILES = [
    "EmDashes.yml",
    "Parentheticals.yml",
    "LongParenthetical.yml",
    "Filler.yml",
    "Sycophancy.yml",
    "PassiveVoice.yml",
    "Nominalizations.yml",
    "Consistency.yml",
    "TechnicalClarity.yml",
    "SentenceLength.yml",
    "WordChoice.yml",
    "Redundancy.yml",
]

EXPECTED_RULE_IDS = [f"DDD.{Path(name).stem}" for name in RULE_FILES]

REQUIRED_KEYS = ("extends", "message", "link", "level")

# One phrase per rule ID that is known to trip that rule.
TRIGGER_MARKDOWN = """\
This is one thing — with a plain em dash in it.

This sentence has (one aside) and also (a second aside) in it.

(This parenthetical clause is deliberately written to exceed fifty characters easily.)

There are quite a few things to note about this.

That's a great question, and I am really happy to help.

The bug was fixed by the on-call engineer.

The implementation of this feature took longer than expected.

We wrote a feature-test for the new feature-test runner.

The team follows the OODA loop for incident response.

This sentence keeps going and going and going and going and going and going and going and going and going and going and going and going and going on for a very long time indeed, well past the threshold.

This component does many things depending on context.

We did this in order to succeed at the task.
"""


def fail(reason: str) -> int:
    print(reason)
    return 1


def read(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def yaml_doc_looks_valid(doc: str) -> str | None:
    """Hand-rolled structural sanity check for one YAML document.

    Returns None if the document looks structurally sound, otherwise a
    short reason string. Used only as a fallback when the real `vale`
    binary is unavailable; not a substitute for actually running it.
    """
    if "\t" in doc:
        return "contains a tab character (YAML forbids tabs for indentation)"
    for key in REQUIRED_KEYS:
        match = re.search(rf"^{key}:\s*(.+)$", doc, re.MULTILINE)
        if not match or not match.group(1).strip():
            return f"missing or empty required key '{key}:'"
    return None


def check_static_artifacts() -> str | None:
    """R1/R2/R2b/R3/R4: files exist and look structurally right. Returns a
    failure reason, or None if everything checked out."""
    if not VALE_INI.is_file():
        return f"R1 missing {VALE_INI.relative_to(REPO)}"
    ini_text = read(VALE_INI)
    for required in ("StylesPath = styles", "Vocab = DDD", "Packages = Google, Joblint"):
        if required not in ini_text:
            return f"R1 .vale.ini missing '{required}'"
    based_on_match = re.search(r"^BasedOnStyles\s*=\s*(.+)$", ini_text, re.MULTILINE)
    if not based_on_match or "DDD" not in {s.strip() for s in based_on_match.group(1).split(",")}:
        return "R1 .vale.ini 'BasedOnStyles =' line must include 'DDD' to enable the custom rules"

    for filename in RULE_FILES:
        path = STYLES_DDD / filename
        if not path.is_file():
            return f"R2 missing rule file styles/DDD/{filename}"
        reason = yaml_doc_looks_valid(read(path))
        if reason:
            return f"R2 styles/DDD/{filename} invalid: {reason}"

    for vocab_file in ("accept.txt", "reject.txt"):
        if not (VOCAB_DDD / vocab_file).is_file():
            return f"R2b missing styles/config/vocabularies/DDD/{vocab_file}"

    if not WORKFLOW.is_file():
        return f"R3 missing {WORKFLOW.relative_to(REPO)}"
    workflow_text = read(WORKFLOW)
    for required in ("errata-ai/vale-action@reviewdog", "fail_on_error: false", "reporter: github-pr-review"):
        if required not in workflow_text:
            return f"R3 .github/workflows/vale.yml missing '{required}'"

    if not DEVELOPMENT_MD.is_file():
        return f"R4 missing {DEVELOPMENT_MD.relative_to(REPO)}"
    dev_text = read(DEVELOPMENT_MD)
    if "vale sync" not in dev_text:
        return "R4 DEVELOPMENT.md must document running 'vale sync'"
    if "brew install vale" not in dev_text:
        return "R4 DEVELOPMENT.md must document installing vale (e.g. 'brew install vale')"

    return None


def check_rules_actually_fire() -> str | None:
    """R5: run the real `vale` binary and confirm every custom rule fires."""
    with tempfile.NamedTemporaryFile(
        mode="w", suffix=".md", dir=REPO, delete=False
    ) as tmp:
        tmp.write(TRIGGER_MARKDOWN)
        probe_path = Path(tmp.name)

    try:
        result = subprocess.run(
            ["vale", "--output=line", probe_path.name],
            cwd=REPO,
            capture_output=True,
            text=True,
            timeout=30,
        )
    finally:
        probe_path.unlink()

    if result.returncode not in (0, 1):
        return (
            f"R5 'vale' exited with code {result.returncode} (config likely failed to "
            f"load):\n{result.stdout}\n{result.stderr}"
        )

    output = result.stdout
    missing = [rule_id for rule_id in EXPECTED_RULE_IDS if rule_id not in output]
    if missing:
        return f"R5 these DDD rules never fired against the probe file: {', '.join(missing)}\n{output}"

    return None


def check_e2e_excluded_skills_included() -> str | None:
    """R6: the documented `--glob` excludes only e2e test/eval fixtures
    (which may deliberately contain the prose patterns Vale flags), not
    skill/agent definitions or reference docs. An earlier version of this
    exclusion covered `**/skills/**` wholesale, working around a fatal,
    whole-run-aborting frontmatter parse error (an unquoted `description:`
    containing a bare `: `) by hiding every skill/reference file from Vale
    instead of fixing the two offending files. Confirms both halves of the
    corrected contract: an e2e doc is excluded, and a skill doc is linted
    (and the whole-repo run itself doesn't crash)."""
    e2e_docs = list(REPO.glob("**/e2e/**/*.md"))
    skill_docs = list(REPO.glob("**/skills/**/SKILL.md"))

    if e2e_docs:
        result = subprocess.run(
            ["vale", "--glob=!{**/e2e/**}", str(e2e_docs[0])],
            cwd=REPO,
            capture_output=True,
            text=True,
            timeout=30,
        )
        if "in 0 files" not in result.stdout:
            return (
                f"R6 --glob='!{{**/e2e/**}}' did not exclude {e2e_docs[0].relative_to(REPO)} "
                f"from linting:\n{result.stdout}\n{result.stderr}"
            )

    if skill_docs:
        result = subprocess.run(
            ["vale", "--glob=!{**/e2e/**}", str(skill_docs[0])],
            cwd=REPO,
            capture_output=True,
            text=True,
            timeout=30,
        )
        if "in 0 files" in result.stdout or result.returncode not in (0, 1):
            return (
                f"R6 --glob='!{{**/e2e/**}}' unexpectedly excluded or crashed on "
                f"{skill_docs[0].relative_to(REPO)}:\n{result.stdout}\n{result.stderr}"
            )

    whole_repo = subprocess.run(
        ["vale", "--glob=!{**/e2e/**}", "."],
        cwd=REPO,
        capture_output=True,
        text=True,
        timeout=120,
    )
    if whole_repo.returncode not in (0, 1):
        return (
            f"R6 whole-repo 'vale --glob=!{{**/e2e/**}} .' crashed (exit "
            f"{whole_repo.returncode}), likely an unquoted frontmatter value "
            f"somewhere under a skills/ tree:\n{whole_repo.stdout}\n{whole_repo.stderr}"
        )

    return None


def main() -> int:
    static_failure = check_static_artifacts()
    if static_failure:
        return fail(static_failure)

    if shutil.which("vale"):
        dynamic_failure = check_rules_actually_fire()
        if dynamic_failure:
            return fail(dynamic_failure)
        dynamic_failure = check_e2e_excluded_skills_included()
        if dynamic_failure:
            return fail(dynamic_failure)
        print("PASS: vale lint setup contract holds (verified by running vale)")
        return 0

    print("PASS: vale lint setup static contract holds ('vale' not on PATH, dynamic check skipped)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
