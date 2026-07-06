# Implementation Plan: Vale-Fix Worked Examples

**Libraries & Skills:** none required (carried from `research.md`/`design.md`; no Vale
agentic skill exists to load — work from Vale's documentation and this repo's existing
`scripts/vale-fix.sh`). No `patterns:*` skill is invoked for Step 0 either: this feature has
no entities, value objects, or lifecycle states — its "domain model" is a flat YAML sidecar
schema plus three shell function signatures, so the entity/value-object/type-state patterns
don't apply.

**Feature test:** `developer/tests/test_vale_fix_examples.py`
**User story:** A file trips `DDD.PassiveVoice` on two separate lines; when `vale-fix.sh`
builds that file's fix prompt, the `DDD.PassiveVoice` worked example appears in the prompt
exactly once, teaching the actor-naming escape instead of leaving Claude to guess a fix that
flips into `Google.We`.

**Steps:**
- [ ] Step 0: API surface area — sidecar schema, seed data, function stubs
- [ ] Step 1: Distinct-rule dedup pass
- [ ] Step 2: Example lookup (auto-derived → sidecar → nothing)
- [ ] Step 3: Render the "Worked examples" prompt section
- [ ] Step 4: `VALE_FIX_DRY_RUN` hook

## Step 0: API surface area

No new bash logic beyond stub declarations. This step establishes the sidecar data schema
and the two hand-authored seed files the feature test reads by exact string match, plus
empty function stubs later steps fill in.

**Sidecar schema** (`styles/config/examples/<Style>/<Rule>.examples.yml`):

```yaml
rule: <Style>.<Rule>
examples:
  - bad: "<the violating sentence>"
    good: "<the corrected sentence>"
    note: "<why this form satisfies every rule in play, optional>"
```

**Seed file 1** — `styles/config/examples/DDD/PassiveVoice.examples.yml` (content fixed by
the feature test's `EXPECTED_BAD`/`EXPECTED_GOOD`/`EXPECTED_NOTE` constants):

```yaml
rule: DDD.PassiveVoice
examples:
  - bad: "This item is mentioned for parity with the sibling skills."
    good: "The skill index mentions this item for parity with the sibling skills."
    note: "Name the specific actor — not 'we' — to satisfy both active voice and Google.We."
```

**Seed file 2** — `styles/config/examples/Google/We.examples.yml` (design.md Specification
item 2 — teaches the same escape from the other side of the loop):

```yaml
rule: Google.We
examples:
  - bad: "We mention this item for parity with the sibling skills."
    good: "The skill index mentions this item for parity with the sibling skills."
    note: "Name the specific actor — not 'we' — to satisfy both Google.We and active voice."
```

**Function stubs** to add to `scripts/vale-fix.sh` (signatures only, empty bodies, not yet
called from the main flow):

```bash
# Echoes the distinct .Check values found in $findings_json for file $f, one per line.
dedup_rules() { :; }            # dedup_rules "$findings_json" "$f"

# Echoes "bad<TAB>good<TAB>note" for $rule, or nothing if no example resolves.
lookup_example() { :; }         # lookup_example "$rule" "$findings_json" "$f"

# Echoes the full "Worked examples" prompt section for the given rule list, or
# nothing if no rule resolved an example.
render_worked_examples_section() { :; }   # render_worked_examples_section "${rules[@]}"
```

**Tests:** none new — Step 0 adds data and unreachable stubs. Confirm `bash -n
scripts/vale-fix.sh` still parses and `python3 developer/tests/test_vale_fix_examples.py`
still fails with the same `missing ...PassiveVoice.examples.yml` message it does today
disappearing (the file now exists), replaced by a later failure (prompt has no worked
example yet) — that shift in the failure message is the signal this step landed correctly.

## Step 1: Distinct-rule dedup pass

**Enables:** foundation for the "exactly once" assertion — `check_prompt_has_example_once`
counts `EXPECTED_GOOD` occurrences and requires exactly 1, even though the probe file trips
`DDD.PassiveVoice` on two lines. Without dedup, later steps would naturally emit the example
once per finding line, not once per rule.

Fill in `dedup_rules`: given the per-file `findings_json` already fetched by the existing
scan loop, emit each distinct `.Check` value once, in `jq`:

```bash
dedup_rules() {
  local findings_json="$1" f="$2"
  jq -r --arg f "$f" '[.[$f][].Check] | unique | .[]' <<<"$findings_json"
}
```

Wire this into the existing per-file scan loop (where `manifest` is currently built) to
also produce a `rules` array (e.g. `mapfile -t rules < <(dedup_rules "$findings_json"
"$file")`) that steps 2–3 will consume. No prompt content changes yet.

**Tests**

```
test "two findings from the same rule collapse to one entry":
  findings_json <- vale --output=JSON against the two-line PassiveVoice probe
  rules <- dedup_rules(findings_json, probe_path)
  assert rules == ["DDD.PassiveVoice"]   # not ["DDD.PassiveVoice", "DDD.PassiveVoice"]
```

- Edge case: a file with zero findings (the existing `count -eq 0` / "clean" branch) — dedup
  is never called; confirm the clean-file path is unaffected.
- Edge case: a file with findings from two different rules — both appear, each once.

**Implementation Outline**

```
for each flagged file:
  findings_json <- vale --output=JSON file        # already computed today
  rules <- dedup_rules(findings_json, file)        # new
  # (manifest building continues unchanged for this step)
```

## Step 2: Example lookup (auto-derived → sidecar → nothing)

**Enables:** the data half of the prompt section — given a rule name, produce its bad/good/
note text (or nothing). This is what Step 3 renders and what the feature test's content
assertions (`EXPECTED_BAD`/`EXPECTED_GOOD`/`EXPECTED_NOTE` all present) ultimately depend on.

Fill in `lookup_example`, in the precise order design.md's Specification item 5 states:

1. **Auto-derived** — search `findings_json` for an entry with `.Check == rule` and a
   non-empty `.Action.Name` (i.e., `substitution`/`existence+action` rules); if found, `bad`
   is `.Match`, `good` is `.Action.Params[0]`, `note` is empty. One `jq` query.
2. **Sidecar** — else split `rule` on the first `.` into `style`/`rule_name`
   (`style="${rule%%.*}"`, `rule_name="${rule#*.}"`), and look for
   `styles/config/examples/$style/$rule_name.examples.yml`. If present, read the *first*
   entry's `bad`/`good`/`note`. The schema is fixed and narrow (one quoted scalar per key,
   no nesting beyond one list) — a full YAML parser is unnecessary and this repo has neither
   `yq` nor PyYAML available. A small `python3` snippet reading the file's lines with a
   `^\s*-?\s*(bad|good|note):\s*"(.*)"\s*$` regex captures all three fields in one pass; do
   not introduce a new YAML-parsing dependency for a two-file, hand-authored corpus.
3. **Nothing** — else emit nothing; the caller skips this rule when rendering (the existing
   findings-list entry, with the rule's own message/link, still stands alone, unchanged from
   today).

**Tests**

```
test "sidecar branch resolves DDD.PassiveVoice from the seed file":
  result <- lookup_example("DDD.PassiveVoice", findings_json_with_no_action, probe_path)
  assert result.bad == EXPECTED_BAD
  assert result.good == EXPECTED_GOOD
  assert result.note == EXPECTED_NOTE
```

- Edge case: auto-derived branch — a rule whose finding carries `.Action.Name` (e.g.
  `DDD.Filler`) resolves from `.Match`/`.Action.Params[0]` without touching any sidecar file.
- Edge case: a rule with neither an action nor a sidecar file (the "nothing" fallback)
  resolves to empty, not an error, and does not abort the script under `set -u`.
- Edge case: rule name with the style prefix split correctly (`Google.We` → `Google` /
  `We`, not `Google.We` / empty).

**Implementation Outline**

```
lookup_example(rule, findings_json, file):
  auto <- jq '.[file][] | select(.Check == rule and .Action.Name != "") | {bad: .Match, good: .Action.Params[0]}' first-match
  if auto: return auto with note=""
  style, rule_name <- split rule on first "."
  sidecar <- styles/config/examples/{style}/{rule_name}.examples.yml
  if sidecar exists:
    return first example's {bad, good, note} via the narrow python3 line-scanner
  return nothing
```

## Step 3: Render the "Worked examples" prompt section

**Enables:** the full prompt-content assertions in `check_prompt_has_example_once` — the
"Worked example" heading text, and the bad/good/note strings appearing in the assembled
prompt exactly once per rule.

Fill in `render_worked_examples_section` to call `lookup_example` once per entry in the
deduped `rules` list (Step 1), skip rules that resolve to nothing, and format each resolved
rule as one block; join with blank lines. Wire the result into the existing prompt assembly
inside the `dispatch` heredoc (today's `PROMPT="Fix the following Vale lint findings...`),
appended as a new section after the "Vale findings" block — heading text must contain
"Worked example" verbatim (design.md: "Worked examples for rules seen above") to satisfy the
test's substring check.

**Tests**

```
test "section appears once per distinct rule, omitting unresolved rules":
  rules <- ["DDD.PassiveVoice", "SomeRuleWithNoExample"]
  section <- render_worked_examples_section(rules, findings_json, file)
  assert section.count(EXPECTED_GOOD) == 1
  assert "SomeRuleWithNoExample" not in section   # nothing-branch rules are omitted
```

- Edge case: all rules resolve to nothing — the whole section is empty/omitted, not an empty
  heading with no content.
- Edge case: rule order in `rules` is preserved in the rendered section (stable output,
  easier to eyeball in review).

**Implementation Outline**

```
render_worked_examples_section(rules, findings_json, file):
  blocks <- []
  for rule in rules:
    example <- lookup_example(rule, findings_json, file)
    if example: blocks.append(format(rule, example))
  if blocks.empty: return ""
  return "Worked examples for rules seen above:\n\n" + join(blocks, "\n\n")
```

At this point the feature test is still red: the prompt is only ever printed by actually
dispatching to `claude -p` (the stub), so nothing observes its content yet — Step 4 adds the
hook the test uses to read it without a live call.

## Step 4: `VALE_FIX_DRY_RUN` hook

**Enables:** both remaining feature-test assertions — under `VALE_FIX_DRY_RUN=1` the stub is
never called and the printed prompt is captured from stdout; without it, the stub is still
called exactly once (the hook must not break the default path, including under the script's
`set -u`).

In the generated `dispatch` script (the heredoc that currently ends in `claude -p "$PROMPT"
...`), branch on the environment variable, defaulted so an unset var never trips `set -u`:

```bash
if [ "${VALE_FIX_DRY_RUN:-}" = "1" ]; then
  echo "$PROMPT"
else
  claude -p "$PROMPT" --model haiku --allowedTools "Read(/$ABS_PATH)" "Edit(/$ABS_PATH)"
fi
```

Since `dispatch` runs under `xargs -P 8`, confirm the env var is inherited by the child
process (it is — `xargs` children inherit the parent's environment by default; no explicit
export needed beyond what the test harness already sets).

**Tests**

This is the feature test itself (`developer/tests/test_vale_fix_examples.py`) going green:
run twice against the same probe (`VALE_FIX_DRY_RUN=1` and unset), asserting the stub
call-count and prompt content documented in `design.md`'s Feature Test section.

- Edge case: `VALE_FIX_DRY_RUN` set to something other than `"1"` (e.g. empty string or
  `"0"`) falls through to the normal dispatch path, not the dry-run path.
- Edge case: dry-run output for a multi-file run — confirm each flagged file's prompt is
  still separately identifiable in stdout (no interleaving corruption from `xargs -P 8`
  writing to the same stream); the feature test only drives one file, so this is a manual
  spot-check during build, not a new automated assertion.

**Implementation Outline**

```
dispatch(manifest):
  ABS_PATH, FINDINGS <- read manifest              # unchanged
  PROMPT <- assemble(FINDINGS, worked_examples_section)   # Step 3's output, unchanged here
  if VALE_FIX_DRY_RUN == "1":
    print(PROMPT)
  else:
    claude -p PROMPT --model haiku --allowedTools ...
```

## Risks and Notes

- **Deliberately out of scope for this plan** (per design.md's own "Coverage boundary," not
  exercised by the feature test, and each substantial enough to warrant its own build cycle):
  - `scripts/vale-generate-examples.sh` (design.md Specification item 3, the LLM-generated
    tier) — a separate offline script with its own dispatch/testing needs. Track as a
    follow-up in `.ailly/developer/TASKS.md` at cleanup, not built in this plan.
  - `vale-check.sh` surfacing examples in human-facing output — explicitly deferred in
    design.md's Alternatives.
- **No new external dependency.** Confirmed neither `yq` nor Python's `PyYAML` is installed
  in this environment; Step 2's sidecar parser is a narrow, schema-specific line-scanner by
  design, not a general YAML reader. If a third sidecar file ever needs a nested/multi-line
  scalar, this parser will need revisiting — acceptable now given exactly two hand-authored
  seed files exist.
- **Termination is still not formally guaranteed** (design.md's own deferred decision) — this
  plan makes the two known loop rules converge; a novel two-rule conflict without an authored
  example could still oscillate.
