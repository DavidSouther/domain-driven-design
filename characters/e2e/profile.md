# `characters` Plugin Harness

After Feature B (progressive disclosure), the character voices are no longer
skills. They are Claude Code **output-styles** (`../output-styles/voice-*.md`)
applied OUTSIDE the model's selection loop. There is nothing in-loop left to
discover or invoke, so the original assemble/run/eval/report axis (which required
a live model and the `../skills/<name>/SKILL.md` tree, and is recorded broken in
TASKS.md) no longer has a subject.

The gate is re-expressed as a structural metric check (`check_metrics.py`, run by
`ci.sh`) that asserts the two Feature B project metrics directly:

1. **Token-share drop.** The four voice descriptions and the `using-characters`
   bootstrap no longer appear in the always-on Level-1 description count: the
   `characters/` plugin exposes zero skill frontmatter to the disclosure
   assembly. Before: 5 choices / ~282 tokens. After: 0.
2. **Capability survives.** Each voice still colors output when activated outside
   the loop: the four output-styles exist, are valid output-style files, opt out
   of auto-apply (`force-for-plugin: false`, so the user selects per voice), and
   preserve their signature persona trait verbatim-in-spirit
   (immaculate-attribution / tortitude / TDD-discipline / guardian-of-language).

No live model is required; the check is structural, consistent with the standing
`ailly`/key deferral recorded in TASKS.md.
