# Harness profile

This directory is an evaluation harness.
It tests one skill plugin in this repository for two independent regressions: whether each skill's `description:` routes the model to it from a realistic situation (discovery), and whether each skill's body shapes the model's output into the structure the skill prescribes (invocation).

This is the standing context for the eval only.
It is not a project the model is editing; it is the operating note the model reads before a single eval turn.

## Axis profile

**Full.**
This harness runs all three arms:

- **discovery** — fixed routing surface, swept over situations; the model names
  which skill applies.
- **invocation** — one skill body loaded; the model produces an artifact in
  that skill's domain.
- **baseline** — the invocation prompts with no skill body loaded, so the
  comparison isolates what the skill contributed.

The harness names no skill and reproduces no skill content; the routing surface and the skill bodies are loaded from their own files when an arm calls for them.
