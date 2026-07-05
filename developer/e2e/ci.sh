#!/usr/bin/env bash
# CI driver for the developer-plugin skill-eval harness.
#
# Drives the full operator journey across the suites: the discovery matrix; the
# invocation/baseline coordinator pair; the invocation-phases/baseline-phases and
# invocation-abilities/baseline-abilities pairs (the lifecycle phases and the
# progressive abilities, both reached through the coordinator); the long-loop /
# long-loop-baseline pair (a single-conversation case for the long-loop mode of ailly,
# which is not a matrix skill); the code-mode/code-mode-baseline pair (the same
# single-conversation shape, for the Code Mode mode of ailly); plus the
# design-artifacts/design-artifacts-baseline pair (a single-conversation case
# measuring the design phase reference's Open Artifact Decisions section, which
# cannot ride the invocation-phases matrix):
#   0. vendor.py        -- copy the live AGENTS.md and regenerate the disclosure
#      table so the SCORED text is current HEAD.
#   1. ailly assemble <suite>     -- always runs; asserts N conversation files
#      land under runs/<id>/ for each suite.
#   2. ailly run runs/<id>/       -- requires a live model. Asserts every
#      conversation's trailing blank assistant slot was filled. With neither
#      ANTHROPIC_API_KEY nor a project .env the script hard-fails: there is no
#      assemble-only success path, so the falsification gate always runs.
#   3. ailly eval <suite> --over runs/<id>/ -- asserts the per-run report landed.
#   4. ailly report ...           -- single-run discovery summary, then several
#      comparisons (baseline-vs-invocation, long-loop-baseline-vs-long-loop,
#      code-mode-baseline-vs-code-mode, ...) whose four buckets the
#      falsification gate reads.
#
# The `ailly` binary is resolved through AILLY_BIN (default `ailly`); a source
# checkout can point it at a built binary:
#   AILLY_BIN=/path/to/ailly_two/target/release/ailly_two bash developer/e2e/ci.sh

set -euo pipefail

project_dir="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
repo_root="$(cd "${project_dir}/../.." && pwd)"
AILLY_BIN="${AILLY_BIN:-ailly}"

cd "${repo_root}"

rm -rf "${project_dir}/runs" "${project_dir}/evals/reports"

# --- CUJ 0: vendor AGENTS.md + disclosure into ./context/ ------------------
# Skill bodies are loaded via `kind: external` (../skills/<name>/SKILL.md) and
# do not need to be copied. Only AGENTS.md and the generated disclosure table
# are vendored.

python3 "${project_dir}/vendor.py"

# --- Falsification hygiene: the baseline-prefix files must not leak an answer.
# Neither the shared AGENTS.md nor profile.md may name a `developer:<skill>`
# identifier; a match would hand the no-skill baseline arm the routing answer
# and the structural artifact's name, making the falsification gap vacuous.
hygiene_targets=("${project_dir}/context/AGENTS.md" "${project_dir}/profile.md")
if grep -nE 'developer:[a-z][a-z-]+' "${hygiene_targets[@]}"; then
  echo "FAIL: a baseline-prefix file names a developer:<skill> identifier (see matches above)." >&2
  exit 1
fi
# Post-consolidation (developer-plugin consolidation): the five lifecycle phases are
# entered by argument and the four progressive abilities (thinking, refactor, initialize,
# program-management) are reached as coordinator references. The discovery answer for any
# of these is the `references/...` reference path the coordinator loads. Those skill
# identifiers are retired, so the reference-path form is the post-consolidation answer
# token; forbid it leaking into the baseline arm's context too. Bare ability/phase names
# (research, design, plan, cleanup, thinking, refactor, initialize) are NOT grepped
# (reviewer decision 2: they false-positive on ordinary prose); the falsification strength
# is carried on the assertion side, which requires BOTH the routing token and the
# reference path the baseline arm cannot emit. The single pattern below covers the
# `references/phases/<phase>`, the `references/abilities/<ability>`, and the
# `references/abilities/program-management/<name>` answer-path forms.
if grep -nE 'references/[a-z][a-z-]*(/[a-z][a-z-]*){0,2}\.md' "${hygiene_targets[@]}"; then
  echo "FAIL: a baseline-prefix file names a references/<...>.md answer path (see matches above); the baseline arm leaks the answer." >&2
  exit 1
fi
echo "OK: baseline-prefix files (AGENTS.md, profile.md) leak no developer:<skill> identifier or references/<...>.md answer path."

# Post-consolidation (developer-plugin consolidation): the invocation/baseline matrix now
# splits into THREE pairs because the bodies load from three different path families:
#   - invocation/baseline           -- the surviving `ailly` coordinator skill (1 case)
#   - invocation-phases/baseline-phases   -- the five lifecycle phase references (5 cases)
#   - invocation-abilities/baseline-abilities -- the three progressive ability references
#     thinking, refactor, initialize (3 cases)
# The matrix total is unchanged from the prior split (1 + 5 + 3 = 9 cases); only the suite
# split changed, because thinking/refactor/initialize moved from standalone skills to
# coordinator references and now load from ../skills/ailly/references/abilities/<ability>.md. The
# discovery matrix (9) and the long-loop pair (1) are untouched. code-mode (1) is
# a new pair, same single-conversation shape as long-loop.
expected_count() {
  case "$1" in
    discovery)              echo 9 ;;
    invocation)             echo 1 ;;
    baseline)               echo 1 ;;
    invocation-phases)      echo 5 ;;
    baseline-phases)        echo 5 ;;
    invocation-abilities)   echo 3 ;;
    baseline-abilities)     echo 3 ;;
    long-loop)              echo 1 ;;
    long-loop-baseline)     echo 1 ;;
    code-mode)              echo 1 ;;
    code-mode-baseline)     echo 1 ;;
    design-artifacts)          echo 1 ;;
    design-artifacts-baseline) echo 1 ;;
    *) echo "FAIL: unknown suite $1" >&2; exit 1 ;;
  esac
}

# Globals populated by assemble_suite; reused by run_suite/eval_suite.
discovery_run_dir=""
invocation_run_dir=""
baseline_run_dir=""
invocation_phases_run_dir=""
baseline_phases_run_dir=""
invocation_abilities_run_dir=""
baseline_abilities_run_dir=""
long_loop_run_dir=""
long_loop_baseline_run_dir=""
code_mode_run_dir=""
code_mode_baseline_run_dir=""
design_artifacts_run_dir=""
design_artifacts_baseline_run_dir=""

set_run_dir() {
  case "$1" in
    discovery)              discovery_run_dir="$2" ;;
    invocation)             invocation_run_dir="$2" ;;
    baseline)               baseline_run_dir="$2" ;;
    invocation-phases)      invocation_phases_run_dir="$2" ;;
    baseline-phases)        baseline_phases_run_dir="$2" ;;
    invocation-abilities)   invocation_abilities_run_dir="$2" ;;
    baseline-abilities)     baseline_abilities_run_dir="$2" ;;
    long-loop)              long_loop_run_dir="$2" ;;
    long-loop-baseline)     long_loop_baseline_run_dir="$2" ;;
    code-mode)              code_mode_run_dir="$2" ;;
    code-mode-baseline)     code_mode_baseline_run_dir="$2" ;;
    design-artifacts)          design_artifacts_run_dir="$2" ;;
    design-artifacts-baseline) design_artifacts_baseline_run_dir="$2" ;;
  esac
}

get_run_dir() {
  case "$1" in
    discovery)              printf '%s\n' "${discovery_run_dir}" ;;
    invocation)             printf '%s\n' "${invocation_run_dir}" ;;
    baseline)               printf '%s\n' "${baseline_run_dir}" ;;
    invocation-phases)      printf '%s\n' "${invocation_phases_run_dir}" ;;
    baseline-phases)        printf '%s\n' "${baseline_phases_run_dir}" ;;
    invocation-abilities)   printf '%s\n' "${invocation_abilities_run_dir}" ;;
    baseline-abilities)     printf '%s\n' "${baseline_abilities_run_dir}" ;;
    long-loop)              printf '%s\n' "${long_loop_run_dir}" ;;
    long-loop-baseline)     printf '%s\n' "${long_loop_baseline_run_dir}" ;;
    code-mode)              printf '%s\n' "${code_mode_run_dir}" ;;
    code-mode-baseline)     printf '%s\n' "${code_mode_baseline_run_dir}" ;;
    design-artifacts)          printf '%s\n' "${design_artifacts_run_dir}" ;;
    design-artifacts-baseline) printf '%s\n' "${design_artifacts_baseline_run_dir}" ;;
  esac
}

assemble_suite() {
  local suite="$1"
  "${AILLY_BIN}" -p "${project_dir}" assemble "${suite}"

  shopt -s nullglob
  local files=("${project_dir}/runs"/*-"${suite}"/*.yaml)
  shopt -u nullglob

  if [[ ${#files[@]} -eq 0 ]]; then
    echo "FAIL: ailly assemble ${suite} produced no conversation files under ${project_dir}/runs/" >&2
    exit 1
  fi

  local expected
  expected="$(expected_count "${suite}")"
  if [[ ${#files[@]} -ne ${expected} ]]; then
    echo "FAIL: ailly assemble ${suite} produced ${#files[@]} conversation file(s); expected ${expected}." >&2
    exit 1
  fi

  echo "OK: ailly assemble ${suite} produced ${#files[@]} conversation file(s):"
  local f
  for f in "${files[@]}"; do
    echo "  ${f#"${repo_root}/"}"
  done

  set_run_dir "${suite}" "$(dirname "${files[0]}")"
}

# --- CUJ 1: assemble (all suites) --------------------------------------

assemble_suite discovery
assemble_suite baseline
assemble_suite invocation
# The phase and ability pairs (modes/abilities reached through the coordinator, not matrix
# skills) mirror the coordinator pair. The `*-baseline`/`*-invocation` globs are suffix-
# anchored by the trailing `/`, so they do not pick up the `*-baseline-phases` /
# `*-invocation-phases` / `*-baseline-abilities` / `*-invocation-abilities` dirs.
assemble_suite baseline-phases
assemble_suite invocation-phases
assemble_suite baseline-abilities
assemble_suite invocation-abilities
# long-loop is a single-conversation pair (a mode of ailly, not a matrix skill).
# Assembled after baseline so the `*-baseline` glob never picks up the
# `*-long-loop-baseline` dir.
assemble_suite long-loop-baseline
assemble_suite long-loop
# code-mode is a single-conversation pair (a mode of ailly, not a matrix
# skill, same shape as long-loop). Assembled after long-loop so the
# suffix-anchored `runs/*-baseline/` glob never picks up the
# `*-code-mode-baseline` dir.
assemble_suite code-mode-baseline
assemble_suite code-mode
# design-artifacts is a single-conversation pair (design phase reference's Open
# Artifact Decisions section; cannot ride the invocation-phases matrix, which
# loads exactly one design prompt per case). Assembled after the plain
# `baseline` suite so the suffix-anchored `runs/*-baseline/` glob does not pick
# up the `*-design-artifacts-baseline` dir (same reason long-loop-baseline
# assembles late).
assemble_suite design-artifacts-baseline
assemble_suite design-artifacts

# --- CUJ 2: run (all suites, gated on credentials) ---------------------

if [[ -z "${ANTHROPIC_API_KEY:-}" && ! -f "${project_dir}/.env" ]]; then
  echo "FAIL: ailly run requires a live model. Set ANTHROPIC_API_KEY in the shell or drop a ${project_dir#"${repo_root}/"}/.env file." >&2
  echo "      The live half exercises the model and the falsification gate; there is no assemble-only success path." >&2
  exit 1
fi

# Asserts that every assembled conversation file under the suite's run_dir has a
# filled assistant turn.
assert_filled() {
  local suite="$1"
  local run_dir
  run_dir="$(get_run_dir "${suite}")"

  shopt -s nullglob
  local files=("${run_dir}"/*.yaml)
  shopt -u nullglob

  local unfilled=()
  local f
  for f in "${files[@]}"; do
    if awk '
      BEGIN { in_doc = 0; role = ""; has_body = 0 }
      /^---[[:space:]]*$/ {
        if (in_doc && role == "assistant" && has_body == 0) { print FILENAME; exit }
        in_doc = 1; role = ""; has_body = 0; next
      }
      /^role:[[:space:]]*assistant[[:space:]]*$/ { role = "assistant"; next }
      /^(body|content):/ { has_body = 1; next }
      END {
        if (in_doc && role == "assistant" && has_body == 0) { print FILENAME }
      }
    ' "${f}" | grep -q .; then
      unfilled+=("${f}")
    fi
  done

  if [[ ${#unfilled[@]} -gt 0 ]]; then
    echo "FAIL: ailly run ${suite} left ${#unfilled[@]} conversation(s) with a blank assistant:" >&2
    local u
    for u in "${unfilled[@]}"; do
      echo "  ${u#"${repo_root}/"}" >&2
    done
    exit 1
  fi

  echo "OK: ailly run ${suite} filled the assistant slot in all ${#files[@]} conversation file(s)."
}

run_suite() {
  local suite="$1"
  local run_dir
  run_dir="$(get_run_dir "${suite}")"
  "${AILLY_BIN}" -p "${project_dir}" run "${run_dir}"
  assert_filled "${suite}"
}

run_suite discovery
run_suite baseline
run_suite invocation
run_suite baseline-phases
run_suite invocation-phases
run_suite baseline-abilities
run_suite invocation-abilities
run_suite long-loop-baseline
run_suite long-loop
run_suite code-mode-baseline
run_suite code-mode
run_suite design-artifacts-baseline
run_suite design-artifacts

# --- CUJ 3: eval (all suites) ------------------------------------------

eval_suite() {
  local suite="$1"
  local run_dir
  run_dir="$(get_run_dir "${suite}")"
  local run_id
  run_id="$(basename "${run_dir}")"
  local report="${project_dir}/evals/reports/${run_id}.json"

  # Allow assertion failures without aborting; the report step aggregates results.
  "${AILLY_BIN}" -p "${project_dir}" eval "${suite}" --over "${run_dir}" || true

  if [[ ! -f "${report}" ]]; then
    echo "FAIL: ailly eval ${suite} did not write a report at ${report#"${repo_root}/"}" >&2
    exit 1
  fi

  python3 - "${suite}" "${report}" <<'PY'
import json
import sys

suite, report_path = sys.argv[1], sys.argv[2]
with open(report_path, encoding="utf-8") as fh:
    data = json.load(fh)
totals = data["totals"]["assertions"]
print(
    f"eval {suite}: "
    f"passed={totals['passed']} "
    f"failed={totals['failed']} "
    f"deferred={totals['deferred']} "
    f"malformed={totals['malformed']} "
    f"errored={totals.get('errored', 0)}"
)
PY

  echo "OK: ailly eval ${suite} wrote ${report#"${repo_root}/"}"
}

eval_suite discovery
eval_suite baseline
eval_suite invocation
eval_suite baseline-phases
eval_suite invocation-phases
eval_suite baseline-abilities
eval_suite invocation-abilities
eval_suite long-loop-baseline
eval_suite long-loop
eval_suite code-mode-baseline
eval_suite code-mode
eval_suite design-artifacts-baseline
eval_suite design-artifacts

# --- CUJ 4: report ----------------------------------------------------------

# Single-eval markdown summary for the discovery suite.
report_discovery() {
  local run_id
  run_id="$(basename "${discovery_run_dir}")"
  "${AILLY_BIN}" -p "${project_dir}" report "${run_id}"

  local report_md="${project_dir}/evals/reports/${run_id}-report.md"
  if [[ ! -f "${report_md}" ]]; then
    echo "FAIL: ailly report ${run_id} did not write ${report_md#"${repo_root}/"}" >&2
    exit 1
  fi
  echo "OK: ailly report wrote ${report_md#"${repo_root}/"}"
}

# Comparison report: arm-a (no skill) vs arm-b (skill loaded). Reused for both
# the baseline-vs-invocation matrix and the long-loop pair, so the falsification
# gate (improved>0, regressed==0) is defined once.
#   report_comparison <arm_a_run_dir> <arm_b_run_dir> <label_a> <label_b>
report_comparison() {
  local arm_a_dir="$1" arm_b_dir="$2" label_a="$3" label_b="$4"
  local run_id_a run_id_b
  run_id_a="$(basename "${arm_a_dir}")"
  run_id_b="$(basename "${arm_b_dir}")"
  "${AILLY_BIN}" -p "${project_dir}" report "${run_id_a}" "${run_id_b}" \
    --label-a "${label_a}" --label-b "${label_b}"

  local stem="${run_id_a}-vs-${run_id_b}"
  local comparison_json="${project_dir}/evals/reports/${stem}.json"
  local comparison_md="${project_dir}/evals/reports/${stem}.md"

  if [[ ! -f "${comparison_json}" ]]; then
    echo "FAIL: ailly report comparison JSON not written at ${comparison_json#"${repo_root}/"}" >&2
    exit 1
  fi
  if [[ ! -f "${comparison_md}" ]]; then
    echo "FAIL: ailly report comparison markdown not written at ${comparison_md#"${repo_root}/"}" >&2
    exit 1
  fi

  # Falsification gate: the invocation arm (skill loaded) must pass assertions
  # the baseline arm (no skill) fails -- improved > 0 -- and must never make a
  # passing baseline case fail -- regressed == 0. A checker too lenient to fail
  # baseline output yields improved == 0 and fails CI here.
  python3 - "${run_id_a}" "${run_id_b}" "${comparison_json}" <<'PY'
import json, sys
id_a, id_b, path = sys.argv[1], sys.argv[2], sys.argv[3]
with open(path, encoding="utf-8") as fh:
    data = json.load(fh)
t = data["totals"]
print(
    f"report {id_a} vs {id_b}: "
    f"improved={t['improved']} "
    f"regressed={t['regressed']} "
    f"unchanged_pass={t['unchanged_pass']} "
    f"unchanged_fail={t['unchanged_fail']}"
)
errors = []
if t["improved"] <= 0:
    errors.append(
        f"improved={t['improved']} (expected > 0): the invocation arm passed no "
        "assertion the baseline arm failed; the checkers are too lenient to "
        "falsify un-skilled output, so the falsification claim is vacuous"
    )
if t["regressed"] != 0:
    errors.append(
        f"regressed={t['regressed']} (expected 0): loading the skill made a "
        "passing baseline case fail"
    )
if errors:
    for e in errors:
        print(f"FAIL: {e}", file=sys.stderr)
    sys.exit(1)
PY

  echo "OK: ailly report wrote ${comparison_json#"${repo_root}/"} and ${comparison_md#"${repo_root}/"} (improved>0, regressed==0)"
}

report_discovery
report_comparison "${baseline_run_dir}" "${invocation_run_dir}" baseline invocation
report_comparison "${baseline_phases_run_dir}" "${invocation_phases_run_dir}" baseline-phases invocation-phases
report_comparison "${baseline_abilities_run_dir}" "${invocation_abilities_run_dir}" baseline-abilities invocation-abilities
report_comparison "${long_loop_baseline_run_dir}" "${long_loop_run_dir}" long-loop-baseline long-loop
report_comparison "${code_mode_baseline_run_dir}" "${code_mode_run_dir}" code-mode-baseline code-mode
report_comparison "${design_artifacts_baseline_run_dir}" "${design_artifacts_run_dir}" design-artifacts-baseline design-artifacts
