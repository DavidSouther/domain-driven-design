# research:codebase findings — patterns plugin catalog shape

## Query
How is the existing `patterns:using-patterns` catalog structured, and what does
the closest-sibling pattern (`arrange-act-assert`, `triangulate`) look like, so
the new `page-objects` reference matches convention?

## Findings
- Catalog root: `patterns/skills/using-patterns/SKILL.md` — a routing table
  (discriminator -> pattern + reference path), a "Discriminators That Are Easy
  to Confuse" section, and a "Pattern Composition" section. Every existing row
  follows the same three-column-in-prose shape.
- Reference files live at
  `patterns/skills/using-patterns/references/patterns/<name>.md`. Most
  patterns additionally have per-language files
  (`<name>/python.md|rust.md|typescript.md`), but the two test-technique
  patterns closest to this ability — `arrange-act-assert.md` and
  `triangulate.md` — are single files with no per-language subdirectory,
  because they teach an organizational technique rather than a language idiom.
- `arrange-act-assert.md` section shape (verified by reading the file):
  Overview -> When to Use (with an explicit "When NOT to use") -> Core Pattern
  (Before/After code) -> Quick Reference (table) -> Common Mistakes (bulleted)
  -> Composes With (bulleted, each pointing at a sibling reference path). This
  is the shape to match for `page-objects.md`.
- `patterns/e2e/` holds a parallel eval harness: `prompts/invocation/<name>.md`
  (a task prompt), `prompts/discovery/<name>-<failure-mode>.md` (a prompt that
  should trigger recognizing the pattern is needed), and
  `evals/scripts/check_<name>.py` (a structural checker reading a candidate
  off stdin and applying ordered rules traced to the skill's "Common
  Mistakes" section, exit 0/1). `triangulate` has all three; whether
  `page-objects` gets this harness in the same feature is a Build-phase sizing
  question (flagged in research.md, not decided here).

## Relevance to issue #27
Confirms the concrete file(s) to add and the shape to match:
`references/patterns/page-objects.md` (single file, no per-language split)
plus one routing-table row and one discriminator entry in `SKILL.md`.

## Sources
Local repository inspection, worktree
`/Users/davidsouther/devel/davidsouther/domain-driven-design-worktrees/2026-07-03-B-page-objects-pattern`,
branch `2026-07-03-B-page-objects-pattern`, commit at time of research (see
`git log -1`): files read —
`patterns/skills/using-patterns/SKILL.md`,
`patterns/skills/using-patterns/references/patterns/arrange-act-assert.md`,
`patterns/e2e/prompts/invocation/triangulate.md`,
`patterns/e2e/evals/scripts/check_triangulate.py`.
