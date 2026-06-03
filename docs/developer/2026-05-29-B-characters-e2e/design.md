# `characters/e2e/` — Skill-Eval Harness for the `characters` Plugin

## Problem Statement

The `characters` plugin ships voice skills (`using-characters`, `voice-ailly`,
`voice-jacki`, `voice-jefri`, `voice-rupert`) that color human-facing prose
without changing methodology. None have regression coverage. A blurred
`voice-jefri` body that softens "brisk" toward "thoughtful" would silently shift
the model's tone across every developer-plugin response, and nothing in the repo
would catch it.

The shared blueprint at `docs/developer/2026-05-29-A-skill-evals/design.md`
specifies a per-plugin `e2e/` directory. The `characters` plugin's profile is
**Invocation + baseline**: no discovery axis (voice loading is rule-based on
plugin presence, not model-driven from `description:` frontmatter), and every
assertion is judge-based (voice fidelity is not structurally scoreable). This
design instantiates that profile, reconciled to the live skills and to the
proven `patterns/e2e/` sibling harness.

### Reconciliation from the blueprint

The blueprint's `characters` subsection named a four-skill cross-section of
`voice-jefri`, `voice-jacki`, `voice-rupert`, and `voice-david`. Two facts force
two adjustments, both recorded here so the design matches what is built:

1. **`voice-david` is not a skill.** The `characters/skills/` tree contains
   `voice-ailly`, not `voice-david`. The invocation arm loads each case's
   `SKILL.md` into the prefix; there is no file to load for a skill that does not
   exist, and the task constraint forbids creating one. The blueprint's own
   pairing rationale names "DDD voices Rupert vs Ailly" as a family, so
   **`voice-ailly` is the correct fourth case** — it is a real skill, it
   completes the stated pair, and it tests a voice in its own territory
   (`general` / `research`) rather than a tone with no backing skill. David —
   the user's own voice — is deferred until it ships as a skill.
2. **Live paths reach the skills through symlinks, not `..` segments.** The
   blueprint sketched assemblies pointing at `../../e2e/AGENTS.md` and
   `../skills/<name>/SKILL.md`. Ailly's project-rooted VFS clamps `..` to the
   project root, so those literal paths do not resolve. The `patterns/e2e/`
   harness solved this by placing two in-root symlinks — `base -> ../../e2e` and
   `skills -> ../skills` — and referencing `base/AGENTS.md` and
   `skills/<name>/SKILL.md`. This harness adopts the same mechanism.

## Prior Art

| Source | Role |
|---|---|
| `docs/developer/2026-05-29-A-skill-evals/design.md` | Shared blueprint. Defines harness shape, falsification convention, AGENTS.md template, ci.sh template, and per-plugin profiles. The `characters` subsection is the spec this document refines and reconciles. |
| `patterns/e2e/` (this repo) | The proven in-repo sibling, green as of 2026-06-03. Provides the verbatim, working shape for the symlink architecture, `assemblies/`, `evals/`, `ci.sh`, `.env`/`.gitignore`, and the `report` comparison gate. This harness inherits its mechanics and drops the discovery axis. |
| `ailly_two/skills/ailly-skill-eval/` (ailly repo) | The method skill: the two axes, the assertion palette, and falsification as an optional-but-applied layer. `references/method.md` is the long-form rationale. |
| `e2e/AGENTS.md` (this repo) | Shared coding-agent constitution. Loaded at position zero of every prefix in this harness via the `base` symlink. |
| `characters/skills/voice-{jefri,jacki,rupert,ailly}/SKILL.md` | The four source skills under test. Each is the authoritative description of its voice's personality, methodology, voice, and quirks. Judge prompts reference markers from these files. |
| `characters/skills/using-characters/SKILL.md` | Routing prefix. Loaded into every invocation assembly to establish the cast and the "voice colors prose, never overrides methodology" rule. |

## Metrics

The blueprint defines the harness-wide metrics. For this profile (no discovery
axis), only two pass rates and the gap matter.

| Metric | Source | Target |
|---|---|---|
| Invocation pass rate | `evals/invocation.yaml` (judge + tokens) | ≥ 0.8 |
| Baseline pass rate | `evals/baseline.yaml` (identical assertions) | as low as the prompt allows |
| **Falsification gap** | invocation − baseline, read as the `report` comparison `improved`/`regressed` buckets | `improved > 0` and `regressed == 0` |

The judge is the headline signal. If the baseline scores anywhere near the
invocation, the prompt is encoding the answer (the prompt tells the model to
write in Jefri's voice) rather than the skill earning the answer (the skill body
teaches the voice). Each invocation prompt is therefore *content-only* — it asks
for a status update, a sketch caption, a glossary entry, a research finding —
never "in Jefri's voice" or "as Rupert would". The skill loaded in the prefix is
what produces the voice; the prompt produces the artifact.

A null result is acceptable and expected for some cases: a capable model may
already reach the register a skill teaches, landing that case in
`unchanged_pass`. The gate is carried by the cases that do flip. Per the method,
a checker is never weakened to manufacture a false `improved`.

## Specification

### Layout

```
characters/e2e/
├── profile.md                            ← purpose + "Invocation + baseline" declaration
├── base -> ../../e2e                     ← symlink: shared coding-agent AGENTS.md, live
├── skills -> ../skills                   ← symlink: the live characters skill tree, graded as-is
├── assemblies/
│   ├── invocation.yaml                   ← matrix over voice-{jefri,jacki,rupert,ailly}
│   └── baseline.yaml                     ← identical matrix, strips kind: system entries
├── prompts/
│   └── invocation/
│       ├── voice-jefri.md
│       ├── voice-jacki.md
│       ├── voice-rupert.md
│       └── voice-ailly.md
├── evals/
│   ├── invocation.yaml                   ← judge + tokens per case
│   ├── baseline.yaml                     ← identical assertions
│   ├── scripts/                          ← .gitkeep only; no checkers in this profile
│   └── reports/                          ← gitignored; created by ailly eval/report
├── runs/                                 ← gitignored; created by ailly assemble
├── ci.sh                                 ← the feature test / driver
├── .env                                  ← gitignored; ANTHROPIC_API_KEY for run/eval
└── .gitignore
```

Notable omissions vs. the full skeleton: no `assemblies/discovery.yaml`, no
`prompts/discovery/`, no `evals/discovery.yaml`, no `fixtures/`, and **no
`context/AGENTS.md`**. The discovery axis is dropped per profile. The
`context/AGENTS.md` that `patterns/e2e/` uses to pin "the codebase is
TypeScript" is omitted because the output medium here is prose: each voice
defines the artifact shape it produces, so there is no language to pin. The
falsification grep therefore scans two files (`base/AGENTS.md` and
`profile.md`), not three.

### Symlinks and the live-paths convention

The two symlinks are how the live trees enter ailly's project-rooted VFS without
a vending step: ailly clamps `..` to the project root, but follows a symlink
*inside* the root out to the real file. Edit a voice in `../skills/` and the next
`assemble` grades the edit. `base -> ../../e2e` reaches the repo-root shared
`AGENTS.md`; `skills -> ../skills` reaches `characters/skills/`. Pinning an older
revision for a sweep is a `git worktree add` of the old SHA, not a vended copy.

### Assemblies

`assemblies/invocation.yaml`:

```yaml
name: invocation
model: claude-sonnet-4-6

matrix:
  skill:
    - voice-jefri
    - voice-jacki
    - voice-rupert
    - voice-ailly

prefix:
  - { kind: file,   path: base/AGENTS.md,                        cache: true }
  - { kind: file,   path: ./profile.md,                          cache: true }
  - { kind: system, path: skills/using-characters/SKILL.md,      cache: true }
  - kind: system
    path: "skills/{{ skill }}/SKILL.md"
    cache: true

conversation:
  - { role: user, path: "prompts/invocation/{{ skill }}.md" }
  - { role: assistant }
```

`assemblies/baseline.yaml`:

```yaml
name: baseline
model: claude-sonnet-4-6

matrix:
  skill:
    - voice-jefri
    - voice-jacki
    - voice-rupert
    - voice-ailly

prefix:
  - { kind: file, path: base/AGENTS.md,  cache: true }
  - { kind: file, path: ./profile.md,    cache: true }

conversation:
  - { role: user, path: "prompts/invocation/{{ skill }}.md" }
  - { role: assistant }
```

The matrix value `voice-{name}` is the literal directory name under
`characters/skills/`, so `{{ skill }}` interpolates cleanly into both the prefix
path (`skills/{{ skill }}/SKILL.md`) and the prompt path. Baseline strips both
`kind: system` entries (the `using-characters` routing prefix and the per-skill
voice file) and keeps both `kind: file` entries.

### profile.md

A single short markdown file appended to the prefix immediately after
`AGENTS.md` (reached via the `base` symlink). It declares (1) the harness's
purpose and (2) the axis profile. It must not name any of the four skills under
test, must not paraphrase any skill content, and must not contain the
`characters:voice-*` identifier pattern. Bare words (`voice`, `tone`, `prose`)
are permitted because they appear in any plausible coding-agent prefix. The
falsification grep (below) enforces this.

### Invocation Prompts

Each prompt asks for a concrete artifact the corresponding voice would naturally
produce in its plugin's territory. None of the four prompts names a character,
references a SKILL.md, or instructs the model on tone, register, or diction. The
voice must come entirely from the SKILL.md loaded in the prefix.

#### `prompts/invocation/voice-jefri.md`

> A new test is being added to the order-creation module. The test exercises the
> rule that a line item with a negative quantity must be rejected. Write a short
> rationale (3–4 sentences) for choosing the test name
> `rejects_negative_quantity_on_line_item` over the candidate `test_validation`.
> Address what the longer name buys, what the shorter name costs, and how the
> choice affects the next person who reads the failing-test output. Do not write
> the test body; the rationale is the deliverable.

Test-name reasoning is the centre of Jefri's territory (test-first, brisk,
narrates the cycle). The contrast between a descriptive and a generic name is
exactly what Jefri has a position on. Content-only — no "in a brisk voice".

#### `prompts/invocation/voice-jacki.md`

> A team needs a "project status" dashboard for a small engineering org (5–10
> contributors). The dashboard surfaces in-flight PRs, current sprint health, and
> any blocked tasks. Propose three rough layout sketches as short captions. Use
> plain ASCII for each sketch (boxes, arrows, columns — no images). For each
> sketch, name what it optimizes for and what it gives up in one short clause. Do
> not commit to one option; the comparison is the deliverable.

Three rough options, low-fidelity ASCII, named trade-offs, deliberate refusal to
pick — Jacki's methodology. The ASCII-sketches constraint forces the
bracket-diagram quirk without naming it. The prompt asks for three options
because that is what the artifact is; the *voice markers* (the sigh, the
`[A] -> [B] -> [C]` margin diagram, the skepticism toward "obviously," the
refusal to discuss one option in isolation) are what the judge keys on, and only
the skill teaches those.

#### `prompts/invocation/voice-rupert.md`

> A logistics team is introducing the term `OrderManifest` to its domain. Write a
> glossary entry that includes (1) the term, (2) a one- or two-sentence
> definition that names what it is and what it is not, (3) one synonym or
> near-miss the team should disambiguate from (for example, `PackingList`,
> `Shipment`, or `BillOfLading`), and (4) a citation to a relevant chapter of a
> classic DDD source. The entry will be appended to the team's glossary file.

Glossary entries are Rupert's home turf — the chapter citation, the gentle
disambiguation, the careful naming. The prompt names the artifact ("glossary
entry") but not the voice; the citation-by-chapter convention should appear
because the skill body teaches it.

#### `prompts/invocation/voice-ailly.md`

> Two records in the project's research log bear on a past decision: why the
> nightly export job replaced the old hourly one this past March. Record one is
> an internal Linear ticket (NOM-412) stating the change was made "to cut
> warehouse load during business hours." Record two is a public AWS cost blog the
> team cited for the projected savings (about \$1,900 per month). A teammate asks:
> "Why did we move the export to nightly?" Write a 3–4 sentence answer they can
> paste into the research log. The two records do not fully agree on the primary
> reason; keep them straight.

A short attributed research finding is the canonical Ailly artifact (her
territory is `general` / `research`). The "keep them straight" framing invites
distinguishing the two sources without instructing the model to "attribute every
claim," so the *register* — cool, professional, clipped, notebook-referencing,
commas not em dashes, no pleasantries — is what the judge discriminates on, and
that register is taught only by the skill.

### Judge Prompts

Each judge prompt is a single declarative paragraph naming three or four
idiolect markers from the source SKILL.md. The judge evaluates whether the
response exhibits the *family* of marker; it does not require exact token
matches. Both `evals/invocation.yaml` and `evals/baseline.yaml` carry identical
judge prompts and identical token budgets per case. The pairing is what makes
the falsification gap legible: same judge, same budget, only the skill prefix
differs.

#### `voice-jefri` judge

> The response reads in a brisk, test-first, methodical register. Verbs lead
> sentences ("write the failing test," "watch it fail," "narrate the cycle"). The
> rationale treats the longer test name as load-bearing information that survives
> into the failure output, and treats the shorter name as a shortcut that pays
> interest later. At least one of: a goat reference, a "loaf achieved"-style
> one-shot whimsy, a refusal to skip a step, or an explicit naming of
> red/green/refactor. No hedging, no "I will attempt to," no decorative apology.

#### `voice-jacki` judge

> The response produces exactly three labelled options ("option one," "option
> two," "option three" or equivalent). Each option includes a low-fidelity ASCII
> sketch (boxes, arrows, columns) and one clause naming what it optimizes for and
> what it gives up. The author does not pick a single option; the comparison
> itself is the deliverable. At least one of: an explicit "(a sigh.)"
> parenthetical, a bracket-diagram pattern like `[A] -> [B] -> [C]`, a refusal to
> discuss one option in isolation, or skepticism about "obviously." No premature
> commitment to a favorite.

#### `voice-rupert` judge

> The response is a single glossary entry, measured and precise. It names the
> term, defines what it is and what it is not, disambiguates from at least one
> neighbouring term, and cites a classic DDD source *by chapter*, never by page
> number (e.g., "Evans, chapter four" or "Vernon, the chapter on aggregates").
> The disambiguation is kind rather than corrective. The response uses the name
> of the concept rather than a pronoun where the pronoun would be ambiguous. No
> lecturing tone; no exhaustive scope creep beyond the entry.

#### `voice-ailly` judge

> The response is a short research finding in a cool, professional, Parisian
> register: short complete sentences, commas rather than em dashes, no
> pleasantries ("happy to help," "great question") and no warm sign-off. The two
> records are kept distinct rather than blended into one unsourced paragraph, and
> the finding does not over-claim a single primary reason the records disagree
> on. At least one of: a notebook reference ("Per my notes," "Filed under…," "the
> Linear ticket, not the blog"), a precise figure or date used in place of a
> vague term, a removed or refused hedge, or a single measured compliment used at
> most once. The response opens on the subject and closes on the finding, not on
> a greeting or a goodbye.

### Token Budgets

Budgets are on `metric: output` — the model's generated tokens only, not the
`total` (which would include the prefix and so differ between the arms, since the
invocation arm loads the skill bodies). The budget is identical across the
invocation and baseline arms so a size difference reads as an
`improved`/`regressed` signal rather than a budget artifact, per the method.

| Case | Budget (`output` tokens) | Rationale |
|---|---|---|
| `voice-jefri` | `< 1000` | Brisk by design; a 3–4 sentence rationale that runs long has padding. |
| `voice-jacki` | `< 2000` | Three labelled options with ASCII sketches and trade-off clauses run longer. |
| `voice-rupert` | `< 1000` | Measured but compact: a glossary entry is short by convention. |
| `voice-ailly` | `< 1000` | A 3–4 sentence finding; Ailly does not pad. |

Budgets are a guard against the padding failure mode (a passable voiced
paragraph followed by generic prose), not the primary discriminator — the judge
is. They are set generously enough that a faithful voiced response passes on both
arms; if the live run shows the invocation arm failing a budget, the budget is
loosened rather than the judge weakened. Empirical values are recorded after the
first green run.

### `evals/invocation.yaml` (shape)

```yaml
name: invocation
cases:
  - name: voice-jefri
    assertions:
      - { type: judge, prompt: "<voice-jefri judge text, above>" }
      - { type: tokens, metric: output, op: "<", value: 1000 }
  - name: voice-jacki
    assertions:
      - { type: judge, prompt: "<voice-jacki judge text, above>" }
      - { type: tokens, metric: output, op: "<", value: 2000 }
  - name: voice-rupert
    assertions:
      - { type: judge, prompt: "<voice-rupert judge text, above>" }
      - { type: tokens, metric: output, op: "<", value: 1000 }
  - name: voice-ailly
    assertions:
      - { type: judge, prompt: "<voice-ailly judge text, above>" }
      - { type: tokens, metric: output, op: "<", value: 1000 }
```

`evals/baseline.yaml` is identical in case names, judge prompts, and token
budgets; only the upstream assembly differs (no skills loaded).

### `evals/scripts/`

An empty directory with a `.gitkeep` file. Voice scoring is judge-only per
profile. If a structural rule emerges (e.g., "Jacki's response must contain
exactly three labelled options"), a placeholder script can land here in a
follow-up session matching the patterns-eval convention.

### `ci.sh`

Adapted from `patterns/e2e/ci.sh` — the proven driver — with these changes:

1. **`$AILLY` indirection.** The binary is invoked as `${AILLY:-ailly}`, so a
   contributor whose binary is not on `$PATH` runs
   `AILLY=/path/to/ailly_two ./ci.sh`. (The built binary in this environment is
   `ailly_two`, not `ailly`.)
2. **`expected_count()`** — drop `discovery`; `invocation: 4`, `baseline: 4`.
3. **Suites driven** — `baseline` and `invocation` only; no discovery assemble /
   run / eval / report. Keep the `report` comparison step.
4. **`repo_root`** — `${project_dir}/../..` (this harness is two levels under the
   repo root), and `cd "${repo_root}"` before invoking ailly so the symlinks
   resolve relative to the project.
5. **Hard-fail without credentials.** If neither `ANTHROPIC_API_KEY` nor a
   project `.env` is present, the script exits non-zero. The live half exercises
   the model and the falsification gate; there is no assemble-only success path.
   (This matches `patterns/e2e/ci.sh` and overrides the blueprint's earlier
   "skip the run phase" note — a regression gate that can pass without ever
   calling the model proves nothing.)
6. **Falsification grep** before assembly:

   ```bash
   grep_leak() {
     local abs="$1"
     if [[ -f "${abs}" ]] && grep -Eq 'characters:voice-(jefri|jacki|rupert|ailly)' "${abs}"; then
       echo "FAIL: ${abs} leaks a characters:voice-* identifier into a baseline-arm file." >&2
       exit 1
     fi
   }
   grep_leak "${repo_root}/e2e/AGENTS.md"
   grep_leak "${project_dir}/profile.md"
   ```

The `report` comparison step (`ailly report <baseline-id> <invocation-id>`)
produces `improved / regressed / unchanged_pass / unchanged_fail` between the
baseline and invocation runs, and the script gates on `improved > 0 &&
regressed == 0`.

### `.env` and `.gitignore`

`.env` carries the `ANTHROPIC_API_KEY` for `run`/`eval` and is gitignored. It is
copied verbatim from the canonical token file; its contents are never read into
the session. `.gitignore` mirrors `patterns/e2e/.gitignore`:

```
runs/
evals/reports/
evals/judges/
evals/scripts/__pycache__/
.env
```

## Alternatives

**Keeping `voice-david` in the matrix.** Rejected. No `voice-david/SKILL.md`
exists, the task forbids creating one, and the invocation arm cannot load a
prefix file that is not there. `voice-ailly` is a live skill that completes the
blueprint's own "Rupert vs Ailly" DDD-voice pair and tests a voice in its own
territory.

**Naming the character in the invocation prompt** ("Write a status update in
David's voice"). Rejected. This collapses the falsification gap immediately — the
baseline, with no skill loaded, would still attempt the voice from the prompt
alone and the judge would have nothing to discriminate. Content-only prompts
force the skill to do the work.

**`metric: total` token budgets** (as the blueprint sketch and the earlier draft
used). Rejected. `total` counts the prefix, and the invocation arm's prefix is
larger by exactly the skill bodies it loads — so an identical-output response
would score a larger `total` on the invocation arm purely as an artifact of the
skill being present. `metric: output` measures only the model's generated text,
keeping the budget fair across arms.

**A `context/AGENTS.md` language pin (as in `patterns/e2e/`).** Rejected for this
profile. Patterns pins TypeScript because its artifacts are code. Voice artifacts
are prose whose shape each skill defines for itself; pinning a language would be
meaningless and would add a third file to the leak surface for no benefit.

**A single combined prompt rendered four times.** Rejected. The four voices live
in different territories — TDD reasoning for Jefri, design comparisons for Jacki,
glossary work for Rupert, research findings for Ailly. A territory-neutral prompt
would test voice in a vacuum the skills never describe themselves operating in.

**Structural Python checkers for each voice.** Rejected for this iteration. Some
markers are mechanically detectable ("loaf achieved" substring, three lines
starting with "option," `chapter` near a classicist surname, "Per my notes").
Judge-only is sufficient for the first run; a follow-up session can add
placeholder scripts matching the patterns-eval `check_<skill>.py` shape.

**Looser token budgets** (`< 5000` per case). Rejected. The padding failure mode
is precisely what budgets exist to catch; loose budgets let a model produce one
voiced paragraph and then drift into generic prose without consequence.

**Skipping the run phase without credentials** (the blueprint's ci.sh note).
Rejected in favour of the `patterns/e2e/` hard-fail. A gate that can go green
without ever calling the model never exercises the falsification comparison, so a
green run would be vacuous.

## Summary

Four invocation prompts and four judge prompts exercise the four live voice
skills in their natural territories — test-name reasoning (Jefri), three-option
layout sketches (Jacki), a glossary entry (Rupert), an attributed research
finding (Ailly). Each prompt is content-only; the skill prefix is what colors the
prose. Each judge names three or four idiolect markers from the source SKILL.md
so the family of voice is verified without exact token matches. Token budgets are
on `metric: output` and tight per case to catch padding. The harness reaches the
live skills through two in-root symlinks (`base`, `skills`) because ailly's VFS
clamps `..`. Baseline runs the same prompts with no skill prefix; the
`report`-comparison falsification gap (`improved > 0`, `regressed == 0`) is the
headline metric. `ci.sh` drives assemble → run → eval → report for the
`baseline` and `invocation` suites and enforces the gate.

**Deferred decisions.**

- Python check scripts for structurally detectable markers
  (`evals/scripts/check_voice_*.py`). Deferred; `evals/scripts/` ships with a
  `.gitkeep` only.
- `voice-david` as a fifth case, once it ships as a skill.
- Score thresholds for the judge assertion. Inherits ailly's default until
  empirical data motivates a per-case override.
- Empirical token-budget calibration. The values above are starting points;
  recorded values land in `plan.md` after the first green run.
- Model-version sweep. `claude-sonnet-4-6` pinned per blueprint default.
- Top-level GitHub Actions workflow that runs every plugin's `ci.sh`.
