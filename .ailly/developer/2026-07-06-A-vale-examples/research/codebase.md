# Codebase: Vale setup and the integration point for a `--examples` capability

## Findings

### The existing Vale wiring (specific lens)

- `.vale.ini`: `StylesPath = styles`, `Vocab = DDD`, `Packages = Google, Joblint`,
  `MinAlertLevel = warning`; `[*.md]` applies `BasedOnStyles = Google, Joblint, DDD`.
- `scripts/vale-check.sh`: `vale sync` then `vale --glob='!{**/e2e/**}' <path|.>`. Plain
  human-facing lint run; no JSON, no examples.
- `scripts/vale-fix.sh`: **this is the reproduction of the human's oscillation loop.** It
  runs `vale --output=JSON "$file"`, parses it with `jq` into a per-file manifest
  (`"- [\(.Severity)] \(.Check) line \(.Line): \(.Message)"`), and dispatches one headless
  `claude -p --model haiku` session per flagged file with those findings pasted into the
  prompt as `Vale findings:`. The prompt says "Fix the following Vale lint findings ...
  Correct only the identified issues" — every violation is stated as a *rule to satisfy*,
  with **no worked example**. This is exactly the shape that produced the transcript loop.
- `developer/tests/test_vale_lint_setup.py`: feature test for the *existing* Vale adoption
  (files exist, 12 DDD rules fire against a probe, e2e glob excludes only e2e). It runs the
  real `vale` binary when on PATH, else falls back to structural checks. A `--examples`
  feature would extend this or add a sibling test.
- `.github/workflows/vale.yml`: uses `errata-ai/vale-action@reviewdog`, `fail_on_error:
  false`, `reporter: github-pr-review`. **Note:** `errata-ai` is the pre-rename org; the
  action now lives at `vale-cli/vale-action` (GitHub redirects the old ref, so this still
  works today, but it is stale).
- `DEVELOPMENT.md` "Prose Linting (Vale)" section documents `brew install vale`, `vale
  sync`, `vale <file>`, `vale --glob='!{**/e2e/**}' .`, and `<!-- vale off -->`.

### The candidate framing HOLDS — and is simpler than the embedded transcript assumed

Confirmed empirically with the installed `vale` 3.15.1 (`vale --output=JSON` on a probe):

- The JSON `vale-fix.sh` already parses carries, **per alert**: `.Check`, `.Severity`,
  `.Line`, `.Span`, `.Message`, **`.Link`**, **`.Match`** (the exact bad text), **`.Action`**
  (`{Name, Params}`), and `.Description`.
- For **substitution / existence-with-`action`** rules, `.Match` is the bad text and
  `.Action.Params[0]` is the good replacement — a complete bad→good pair, already resolved
  for the specific match, **already in the JSON**. Probe: `DDD.Filler` on "quite a few"
  returns `Action:{Name:"replace", Params:["many"]}`; `DDD.WordChoice` on "thing" returns
  `Params:["the specific object or concept"]`.
- Therefore the auto-derived tier the transcript proposes needs **no `--output=template`,
  no Go, no fork, no re-reading of `styles/*/*.yml` swap maps at report time.** The smallest
  integration point is to extend the existing `jq` line in `vale-fix.sh` (and optionally
  print in `vale-check.sh`) to emit `.Match → .Action.Params` when `.Action.Name != ""`.

### But the auto-derive tier does NOT touch the motivating case

- The loop rules are all `extends: existence` with **no `action`/`swap`**:
  - `styles/DDD/PassiveVoice.yml` — `existence`, `level: warning`, `raw:
    '\b(is|are|was|were|be|being|been)\s+\w+(ed|en)\b'`. Empty `.Action` in JSON.
  - `styles/Google/We.yml` — `existence`, `level: warning`, `tokens: we, we've/we're,
    ours?, us, let's`. Empty `.Action`.
  - `styles/Google/Passive.yml` — `existence`, **`level: suggestion`**, `raw` + irregular-
    participle `tokens`. Empty `.Action`.
- These emit **nothing** derivable. They are precisely the hand-authored tier. So the
  auto-derive tier, though free, solves 0% of the human's actual pain; the design effort is
  the **hand-written example database for existence rules**.

### Two secondary findings the transcript missed

1. **`Google.Passive` never fires in this repo.** It is `level: suggestion`; `.vale.ini`
   sets `MinAlertLevel = warning`, which filters suggestions out. The probe confirms only
   `DDD.PassiveVoice` (warning) and `Google.We` (warning) fire. So the "two passive-voice
   rules conflict" concern is dormant at the current threshold — only `DDD.PassiveVoice`
   participates in the loop. (If MinAlertLevel were lowered, both would double-flag the same
   spans.)
2. **The loop is a genuine mutual-exclusion trap, so a naive example perpetuates it.**
   "X is mentioned" trips `DDD.PassiveVoice`; the obvious active rewrite "We mention X" trips
   `Google.We`; "X is listed" trips `DDD.PassiveVoice` again. The only escape is a *third*
   form that names a concrete non-"we" actor ("The sibling skills list this item…") or
   restructures the sentence. A worked example for `DDD.PassiveVoice` that shows "use active
   voice: We do X" would actively feed the loop. The example content must encode the escape,
   not just the rule's own message — which is the whole point of the editor SME's advice.

### Corpus shape (what the auto-derive tier would and would not cover)

Across `styles/{Google,Joblint,DDD}` rule files: **46 `existence`, 12 `substitution`, 1
`conditional`, 1 `capitalization`**. Files with `swap:` maps: 12 (all 6 DDD substitution
rules; Google Contractions/GenderBias/Latin/WordList; Joblint Acronyms/TechTerms). Files
with an `action:` (name replace/edit) block: the 6 DDD substitution rules plus Google
Contractions/EmDash/Exclamation/GenderBias/HeadingPunctuation/Latin/LyHyphens/
OptionalPlurals/WordList and Joblint Acronyms/TechTerms. Caveat: several DDD swap values are
empty strings (delete-the-word, e.g. `"basically": ""`) or bracketed placeholders
(`"various": "specific [term]"`), which are *not* clean 1:1 worked pairs and would need
care even in the "free" tier.

### Sync-safe storage location is available and already used

`styles/config/` currently holds only `vocabularies/DDD/{accept,reject}.txt`.
`styles/.gitignore` today is just `Google\nJoblint` (ignores the two synced package folders;
`config/` and `DDD/` are tracked). This repo already follows the "synced folders are
disposable, `config/` persists" convention, so an examples sidecar under
`styles/config/examples/<Style>/<Rule>.examples.yml` would ride through `vale sync`
untouched, consistent with how vocabularies already live.

## Sources

- `/Users/david.souther/devel/davidsouther/ailly/ailly_developer/.vale.ini`
- `/Users/david.souther/devel/davidsouther/ailly/ailly_developer/scripts/vale-check.sh`
- `/Users/david.souther/devel/davidsouther/ailly/ailly_developer/scripts/vale-fix.sh`
- `/Users/david.souther/devel/davidsouther/ailly/ailly_developer/styles/DDD/PassiveVoice.yml`
- `/Users/david.souther/devel/davidsouther/ailly/ailly_developer/styles/Google/Passive.yml`
- `/Users/david.souther/devel/davidsouther/ailly/ailly_developer/styles/Google/We.yml`
- `/Users/david.souther/devel/davidsouther/ailly/ailly_developer/styles/DDD/{Filler,WordChoice}.yml`
- `/Users/david.souther/devel/davidsouther/ailly/ailly_developer/styles/.gitignore`,
  `styles/config/vocabularies/DDD/`
- `/Users/david.souther/devel/davidsouther/ailly/ailly_developer/.github/workflows/vale.yml`
- `/Users/david.souther/devel/davidsouther/ailly/ailly_developer/developer/tests/test_vale_lint_setup.py`
- `/Users/david.souther/devel/davidsouther/ailly/ailly_developer/DEVELOPMENT.md`
- Empirical: `vale 3.15.1`, `vale --output=JSON` / `--output=<tmpl>` on local probe files.
