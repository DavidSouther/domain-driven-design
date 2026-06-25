#!/usr/bin/env bash
# CI driver for the patterns/e2e regression harness.
#
# Exercises both halves of the operator's journey across three suites
# (discovery, baseline, invocation):
#   0. Falsification grep -- pre-flight. Neither the shared AGENTS.md nor
#      profile.md may contain a `patterns:<skill>` identifier; a leak there
#      would let the baseline arm see the answer. Hard-fails on any match.
#   1. `ailly assemble <suite>` -- always runs; asserts N conversation files
#      land under runs/<id>/ for each suite (discovery=16, baseline=16,
#      invocation=16 — all 16 testable patterns skills).
#   2. `ailly run runs/<id>/` -- requires a live model. Asserts every
#      conversation file's trailing blank assistant slot was filled. With
#      neither ANTHROPIC_API_KEY nor a project .env the script hard-fails:
#      there is no assemble-only success path, so the live half (and the
#      falsification gate below) always runs.
#   3. `ailly eval <suite> --over runs/<id>/` -- runs after `ailly run`;
#      asserts the per-run report landed at evals/reports/<run-id>.json and
#      prints a deferred-tolerance summary line per suite.
#   4. `ailly report` -- single-run markdown for discovery, then the
#      baseline-vs-invocation comparison whose four buckets feed the
#      falsification gate: improved > 0 and regressed == 0.
#
# The ailly CLI is invoked as `${AILLY:-ailly}`: it expects `ailly` on $PATH,
# or an explicit binary via `AILLY=/path/to/ailly_two ./ci.sh`.

set -euo pipefail

AILLY="${AILLY:-ailly}"

project_dir="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
repo_root="$(cd "${project_dir}/../.." && pwd)"

cd "${repo_root}"

rm -rf "${project_dir}/runs" "${project_dir}/evals/reports"

# --- CUJ 0: falsification grep ----------------------------------------------
# Fail if the coding-agent constitution or the harness profile leaks a
# plugin-prefixed skill identifier into the baseline arm's context. Both are the
# in-project files the baseline prefix loads (AGENTS.md is a symlink to the shared
# e2e/AGENTS.md; grep -L follows it).
for f in "${project_dir}/AGENTS.md" "${project_dir}/profile.md"; do
  if grep -E 'patterns:[a-z][a-z-]+' "${f}" >/dev/null 2>&1; then
    echo "FAIL: ${f#"${repo_root}/"} contains a 'patterns:*' identifier; the baseline arm leaks the answer." >&2
    exit 1
  fi
  # Post-consolidation: the discovery answer is the bare pattern name AND its
  # `references/patterns/<name>.md` path. The leaf identifiers are retired, so the
  # reference-path form is the post-consolidation answer token; forbid it leaking into
  # the baseline arm's context too. Bare pattern names are NOT grepped (reviewer
  # decision 2: they false-positive on prose like "builder"/"repository"); the
  # falsification strength is carried on the assertion side, which requires BOTH the
  # name and the path that the baseline arm cannot emit.
  if grep -E 'references/patterns/[a-z][a-z-]+' "${f}" >/dev/null 2>&1; then
    echo "FAIL: ${f#"${repo_root}/"} contains a 'references/patterns/<name>' path; the baseline arm leaks the answer." >&2
    exit 1
  fi
done
echo "OK: falsification grep clean (no 'patterns:*' identifier or 'references/patterns/<name>' path in AGENTS.md or profile.md)."

expected_count() {
  case "$1" in
    discovery)  echo 16 ;;
    invocation) echo 16 ;;
    baseline)   echo 16 ;;
    *) echo "FAIL: unknown suite $1" >&2; exit 1 ;;
  esac
}

# Globals populated by assemble_suite; reused by run_suite/eval_suite.
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

assemble_suite() {
  local suite="$1"
  "${AILLY}" -p "${project_dir}" assemble "${suite}"

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

# --- CUJ 1: assemble (all suites) -------------------------------------------

assemble_suite discovery
assemble_suite baseline
assemble_suite invocation

# --- CUJ 2: run (all suites, gated on credentials) --------------------------

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
  "${AILLY}" -p "${project_dir}" run "${run_dir}"
  assert_filled "${suite}"
}

run_suite discovery
run_suite baseline
run_suite invocation

# --- CUJ 3: eval (all suites) -----------------------------------------------

eval_suite() {
  local suite="$1"
  local run_dir
  run_dir="$(get_run_dir "${suite}")"
  local run_id
  run_id="$(basename "${run_dir}")"
  local report="${project_dir}/evals/reports/${run_id}.json"

  # Allow assertion failures without aborting; the report step aggregates results.
  "${AILLY}" -p "${project_dir}" eval "${suite}" --over "${run_dir}" || true

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

# --- CUJ 4: report ----------------------------------------------------------

# Single-eval markdown summary for the discovery suite.
report_discovery() {
  local run_id
  run_id="$(basename "${discovery_run_dir}")"
  "${AILLY}" -p "${project_dir}" report "${run_id}"

  local report_md="${project_dir}/evals/reports/${run_id}-report.md"
  if [[ ! -f "${report_md}" ]]; then
    echo "FAIL: ailly report ${run_id} did not write ${report_md#"${repo_root}/"}" >&2
    exit 1
  fi
  echo "OK: ailly report wrote ${report_md#"${repo_root}/"}"
}

# Comparison report: baseline (arm-a) vs invocation (arm-b).
report_comparison() {
  local run_id_a run_id_b
  run_id_a="$(basename "${baseline_run_dir}")"
  run_id_b="$(basename "${invocation_run_dir}")"
  "${AILLY}" -p "${project_dir}" report "${run_id_a}" "${run_id_b}"

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

  # Falsification gate: the invocation arm (skill loaded) must pass assertions the
  # baseline arm (no skill) fails -- improved > 0 -- and the skill must never make a
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
report_comparison
