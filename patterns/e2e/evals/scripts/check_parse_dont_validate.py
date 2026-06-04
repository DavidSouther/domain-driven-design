#!/usr/bin/env python3
"""Structural checker for `patterns:parse-dont-validate` invocation cases.

Reads a TypeScript candidate from stdin and applies an ordered list of rules,
each tracing 1:1 to a bullet in the parse-dont-validate SKILL.md "Common
Mistakes" section. On the first violated rule it prints a single-line reason to
stdout and exits 1; if every rule holds it exits 0. stderr is left untouched so
the eval runner records a genuine Fail, never an `Errored` broken checker.

Rules:
- R1 a boundary parser exists ("Validating everywhere instead of parsing once").
- R2 the parser returns the domain type, not a boolean ("the type itself encodes
  the validity proof", not a boolean check the caller must remember to run).
- R3 the parser signals failure with a thrown, specific error and does not return
  a nullable domain value ("Silent failures … returning null/undefined").
- R4 a downstream function accepts the parsed `Order` type ("Stringly typed
  domain models … defensively re-check"); the proof flows into the domain.
"""

import re
import sys

from _checker_utils import extract_code, fail, strip_comments

# Signature of the parser: `function parseX(...): Ret` or `const parseX = (...): Ret`.
PARSER_SIG = re.compile(
    r"\bparse\w*\s*(?:=\s*(?:async\s*)?)?\(([^)]*)\)\s*:\s*([^={;\n]+)"
)


def main() -> int:
    src = strip_comments(extract_code(sys.stdin.read()))

    # R1 — a boundary parser exists.
    if not re.search(r"\bparse[A-Za-z]\w*\s*(?:=\s*(?:async\s*)?)?\(", src):
        return fail(
            "R1 boundary parser: no `parse*` function; parse the raw input once at the "
            "boundary into a domain value instead of validating it in place"
        )

    sig = PARSER_SIG.search(src)
    rettype = sig.group(2).strip() if sig else ""

    # R2 — parser returns the domain type, not a boolean.
    if re.search(r"\bboolean\b", rettype):
        return fail(
            "R2 parser returns a proof, not a boolean: the parser's return type is "
            f"`{rettype}`; return the typed domain value (whose existence is the proof "
            "of validity), not a boolean the caller must re-check"
        )

    # R3 — failure is a thrown, specific error; the return type is not nullable.
    if re.search(r"\|\s*(?:null|undefined)\b", rettype) or rettype.endswith("?"):
        return fail(
            "R3 no silent failure: the parser return type is nullable "
            f"(`{rettype}`); a parser must throw a specific, actionable error on bad "
            "input, not return null/undefined the caller can ignore"
        )
    if not re.search(r"\bthrow\b", src):
        return fail(
            "R3 no silent failure: the parser never `throw`s; signal each failure mode "
            "with a specific, actionable error rather than returning a sentinel"
        )

    # R4 — a downstream function consumes the parsed `Order` type.
    if not re.search(r"[(,]\s*\w+\s*:\s*Order\b", src):
        return fail(
            "R4 parsed type flows into the domain: no function takes an `Order` "
            "parameter; downstream code should accept the parsed type (not raw "
            "`unknown`) and trust the parser's proof"
        )

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
