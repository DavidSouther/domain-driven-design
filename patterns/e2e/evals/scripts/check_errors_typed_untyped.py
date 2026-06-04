#!/usr/bin/env python3
"""Structural checker for `patterns:errors-typed-untyped` invocation cases.

Reads a TypeScript candidate from stdin and applies ordered rules tracing to the
errors-typed-untyped SKILL.md "Common Mistakes" section. First violated rule prints
a single-line reason to stdout and exits 1; all holding exits 0. stderr untouched.

Rules:
- R1 the library failure is a tagged/discriminated type, not a bare `Error` string
  ("Result<T, string> in a library").
- R2 the failure has two or more named variants the caller can exhaust.
- R3 the application does not dispatch on error message text ("Dispatching on error
  message text").
"""

import re
import sys

from _checker_utils import extract_code, fail, strip_comments

DISCRIMINANT = re.compile(r"(?:kind|type|tag|_tag)\s*:\s*[\"'](\w+)[\"']")


def main() -> int:
    src = strip_comments(extract_code(sys.stdin.read()))

    # R1 — a tagged union or enum error type. (The union spans several intra-variant
    # `;`, so detect the pieces across `src` rather than capturing one balanced span.)
    type_decl = re.search(r"\btype\s+\w*Error\w*\s*=", src)
    enum = re.search(r"\benum\s+\w*Error\w*\b", src)
    discriminants = set(DISCRIMINANT.findall(src))
    has_union_bar = bool(type_decl and "|" in src[type_decl.end() : type_decl.end() + 1000])
    tagged_union = bool(type_decl and has_union_bar and discriminants)
    if not (tagged_union or enum):
        return fail(
            "R1 typed failure: no tagged union (a `type *Error = ... | ...` with a "
            "`kind`/`tag` discriminant) or enum; a library must expose a structured "
            "failure the caller can match on, not a stringly-typed `Error`"
        )

    # R2 — two or more named variants.
    if enum:
        body_m = re.search(r"\benum\s+\w*Error\w*\b[^{]*\{([^}]*)\}", src, re.DOTALL)
        members = [m for m in (body_m.group(1).split(",") if body_m else []) if m.strip()]
        variants = max(len(members), len(discriminants))
    else:
        variants = len(discriminants)
    if variants < 2:
        return fail(
            f"R2 named variants: only {variants} failure variant(s); the caller must be "
            "able to tell the distinct failure modes apart and react to each"
        )

    # R3 — no dispatch on message text at the application boundary.
    if re.search(r"\.\s*message\b[^;\n]*?(?:includes|indexOf|startsWith|match|===|==)\s*", src):
        return fail(
            "R3 no message-text dispatch: a branch inspects `.message` text; match on "
            "the tag, not on the human-readable string, which is not part of the API"
        )

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
