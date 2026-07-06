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

  manifest="$WORKDIR/$scanned.manifest"
  {
    echo "$REPO_ROOT/$file"
    jq -r --arg f "$file" \
      '.[$f][] | "- [\(.Severity)] \(.Check) line \(.Line): \(.Message)"' \
      <<<"$findings_json"
  } > "$manifest"
  echo "$manifest" >> "$manifest_list"
done <<<"$FILES"

dispatch="$WORKDIR/dispatch.sh"
cat > "$dispatch" <<'DISPATCH'
#!/usr/bin/env bash
set -uo pipefail
manifest="$1"
ABS_PATH="$(head -n 1 "$manifest")"
FINDINGS="$(tail -n +2 "$manifest")"
PROMPT="Fix the following Vale lint findings in $ABS_PATH. Preserve the file's current tone and voice. Correct only the identified issues; make no other edits.

Vale findings:
$FINDINGS"

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
