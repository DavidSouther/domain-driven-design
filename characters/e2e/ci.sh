#!/usr/bin/env bash
# CI driver / feature test for the characters/e2e regression harness.
#
# Exercises the Invocation + baseline profile (no discovery axis) against the
# live ../skills/<name>/SKILL.md tree, reached through the in-root symlinks
# `base -> ../../e2e` and `skills -> ../skills` (ailly clamps `..` to the
# project root but follows a symlink inside it):
#   0. falsification grep -- asserts the two baseline-arm files (base/AGENTS.md,
#      profile.md) leak no `characters:voice-*` identifier, so the baseline arm
#      cannot pass by reading the answer out of its own prefix.
#   1. `ailly assemble <suite>` -- asserts 4 conversation files land under
#      runs/<id>/ for each suite (baseline, invocation).
#   2. `ailly run runs/<id>/`   -- requires a live model. Asserts every
#      conversation's trailing blank assistant slot has been filled. With
#      neither ANTHROPIC_API_KEY nor a project .env the script hard-fails:
#      there is no assemble-only success path.
#   3. `ailly eval <suite> --over runs/<id>/` -- asserts the per-run report
#      landed and prints a tolerance summary per suite.
#   4. `ailly report <baseline-id> <invocation-id>` -- the comparison report,
#      gated on improved>0 && regressed==0 (the falsification gap).
#
# `ailly` is taken from $AILLY (defaults to `ailly` on $PATH). The built binary
# in this environment is named `ailly_two`; point $AILLY at it, e.g.
#   AILLY=/path/to/ailly_two/target/release/ailly_two ./ci.sh

set -euo pipefail

project_dir="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
repo_root="$(cd "${project_dir}/../.." && pwd)"
AILLY="${AILLY:-ailly}"

cd "${repo_root}"

rm -rf "${project_dir}/runs" "${project_dir}/evals/reports"

# --- CUJ 0: falsification grep ----------------------------------------------
# Neither baseline-arm file may name a skill under test by its plugin-prefixed
# identifier, or the baseline arm would be reading the answer out of its prefix.
grep_leak() {
  local rel="$1"
  local abs="${project_dir}/${rel}"
  if [[ -f "${abs}" ]] && grep -Eq 'characters:voice-(jefri|jacki|rupert|ailly)' "${abs}"; then
    echo "FAIL: ${rel} leaks a 'characters:voice-*' identifier; the baseline arm leaks the answer." >&2
    grep -nE 'characters:voice-(jefri|jacki|rupert|ailly)' "${abs}" >&2
    exit 1
  fi
}
grep_leak "base/AGENTS.md"
grep_leak "profile.md"
echo "OK: no 'characters:voice-*' identifier leaks into the baseline-arm files."

expected_count() {
  case "$1" in
    invocation) echo 4 ;;
    baseline)   echo 4 ;;
    *) echo "FAIL: unknown suite $1" >&2; exit 1 ;;
  esac
}

# Globals populated by assemble_suite; reused by run_suite/eval_suite.
invocation_run_dir=""
baseline_run_dir=""

set_run_dir() {
  case "$1" in
    invocation) invocation_run_dir="$2" ;;
    baseline)   baseline_run_dir="$2" ;;
  esac
}

get_run_dir() {
  case "$1" in
    invocation) printf '%s\n' "${invocation_run_dir}" ;;
    baseline)   printf '%s\n' "${baseline_run_dir}" ;;
  esac
}

assemble_suite() {
  local suite="$1"
  ${AILLY} -p "${project_dir}" assemble "${suite}"

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

# --- CUJ 1: assemble (both suites) ------------------------------------------

assemble_suite baseline
assemble_suite invocation

# --- CUJ 2: run (both suites, gated on credentials) -------------------------

if [[ -z "${ANTHROPIC_API_KEY:-}" && ! -f "${project_dir}/.env" ]]; then
  echo "FAIL: ailly run requires a live model. Set ANTHROPIC_API_KEY in the shell or drop a ${project_dir#"${repo_root}/"}/.env file." >&2
  echo "      The live half exercises the model and the falsification gate; there is no assemble-only success path." >&2
  exit 1
fi

# Asserts that every assembled conversation file under the suite's
# run_dir has a filled assistant turn.
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
  ${AILLY} -p "${project_dir}" run "${run_dir}"
  assert_filled "${suite}"
}

run_suite baseline
run_suite invocation

# --- CUJ 3: eval (both suites) ----------------------------------------------

eval_suite() {
  local suite="$1"
  local run_dir
  run_dir="$(get_run_dir "${suite}")"
  local run_id
  run_id="$(basename "${run_dir}")"
  local report="${project_dir}/evals/reports/${run_id}.json"

  # Allow assertion failures without aborting; the report step aggregates results.
  ${AILLY} -p "${project_dir}" eval "${suite}" --over "${run_dir}" || true

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

eval_suite baseline
eval_suite invocation

# --- CUJ 4: comparison report (falsification gate) --------------------------

# Comparison report: baseline (arm-a) vs invocation (arm-b).
report_comparison() {
  local run_id_a run_id_b
  run_id_a="$(basename "${baseline_run_dir}")"
  run_id_b="$(basename "${invocation_run_dir}")"
  ${AILLY} -p "${project_dir}" report "${run_id_a}" "${run_id_b}"

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
  # the baseline arm (no skill) fails -- improved > 0 -- and the skill must never
  # make a passing baseline case fail -- regressed == 0.
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
        "assertion the baseline arm failed; the judges are too lenient to "
        "falsify un-voiced output, so the falsification claim is vacuous"
    )
if t["regressed"] != 0:
    errors.append(
        f"regressed={t['regressed']} (expected 0): loading the voice skill made a "
        "passing baseline case fail"
    )
if errors:
    for e in errors:
        print(f"FAIL: {e}", file=sys.stderr)
    sys.exit(1)
PY

  echo "OK: ailly report wrote ${comparison_json#"${repo_root}/"} and ${comparison_md#"${repo_root}/"} (improved>0, regressed==0)"
}

report_comparison
