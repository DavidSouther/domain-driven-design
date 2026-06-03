# general/e2e profile

This directory is a regression harness for the `general` skill plugin. It runs
the full axis profile:

- **discovery** — given a coding situation, the model names the right skill from
  its description alone.
- **invocation** — with one skill loaded, the model produces an artifact that
  structurally exhibits what the skill prescribes.
- **baseline** — the same invocation prompts with no skill loaded, so the
  comparison report shows what each skill actually changes.

This file declares the harness purpose and the axis profile only. It names no
skill identifier and reproduces no skill content.
