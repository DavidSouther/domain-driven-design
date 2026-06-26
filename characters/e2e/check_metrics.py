#!/usr/bin/env python3
"""Re-expressed characters/e2e gate (Feature B, progressive-disclosure).

The original characters/e2e harness ran an in-loop discovery/invocation suite
against ../skills/<name>/SKILL.md. After Feature B the voices are no longer
skills: they are Claude Code output-styles applied OUTSIDE the model's selection
loop. There is nothing in-loop left to discover, so the old assemble/run/eval/
report shape (which required a live model and the skill tree) no longer has a
subject. TASKS.md already records that harness as broken / never produced a run.

This checker replaces it with a structural assertion of the two project metrics
the design fixes for Feature B (design.md "Feature B", plan.md outline):

  Metric 1 (token-share drop). The four voice descriptions and the
    using-characters bootstrap no longer appear in the always-on Level-1
    description count. We assert characters/ exposes ZERO skill frontmatter
    (no skills/ tree contributing a `description:` to the disclosure assembly,
    the same surface vendor.py scans), and report the before/after token count.

  Metric 2 (capability survives). A voice still colors output when activated
    outside the loop. We assert each of the four output-styles exists, is a
    valid output-style file (frontmatter name + description), opts out of
    auto-apply (force-for-plugin: false, so the user selects per voice), and
    still carries its signature persona trait verbatim-in-spirit
    (immaculate-attribution / tortitude / TDD-discipline / guardian-of-language).
    The trait text surviving in the activation channel is the structural stand-in
    for "the voice still colors output," verifiable without a live model.

No live model is required: the gate is structural, consistent with the standing
ailly/key deferral recorded in TASKS.md.

Exit 0 on pass, 1 on any failure.
"""

import re
import sys
from pathlib import Path

E2E_DIR = Path(__file__).resolve().parent
PLUGIN_DIR = E2E_DIR.parent
SKILLS_DIR = PLUGIN_DIR / "skills"
STYLES_DIR = PLUGIN_DIR / "output-styles"

# Baseline (pre-Feature-B) always-on Level-1 view for the characters plugin:
# 5 skills (using-characters + 4 voices), ~282 tokens by the inventory's
# heuristic (~230 by tiktoken cl100k_base). Recorded so the gate reports the
# drop, not just asserts the end state.
BEFORE_CHOICES = 5
BEFORE_TOKENS_HEURISTIC = 282

# Each voice -> (output-style filename, signature trait, marker substrings that
# must survive verbatim-in-spirit in the activation channel).
VOICES = {
    "ailly": (
        "voice-ailly.md",
        "immaculate-attribution",
        ["notebook", "attribution", "source"],
    ),
    "jacki": (
        "voice-jacki.md",
        "tortitude / three-options-first",
        ["tortitude", "three", "sketch"],
    ),
    "jefri": (
        "voice-jefri.md",
        "TDD-discipline",
        ["failing test", "red", "green", "refactor"],
    ),
    "rupert": (
        "voice-rupert.md",
        "guardian-of-language",
        ["ubiquitous language", "glossary", "chapter"],
    ),
}


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
        fields[key] = value
    return fields


def approx_tokens(text: str) -> int:
    # Same heuristic family the inventory used; ~char/4. Used only to report
    # the after-count for the dropped descriptions (which is 0).
    return max(0, round(len(text) / 4))


def fail(msg: str) -> None:
    print(f"FAIL: {msg}", file=sys.stderr)


def main() -> int:
    errors = 0

    # --- Metric 1: token-share drop -----------------------------------------
    leftover_descriptions = []
    if SKILLS_DIR.is_dir():
        for skill in sorted(SKILLS_DIR.glob("*/SKILL.md")):
            fm = frontmatter(skill)
            if "name" in fm and "description" in fm:
                leftover_descriptions.append((fm["name"], fm["description"]))

    after_choices = len(leftover_descriptions)
    after_tokens = sum(approx_tokens(d) for _, d in leftover_descriptions)

    if after_choices != 0:
        errors += 1
        fail(
            "characters/ still exposes "
            f"{after_choices} Level-1 skill description(s); expected 0 after "
            "Feature B (voices are output-styles, not skills): "
            + ", ".join(n for n, _ in leftover_descriptions)
        )
    else:
        print(
            "OK metric 1 (token-share drop): characters/ exposes 0 Level-1 "
            "skill descriptions.\n"
            f"  before: {BEFORE_CHOICES} choices / ~{BEFORE_TOKENS_HEURISTIC} tokens "
            "(using-characters + 4 voice-*).\n"
            f"  after:  {after_choices} choices / ~{after_tokens} tokens."
        )

    # --- Metric 2: capability survives outside the loop ---------------------
    if not STYLES_DIR.is_dir():
        errors += 1
        fail(f"output-styles dir not found at {STYLES_DIR}")
    else:
        for voice, (fname, trait, markers) in VOICES.items():
            path = STYLES_DIR / fname
            if not path.is_file():
                errors += 1
                fail(f"voice {voice}: output-style missing at {path}")
                continue
            fm = frontmatter(path)
            body = path.read_text(encoding="utf-8")

            if "name" not in fm or "description" not in fm:
                errors += 1
                fail(
                    f"voice {voice}: {fname} is not a valid output-style "
                    "(missing frontmatter name/description)."
                )
            # Auto-apply must be off so the user selects per voice; absent key
            # defaults to false, which is also acceptable.
            ffp = fm.get("force-for-plugin", "false").lower()
            if ffp not in ("false", ""):
                errors += 1
                fail(
                    f"voice {voice}: {fname} sets force-for-plugin: {fm.get('force-for-plugin')}; "
                    "expected false (no auto-apply; the user selects the voice)."
                )

            low = body.lower()
            missing = [m for m in markers if m.lower() not in low]
            if missing:
                errors += 1
                fail(
                    f"voice {voice}: signature trait '{trait}' not preserved in "
                    f"{fname}; missing marker(s): {missing}"
                )
            else:
                print(
                    f"OK metric 2 (capability survives): {voice} -> {fname} "
                    f"valid output-style, trait '{trait}' preserved."
                )

    if errors:
        print(f"\nFAIL: {errors} check(s) failed.", file=sys.stderr)
        return 1
    print(
        "\nOK: characters/e2e metrics pass. Voices removed from the always-on "
        "Level-1 view; the four voices still color output via output-styles "
        "selected outside the model's loop."
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
