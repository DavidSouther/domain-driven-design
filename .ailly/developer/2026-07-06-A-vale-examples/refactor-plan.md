# Refactor Plan

Files touched this loop (`git diff --name-only HEAD~4 HEAD`): `scripts/vale-fix.sh`,
`developer/tests/test_vale_fix_examples.py`.

- [x] `scripts/vale-fix.sh:66-93` **Indecent Exposure / hidden coupling** —
  `render_worked_examples_section` reads `$findings_json`/`$file` implicitly from the
  caller's scope instead of taking them as parameters. Every other lookup function
  (`dedup_rules`, `lookup_example`) takes its data explicitly; this one silently depends on
  variable names set by the enclosing scan loop, which is surprising to a reader and made
  ad-hoc testing harder (had to pre-set globals to call it standalone). Resolution: add
  `findings_json` and `file` as its first two positional parameters, update the one call site.
- [x] `scripts/vale-fix.sh:73-82` **Duplicated code** — the `if [ -n "$note" ]` branch
  repeats the `Rule:`/`Bad:`/`Good:` lines in both arms, differing only in whether a `Note:`
  line is appended. Resolution: build the three-line block once, then conditionally append
  the `Note:` line.
- [x] `scripts/vale-fix.sh:4` **Comment referencing a specific session artifact** — the
  file-header comment points at `.ailly/developer/2026-07-05-B-vale-autofix/plan.md`, a
  session-specific path that will rot once that session folder is cleaned up (pre-existing,
  but directly adjacent to this loop's changes). Resolution: drop the specific path reference,
  keep the general purpose description.

No other smells identified in the touched functions warranting action now; the sentinel-line
manifest encoding (`__WORKED_EXAMPLES__`) is string-parsing-heavy but is the simplest way to
carry data across the `xargs`-spawned dispatch process boundary and isn't worth adding new
indirection to avoid.
