# `domain` Plugin Harness

This directory is a regression harness for the `domain` skill plugin.
It exercises the full discovery + invocation + baseline triple: discovery checks that routing prompts select the correct skill from `description:` frontmatter alone; invocation checks that a loaded skill produces an artifact with the expected structural shape; baseline runs the same invocation prompts with no skill loaded as a falsification floor.
A non-degenerate gap between the invocation and baseline pass rates is the headline signal.
