#!/usr/bin/env python3
"""Structural checker for `patterns:repository` invocation cases.

Reads a TypeScript candidate from stdin and applies an ordered list of rules,
each tracing 1:1 to a bullet in the repository SKILL.md "Common Mistakes" section.
On the first violated rule it prints a single-line reason to stdout and exits 1;
if every rule holds it exits 0. stderr is left untouched so the eval runner
records a genuine Fail, never an `Errored` broken checker.

Rules:
- R1 an abstract repository interface is declared ("Interface in the wrong
  layer" — the abstraction must exist, in the domain).
- R2 at least two concrete implementations exist (in-memory + SQL).
- R3 the domain service depends on the abstract interface, not a concrete one.
- R4 no ORM/SQL/driver/connection type leaks onto the domain surface — the
  interface body and the service signature ("Leaking ORM models into domain
  logic"). The concrete SQL implementation may reference infra types freely.
"""

import re
import sys

from _checker_utils import extract_code, fail, strip_comments

# Infrastructure types that must not appear on the domain surface (interface body
# and the domain-service signature). The concrete SQL repo legitimately uses them.
INFRA = re.compile(
    r"\b(?:Pool|PoolClient|PgClient|Connection|Knex|Sequelize|Prisma\w*|DataSource"
    r"|EntityManager|QueryRunner|Session|Database|Datastore)\b"
)


def brace_block(src: str, open_index: int) -> str:
    """Return the substring from `{` at open_index through its matching `}`."""
    depth = 0
    for i in range(open_index, len(src)):
        if src[i] == "{":
            depth += 1
        elif src[i] == "}":
            depth -= 1
            if depth == 0:
                return src[open_index : i + 1]
    return src[open_index:]


def main() -> int:
    src = strip_comments(extract_code(sys.stdin.read()))

    # R1 — abstract repository interface declared.
    iface = re.search(r"\b(?:interface|abstract\s+class)\s+OrderRepository\b[^{]*\{", src)
    if not iface:
        return fail(
            "R1 abstract interface: no `interface OrderRepository` (or abstract class); "
            "define the repository abstraction in the domain layer"
        )

    # R2 — at least two concrete implementations.
    impls = re.findall(r"\bclass\s+\w+\s+(?:implements|extends)\s+OrderRepository\b", src)
    if len(impls) < 2:
        return fail(
            f"R2 two implementations: found {len(impls)} class implementing "
            "`OrderRepository`; provide an in-memory implementation for tests and a SQL "
            "one for production"
        )

    # R3 — domain service depends on the abstract interface, not a concrete one.
    svc = re.search(r"\bplaceOrder\s*\(([^)]*)\)", src)
    if not svc:
        return fail(
            "R3 domain service signature: no `placeOrder(...)` service found to check "
            "its dependency on the abstract interface"
        )
    params = svc.group(1)
    if re.search(r":\s*(?:InMemory|Sql|Sqlite|Postgres|Mongo)\w*OrderRepository\b", params):
        return fail(
            "R3 depends on a concrete repository: `placeOrder` names a concrete "
            "implementation in its parameters; depend only on the abstract "
            "`OrderRepository` so storage can change without touching the service"
        )
    if "OrderRepository" not in params:
        return fail(
            "R3 depends on the abstraction: `placeOrder` does not take an "
            "`OrderRepository`; the domain service must receive the repository through "
            "the abstract interface"
        )

    # R4 — no infra type leaks onto the domain surface (interface body + service sig).
    iface_body = brace_block(src, iface.end() - 1)
    domain_surface = iface_body + "\n" + svc.group(0)
    leak = INFRA.search(domain_surface)
    if leak:
        return fail(
            f"R4 ORM/SQL leak on the domain surface: `{leak.group(0)}` appears in the "
            "repository interface or the service signature; keep ORM/session/connection "
            "types inside the concrete infrastructure implementation only"
        )

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
