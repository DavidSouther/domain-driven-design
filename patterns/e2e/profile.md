# Harness profile

This directory is a regression harness for the `patterns:*` skill plugin.
It exercises the full discovery + invocation + baseline triple: discovery checks that routing prompts select the correct skill from the routing table alone; invocation checks that a loaded skill produces code with the expected structural signature; baseline runs the same invocation prompts with no skill loaded as a falsification floor.
A non-degenerate gap between invocation and baseline is the headline signal.

The candidate codebase is a small TypeScript service (Node, `tsc` strict).
Answer every coding task with TypeScript source, showing the type or function definition and, where the task asks for one, a single example call site.
