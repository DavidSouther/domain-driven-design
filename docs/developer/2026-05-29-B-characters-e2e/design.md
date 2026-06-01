# `characters/e2e/` — Skill-Eval Harness for the `characters` Plugin

*DRAFT 2026-05-29*

## Problem Statement

The `characters` plugin ships six voice skills (`using-characters`, `voice-ailly`, `voice-david`, `voice-jacki`, `voice-jefri`, `voice-rupert`) that color human-facing prose without changing methodology. None have regression coverage. A blurred `voice-jefri` body that softens "brisk" toward "thoughtful" would silently shift the model's tone across every developer-plugin response, and nothing in the repo would catch it.

The shared blueprint at `docs/developer/2026-05-29-A-skill-evals/design.md` specifies a per-plugin `e2e/` directory. The `characters` plugin's profile is **Invocation + baseline**: no discovery axis (voice loading is rule-based on plugin presence, not model-driven from `description:` frontmatter), and every assertion is judge-based (voice fidelity is not structurally scoreable). This design instantiates that profile.

## Prior Art

| Source | Role |
|---|---|
| `docs/developer/2026-05-29-A-skill-evals/design.md` | Shared blueprint. Defines harness shape, falsification convention, AGENTS.md template, ci.sh template, and per-plugin profiles. The `characters` subsection is the authoritative spec this document refines. |
| `ailly_two/e2e/patterns-eval/` (in the ailly repo) | The only working harness so far. Provides verbatim shape for `assemblies/`, `evals/`, `ci.sh`, and the placeholder-script convention. Uses vended-context paths; this harness uses live `../skills/...` paths per blueprint. |
| `e2e/AGENTS.md` (this repo) | Shared coding-agent constitution. Loaded at position zero of every prefix in this harness. |
| `characters/skills/voice-{jefri,jacki,rupert,david}/SKILL.md` | The four source skills under test. Each is the authoritative description of its voice's personality, methodology, voice, and quirks. Judge prompts reference markers from these files. |
| `characters/skills/using-characters/SKILL.md` | Routing prefix. Loaded into every invocation assembly to establish the cast and the "voice colors prose, never overrides methodology" rule. |

## Metrics

The blueprint defines the harness-wide metrics. For this profile (no discovery axis), only two pass rates and the gap matter.

| Metric | Source | Target |
|---|---|---|
| Invocation pass rate | `evals/invocation.yaml` (judge + tokens) | ≥ 0.8 |
| Baseline pass rate | `evals/baseline.yaml` (identical assertions) | as low as the prompt allows |
| **Falsification gap** | invocation − baseline | ≥ 0.5 |

The judge is the headline signal. If the baseline scores anywhere near the invocation, the prompt is encoding the answer (the prompt is telling the model to write in Jefri's voice) rather than the skill earning the answer (the skill body is what teaches the voice). Each invocation prompt is therefore *content-only* — it asks for a status update, a sketch caption, a glossary entry, a test-name rationale — never "in Jefri's voice" or "as Rupert would". The skill loaded in the prefix is what produces the voice; the prompt produces the artifact.

## Specification

### Layout

```
characters/e2e/
├── profile.md                            ← purpose + "Invocation + baseline" declaration
├── assemblies/
│   ├── invocation.yaml                   ← matrix over voice-{jefri,jacki,rupert,david}
│   └── baseline.yaml                     ← identical matrix, strips kind: system entries
├── prompts/
│   └── invocation/
│       ├── voice-jefri.md
│       ├── voice-jacki.md
│       ├── voice-rupert.md
│       └── voice-david.md
├── evals/
│   ├── invocation.yaml                   ← judge + tokens per case
│   ├── baseline.yaml                     ← identical assertions
│   ├── scripts/                          ← empty placeholder dir; no checkers in this profile
│   └── reports/                          ← created by ailly eval
├── runs/                                 ← created by ailly assemble
└── ci.sh                                 ← adapted from patterns-eval/ci.sh
```

Notable omissions vs. the full skeleton: no `assemblies/discovery.yaml`, no `prompts/discovery/`, no `evals/discovery.yaml`, no `fixtures/`. The discovery axis is dropped per profile; voice cases are stateless, so no fixtures are needed.

### Assemblies

Per the blueprint's live-paths convention, both assemblies reference SKILL.md sources directly via `../skills/{name}/SKILL.md`.

`assemblies/invocation.yaml`:

```yaml
name: invocation
model: claude-sonnet-4-6

matrix:
  skill:
    - voice-jefri
    - voice-jacki
    - voice-rupert
    - voice-david

prefix:
  - { kind: file,   path: ../../e2e/AGENTS.md,                           cache: true }
  - { kind: file,   path: ./profile.md,                                  cache: true }
  - { kind: system, path: ../skills/using-characters/SKILL.md,           cache: true }
  - kind: system
    path: "../skills/{{ skill }}/SKILL.md"
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
    - voice-david

prefix:
  - { kind: file, path: ../../e2e/AGENTS.md,  cache: true }
  - { kind: file, path: ./profile.md,         cache: true }

conversation:
  - { role: user, path: "prompts/invocation/{{ skill }}.md" }
  - { role: assistant }
```

The matrix value `voice-{name}` is the literal directory name under `characters/skills/`, so `{{ skill }}` interpolates cleanly into both the prefix path and the prompt path. Baseline strips both `kind: system` entries (the `using-characters` routing prefix and the per-skill voice file) and keeps both `kind: file` entries.

### profile.md

A single short markdown file appended to the prefix immediately after `AGENTS.md`. It declares (1) the harness's purpose and (2) the axis profile. It must not name any of the four skills under test, must not paraphrase any skill content, and must not contain the `characters:voice-*` identifier pattern. Bare words (`voice`, `tone`, `prose`) are permitted because they appear in any plausible coding-agent prefix.

Proposed text (~80 words):

> This directory exercises the `characters` skill plugin. The harness runs the **Invocation + baseline** axis profile only: each case asks the model to produce a concrete artifact (a status update, a caption, an entry, a rationale), and a paired baseline runs the same prompt with no skill prefix. The falsification gap between the two pass rates is the headline signal. Judge assertions evaluate whether the response reads in the expected register; token budgets are the only quantitative guard against padding.

### Invocation Prompts

Each prompt asks for a concrete artifact the corresponding voice would naturally produce in its plugin's territory. None of the four prompts names a character, references a SKILL.md, or instructs the model on tone, register, or diction. The voice must come entirely from the SKILL.md loaded in the prefix.

#### `prompts/invocation/voice-jefri.md`

> A new test is being added to the order-creation module. The test exercises the rule that a line item with a negative quantity must be rejected. Write a short rationale (3–4 sentences) for choosing the test name `rejects_negative_quantity_on_line_item` over the candidate `test_validation`. Address what the longer name buys, what the shorter name costs, and how the choice affects the next person who reads the failing-test output. Do not write the test body; the rationale is the deliverable.

Why this case: test-name reasoning is the centre of Jefri's territory (test-first, brisk, narrates the cycle). The contrast between a descriptive name and a generic one is exactly the kind of thing Jefri has a position on. The prompt is content-only — it does not say "in a brisk voice" or "as Jefri would" — so any disciplined-TDD diction in the response comes from the skill body, not the prompt.

#### `prompts/invocation/voice-jacki.md`

> A team needs a "project status" dashboard for a small engineering org (5–10 contributors). Propose three rough layout sketches as short captions. Use plain ASCII for each sketch (boxes, arrows, columns — no images). For each sketch, name what it optimizes for and what it gives up in one short clause. Do not commit to one option; the comparison is the deliverable.

Why this case: three rough options labelled option one / two / three, low-fidelity ASCII, named trade-offs, deliberate refusal to pick — this is exactly Jacki's methodology. The ASCII-sketches constraint forces the bracket-diagram quirk (`[A] -> [B] -> [C]`) without naming it.

#### `prompts/invocation/voice-rupert.md`

> A logistics team is introducing the term `OrderManifest` to its domain. Write a glossary entry that includes (1) the term, (2) a one- or two-sentence definition that names what it is and what it is not, (3) one synonym or near-miss the team should disambiguate from (e.g., `PackingList`, `Shipment`), and (4) a citation to a relevant chapter of a classic DDD source. The entry will be appended to the team's glossary file.

Why this case: glossary entries are Rupert's home turf — the chapter citation, the gentle disambiguation, the careful naming. The prompt names the artifact ("glossary entry") but not the voice; the citation-by-chapter convention should appear because the skill body teaches it.

#### `prompts/invocation/voice-david.md`

> Write a one-paragraph Slack message to the `#sw-connect` channel giving a status update on PR #482. The PR adds a search side panel to Connect with channel-and-chart results, ready for review. There is one open question: deep-linking to a specific tab and scroll position is working in the prototype but the URL scheme has not been agreed with the Core team. Lead with the bottom line; the rest of the structure is your call.

Why this case: a Slack status update is the canonical David artifact. The "lead with the bottom line" hint nudges toward Short/Long answer or TL;DR (both are in the skill body) without naming either; the open-question detail invites a parenthetical aside or asterisk footnote. The prompt does not say "informal" or "use parentheticals".

### Judge Prompts

Each judge prompt is a single declarative paragraph naming three or four idiolect markers from the source SKILL.md. The judge evaluates whether the response exhibits the *family* of marker; it does not require exact token matches. This shape mirrors patterns-eval's judge prompts (declarative description of the artifact the response should be).

Both `evals/invocation.yaml` and `evals/baseline.yaml` carry identical judge prompts and identical token budgets per case. The pairing is what makes the falsification gap legible: the same judge, same budget, only the skill prefix differs.

#### `voice-jefri` judge

> The response reads in a brisk, test-first, methodical register. Verbs lead sentences ("write the failing test," "watch it fail," "narrate the cycle"). The rationale treats the longer test name as load-bearing information that survives into the failure output, and treats the shorter name as a shortcut that pays interest later. At least one of: a goat reference, a "loaf achieved"-style one-shot whimsy, a refusal to skip a step, or an explicit naming of red/green/refactor. No hedging, no "I will attempt to," no decorative apology.

#### `voice-jacki` judge

> The response produces exactly three labelled options ("option one," "option two," "option three" or equivalent). Each option includes a low-fidelity ASCII sketch (boxes, arrows, columns) and one clause naming what it optimizes for and what it gives up. The author does not pick a single option; the comparison itself is the deliverable. At least one of: an explicit "(a sigh.)" parenthetical, a bracket-diagram pattern like `[A] -> [B] -> [C]`, a refusal to discuss one option in isolation, or skepticism about "obviously." No premature commitment to a favorite.

#### `voice-rupert` judge

> The response is a single glossary entry, measured and precise. It names the term, defines what it is and what it is not, disambiguates from at least one neighbouring term, and cites a classic DDD source *by chapter*, never by page number (e.g., "Evans, chapter four" or "Vernon, the chapter on aggregates"). The disambiguation is kind rather than corrective. The response uses the name of the concept rather than a pronoun where the pronoun would be ambiguous. No lecturing tone; no exhaustive scope creep beyond the entry.

#### `voice-david` judge

> The response is a Slack message in an informal-technical register. It leads with the bottom line (e.g., "Short answer:" / "Long answer:" or a "TL;DR:" one-liner) and follows with structured detail. At least one of: a numbered concrete workflow list, an asterisk-footnote aside, a nested parenthetical that the author self-monitors, a `:slightly_smiling_face:` or `:wink:` doing tonal work, or a "spitball" framing for the open question. No throat-clearing preamble, no formal sign-off, no hedging around the conclusion that the PR is ready.

### Token Budgets

| Case | Budget (total tokens) | Rationale |
|---|---|---|
| `voice-jefri` | `< 2500` | Brisk by design; a 3–4 sentence rationale that runs long has padding. |
| `voice-jacki` | `< 3500` | Three labelled options with ASCII sketches and trade-off clauses. |
| `voice-rupert` | `< 3000` | Measured but compact: a glossary entry is short by convention. |
| `voice-david` | `< 3000` | One paragraph plus optional footnote; Slack messages are short. |

Budgets are deliberately tight. Voice fidelity is judge-scored; the budget catches a different failure mode — the model successfully imitating the voice for the first paragraph and then padding with generic prose. Both invocation and baseline use the same per-case budget so a verbose baseline fails on tokens as well as on judge.

### `evals/invocation.yaml` (sketch)

```yaml
name: invocation
cases:
  - name: voice-jefri
    assertions:
      - type: judge
        prompt: |
          <judge text for voice-jefri, above>
      - { type: tokens, metric: total, op: "<", value: 2500 }

  - name: voice-jacki
    assertions:
      - type: judge
        prompt: |
          <judge text for voice-jacki, above>
      - { type: tokens, metric: total, op: "<", value: 3500 }

  - name: voice-rupert
    assertions:
      - type: judge
        prompt: |
          <judge text for voice-rupert, above>
      - { type: tokens, metric: total, op: "<", value: 3000 }

  - name: voice-david
    assertions:
      - type: judge
        prompt: |
          <judge text for voice-david, above>
      - { type: tokens, metric: total, op: "<", value: 3000 }
```

`evals/baseline.yaml` is byte-identical for case names, judge prompts, and token budgets; only the assembly upstream differs (no skills loaded).

### `evals/scripts/`

An empty directory with a `.gitkeep` file. Voice scoring is judge-only per profile. If a structural rule emerges (e.g., "Jacki's response must contain exactly three labelled options"), a placeholder script can land here in a follow-up session matching the patterns-eval convention.

### `ci.sh`

Copy from `ailly_two/e2e/patterns-eval/ci.sh` with the following modifications per the blueprint:

1. **`expected_count()` table** — drop `discovery`; keep `invocation: 4` and `baseline: 4`.
2. **Suites driven** — remove `assemble_suite discovery`, `run_suite discovery`, `eval_suite discovery`, and `report_discovery`. Keep `baseline` and `invocation` and the `report_comparison` step (this is where the falsification gap is reported).
3. **`repo_root`** — `${project_dir}/../..` (this harness is two levels under the repo root, not one as in the ailly repo).
4. **`ailly` invocation** — `ailly -p "${project_dir}" assemble <suite>` rather than `cargo run`, per blueprint.
5. **Falsification grep** — add the blueprint's grep step before assembly:

   ```bash
   if grep -Eq 'characters:voice-(jefri|jacki|rupert|david)' \
        "${repo_root}/e2e/AGENTS.md" "${project_dir}/profile.md"; then
     echo "FAIL: falsification leak — skill identifier present in AGENTS.md or profile.md" >&2
     exit 1
   fi
   ```

The `report_comparison` step (already in the patterns-eval template) is the headline output: it produces `improved / regressed / unchanged_pass / unchanged_fail` between the baseline and invocation runs. The falsification gap is `improved − regressed` over the four cases.

## Alternatives

**Naming the character in the invocation prompt** ("Write a status update in David's voice"). Rejected. This collapses the falsification gap immediately — the baseline, with no skill loaded, would still attempt David's voice from the prompt alone and the judge would have nothing to discriminate. Content-only prompts force the skill to do the work.

**A single combined prompt rendered four times** (one prompt asking for "a short artifact in the loaded voice"). Rejected. The four voices live in different territories — TDD reasoning for Jefri, design comparisons for Jacki, glossary work for Rupert, Slack updates for David. A territory-neutral prompt would test voice in a vacuum the skills never describe themselves operating in, and would punish the skills for not generalising beyond their stated scope.

**Structural Python checkers for each voice.** Rejected for this iteration. Some markers are mechanically detectable ("loaf achieved" substring, three lines starting with "option", "Short answer:" / "Long answer:" pair, `chapter` near a classicist surname). A future session could add placeholder scripts matching patterns-eval's `check_<skill>.py` shape; the seed prompt explicitly defers this and judge-only is sufficient for the first run.

**Looser token budgets** (`< 5000` per case). Rejected. The padding failure mode is precisely what budgets exist to catch; loose budgets allow a model to produce one passable voice-coloured paragraph and then drift into generic helpful-assistant prose without consequence.

**Including `voice-ailly` in the matrix.** Rejected for this iteration. The seed prompt names exactly four cases (`voice-jefri`, `voice-jacki`, `voice-rupert`, `voice-david`). The blueprint's `characters` subsection explicitly identifies these four as the minimal cross-section: two paired families (developer voices Jefri vs Jacki, DDD voices Rupert vs Ailly) and David. Ailly is the natural fifth case but is deferred; voice-david is in this set because the user's own voice tests a different surface (drafting on the user's behalf, not plugin-tied loading).

**Multi-turn conversations** (assistant pre-fill setting context, then user prompt). Rejected per blueprint convention. Single-shot prompts with all context in the prefix keep the conversation file shape consistent with patterns-eval.

## Summary

Four invocation prompts and four judge prompts that exercise the four voice skills in their natural territories — test-name reasoning (Jefri), three-option layout sketches (Jacki), a glossary entry (Rupert), a Slack status update (David). Each prompt is content-only; the skill prefix is what colors the prose. Each judge prompt names three or four idiolect markers from the source SKILL.md so the family of voice can be verified without requiring exact token matches. Token budgets are tight per case to catch padding. Baseline runs the same prompts with no skill prefix; the falsification gap between the two pass rates is the headline metric.

The harness instantiates the blueprint's "Invocation + baseline" profile without modification.

**Deferred decisions.**

- Python check scripts for structurally detectable markers (`evals/scripts/check_voice_*.py`). Deferred per seed prompt. The `evals/scripts/` directory ships with a `.gitkeep` only.
- `voice-ailly` as a fifth case. Deferred. The minimal cross-section names four; ailly is the natural extension once judges are calibrated.
- Score thresholds for the judge assertion. Inherits ailly's default until empirical data motivates a per-case override.
- Model-version sweep. `claude-sonnet-4-6` pinned per blueprint default.
- Top-level GitHub Actions workflow that runs every plugin's `ci.sh`. Per-plugin `ci.sh` is independent; the matrix is a follow-up at the repo root.
- Whether `profile.md` should differ between the invocation and baseline runs to further reduce leakage (currently identical). The blueprint specifies a single shared `profile.md`; deviation would need its own design step.
