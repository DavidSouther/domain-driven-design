#!/usr/bin/env bash
# Root e2e/ CI entrypoint for Ailly's STATIC feature-test suites.
#
# Unlike every plugin's `<plugin>/e2e/ci.sh` (which assembles a model
# conversation via `ailly assemble`, fills it via `ailly run`, and scores it
# via `ailly eval`/`ailly report` -- and per `research/e2e/README.md`, `run`,
# `eval`, and `report` all call a live model), this driver never invokes the
# `ailly` binary and never calls a model. Root `e2e/` holds Ailly's own
# reference-architecture feature tests (DEVELOPMENT.md, "## Evals": "Feature
# tests are authored in the root e2e/ folder"), and those checks are
# deterministic source-level assertions over this repo's own markdown --
# there is no model transcript here for a judge to grade.
#
# Suites live under `e2e/evals/*.yaml` (the same `name`/`cases`/`assertions`
# shape used by the model-driven suites, restricted to `type: script`
# assertions); each case's checker script lives under `e2e/evals/scripts/`
# and follows the same stdout-reason/exit-code contract as every plugin's
# checkers. See `e2e/run_static_evals.py` for the driver and `e2e/README.md`
# for the fuller rationale.
set -euo pipefail
cd "$(dirname "${BASH_SOURCE[0]}")"
python3 run_static_evals.py
