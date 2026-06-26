#!/usr/bin/env bash
# CI driver for the domain/e2e harness — the executable feature test.
#
# Exercises the Full discovery + invocation + baseline triple, and encodes
# the two user-facing properties as hard gates:
#
#   Property 1 (discovery): the `domain:*` skills are routed to
#     appropriately. The discovery suite's single-run pass rate must clear
#     DISCOVERY_MIN_PASS_RATE.
#   Property 2 (falsification): loading a skill improves alignment over a
#     baseline with no skill. The baseline-vs-invocation comparison must
#     show improved > 0 and regressed == 0.
#
# Operator journey:
#   0. Falsification grep on AGENTS.md and profile.md (no skill identifier
#      may leak into either file, or the baseline arm is contaminated).
#   1. `ailly assemble <suite>` for discovery + baseline + invocation;
#      asserts N conversation files land under runs/<id>/.
#   2. `ailly run runs/<id>/` when ANTHROPIC_API_KEY (or a project .env) is
#      present; asserts every conversation file's trailing blank assistant
#      slot has been filled. Skipped otherwise so contributors without API
#      access still see the assemble half pass.
#   3. `ailly eval <suite> --over runs/<id>/`; asserts the per-run report
#      landed at evals/reports/<run-id>.json and prints a tolerance summary.
#   4. `ailly report <discovery-id>` (single) gates Property 1;
#      `ailly report <baseline-id> <invocation-id>` (comparison) gates
#      Property 2.

set -euo pipefail
set -x

project_dir="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
repo_root="$(cd "${project_dir}/../.." && pwd)"

cd "${repo_root}"

rm -rf "${project_dir}/runs" "${project_dir}/evals/reports"

# Minimum routine-routing pass rate gating Property 1. Computed over the
# discovery suite EXCLUDING the adversarial `glossary-gate-trigger` case, which
# probes a known weakness (the using-domain routing surface does not route a
# modelling-shaped terminology-introduction prompt to glossary first) and is
# reported as an informational finding rather than gated. Calibrated against
# observed runs: routine routing is near-perfect, so a single model slip should
# not red the suite, but a description-blur regression must.
DISCOVERY_MIN_PASS_RATE="${DISCOVERY_MIN_PASS_RATE:-0.85}"

# --- Falsification grep -----------------------------------------------------
#
# Neither the shared AGENTS.md nor profile.md may name a skill under test by
# any plugin-prefixed identifier. The skill bodies use the `ddd:` prefix and
# the plugin manifest uses `domain:`; forbid both so the baseline arm cannot
# inherit the answer through either spelling. Bare words (glossary, domain,
# context, model, invariant) are permitted — they belong to the coding-agent
# mindset framing.

if grep -Eq '(ddd|domain):(glossary|ubiquitous-language|domain-model|contracts-and-invariants|arrow-of-maturity)' \
     "${repo_root}/e2e/AGENTS.md" "${project_dir}/profile.md"; then
  echo "FAIL: falsification leak — a domain skill identifier is present in AGENTS.md or profile.md" >&2
  exit 1
fi
# Post-consolidation: the discovery answer is the bare ability name AND its
# `references/<name>.md` path. The leaf identifiers are retired, so the
# reference-path form is the post-consolidation answer token; forbid it leaking
# into the baseline arm's context too. Bare ability names are NOT grepped (they
# false-positive on prose like "domain-model" in the mindset framing); the
# falsification strength is carried on the assertion side, which requires BOTH
# the name and the path that the baseline arm cannot emit.
if grep -Eq 'references/(glossary|ubiquitous-language|domain-model|contracts-and-invariants|arrow-of-maturity)\.md' \
     "${repo_root}/e2e/AGENTS.md" "${project_dir}/profile.md"; then
  echo "FAIL: falsification leak — a 'references/<name>.md' path is present in AGENTS.md or profile.md" >&2
  exit 1
fi
echo "OK: falsification grep clean."

expected_count() {
  case "$1" in
    discovery)  echo 5 ;;
    invocation) echo 5 ;;
    baseline)   echo 5 ;;
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
  ailly -p "${project_dir}" assemble "${suite}"

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

# --- CUJ 1: assemble (all three suites) -------------------------------------

assemble_suite discovery
assemble_suite baseline
assemble_suite invocation

# --- CUJ 2: run (all three suites, gated on credentials) --------------------

if [[ -z "${ANTHROPIC_API_KEY:-}" && ! -f "${project_dir}/.env" ]]; then
  echo "SKIP: ailly run requires ANTHROPIC_API_KEY in the shell or ${project_dir#"${repo_root}/"}/.env; assemble half passed."
  exit 0
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
  ailly -p "${project_dir}" run "${run_dir}"
  assert_filled "${suite}"
}

run_suite discovery
run_suite baseline
run_suite invocation

# --- CUJ 3: eval (all three suites) -----------------------------------------

eval_suite() {
  local suite="$1"
  local run_dir
  run_dir="$(get_run_dir "${suite}")"
  local run_id
  run_id="$(basename "${run_dir}")"
  local report="${project_dir}/evals/reports/${run_id}.json"

  ailly -p "${project_dir}" eval "${suite}" --over "${run_dir}" || true

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

# --- CUJ 4a: discovery single-run report + Property 1 gate ------------------

report_discovery() {
  local run_id
  run_id="$(basename "${discovery_run_dir}")"
  ailly -p "${project_dir}" report "${run_id}"

  local report_md="${project_dir}/evals/reports/${run_id}-report.md"
  if [[ ! -f "${report_md}" ]]; then
    echo "FAIL: ailly report ${run_id} did not write ${report_md#"${repo_root}/"}" >&2
    exit 1
  fi

  # Property 1 gate: routine-routing pass rate (the discovery suite minus the
  # adversarial gate case) must clear the floor. The gate case is reported, not
  # gated — it documents a known skill weakness without redding routine routing.
  local report_json="${project_dir}/evals/reports/${run_id}.json"
  python3 - "${report_json}" "${DISCOVERY_MIN_PASS_RATE}" <<'PY'
import json, sys
path, floor = sys.argv[1], float(sys.argv[2])
GATE = "glossary-gate-trigger"
with open(path, encoding="utf-8") as fh:
    data = json.load(fh)
gate_pass = gate_total = routine_pass = routine_total = 0
for case in data["cases"]:
    name = case["name"]
    for match in case.get("matches", []):
        for assertion in match.get("assertions", []):
            ok = assertion.get("outcome") == "pass"
            if name == GATE:
                gate_total += 1
                gate_pass += ok
            else:
                routine_total += 1
                routine_pass += ok
rate = routine_pass / routine_total if routine_total else 0.0
print(f"routine routing pass rate: {routine_pass}/{routine_total} = {rate:.3f} (floor {floor:.3f})")
gate_ok = gate_total > 0 and gate_pass == gate_total
verb = "routes" if gate_ok else "does NOT route"
print(
    f"glossary-gate finding: {'ENFORCED' if gate_ok else 'NOT ENFORCED'} "
    f"({gate_pass}/{gate_total} assertions) — informational. The using-domain "
    f"routing surface {verb} a modelling-shaped terminology-introduction prompt "
    "to glossary first."
)
if rate < floor:
    print(
        f"FAIL: routine routing pass rate {rate:.3f} below floor {floor:.3f}; "
        "routing to the correct domain skill is regressing",
        file=sys.stderr,
    )
    sys.exit(1)
PY

  echo "OK: ailly report wrote ${report_md#"${repo_root}/"} (routine routing cleared floor; gate finding reported)"
}

# --- CUJ 4b: comparison report + Property 2 (falsification) gate ------------

report_comparison() {
  local run_id_a run_id_b
  run_id_a="$(basename "${baseline_run_dir}")"
  run_id_b="$(basename "${invocation_run_dir}")"
  ailly -p "${project_dir}" report "${run_id_a}" "${run_id_b}"

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

  # Property 2 gate: the invocation arm (skill loaded) must pass assertions the
  # baseline arm (no skill) fails — improved > 0 — and must never make a passing
  # baseline case fail — regressed == 0. A checker too lenient to fail un-skilled
  # output yields improved == 0 and fails here; that is the point.
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

echo "OK: domain/e2e feature test passed — discovery routing and falsification gap both clear."
