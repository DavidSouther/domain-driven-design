#!/usr/bin/env python3
"""Structural checker for `patterns:aggregate` invocation cases.

Reads a TypeScript candidate from stdin and applies an ordered list of rules,
each tracing 1:1 to a bullet in the aggregate SKILL.md "Common Mistakes" section
(and the prompt's structural signature). On the first violated rule it prints a
single-line reason to stdout and exits 1; if every rule holds it exits 0. stderr
is left untouched so the eval runner records a genuine Fail, never an `Errored`
broken checker.

The rules are conservative: they fail only on an unambiguous structural violation
so a correct-but-differently-phrased answer still passes (the judge carries the
finer-grained signal). What fails is a missing root, an exposed mutable internal
collection, or a call site that mutates the internals directly.

Rules:
- R1 aggregate root present (the root is the sole public entry point).
- R2 internal collection not a public mutable handle ("Exposing internal
  entities: returning a raw LineItem[] reference").
- R3 mutation goes through a named method on the root, not a field write at the
  call site ("Multiple aggregate calls per request" / field assignment).
"""

import re
import sys

from _checker_utils import extract_code, fail, strip_comments

# A mutable line-item array type. `readonly LineItem[]` / `ReadonlyArray<LineItem>`
# are the encapsulated forms and are deliberately excluded.
MUTABLE_ARRAY = r"(?:LineItem\s*\[\]|Array\s*<\s*LineItem\s*>)"


def main() -> int:
    src = strip_comments(extract_code(sys.stdin.read()))

    # R1 — aggregate root present.
    if not re.search(r"\bclass\s+Order\b", src):
        return fail(
            "R1 aggregate root present: no `class Order` root; an aggregate needs a "
            "single root type that owns the LineItems and is the only entry point"
        )

    # R2 — internal collection not a public mutable handle.
    # 2a: a getter that returns the mutable internal array by reference.
    getter = re.compile(
        r"\bget\s+\w+\s*\(\s*\)\s*:\s*(?!readonly)(?:" + MUTABLE_ARRAY + r")"
    )
    if getter.search(src):
        return fail(
            "R2 internal collection exposed: a getter returns a mutable `LineItem[]`; "
            "hand back `readonly LineItem[]` or a copy so callers cannot mutate the "
            "aggregate's internals outside the root"
        )
    # 2b: a field declared with explicit `public` and a mutable array type.
    if re.search(r"\bpublic\s+(?!readonly)\w+\s*:\s*" + MUTABLE_ARRAY, src):
        return fail(
            "R2 internal collection exposed: a `public` mutable `LineItem[]` field lets "
            "callers mutate the line items without going through the root; make it "
            "private/readonly"
        )

    # R3 — mutation through a named method, not a field write at the call site.
    # Direct push/splice onto an order's item collection from outside the root, or
    # array assignment. `this.items.push(...)` inside a root method is the correct
    # form and is exempted (receiver must not be `this`).
    push = re.compile(
        r"(\w+)\s*\.\s*(?:items|lineItems|lines)\s*\.\s*(?:push|splice|pop|shift|unshift)\s*\("
    )
    for m in push.finditer(src):
        if m.group(1) != "this":
            return fail(
                "R3 call-site mutation: the example mutates the line-item collection "
                "directly (`" + m.group(1) + ".items.push(...)`); add the line through a "
                "named method on the root (e.g. `order.addLine(...)`) so the invariant "
                "is enforced"
            )
    if re.search(r"\b\w*[Oo]rder\w*\s*\.\s*(?:items|lineItems|lines)\s*=", src):
        return fail(
            "R3 call-site mutation: the example assigns the line-item collection "
            "directly; mutate through a named method on the root, not field assignment"
        )

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
