#!/usr/bin/env bash
# CI driver for the general/e2e skill-eval harness.
#
# Exercises the full operator journey across three suites (discovery,
# invocation, baseline):
#   0. refresh   -- vendor the live skills under context/ and regenerate
#      disclosure.md, so the eval scores the current skill text. Also run a
#      falsification grep: neither the coding-agent AGENTS.md nor profile.md
#      may name a general:<skill> identifier, or the baseline arm is not
#      skill-free.
#   1. assemble  -- always runs; asserts N conversation files land under
#      runs/<id>/ for each suite (discovery=5, invocation=5, baseline=5).
#   2. run       -- requires a live model. Asserts every conversation's
#      trailing blank assistant slot was filled. With neither ANTHROPIC_API_KEY
#      nor a project .env the script hard-fails: there is no assemble-only
#      success path, so the live half (and the falsification gate) always runs.
#   3. eval      -- asserts the per-run report landed at
#      evals/reports/<run-id>.json and prints a summary line per suite.
#   4. report    -- single-run discovery summary, then the baseline-vs-
#      invocation comparison whose falsification gate (improved>0, regressed==0)
#      is the headline signal that the skills earn their place.
#
# Ailly is invoked through ${AILLY} (default: the locally built ailly_two debug
# binary), overridable to a packaged `ailly` in CI.

set -euo pipefail

project_dir="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"   # general/e2e
repo_root="$(cd "${project_dir}/../.." && pwd)"               # repo clone root

AILLY="${AILLY:-/Users/david.souther/devel/davidsouther/ailly/ailly_two/target/debug/ailly_two}"

cd "${repo_root}"

rm -rf "${project_dir}/runs" "${project_dir}/evals/reports"

# --- CUJ 0: refresh vendored context + disclosure, falsification grep --------

bash "${project_dir}/evals/scripts/vendor.sh"
bash "${project_dir}/evals/scripts/gen_disclosure.sh"

# The baseline arm shares exactly two files with the invocation arm:
# context/AGENTS.md (vendored from e2e/AGENTS.md) and profile.md. Neither may
# name a general:<skill> identifier, or "no skill loaded" is a false claim.
if grep -Eq 'general:(conversation|dispatching-parallel-agents|review|using-general|writing-paired-skills|writing-pattern-skills|writing-skills)' \
     "${repo_root}/e2e/AGENTS.md" "${project_dir}/profile.md"; then
  echo "FAIL: e2e/AGENTS.md or profile.md names a general:<skill> identifier" >&2
  exit 1
fi
echo "OK: falsification grep clean (no general:<skill> identifier in AGENTS.md / profile.md)"

expected_count() {
  case "$1" in
    discovery)  echo 5 ;;
    invocation) echo 5 ;;
    baseline)   echo 5 ;;
    *) echo "FAIL: unknown suite $1" >&2; exit 1 ;;
  esac
}

discovery_run_dir=""
invocation_run_dir=""
baseline_run_dir=""

set_run_dir() {
  case "$1" in
    discovery)  discovery_run_dir="$2" ;;
    invocation) invocation_run_dir="$2" ;;
    baseline)   baseline_run_dir="$2" ;;
  esac
}

get_run_dir() {
  case "$1" in
    discovery)  printf '%s\n' "${discovery_run_dir}" ;;
    invocation) printf '%s\n' "${invocation_run_dir}" ;;
    baseline)   printf '%s\n' "${baseline_run_dir}" ;;
  esac
}

# --- CUJ 1: assemble --------------------------------------------------------

assemble_suite() {
  local suite="$1"
  ${AILLY} -p "${project_dir}" assemble "${suite}"

  shopt -s nullglob
  local files=("${project_dir}/runs"/*-"${suite}"/*.yaml)
  shopt -u nullglob

  if [[ ${#files[@]} -eq 0 ]]; then
    echo "FAIL: assemble ${suite} produced no conversation files under ${project_dir}/runs/" >&2
    exit 1
  fi

  local expected
  expected="$(expected_count "${suite}")"
  if [[ ${#files[@]} -ne ${expected} ]]; then
    echo "FAIL: assemble ${suite} produced ${#files[@]} conversation file(s); expected ${expected}." >&2
    exit 1
  fi

  echo "OK: assemble ${suite} produced ${#files[@]} conversation file(s)."
  set_run_dir "${suite}" "$(dirname "${files[0]}")"
}

assemble_suite discovery
assemble_suite baseline
assemble_suite invocation

# --- CUJ 2: run (gated on credentials) --------------------------------------

if [[ -z "${ANTHROPIC_API_KEY:-}" && ! -f "${project_dir}/.env" ]]; then
  echo "FAIL: run requires a live model. Set ANTHROPIC_API_KEY or drop a ${project_dir#"${repo_root}/"}/.env file." >&2
  exit 1
fi

assert_filled() {
  local suite="$1" run_dir
  run_dir="$(get_run_dir "${suite}")"

  shopt -s nullglob
  local files=("${run_dir}"/*.yaml)
  shopt -u nullglob

  local unfilled=() f
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
    echo "FAIL: run ${suite} left ${#unfilled[@]} conversation(s) with a blank assistant:" >&2
    local u
    for u in "${unfilled[@]}"; do echo "  ${u#"${repo_root}/"}" >&2; done
    exit 1
  fi
  echo "OK: run ${suite} filled the assistant slot in all ${#files[@]} conversation file(s)."
}

run_suite() {
  local suite="$1" run_dir
  run_dir="$(get_run_dir "${suite}")"
  ${AILLY} -p "${project_dir}" run "${run_dir}"
  assert_filled "${suite}"
}

run_suite discovery
run_suite baseline
run_suite invocation

# --- CUJ 3: eval ------------------------------------------------------------

eval_suite() {
  local suite="$1" run_dir run_id report
  run_dir="$(get_run_dir "${suite}")"
  run_id="$(basename "${run_dir}")"
  report="${project_dir}/evals/reports/${run_id}.json"

  ${AILLY} -p "${project_dir}" eval "${suite}" --over "${run_dir}" || true

  if [[ ! -f "${report}" ]]; then
    echo "FAIL: eval ${suite} did not write a report at ${report#"${repo_root}/"}" >&2
    exit 1
  fi

  python3 - "${suite}" "${report}" <<'PY'
import json, sys
suite, report_path = sys.argv[1], sys.argv[2]
with open(report_path, encoding="utf-8") as fh:
    data = json.load(fh)
totals = data["totals"]["assertions"]
print(
    f"eval {suite}: passed={totals['passed']} failed={totals['failed']} "
    f"deferred={totals['deferred']} malformed={totals['malformed']} "
    f"errored={totals.get('errored', 0)}"
)
PY
  echo "OK: eval ${suite} wrote ${report#"${repo_root}/"}"
}

eval_suite discovery
eval_suite baseline
eval_suite invocation

# --- CUJ 4: report ----------------------------------------------------------

report_discovery() {
  local run_id report_md
  run_id="$(basename "${discovery_run_dir}")"
  ${AILLY} -p "${project_dir}" report "${run_id}"
  report_md="${project_dir}/evals/reports/${run_id}-report.md"
  if [[ ! -f "${report_md}" ]]; then
    echo "FAIL: report ${run_id} did not write ${report_md#"${repo_root}/"}" >&2
    exit 1
  fi
  echo "OK: report wrote ${report_md#"${repo_root}/"}"
}

report_comparison() {
  local run_id_a run_id_b stem comparison_json comparison_md
  run_id_a="$(basename "${baseline_run_dir}")"
  run_id_b="$(basename "${invocation_run_dir}")"
  ${AILLY} -p "${project_dir}" report "${run_id_a}" "${run_id_b}" --label-a baseline --label-b invocation

  stem="${run_id_a}-vs-${run_id_b}"
  comparison_json="${project_dir}/evals/reports/${stem}.json"
  comparison_md="${project_dir}/evals/reports/${stem}.md"

  if [[ ! -f "${comparison_json}" || ! -f "${comparison_md}" ]]; then
    echo "FAIL: comparison report not written at ${comparison_json#"${repo_root}/"}" >&2
    exit 1
  fi

  # Falsification gate: the invocation arm must pass assertions the baseline
  # fails (improved > 0) and must break nothing the baseline passed
  # (regressed == 0). A checker too lenient to fail un-skilled output yields
  # improved == 0 and fails CI here, making the falsification claim non-vacuous.
  python3 - "${run_id_a}" "${run_id_b}" "${comparison_json}" <<'PY'
import json, sys
id_a, id_b, path = sys.argv[1], sys.argv[2], sys.argv[3]
with open(path, encoding="utf-8") as fh:
    data = json.load(fh)
t = data["totals"]
print(
    f"report {id_a} vs {id_b}: improved={t['improved']} regressed={t['regressed']} "
    f"unchanged_pass={t['unchanged_pass']} unchanged_fail={t['unchanged_fail']}"
)
errors = []
if t["improved"] <= 0:
    errors.append(f"improved={t['improved']} (expected > 0): the invocation arm passed "
                  "no assertion the baseline failed; the checkers are too lenient")
if t["regressed"] != 0:
    errors.append(f"regressed={t['regressed']} (expected 0): loading the skill made a "
                  "passing baseline case fail")
if errors:
    for e in errors: print(f"FAIL: {e}", file=sys.stderr)
    sys.exit(1)
PY
  echo "OK: comparison wrote ${comparison_md#"${repo_root}/"} (improved>0, regressed==0)"
}

report_discovery
report_comparison

echo "ci.sh: all suites assembled, ran, evaluated, and the falsification gate held."
