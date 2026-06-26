#!/usr/bin/env bash
# CI driver for the research-eval project.
#
# Exercises the operator's four-subcommand journey across three suites
# (discovery, baseline, invocation):
#   1. assemble <suite> -- always runs (reads files only); asserts the
#      expected conversation count lands under runs/<id>-<suite>/.
#   2. run <run-dir>    -- requires a live model; asserts every trailing blank
#      assistant slot was filled. Gated on ANTHROPIC_API_KEY or a project .env.
#   3. eval <suite>     -- scores the conversations; asserts the per-run report
#      landed at evals/reports/<run-id>.json and prints a tolerance summary.
#   4. report           -- a single-run summary for discovery, then a
#      baseline-vs-invocation comparison that surfaces the four falsification
#      buckets. The falsification gate requires improved > 0 and regressed == 0.
#
# The harness fills one assistant turn per conversation with no live tool
# execution, so there is no per-case credential gating: every case is a single
# text completion regardless of which external transports are configured. See
# AGENTS.md ("A note on transports").
#
# Override the ailly binary with AILLY_BIN, or its repo with AILLY_HOME.
# Kept POSIX/bash-3.2 compatible (no associative arrays) so it runs on a stock
# macOS /bin/bash.

set -euo pipefail

project_dir="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "${project_dir}"

AILLY_HOME="${AILLY_HOME:-/Users/david.souther/devel/davidsouther/ailly/ailly_two}"
AILLY_BIN="${AILLY_BIN:-${AILLY_HOME}/target/release/ailly_two}"
if [[ ! -x "${AILLY_BIN}" ]]; then
  echo "ailly binary not found at ${AILLY_BIN}; building release…"
  ( cd "${AILLY_HOME}" && cargo build --release )
fi
AILLY=("${AILLY_BIN}" -p .)

rm -rf runs evals/reports

# --- Falsification grep ------------------------------------------------------
# The baseline-shared prefix (AGENTS.md, context/AGENTS.md) must never name a
# research:<id>; leaking one would hand the baseline arm the answer and make the
# falsification gap vacuous.
for f in AGENTS.md context/AGENTS.md; do
  if grep -Eq 'research:[a-z-]+' "${f}"; then
    echo "FAIL: ${f} leaks a 'research:<id>' into the baseline-shared prefix." >&2
    exit 1
  fi
  # Post-consolidation (Feature C): the five setup-only configuring-* descriptions were
  # deferred to references; the discovery answer for a configuring case is now the
  # `references/configuring/<name>.md` reference path the using-research bootstrap teaches.
  # Forbid that path leaking into the baseline-shared prefix too, so the baseline arm cannot
  # see the answer through the renamed token. (Bare source names are not grepped; the
  # positive assertion requires the reference path the baseline cannot emit.)
  if grep -Eq 'references/configuring/[a-z-]+' "${f}"; then
    echo "FAIL: ${f} leaks a 'references/configuring/<name>' path into the baseline-shared prefix." >&2
    exit 1
  fi
done
echo "OK: no 'research:<id>' identifier or 'references/configuring/<name>' path leak in the baseline-shared prefix."

# --- CUJ 1: assemble ---------------------------------------------------------

# Post-consolidation (Feature C): the discovery matrix still sweeps 10 cases (the two
# configuring-*-trigger cases were re-expressed to assert the relocated reference path, not
# dropped). The invocation/baseline matrices dropped the two configuring cases — those
# skills no longer have a standalone body to invoke — leaving the eight research SOURCE
# leaves, so each pair still compares same-named cases.
expected_count() {
  case "$1" in
    discovery)  echo 10 ;;
    baseline)   echo 8 ;;
    invocation) echo 8 ;;
    *) echo "FAIL: unknown suite $1" >&2; exit 1 ;;
  esac
}

# bash-3.2 has no associative arrays; carry the three run dirs as globals.
discovery_run_dir=""
baseline_run_dir=""
invocation_run_dir=""

set_run_dir() {
  case "$1" in
    discovery)  discovery_run_dir="$2" ;;
    baseline)   baseline_run_dir="$2" ;;
    invocation) invocation_run_dir="$2" ;;
  esac
}

get_run_dir() {
  case "$1" in
    discovery)  printf '%s\n' "${discovery_run_dir}" ;;
    baseline)   printf '%s\n' "${baseline_run_dir}" ;;
    invocation) printf '%s\n' "${invocation_run_dir}" ;;
  esac
}

assemble_suite() {
  local suite="$1"
  "${AILLY[@]}" assemble "${suite}" >/dev/null

  shopt -s nullglob
  local files=(runs/*-"${suite}"/*.yaml)
  shopt -u nullglob

  local expected
  expected="$(expected_count "${suite}")"
  if (( ${#files[@]} != expected )); then
    echo "FAIL: assemble ${suite} produced ${#files[@]} file(s); expected ${expected}." >&2
    exit 1
  fi

  set_run_dir "${suite}" "$(dirname "${files[0]}")"
  echo "OK: assemble ${suite} produced ${#files[@]} conversation(s) -> $(get_run_dir "${suite}")"
}

assemble_suite discovery
assemble_suite baseline
assemble_suite invocation

# --- CUJ 2: run (gated on credentials) ---------------------------------------

if [[ -z "${ANTHROPIC_API_KEY:-}" && ! -f .env ]]; then
  echo "FAIL: run/eval require a live model. Set ANTHROPIC_API_KEY or drop a .env." >&2
  exit 1
fi

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
      END { if (in_doc && role == "assistant" && has_body == 0) print FILENAME }
    ' "${f}" | grep -q .; then
      unfilled+=("${f}")
    fi
  done

  if (( ${#unfilled[@]} > 0 )); then
    echo "FAIL: run ${suite} left ${#unfilled[@]} conversation(s) blank." >&2
    printf '  %s\n' "${unfilled[@]}" >&2
    exit 1
  fi
  echo "OK: run ${suite} filled the assistant slot in all ${#files[@]} conversation(s)."
}

run_suite() {
  local suite="$1"
  "${AILLY[@]}" run "$(get_run_dir "${suite}")"
  assert_filled "${suite}"
}

run_suite discovery
run_suite baseline
run_suite invocation

# --- CUJ 3: eval -------------------------------------------------------------

eval_suite() {
  local suite="$1"
  local run_dir run_id report
  run_dir="$(get_run_dir "${suite}")"
  run_id="$(basename "${run_dir}")"
  report="evals/reports/${run_id}.json"

  # Assertion failures are expected (the baseline arm fails by design); let eval
  # exit non-zero and read the totals from the report instead of aborting.
  "${AILLY[@]}" eval "${suite}" --over "${run_dir}" || true

  if [[ ! -f "${report}" ]]; then
    echo "FAIL: eval ${suite} did not write a report at ${report}" >&2
    exit 1
  fi

  python3 - "${suite}" "${report}" <<'PY'
import json, sys
suite, path = sys.argv[1], sys.argv[2]
with open(path, encoding="utf-8") as fh:
    data = json.load(fh)
t = data["totals"]["assertions"]
print(
    f"eval {suite}: passed={t['passed']} failed={t['failed']} "
    f"deferred={t['deferred']} malformed={t['malformed']} "
    f"errored={t.get('errored', 0)}"
)
PY
  echo "OK: eval ${suite} wrote ${report}"
}

eval_suite discovery
eval_suite baseline
eval_suite invocation

# --- CUJ 4: report -----------------------------------------------------------

report_discovery() {
  local run_id md
  run_id="$(basename "$(get_run_dir discovery)")"
  "${AILLY[@]}" report "${run_id}" >/dev/null
  md="evals/reports/${run_id}-report.md"
  [[ -f "${md}" ]] || { echo "FAIL: report ${run_id} did not write ${md}" >&2; exit 1; }
  echo "OK: report wrote ${md}"
}

# Comparison: baseline (arm-a) vs invocation (arm-b). The skill body is the only
# difference, so any flipped assertion is attributable to the skill.
report_comparison() {
  local id_a id_b stem json md
  id_a="$(basename "$(get_run_dir baseline)")"
  id_b="$(basename "$(get_run_dir invocation)")"
  "${AILLY[@]}" report "${id_a}" "${id_b}" >/dev/null

  stem="${id_a}-vs-${id_b}"
  json="evals/reports/${stem}.json"
  md="evals/reports/${stem}.md"
  [[ -f "${json}" ]] || { echo "FAIL: comparison JSON not written at ${json}" >&2; exit 1; }
  [[ -f "${md}"   ]] || { echo "FAIL: comparison markdown not written at ${md}" >&2; exit 1; }

  python3 - "${id_a}" "${id_b}" "${json}" <<'PY'
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
    errors.append(
        f"improved={t['improved']} (expected > 0): the invocation arm passed no "
        "assertion the baseline failed; the checkers are too lenient to falsify "
        "un-skilled output, so the falsification claim is vacuous"
    )
if t["regressed"] != 0:
    errors.append(
        f"regressed={t['regressed']} (expected 0): loading the skill made a passing "
        "baseline assertion fail"
    )
if errors:
    for e in errors:
        print(f"FAIL: {e}", file=sys.stderr)
    sys.exit(1)
PY

  echo "OK: report wrote ${json} and ${md} (improved > 0, regressed == 0)"
}

report_discovery
report_comparison

echo "PASS: research-eval CI complete."
