#!/usr/bin/env python3
"""Feature test: current, portable subagent model-selection guidance.

Given a maintainer uses the repository's model-selection reference after the
July 2026 provider releases, when they choose candidates to evaluate for a
supported harness, then they see a complexity-first, provider-grounded
illustrative snapshot covering current Anthropic, OpenAI, Google, and
open-weight/self-hosted options. The future eval suite remains the gate to a
default, and provider availability, API identifiers, and harness dispatch
support remain different contracts.

This executable contract checks that primary story end to end across the
central guidance, its maintenance policy, its Code Mode cost grounding, and
the harness adapters. It needs no model and no pytest, and exits 0 (all rules
hold) or 1 with a single reason line on stdout.
"""

import re
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
DEV = REPO / "developer"
GENERAL = REPO / "general"
AILLY = DEV / "skills" / "ailly" / "SKILL.md"
DEVELOPMENT = REPO / "DEVELOPMENT.md"
THRESHOLDS = DEV / "skills" / "ailly" / "references" / "shapes" / "code-mode-thresholds.md"
ADAPTERS = DEV / "skills" / "ailly" / "references" / "agents"

EXPECTED_TIER_TERMS = {
    "high": {
        "anthropic": ["opus 5", "fable 5"],
        "openai": ["gpt-5.6 sol"],
        "google": ["gemini 3.5 flash", "sustained"],
        "open-weight / self-hosted": ["kimi k2.7 code", "specialist", "hardware", "eval"],
    },
    "balanced": {
        "anthropic": ["sonnet 5"],
        "openai": ["gpt-5.6 terra"],
        "google": ["gemini 3.6 flash"],
    },
    "economy": {
        "anthropic": ["haiku 4.5"],
        "openai": ["gpt-5.6 luna"],
        "google": ["gemini 3.5 flash-lite"],
    },
}
EXPECTED_PROVIDER_HEADERS = [
    "Complexity profile",
    "Anthropic",
    "OpenAI",
    "Google",
    "Open-weight / self-hosted",
    "Ailly Phases",
]

# The complexity-dimension axes research surfaced; the guidance must key on
# at least one of these rather than organizing solely by Ailly phase name.
COMPLEXITY_TERMS = [
    "complexity dimension",
    "reasoning depth",
    "constraint",
    "domain specificity",
    "generation-vs-evaluation",
    "generation vs evaluation",
    "generation/evaluation",
]


def fail(reason: str) -> int:
    print(reason)
    return 1


def find_general_model_guidance():
    """Return (path, text) of the first general/**/*.md file that reads like
    subagent model-selection guidance, else (None, "")."""
    if not GENERAL.is_dir():
        return None, ""
    for path in sorted(GENERAL.rglob("*.md")):
        text = path.read_text()
        low = text.lower()
        if "model" not in low or "alias" not in low:
            continue
        if any(t in low for t in ("subagent", "dispatch", "select", "selection")):
            return path, text
    return None, ""


def section(text: str, heading_re: str) -> str:
    """Return the body of the `##` section whose heading matches, up to the
    next `##` heading (case-insensitive), or "" if not found."""
    m = re.search(rf"(?ims)^##\s+{heading_re}\s*$(.*?)(?=^##\s+|\Z)", text)
    return m.group(1) if m else ""


def markdown_cells(line: str):
    return [cell.strip() for cell in line.strip().strip("|").split("|")]


def dated_provider_table(text: str):
    """Return (section text, headers, tier rows) for the dated example table.

    This intentionally scopes assertions to the table instead of allowing a
    model name mentioned elsewhere in the document to satisfy the contract.
    """
    example = section(text, r"Principle\s*(?:→|->)\s*Provider Example")
    lines = example.splitlines()
    table_lines = []
    for index, line in enumerate(lines):
        if line.lstrip().startswith("|") and "complexity profile" in line.lower():
            table_lines = [candidate for candidate in lines[index:] if candidate.lstrip().startswith("|")]
            break
    if len(table_lines) < 3:
        return example, [], {}

    headers = markdown_cells(table_lines[0])
    normalized_headers = [header.lower() for header in headers]
    rows = {}
    for line in table_lines[2:]:
        values = markdown_cells(line)
        if len(values) != len(headers):
            continue
        normalized_values = [value.lower() for value in values]
        profile = normalized_values[0]
        for tier in EXPECTED_TIER_TERMS:
            if profile.startswith(tier):
                if tier in rows:
                    rows[tier] = {}
                    break
                rows[tier] = dict(zip(normalized_headers, normalized_values))
    return example, headers, rows


def main() -> int:
    # T1 - a general/ home for subagent model-selection guidance exists,
    # using alias language, and organizes by complexity dimension rather than
    # solely by Ailly phase name.
    path, text = find_general_model_guidance()
    if not path:
        return fail(
            "T1 general home: no file under general/ carries subagent "
            "model-selection guidance (expected alias language plus a "
            "subagent/dispatch/selection keyword)"
        )
    low = text.lower()
    if not any(t in low for t in COMPLEXITY_TERMS):
        return fail(
            f"T1 organization: {path.relative_to(REPO)} does not organize by "
            "any complexity-dimension term (e.g. 'reasoning depth', "
            "'constraint', 'domain specificity', 'generation-vs-evaluation'); "
            "the guidance must key on complexity dimension, not phase name alone"
        )

    # T2 - find and extract the deliberately dated provider table; document-
    # wide mentions of model names must not satisfy the snapshot contract.
    example, headers, tier_rows = dated_provider_table(text)
    example_low = example.lower()
    if "last reviewed 2026-07-29" not in example_low:
        return fail(
            f"T2 review stamp: {path.relative_to(REPO)} is not stamped "
            "'Last reviewed 2026-07-29'"
        )

    # T3 - the actual table has every provider column, including accurate
    # downloadable/self-hosted terminology.
    if headers != EXPECTED_PROVIDER_HEADERS:
        return fail(
            f"T3 provider schema: {path.relative_to(REPO)} has headers "
            f"{headers}; expected {EXPECTED_PROVIDER_HEADERS}"
        )
    if set(tier_rows) != set(EXPECTED_TIER_TERMS) or any(
        not row for row in tier_rows.values()
    ):
        return fail(
            f"T3 provider schema: {path.relative_to(REPO)} must contain "
            "exactly one high, balanced, and economy row"
        )

    # T4 - provider-grounded illustrative candidates are mapped by tier in the
    # table; they are not asserted to have cleared the future eval suite.
    missing_mappings = {}
    for tier, expected_cells in EXPECTED_TIER_TERMS.items():
        row = tier_rows.get(tier, {})
        for provider, terms in expected_cells.items():
            missing = [term for term in terms if term not in row.get(provider, "")]
            if missing:
                missing_mappings[f"{tier}/{provider}"] = missing
    if missing_mappings:
        return fail(
            f"T4 tier mapping: {path.relative_to(REPO)} has missing table "
            f"mapping terms {missing_mappings}"
        )
    if not all(term in example_low for term in ("illustrative", "provider", "future work")):
        return fail(
            "T4 candidate status: the dated-table section must say its "
            "provider-grounded mappings are illustrative pending future-work evals"
        )
    high_anthropic = tier_rows["high"]["anthropic"]
    if not all(term in high_anthropic for term in ("exceptional", "highest", "long-horizon")):
        return fail(
            "T4 Fable qualification: the high-tier Anthropic cell must present "
            "Fable 5 as an exceptional highest-capability/long-horizon option"
        )
    if "not automatic" not in example_low:
        return fail(
            "T4 Fable qualification: the dated-table section must say Fable 5 "
            "is not an automatic replacement for the high-tier default"
        )
    if "fable 5" in tier_rows["balanced"]["anthropic"] or "fable 5" in tier_rows["economy"]["anthropic"]:
        return fail("T4 Fable mapping: Fable 5 must not be an automatic lower-tier replacement")
    open_weight_column = "\n".join(
        row["open-weight / self-hosted"] for row in tier_rows.values()
    )
    if "kimi k2.7 code" in tier_rows["economy"]["open-weight / self-hosted"]:
        return fail("T4 Kimi mapping: Kimi K2.7 Code must not be an economy default")
    if "deepseek" in open_weight_column:
        return fail(
            "T4 open-weight accuracy: API-only DeepSeek products must not "
            "appear in the open-weight/self-hosted table column"
        )
    if not all(term in example_low for term in ("deepseek", "api", "not open-weight")):
        return fail(
            "T4 DeepSeek caveat: the dated-table section must state that "
            "API-only DeepSeek products are not open-weight releases"
        )

    # T5 - the guidance keeps its eval-first principle and separates provider
    # availability, API-ID stability, and harness dispatchability.
    portability_terms = (
        ("eval",),
        ("provider availability", "available from the provider"),
        ("harness", "dispatch"),
        ("api id", "api identifier"),
        ("stable", "pinned"),
    )
    missing_portability = [
        alternatives
        for alternatives in portability_terms
        if not any(term in low for term in alternatives)
    ]
    if missing_portability:
        return fail(
            f"T5 portability: {path.relative_to(REPO)} does not distinguish "
            f"all required contracts; missing term groups {missing_portability}"
        )

    # T6 - DEVELOPMENT.md carries a maintenance nudge for that dated table.
    if not DEVELOPMENT.is_file():
        return fail(f"T6 {DEVELOPMENT.relative_to(REPO)} not found")
    development_blocks = [
        block.lower() for block in re.split(r"\n\s*\n", DEVELOPMENT.read_text())
    ]
    has_bounded_nudge = any(
        any(term in block for term in ("model-selection", "model selection"))
        and "dated" in block
        and any(term in block for term in ("example table", "snapshot table"))
        and any(term in block for term in ("periodic", "check whether", "review"))
        for block in development_blocks
    )
    if not has_bounded_nudge:
        return fail(
            f"T6 maintenance nudge: {DEVELOPMENT.relative_to(REPO)} does not "
            "contain one paragraph tying periodic review to the dated "
            "model-selection example table"
        )

    # T7 - Code Mode's provider-doc-verified snapshot contains an implementable
    # exact Opus 5 price/context row.
    if not THRESHOLDS.is_file():
        return fail(f"T7 {THRESHOLDS.relative_to(REPO)} not found")
    thresholds_low = THRESHOLDS.read_text().lower()
    cost_header = next(
        (line.lower() for line in THRESHOLDS.read_text().splitlines()
         if line.lstrip().startswith("|") and "input ($/1m)" in line.lower()),
        "",
    )
    cost_header_cells = markdown_cells(cost_header)
    opus_row = next(
        (line.lower() for line in THRESHOLDS.read_text().splitlines()
         if line.lstrip().startswith("|") and "opus 5" in line.lower()),
        "",
    )
    opus_cells = markdown_cells(opus_row)
    if (
        "july 2026" not in thresholds_low
        or "verified against provider documentation" not in thresholds_low
        or cost_header_cells != ["model", "input ($/1m)", "output ($/1m)", "context"]
        or opus_cells != ["opus 5", "$5", "$25", "1m"]
    ):
        return fail(
            f"T7 cost grounding: {THRESHOLDS.relative_to(REPO)} does not "
            "include a provider-doc-verified July 2026 Opus 5 row with "
            "$5 input, $25 output per 1M tokens, and 1M context"
        )

    # T8 - harness adapters accurately describe whether model selection is
    # confirmed and do not equate provider availability with accepted values.
    codex = (ADAPTERS / "codex.md").read_text().lower()
    gemini = (ADAPTERS / "gemini.md").read_text().lower()
    if not any(term in codex for term in ("tool schema", "advertised", "accepted model")):
        return fail(
            "T8 Codex adapter: model dispatch guidance does not constrain "
            "values to those confirmed by the active harness"
        )
    if "no confirmed model-selection field" not in gemini or "announce" not in gemini:
        return fail(
            "T8 Gemini adapter: announce-only fallback is not explicit"
        )

    # T9 - the coordinator's Phase Isolation section documents mandate-with-
    # announce: setting the model when the mechanism exists, AND announcing
    # the choice either way (not silent mandate, not announce-only).
    if not AILLY.is_file():
        return fail(f"T9 {AILLY.relative_to(REPO)} not found")
    ailly = AILLY.read_text()
    isolation = section(ailly, "Phase Isolation")
    if not isolation:
        return fail(
            f"T9 coordinator: no `## Phase Isolation` section found in "
            f"{AILLY.relative_to(REPO)}"
        )
    iso_low = isolation.lower()
    if "model" not in iso_low:
        return fail(
            "T9 mandate: the Phase Isolation section does not mention the "
            "subagent's model at all"
        )
    mandates = any(
        t in iso_low
        for t in ("set the model", "sets the model", "mandate", "model=", "model parameter", "model argument")
    )
    announces = "announce" in iso_low
    if not (mandates and announces):
        return fail(
            "T9 mandate-with-announce: the Phase Isolation section must both "
            "document actively setting the subagent's model where the "
            "mechanism exists AND announcing the choice, not one alone"
        )

    # T10 - the mandate is unconditional: the general home must be loaded on
    # every dispatch, not situationally.
    if not any(t in iso_low for t in ("unconditional", "every dispatch", "every subagent dispatch")):
        return fail(
            "T10 unconditional load: the Phase Isolation section does not "
            "state that the general model-selection reference is loaded on "
            "every subagent dispatch, unconditionally"
        )

    # T11 - the mandate reaches sub-steps described within a phase's own body,
    # not only the phase's single top-level dispatch.
    if not any(t in iso_low for t in ("within a phase", "within the phase", "sub-step", "inside a phase")):
        return fail(
            "T11 within-phase mandate: the Phase Isolation section does not "
            "extend the subagent mandate to sub-steps described inside a "
            "phase's own body, only to the phase's top-level dispatch"
        )

    print("PASS: subagent model mandate contract holds")
    return 0


if __name__ == "__main__":
    sys.exit(main())
