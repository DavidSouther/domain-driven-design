#!/usr/bin/env bash
# CI driver / feature test for the characters plugin (Feature B, progressive
# disclosure).
#
# The voices are no longer skills: they are Claude Code output-styles applied
# OUTSIDE the model's selection loop. The old in-loop assemble/run/eval/report
# harness (which required a live model and the ../skills/<name>/SKILL.md tree)
# has no in-loop subject left and is recorded broken in TASKS.md. It is replaced
# by a structural metric check that asserts the two Feature B project metrics
# directly (see check_metrics.py):
#   1. token-share drop -- the four voice descriptions and using-characters no
#      longer appear in the always-on Level-1 description count.
#   2. capability survives -- each voice still colors output via an output-style
#      selectable outside the loop, with its signature trait preserved.
#
# No live model is required; the gate is structural (consistent with the
# standing ailly/key deferral in TASKS.md).

set -euo pipefail

project_dir="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

python3 "${project_dir}/check_metrics.py"
