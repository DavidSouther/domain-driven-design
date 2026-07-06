#!/usr/bin/env bash
# Vale autofix (Code Mode): run vale over the skills/references docs, and
# dispatch one path-scoped headless Claude Haiku session per flagged file to
# fix the findings. See .ailly/developer/2026-07-05-B-vale-autofix/plan.md.
# Pass a single file path as $1 to test the dispatch flow against just that
# file instead of scanning the whole corpus.
set -uo pipefail

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$REPO_ROOT" || exit 1

WORKDIR="$(mktemp -d)"
trap 'rm -rf "$WORKDIR"' EXIT

# Echoes the distinct .Check values found in $findings_json for file $f, one per line.
dedup_rules() {                 # dedup_rules "$findings_json" "$f"
  local findings_json="$1" f="$2"
  jq -r --arg f "$f" '[.[$f][].Check] | unique | .[]' <<<"$findings_json"
}

# Echoes "bad<TAB>good<TAB>note" for $rule, or nothing if no example resolves.
lookup_example() {              # lookup_example "$rule" "$findings_json" "$f"
  local rule="$1" findings_json="$2" f="$3"

  local auto
  auto="$(jq -r --arg f "$f" --arg rule "$rule" '
    [.[$f][] | select(.Check == $rule and ((.Action.Name // "") != ""))][0] as $m
    | if $m == null then empty else "\($m.Match)\t\($m.Action.Params[0])\t" end
  ' <<<"$findings_json")"
  if [ -n "$auto" ]; then
    printf '%s\n' "$auto"
    return
  fi

  local style="${rule%%.*}" rule_name="${rule#*.}"
  local sidecar="styles/config/examples/$style/$rule_name.examples.yml"
  if [ -f "$sidecar" ]; then
    python3 - "$sidecar" <<'PY'
import re
import sys

bad = good = note = ""
seen_bad = False
with open(sys.argv[1], encoding="utf-8") as fh:
    for line in fh:
        m = re.match(r'^\s*-?\s*(bad|good|note):\s*"(.*)"\s*$', line)
        if not m:
            continue
        key, val = m.group(1), m.group(2)
        if key == "bad":
            if seen_bad:
                break
            bad, seen_bad = val, True
        elif key == "good" and not good:
            good = val
        elif key == "note" and not note:
            note = val
print(f"{bad}\t{good}\t{note}")
PY
  fi
}

# Echoes the full "Worked examples" prompt section for the given rule list, or
# nothing if no rule resolved an example. Reads $findings_json/$file from the
# calling scope's scan-loop variables (see lookup_example's parameters).
render_worked_examples_section() {   # render_worked_examples_section "${rules[@]}"
  local rule example bad good note
  local blocks=()
  for rule in "$@"; do
    example="$(lookup_example "$rule" "$findings_json" "$file")"
    [ -z "$example" ] && continue
    IFS=$'\t' read -r bad good note <<<"$example"
    if [ -n "$note" ]; then
      blocks+=("Rule: $rule
Bad:  $bad
Good: $good
Note: $note")
    else
      blocks+=("Rule: $rule
Bad:  $bad
Good: $good")
    fi
  done

  [ "${#blocks[@]}" -eq 0 ] && return

  printf 'Worked examples for rules seen above:\n\n'
  local i last=$(( ${#blocks[@]} - 1 ))
  for i in "${!blocks[@]}"; do
    printf '%s\n' "${blocks[$i]}"
    [ "$i" -lt "$last" ] && printf '\n'
  done
}

if [ "$#" -gt 0 ]; then
  FILES="${1#"$REPO_ROOT"/}"
else
  FILES="$(find developer/skills domain/skills patterns/skills research/skills general/skills \
       research/references \
       -name "*.md" -not -path "*/e2e/*")"
fi

manifest_list="$WORKDIR/manifests.list"
: > "$manifest_list"

scanned=0
clean=0
dispatched=0
dispatched_files=()

while IFS= read -r file; do
  [ -z "$file" ] && continue
  scanned=$((scanned + 1))
  findings_json="$(vale --output=JSON "$file" 2>/dev/null)"
  count="$(jq --arg f "$file" '(.[$f] // []) | length' <<<"$findings_json")"

  if [ "$count" -eq 0 ]; then
    clean=$((clean + 1))
    echo "clean:   $file"
    continue
  fi

  dispatched=$((dispatched + 1))
  dispatched_files+=("$file")
  echo "flagged: $file ($count finding(s))"

  rules=()
  while IFS= read -r rule; do
    rules+=("$rule")
  done < <(dedup_rules "$findings_json" "$file")

  manifest="$WORKDIR/$scanned.manifest"
  {
    echo "$REPO_ROOT/$file"
    jq -r --arg f "$file" \
      '.[$f][] | "- [\(.Severity)] \(.Check) line \(.Line): \(.Message)"' \
      <<<"$findings_json"
    echo "__WORKED_EXAMPLES__"
    render_worked_examples_section "${rules[@]}"
  } > "$manifest"
  echo "$manifest" >> "$manifest_list"
done <<<"$FILES"

dispatch="$WORKDIR/dispatch.sh"
cat > "$dispatch" <<'DISPATCH'
#!/usr/bin/env bash
set -uo pipefail
manifest="$1"
ABS_PATH="$(head -n 1 "$manifest")"
FINDINGS="$(sed -n '2,/^__WORKED_EXAMPLES__$/p' "$manifest" | sed '$d')"
WORKED_EXAMPLES="$(sed -n '/^__WORKED_EXAMPLES__$/,$p' "$manifest" | tail -n +2)"
PROMPT="Fix the following Vale lint findings in $ABS_PATH. Preserve the file's current tone and voice. Correct only the identified issues; make no other edits.

Vale findings:
$FINDINGS"
if [ -n "$WORKED_EXAMPLES" ]; then
  PROMPT="$PROMPT

$WORKED_EXAMPLES"
fi

claude -p "$PROMPT" \
  --model haiku \
  --allowedTools "Read(/$ABS_PATH)" "Edit(/$ABS_PATH)"
DISPATCH
chmod +x "$dispatch"

if [ "$dispatched" -gt 0 ]; then
  xargs -P 8 -I{} "$dispatch" {} < "$manifest_list"
fi

echo
echo "=== Vale autofix summary ==="
echo "files scanned:    $scanned"
echo "files clean:      $clean"
echo "files dispatched: $dispatched"
if [ "$dispatched" -gt 0 ]; then
  echo
  echo "Affected files (review the diff before committing):"
  printf '  %s\n' "${dispatched_files[@]}"
fi
