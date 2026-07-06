# Research: Vale `--examples` — worked bad→good examples for violated rules

## Topic and Intent

Verbatim source — the full contents of `.ailly/prompts/vale_examples`. This is the durable
intent anchor a later intent-review reads backward from. Note that everything below the
second `---` is a *prior, second-hand assistant conversation* reproduced as the human wrote
it; it is quoted for fidelity, **not** endorsed — this research verifies or falsifies its
claims (see Falsification/Refine).

````text
/ailly on the Vale branch, within the Vale feature, pick up this work.

---

When running vale-fix and vale-check on a file, Claude got into this cycle:

```
Vale:  57:117  warning  Passive voice obscures agency: 'is mentioned'. Rewrite in active voice: subject + verb + object.  DDD.PassiveVoice   

Claude: 2. **Line 57 (passive voice)**: Changed "This item is mentioned for parity with the sibling skills" to "We mention this item for parity with the sibling skills" to use active voice.

Vale:  57:107  warning  Try to avoid using first-person plural like 'We'.  Google.We 

Claude: Done. Changed "We mention this item for parity with the sibling skills" to "This item is listed for parity with the sibling skills" on line 57, removing the first-person plural while maintaining the instructional tone.

Vale:  57:117  warning  Passive voice obscures agency: 'is listed'. Rewrite in active voice: subject + verb + object.  DDD.PassiveVoice 

Claude: Done. Converted “is listed" to active voice: "We list this item for parity with the sibling skills."
```

From an editor subject matter expert: "LLMs aren't good at applying rules. They will follow examples more than rules, the rule tells them what example to look at."

So my thought is --examples (or similar) will collect a list of rules that had errors, then write a second stanza of output with examples for each rule.

Follow the approach from the below conversational session.

---

/ailly find resources for vale.sh that provide examples on how to correct failing rules. I want to add a --examples flag to it, which has a database of examples for fixing each rule. Then when a run is complete, it prints those examples for every rule that had any violations.


Charted implementation paths for adding examples flag to Vale CLI
Charted implementation paths for adding examples flag to Vale CLI
Two live options here, one needs no fork.

Skip the fork. Vale already exposes exactly the data you'd want through its --output template system: pass --output=template.tmpl and the template gets Data{Files []ProcessedFile; LintedTotal int} where each file has Alerts []core.Alert, and Alert carries .Check (the rule name, e.g. Google.Passive), .Message, .Line, .Span (Templates docs). Build your examples database as a map[string]string keyed by check name, drop it into a small Go template using Sprig helpers, range over .Files, collect the distinct .Check values you saw, and print the matching example for each at the end. That's the whole feature, zero patches to Vale itself, works today on any installed Vale ≥ the templates release.

If you actually want a native --examples flag, note the project renamed: it's now vale-cli/vale, not errata-ai/vale (same code, new org). The flag lives in cmd/vale/flag.go, which is a flat pflag init block wired to a core.CLIFlags struct, so adding Flags.Examples there is a one-liner, e.g.:

go
pflag.BoolVar(&Flags.Examples, "examples", false, "Print a fix example for each rule that was violated.")
Then thread it through wherever the run's final report gets assembled, alongside json.go and line.go — those two files are Vale's other two built-in output styles and show the pattern for iterating LintedTotal/ProcessedFile.Alerts before exit. You'd dedupe Alert.Check across all files, look each one up in your examples map, and print after the summary line.

For the example database's content itself, Per my notes, Red Hat's Vale rule reference guide is the best model I found: it documents each rule with a violation example and its resolution, rule by rule, which is precisely the shape you need for a map[ruleName]fixExample. It's Apache/EPL-licensed so you can plausibly seed your database from it rather than writing every entry by hand.

One open question: does the check-name-to-example lookup need to cover custom/third-party styles too, or just Vale's own built-in rules plus one style you control?

Oh, cool. Let's focus on that output template.  The interesting question is the database of example corrections, not the invocation mechanism.


Architected two-tier examples database strategy for style rules
Architected two-tier examples database strategy for style rules
Good split. The database is the actual design problem; the flag is trivial once you know what to look up.

Here's the thing: for a large chunk of rules, you don't need to author examples at all. substitution rules already contain their own bad→good pairs. Look at the swap map: swap: {abundance: plenty, accelerate: speed up} (substitution docs). That's your example, verbatim, for free. Same for any existence rule that carries an action: {name: replace, params: [...]} or action: {name: edit, params: [remove, '.?!']} block (existence docs) — the action tells you mechanically what the "after" looks like. Parse those two extension points at vale sync time (or at build time, walking the StylesPath), and you get a real example database with zero hand-authoring, for every Microsoft/Google/Red Hat-style rule built on substitution or existence-with-replace. Those two checks cover the bulk of most published styles, per the Contentsquare and Docsio writeups of real Vale setups.

What's left uncovered: occurrence, repetition, consistency, conditional, capitalization, readability/metric, spelling, sequence, script. These flag a pattern (too many commas, inconsistent heading case, a Flesch-Kincaid score) without stating a corrected form anywhere in the YAML — there's nothing to mechanically derive. Those need real, hand-written before/after pairs.

For that tier, I'd store a sidecar file next to each rule rather than one giant lookup table: <RuleName>.examples.yml beside <RuleName>.yml in the style folder. That matches Vale's own authoring model — rules are already just files a style author drops in — so a style package can ship its own examples the same way it ships its own rules, and community styles (Microsoft, Google, write-good, Red Hat) can add these incrementally rather than you maintaining one central file for every style in existence. Schema, keeping it close to how Vale already writes messages:

yaml
# Google/Passive.examples.yml
rule: Google.Passive
examples:
  - bad: "The document was reviewed by the team."
    good: "The team reviewed the document."
    note: "Active voice names the actor."
At --examples print time: look up Alert.Check (e.g. "Google.Passive") — first check for an auto-derived entry from substitution/existence, fall back to the sidecar file, fall back to nothing (print the rule's own link field if set, so there's always something actionable).

For seeding the hand-written tier, the Red Hat Vale reference guide is worth mining directly — it's Apache/EPL-licensed and already structured as violation-plus-resolution per rule, so it's closer to "convert format" than "write from scratch" for any style that overlaps with Red Hat's.

One thing worth deciding before you build the sidecar loader: do you want examples versioned and synced alongside styles via vale sync (so a style's package bundle carries its own examples), or kept local to the user's config regardless of which styles they pull in?

Any way to split that? Since I don't manage the Google rules, and want them to keep syncing, I would need to merge their rules with my examples.


Architected sync-safe example storage leveraging existing config conventions
Architected sync-safe example storage leveraging existing config conventions
Yes — and Vale already has the pattern you want, right there in its own docs. vale sync only overwrites the named style folders (StylesPath/Google/, StylesPath/write-good/, etc). It leaves StylesPath/config/ alone — that's exactly why vocabularies, dictionaries, and templates all live under config/ instead of inside a style folder (Packages docs). The docs even ship a .gitignore for this precise problem, ignoring the whole StylesPath except config/ so synced packages stay disposable while your local additions persist:

gitignore
.github/styles/*
!.github/styles/config/
.github/styles/config/*
!.github/styles/config/vocabularies/
.github/styles/config/vocabularies/* 
!.github/styles/config/vocabularies/Base
Do the same thing for examples. Put them in <StylesPath>/config/examples/<Style>/<Rule>.examples.yml:

styles/
├── Google/              ← re-synced, do not touch
│   └── Passive.yml
└── config/
    ├── vocabularies/
    └── examples/
        └── Google/
            └── Passive.examples.yml   ← yours, survives sync
vale sync never walks into config/, so your file rides through every re-sync untouched, and there's no merge step because there's nothing to merge — the two files never occupy the same path.

This also fixes something in yesterday's auto-derive plan: for substitution/existence-with-replace rules, don't cache the derived bad→good pairs anywhere. Read Google/Passive.yml's swap map live, at report time, off whatever sync most recently dropped there. If Google tweaks their swap list next release, your auto-derived examples update for free on the next vale sync with zero action from you. The sidecar file under config/examples/ is reserved for the tier you actually have to write by hand — occurrence, readability, and the rest — where there's no bad→good pair sitting in the upstream YAML to begin with.

Lookup logic stays a single flat rule: for Alert.Check == "Google.Passive", try deriving from styles/Google/Passive.yml first, fall back to styles/config/examples/Google/Passive.examples.yml, fall back to the rule's own link. Same code path whether the rule came from Google, write-good, or a style you actually own.




````

**In the user's own framing (added after the verbatim quote):** When Claude fixes Vale
findings it can livelock — oscillating forever between two rules whose "corrections" trip
each other (the transcript: `DDD.PassiveVoice` ⇄ `Google.We` on one line). An editor SME's
guidance is that LLMs follow *examples* better than *rules*. The intent is a capability
(sketched as `--examples`) that, for each rule violated in a run, surfaces a worked bad→good
example so the fixer imitates an example instead of re-satisfying a rule. Work continues on
the existing Vale feature branch and should follow the embedded conversation's approach —
after verifying it.

## Search/Expand (general lens)

- **The SME's premise is sound and standard.** Steering an LLM with a worked example (a
  one-shot demonstration) rather than an imperative rule is ordinary prompt-engineering
  practice for style-transformation tasks. This reframes the task: it is a *prompt-quality*
  improvement to an LLM-in-the-loop autofix, not a change to the linter engine.
- **"Diagnostic + example fix" is a well-worn linter pattern**, but no linter ships it as an
  LLM-fixer input. ESLint pairs each rule with a docs page (worked examples) and a `--fix`;
  Vale itself already carries a per-rule `link:` URL and, for `substitution` rules, a
  single-token replacement. The novel piece here is folding the example into the *prompt* a
  headless fixer consumes, which this repo already builds in `scripts/vale-fix.sh`.
- **The oscillation is a livelock, not just a bad prompt.** "X is mentioned" trips
  `DDD.PassiveVoice`; the natural active rewrite "We mention X" trips `Google.We`; "X is
  listed" trips `DDD.PassiveVoice` again. Two greedy single-rule fixes form a cycle. This
  matters for the general framing: a better example *mitigates* the loop only if it teaches
  the joint escape (name a concrete non-"we" actor, or restructure) — it does not *formally*
  guarantee termination. An example that just says "use active voice" would feed the loop.
- **Confirmed gap in the ecosystem.** No Vale `--examples` flag, no examples-database
  feature, and no third-party plugin that injects worked before/after examples into Vale
  output exists (verified against Vale's CLI reference and ecosystem search). The feature is
  genuinely net-new — there is nothing to adopt wholesale. Full detail in
  `research/public.md`.

## Libraries & Skills

> **Before doing any work in this feature, load these skills via the active harness's
> skill-loading mechanism:** *(none exist for the library)* — **there is no published Vale
> agentic skill (`SKILL.md`) or Claude skill to load.** This omission is a finding, not a
> gap in this research: the major skill directories (`VoltAgent/awesome-agent-skills`,
> `BehiSecc/awesome-claude-skills`) and GitHub-scoped search surface none for the vale.sh
> prose linter. Downstream phases must therefore work from the Vale documentation and the
> empirically-confirmed data shapes recorded here, **not** invent a framework abstraction.

Carry the directive above verbatim into `design.md` and `plan.md`.

**Vale (vale.sh) — the one library this task touches.** Version in use locally: `3.15.1`.
Load-bearing docs, all verified this session:

- **JSON / template output** (`vale.sh/docs/templates`): `--output=JSON` and
  `--output=<tmpl>` both expose per-alert `.Check`, `.Message`, `.Line`, `.Span`,
  `.Severity`, `.Link`, `.Match`, `.Action{Name,Params}`. Empirically, for
  `substitution`/`action` rules the JSON already contains the full bad→good pair (`.Match` +
  `.Action.Params[0]`). This is the closest worked recipe to what's being built.
- **Checks** (`vale.sh/docs/checks/substitution`, `vale.sh/docs/styles`): `substitution`
  uses a `swap:` map (`bad: good`); `existence` supports `action: {name: replace|edit,
  params}`. Check types: `existence`, `substitution`, `occurrence`, `repetition`,
  `consistency`, `conditional`, `capitalization`, `metric`, `spelling`, `sequence`,
  `script`.
- **Packages / sync** (`vale.sh/docs/keys/packages`): `vale sync` overwrites only named
  package style folders; `config/` is preserved. Confirms a sidecar under
  `styles/config/examples/` is sync-safe.

**Adjacent prior art (context, not to load):** a Vale MCP server exists —
`ChrisChinchilla/Vale-MCP` (MIT; tools `vale_status`/`vale_sync`/`check_file`/`check_text`),
successor to the archived `theletterf/vale-mcp-server`. It only wraps `vale check`; it has
no examples database and is not the integration this task needs. A Vale LSP (`vale-cli/
vale-ls`) also exists. Note the project renamed org `errata-ai` → `vale-cli`; this repo's
`.github/workflows/vale.yml` still pins the old `errata-ai/vale-action` (redirected, still
works — adjacent cleanup, out of scope here).

## Falsification/Refine (specific lens)

- **Size: a single, small feature** (borderline enhancement-to-existing-script), not a
  project and not a pure bug fix. It touches `scripts/vale-fix.sh`, a small examples data
  source, and a feature test.
- **Off-the-shelf? No.** Confirmed no existing `--examples`/examples-db/plugin; the MCP
  server does not do it. Must be built here.
- **The embedded plan's mechanism is over-built — falsified in three places:**
  1. *No fork, no `--output=template`, no Go needed.* `scripts/vale-fix.sh` **already**
     parses `vale --output=JSON` with `jq`. Empirically the JSON already carries the matched
     bad text and its replacement for substitution/action rules, so the "auto-derive" tier
     is a one-line `jq` addition (emit `.Match → .Action.Params[0]` when `.Action.Name`
     is set) — strictly simpler than the transcript's "read the swap map live from YAML."
     **The "extend the existing shell+jq pipeline" framing holds up and is the smallest
     integration point.**
  2. *The auto-derive tier does not touch the motivating case.* The loop rules —
     `DDD.PassiveVoice`, `Google.We` (and `Google.Passive`) — are all `extends: existence`
     with **no** `action`/`swap`, so they derive **nothing**. The real work is the
     hand-authored tier, and it is exactly the rules that caused the pain.
  3. *Red Hat is not the free seed the transcript claims.* `redhat-documentation/
     vale-at-red-hat` is **MIT** (not Apache/EPL) and is a Vale *style package*, not a
     worked-example guide — its generated reference lists rule messages + links, not
     incorrect→corrected sentence pairs. Seeding is "write from scratch (style-guide
     informed)," not "reformat an existing example set."
- **Smallest version that still meets the intent — a deliberate two-phase split** (human
  direction from the draft-gate review, echoing the embedded conversation's own instinct:
  "the database is the actual design problem; the flag is trivial once you know what to
  look up"):
  1. **Vale-side plumbing stays hacky.** `vale-fix.sh`'s only job is handing Claude the
     *deduplicated* set of rules that fired in the file it is fixing — one entry per rule,
     not one per finding, so a rule tripped on five lines contributes a single entry. This
     is a few lines of `jq` (`[.[$f][].Check] | unique`) bolted onto the manifest-building
     step that already exists; it is not a general-purpose flag and does not need to be
     elegant. No fork, no `--output=template`, no new CLI flag.
  2. **The examples database is the actual design problem.** Once Claude has the
     deduplicated rule list, the substantive work is the lookup behind it: schema and
     storage for (a) the auto-derived pair from JSON `.Match`/`.Action.Params` for
     substitution/action rules, and (b) hand-authored bad→good pairs for the `existence`
     rules that fire and loop (at minimum `DDD.PassiveVoice` and `Google.We`), whose "good"
     form must teach the *joint escape* from the passive⇄we loop, not just restate "use
     active voice." Design phase should spend its effort here, not on the plumbing.

## Scope

**In (for the design phase):**

*Phase 1 — vale-side plumbing (deliberately minimal/"hacky"; not the design focus):*

- Add a `jq` dedup pass in `scripts/vale-fix.sh` (`[.[$f][].Check] | unique`) alongside the
  existing per-finding manifest, so the per-file prompt receives each violated rule once,
  regardless of how many lines it fired on.
- Wire that deduplicated rule list into the existing per-file prompt so Claude receives it
  alongside the findings list already there. Just enough to hand Claude what it needs — no
  new CLI flag, no polish.

*Phase 2 — the examples database (the actual design problem):*

- Auto-derived tier: emit `.Match`→`.Action.Params[0]` straight from the JSON
  `vale-fix.sh` already parses (no template, no fork, no YAML re-parse).
- Hand-authored tier: a small examples store for the `existence` rules that fire/loop,
  stored sync-safe under `styles/config/examples/<Style>/<Rule>.examples.yml`, with content
  that resolves the `DDD.PassiveVoice` ⇄ `Google.We` livelock (name an actor / restructure),
  not just restating "use active voice."
- Lookup order design must specify precisely: auto-derived → hand-authored sidecar → (rule's
  own `link`, or nothing).
- A feature test: a file tripping a rule with a hand-authored example causes that example to
  appear in the dispatched fix prompt, once, regardless of how many lines trip the rule.
- In parallel: A full LLM generated tier, for rules without `swap` or clear examples already.
  Limited to Warning and Error tiers.

**Out / deferred:**

- Any fork of Vale, native `--examples` flag, Go changes, or `--output=template` path.
- Reading `swap`/`action` live from style YAML at report time (JSON already carries it).
- Surfacing examples in `scripts/vale-check.sh`'s human-facing output — this feature targets
  `vale-fix.sh`'s Claude-facing prompt only (resolved during draft-gate review; see Resolved
  Decisions).
- A formal termination guarantee for the fixer loop (examples mitigate; note as risk).
- Bumping `errata-ai/vale-action` → `vale-cli/vale-action` in the workflow (adjacent
  cleanup).
- Adopting the Vale MCP server / LSP.

## Resolved Decisions

**Answered by this research:**

- **Mechanism:** shell + `jq` inside the existing `vale-fix.sh` pipeline — and simpler than
  the transcript's template plan, because `--output=JSON` already carries `.Match` +
  `.Action.Params`. Verified empirically with `vale 3.15.1`.
- **Sync-safe storage:** `styles/config/examples/` — `vale sync` preserves `config/`, and
  this repo already uses that convention for `styles/config/vocabularies/DDD/`.
- **Does auto-derive help the loop?** No. The loop rules are pure `existence` with no
  derivable fix; they need hand-authored examples.
- **Red Hat as seed source:** falsified as a low-effort seed — MIT (not Apache/EPL) and not
  structured as worked bad→good pairs. Usable for reference, not lift-and-reformat.
- **Off-the-shelf tool exists?** No — no `--examples`, no examples database, no plugin.
- **Do the two passive rules conflict?** Not at the current threshold: `Google.Passive` is
  `level: suggestion`, below `MinAlertLevel = warning`, so only `DDD.PassiveVoice` fires. A
  live conflict would appear only if the threshold were lowered.

**Answered during draft-gate review (human direction, 2026-07-06):**

- **Surface:** `vale-fix.sh`'s per-file Claude-facing prompt only. `vale-check.sh`'s
  human-facing output is explicitly out of scope for this feature (see Scope).
- **Design emphasis:** keep the vale-side integration (the `jq` dedup pass and wiring it
  into the prompt) intentionally minimal/"hacky." The design phase's effort belongs on the
  examples database — its schema, storage, and hand-authored content — not on the plumbing
  that delivers it to Claude.
- **Dedup granularity:** one example per distinct rule per file, not once per finding line.
  A rule tripped on five lines in the same file surfaces its example once.

**Open for the human:**

- **Corpus breadth** (the transcript's own open question): hand-author examples only for the
  rules observed to loop, or a broader seed covering more built-in/third-party styles?
- **Content source & house style:** the "good" form of the passive⇄we escape encodes a
  style decision (prefer "name the actor," accept a `<!-- vale off -->` exception, or
  restructure). This is the human's call and drives every hand-authored example.
- **Note-only:** the topic originates from a local prompt file, not a tracker thread, so
  there is no thread to digest and no postdating comment that reframes scope. Intent is
  fully captured by the verbatim quote above.

## Sources

Per-skill findings with full citation lists:
`research/codebase.md` (repo grounding + empirical `vale` probes) and `research/public.md`
(Vale docs + ecosystem verification).

[1] "Templates — Vale CLI," vale.sh/docs/templates.
[2] "substitution — Vale CLI," docs.vale.sh/checks/substitution.
[3] "Styles — Vale CLI," vale.sh/docs/styles.
[4] "Packages — Vale CLI," vale.sh/docs/keys/packages.
[5] "CLI — Vale," vale.sh/docs/cli (no `--examples` flag).
[6] "GitHub — vale-cli/vale" (MIT; renamed from errata-ai) and "vale-cli/vale-action."
[7] "redhat-documentation/vale-at-red-hat," github.com/redhat-documentation/vale-at-red-hat
    (MIT; style package) and its generated reference guide.
[8] "Vale-MCP," github.com/ChrisChinchilla/Vale-MCP (MIT MCP server; no examples db).
[9] "VoltAgent/awesome-agent-skills" and "BehiSecc/awesome-claude-skills" (no Vale skill).
[10] Local repo files: `.vale.ini`, `scripts/vale-{check,fix}.sh`, `styles/DDD/*`,
     `styles/Google/{Passive,We}.yml`, `styles/.gitignore`, `.github/workflows/vale.yml`,
     `developer/tests/test_vale_lint_setup.py`, `DEVELOPMENT.md`; `vale 3.15.1` JSON/template
     probes.
