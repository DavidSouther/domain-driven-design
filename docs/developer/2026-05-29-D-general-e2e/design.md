# `general/e2e/` Skill-Eval Harness

*Finalized 2026-06-03*

## Problem Statement

The `general` plugin ships seven skills (`conversation`, `dispatching-parallel-agents`, `review`, `using-general`, `writing-paired-skills`, `writing-pattern-skills`, `writing-skills`) and has no regression coverage. The three `writing-*` skills sit in adjacent description space — they all open with skill-authoring vocabulary — so a small edit to any one of them can silently route the model to the wrong skill. The harness needs to catch that drift. It also needs to catch invocation regressions (structural changes to the artifacts the four cross-section skills produce) and to demonstrate that the skills themselves, not the prompt, are doing the work.

## Prior Art

- The shared blueprint in [`docs/developer/2026-05-29-A-skill-evals/design.md`](../2026-05-29-A-skill-evals/design.md) defines the harness shape, the three-axis profile, the live-`SKILL.md` reference convention, and the falsification gap as the headline metric. The `general` subsection under "Specification — Per-Plugin Profiles" lists the minimal cross-section (4), the five discovery cases, the four invocation cases, and the wrinkles.
- `ailly_two/e2e/patterns-eval/` is the working reference harness. The new harness inherits its file layout almost verbatim, replacing the `context/skills/` vended tree with live `../skills/...` paths and using the shared `e2e/AGENTS.md` plus a short per-plugin `profile.md` in place of patterns-eval's terser standalone `AGENTS.md`.
- The four cross-section SKILL.md files themselves are the source of truth for both the structural assertions (their published section conventions) and the discovery descriptions the harness exercises.

## Metrics

The harness reports the three blueprint pass rates and the falsification gap. Target windows for this harness:

| Metric | Source | Target |
|---|---|---|
| Discovery pass rate | `evals/discovery.yaml` | ≥ 0.9 (5 cases, expect 4–5 passing) |
| Invocation pass rate | `evals/invocation.yaml` | ≥ 0.8 (4 cases, expect ≥ 3 passing) |
| Baseline pass rate | `evals/baseline.yaml` | as low as the prompt allows |
| **Falsification gap** | invocation − baseline | ≥ 0.5 |

The discovery pass rate is the headline regression signal for the writing-* triplet. The three paired-blur cases divide the description-space pairwise; a directional edit that moves one description toward an adjacent one (drift, not weakening) should flip exactly one case from pass to fail. An edit that uniformly weakens a description across the board (drops the discriminating anchor without adding a new one) can legitimately flip both cases that depend on that skill — that is the harness reporting a real loss of selection signal, not a prompt-overlap bug. If a *directional* edit flips two cases, the prompts have over-anchored and the blurs need to be re-separated.

## Implementation Decisions (finalization)

Three refinements settled at finalization, all tightening the harness toward the [`ailly-skill-eval`](../../../../ailly/ailly_two/skills/ailly-skill-eval/SKILL.md) method this repo's blueprint generalizes:

1. **Discovery loads a live `disclosure.md`.** The blueprint draft put only `using-general/SKILL.md` in the discovery prefix and relied on its paraphrased "General Skills" table as the routing surface. The eval method is explicit that the discovery surface under test must be the *real* concatenated `description:` frontmatter — that is what ships and what regresses. The discovery prefix therefore loads a `disclosure.md` (the verbatim frontmatter of the five candidate skills) *in addition to* `using-general/SKILL.md` (the bootstrap routing skill), matching `patterns-eval` exactly. To honour the live-paths philosophy, `disclosure.md` is regenerated from the live `../skills/*/SKILL.md` frontmatter by `evals/scripts/gen_disclosure.sh` at the top of `ci.sh`, so a description edit takes effect on the next run. A committed copy exists so a standalone `assemble` works without `ci.sh`.

2. **Real check scripts, not placeholders.** The blueprint deferred concrete checker bodies to "the upstream eval-script slice." This harness must actually evaluate property #2 (the skill improves alignment over baseline) and clear the falsification gate (`improved > 0`), so the four `check_*.py` scripts are written in full now. Each encodes its skill's structural rules — drawn from that skill's body and "Common Mistakes" — as an ordered rule list following the `patterns-eval` checker contract: read the candidate on stdin, exit 0 when every rule holds, else print one line to stdout and exit 1, leaving stderr untouched.

3. **Concrete Ailly invocation.** `ailly` is not on `PATH`; it is the `ailly_two` Cargo crate. `ci.sh` invokes the built binary through an overridable `AILLY` variable (default: the `ailly_two` debug binary), not `cargo run`, to avoid a rebuild per call. The Anthropic credential is supplied by copying `ailly_two/.env` to `general/e2e/.env` (git-ignored); `ailly` loads it from the `-p` project directory.

## Specification

### Layout

```
general/e2e/
├── profile.md
├── disclosure.md            # generated: verbatim frontmatter of the 5 discovery candidates
├── .env                     # git-ignored; copied from ailly_two/.env
├── assemblies/
│   ├── discovery.yaml
│   ├── invocation.yaml
│   └── baseline.yaml
├── prompts/
│   ├── discovery/
│   │   ├── writing-skills-vs-writing-pattern-skills.md
│   │   ├── writing-skills-vs-writing-paired-skills.md
│   │   ├── writing-paired-skills-vs-writing-pattern-skills.md
│   │   ├── review-trigger.md
│   │   └── conversation-vs-review.md
│   └── invocation/
│       ├── writing-skills.md
│       ├── writing-paired-skills.md
│       ├── writing-pattern-skills.md
│       ├── review.md
│       └── conversation.md
├── evals/
│   ├── discovery.yaml
│   ├── invocation.yaml
│   ├── baseline.yaml
│   ├── scripts/
│   │   ├── _checker_utils.py            # shared: extract_code / fenced-markdown split / fail()
│   │   ├── gen_disclosure.sh            # regenerates disclosure.md from live SKILL.md frontmatter
│   │   ├── check_writing_skills.py
│   │   ├── check_writing_paired_skills.py
│   │   ├── check_writing_pattern_skills.py
│   │   ├── check_review.py
│   │   └── check_conversation.py
│   └── reports/         # populated by ailly eval / ailly report
├── runs/                # populated by ailly assemble / ailly run
└── ci.sh
```

The shared `e2e/AGENTS.md` at the repo root is loaded by every assembly's prefix; it is *not* duplicated under `general/e2e/`. `disclosure.md` and `.env` live only under `general/e2e/`.

### Profile

Full triple (discovery + invocation + baseline). The minimal cross-section is four skills: `writing-skills`, `writing-paired-skills`, `writing-pattern-skills`, `review`. Wrinkles:

- `using-general` is the routing prefix loaded by discovery and invocation assemblies; it is not itself a discovery target.
- `dispatching-parallel-agents` is excluded — its output is a tool-call sequence, not a single completion the eval harness can score structurally.
- `conversation` is the `conversation-vs-review` discovery foil **and** (added 2026-06-03 at the user's request) a fifth invocation case. It is an interaction-meta skill: its "artifact" is a conversational turn, not a structured document, so it leans on a judge plus a light structural script (the y/yes accept affordance, the 3-4 option band, one-question-at-a-time). Note `e2e/AGENTS.md` already encodes some interaction guidance ("ask one clarifying question, do not ask three"), so a partial null result on `conversation` is expected and legitimate; the gate does not depend on it.

### Discovery cases (5)

The three `writing-*` skills form a triangle. One paired-blur case covers each edge so that an edit to a single description that drifts toward an adjacent one lights up exactly one case. The remaining two cases cover `review` (a trigger case for the canonical critique skill) and the `conversation` vs `review` boundary (the gentlest near-neighbour outside the writing-* family).

| Case | Right answer | Foil | Discriminator |
|---|---|---|---|
| `writing-skills-vs-writing-pattern-skills` | `writing-pattern-skills` | `writing-skills` | The author names an Alexandrian-form pattern (Builder for an HTTP client). `writing-pattern-skills` is the patterns-plugin specialist; `writing-skills` is the generalist. |
| `writing-skills-vs-writing-paired-skills` | `writing-paired-skills` | `writing-skills` | The author has a wiring/practice cadence asymmetry (configure-once vs. per-call) and wants to know whether the existing pair is wired right. The cadence vocabulary fires `writing-paired-skills`. |
| `writing-paired-skills-vs-writing-pattern-skills` | `writing-pattern-skills` | `writing-paired-skills` | The author wants a single Alexandrian pattern with no cadence asymmetry — the work has one cadence, not two. The pattern vocabulary fires `writing-pattern-skills`; the absence of a wiring/practice split rules out `writing-paired-skills`. |
| `review-trigger` | `review` | none | A standalone trigger: the author is finishing a work product and wants a final-pass critique with a rubric. |
| `conversation-vs-review` | `conversation` | `review` | The author wants to *discuss* whether an approach is right (mid-work, exploratory), not to receive a final-pass critique. `conversation` handles open-ended questions; `review` is for finished work products. |

The `writing-skills` skill is not in the right-answer column. It is the catch-all that the three blurs route *away* from. That is the desired property: the harness tests the discriminators, not the default. If the model picks `writing-skills` in any of the three paired-blur cases, the description language for the more specific skill has lost its purchase. (The blueprint's original `writing-skills-baseline` case is therefore not needed — the catch-all behaviour is already implicit in the three blurs failing if `writing-skills` over-claims.)

The three paired-blur prompts each contain exactly one anchor for the right-answer skill and exactly one decoy for the foil. The judge prompt verifies that the model named the right skill *and* gave a reason that cited the anchor.

#### Paired-blur prompt drafts

`writing-skills-vs-writing-pattern-skills.md`:

```
I want to add a SKILL.md for an HTTP-client builder. The pattern has a
private constructor, a fluent `with_*` chain, and a terminal `build()`
that validates required fields. I'd like a Quick Reference table and the
Before / After framing the other patterns in the plugin use. Which
`general:*` skill applies?
```

Anchor: "the other patterns in the plugin", "Quick Reference", "Before / After" — all explicit patterns-plugin template vocabulary from `writing-pattern-skills`. Decoy: the generic "add a SKILL.md" framing that `writing-skills` would answer. Correct answer: `writing-pattern-skills`.

`writing-skills-vs-writing-paired-skills.md`:

```
We have two SKILL.md files for our project's logging story. One sets up
the subscriber registry once at startup. The other gets loaded at every
log call site. They reference each other in the body, but I'm not sure
the contract between them is right — the per-call skill keeps growing
a "before you start, make sure you have..." section. Which `general:*`
skill applies?
```

Anchor: "two SKILL.md files", "once at startup" / "every log call site" (cadence asymmetry), "the contract between them", "before you start, make sure you have..." (the drift signal named in `writing-paired-skills`). Decoy: the surface framing "I'm not sure ... is right", which could read as a generic skill-authoring question. Correct answer: `writing-paired-skills`.

`writing-paired-skills-vs-writing-pattern-skills.md`:

```
I want to add a single SKILL.md to the patterns plugin for the
Anti-Corruption Layer pattern from Evans. It's one cadence — every time
you cross an external boundary, you write a translator. The Quick
Reference table and the Composes With section will name Repository and
Aggregate. Which `general:*` skill applies?
```

Anchor: "single SKILL.md to the patterns plugin", "Quick Reference", "Composes With" — patterns-plugin template vocabulary; "one cadence" explicitly denies the wiring/practice asymmetry. Decoy: "every time you cross an external boundary, you write a translator" — surface language ("every time", "once you cross") that could read as a cadence asymmetry. Correct answer: `writing-pattern-skills`.

#### Remaining discovery prompts

`review-trigger.md`:

```
I think this branch is ready to merge. Can you give it a final pass
before I open the PR? Which `general:*` skill applies?
```

Anchor: "ready to merge", "final pass", "before I open the PR" — all in `review`'s description. Correct answer: `review`.

`conversation-vs-review.md`:

```
I'm halfway through refactoring the order-pricing service and I'm
second-guessing the direction. Can we talk through whether splitting
the discount calculator into its own module is the right call? Which
`general:*` skill applies?
```

Anchor: "halfway through", "second-guessing", "can we talk through whether ... is the right call" — exploratory question framing from `conversation`. Decoy: the word "review" is absent but the surface shape ("look at my work") could plausibly route to `review`. Correct answer: `conversation`.

### Invocation cases (5)

Each case loads `using-general` plus the named skill, runs a single-shot prompt that asks for the skill's structural artifact, and scores with a Python check script plus a judge plus a token budget. (`conversation` was added as the fifth case on 2026-06-03; see its subsection below.)

#### `writing-skills`

Prompt: produce a SKILL.md from a one-line description. The prompt names a concrete authoring situation that has no pattern-plugin or paired-cadence character, so the answer must use the generic template.

```
Author a SKILL.md called `condition-based-waiting` for a generic skills
plugin. The skill is for use when tests use sleep/setTimeout and are
flaky from race conditions; the technique is to wait on a predicate
becoming true rather than a fixed duration. Produce the SKILL.md, no
other files.
```

Structural assertions (script):
- File begins with YAML frontmatter delimited by `---` on lines 1 and N.
- Frontmatter contains `name: condition-based-waiting` and a `description:` field.
- `description:` value begins with `Use when` (per the CSO rule in `writing-skills`).
- Body contains a level-1 heading and at least one of the conventional sections (`Overview`, `When to Use`, `Core Pattern`, `Quick Reference`, `Common Mistakes`).
- Frontmatter does not exceed 1024 characters.

Judge: confirms the description names triggering conditions only (no workflow summary).

Token budget: total < 6000.

#### `writing-paired-skills`

Prompt: given a single SKILL.md that mixes two cadences, split it into a paired pair.

```
Below is a single SKILL.md that has grown two cadences: the front half
explains how to configure a project's pre-commit hook layout (runs
once when the project is set up), and the back half explains what to
do every time a developer wants to add a new check (per change).
Split it into a paired pair — one wiring skill and one practice skill.
Produce both SKILL.md files in full, in order.

[Inline 30-line single SKILL.md with mixed cadences — see fixture below.]
```

The mixed SKILL.md is short enough to inline in the prompt body; no separate `fixtures/` file. This keeps the assembly prefix uniform with the other invocation cases. The implementer authors the 30-line mixed skill so it has genuinely two cadences but no built-in answer (no contract block, no cadence clauses).

Structural assertions (script):
- Output contains two YAML frontmatter blocks (two `---\nname:` openers).
- Each frontmatter has a distinct `name:` value.
- Each `description:` begins with `Use when` and contains a cadence clause (one of: `once`, `every`, `per`, `applies when bootstrapping`, `applies every time`).
- Both bodies contain a `When NOT to use` paragraph that mentions the *other* skill's name (cross-reference).
- Exactly one of the two bodies publishes a contract (looks for the literal substring `Contract` or `After this skill runs` as a heading or label).

Judge: confirms the wiring skill is idempotent in its instructions, the practice skill cites the contract, and the cross-references are symmetric.

Token budget: total < 8000.

#### `writing-pattern-skills`

Prompt: produce a pattern SKILL.md plus a references/ directory entry for one language.

```
Author a pattern SKILL.md called `value-object` for the patterns plugin.
The pattern: a class whose identity is determined entirely by its
attribute values (Evans, DDD ch. 5). The design pressure: callers reach
into a domain object's fields and compare them piecewise, or two
"equal" instances are treated as distinct by reference equality.
Produce SKILL.md and references/python.md.
```

Structural assertions (script):
- SKILL.md frontmatter contains `name: value-object` and a `description:`.
- `description:` begins with `Use when`.
- Body contains all six canonical sections from `writing-pattern-skills`'s template: `Overview`, `When to Use`, `Core Pattern`, `Quick Reference`, `Common Mistakes`, `Composes With`.
- `Common Mistakes` contains at least three bolded entries (Markdown `**...**`).
- `Composes With` contains at least one cross-reference in `plugin:skill` form (regex: `` `[a-z]+:[a-z-]+` ``).
- `references/python.md` exists in the output and contains executable-looking Python (a `class` or `def` definition).

Judge: confirms the Core Pattern uses Before / After framing and the description names the design pressure (not the steps).

Token budget: total < 8000.

#### `review`

Prompt: review a fixture PR diff against a task description. The diff is inlined into the prompt body for the same reason as the paired-skills mixed file — keeps the assembly uniform.

```
You are about to claim the following change complete. Run a review pass
first.

Task: "Add a `is_admin: bool` field to the User struct and surface it
on the `/users/:id` JSON response."

Diff:
[Inline ~25-line patch that adds the field, surfaces it, and also
silently renames an unrelated function and removes a test. The patch
is deliberately constructed so a proper review rubric catches at least
two of: scope creep, removed test, missing test for the new field,
ambiguous serialization behaviour for the new field.]

Produce the review output the `review` skill prescribes.
```

Structural assertions (script):
- Output contains an explicit rubric (a numbered or bulleted list with at least three named criteria).
- Rubric mentions at least one of: `correctness`, `completeness`, `clarity`, `conciseness` (the four criteria in `review`'s body).
- Output identifies at least one issue and names it (does not say "looks good").
- Output does not produce edits inline (no diff blocks, no `git apply` instructions) — the review skill keeps evaluation and editing in separate agents.

Judge: confirms the rubric is task-specific (mentions the User struct or the `/users/:id` endpoint) and the issues identified are real ones in the diff.

Token budget: total < 6000.

#### `conversation` (added 2026-06-03)

Prompt: a decision point that calls for pausing rather than implementing — "help me settle on the notifications delivery channel before I write any code; don't start implementing yet." The conversation skill should produce an interaction that presents a single clarifying step (3-4 options or one recommendation), offers a simple `y`/`yes` accept, and asks one question at a time.

Structural assertions (`check_conversation.py`):
- R1 — no fenced code block (the prompt forbids implementing; conversation suggests, it does not act).
- R2 — interaction pattern: a `y`/`yes` accept affordance, OR a clarifying list of 3-4 options (a 2-option set should be a suggestion; 5+ is too many).
- R3 — one question at a time: not an interrogation (≤ 5 question marks).

Judge: confirms the response pauses for the user's decision, frames a single clarifying step with a simple affirmative accept, and leaves the decision to the user.

Token budget: output < 3000.

This case is expected to be a partial null result, since `e2e/AGENTS.md` already tells the model to "ask one clarifying question." The discriminating signal, when present, is the `y`/`yes` accept affordance and the 3-4 option framing, which `AGENTS.md` does not prescribe.

### Assemblies

Three files under `assemblies/`. Each follows the blueprint's live-paths template verbatim.

`discovery.yaml`:

```yaml
name: discovery
model: claude-sonnet-4-6

matrix:
  case:
    - writing-skills-vs-writing-pattern-skills
    - writing-skills-vs-writing-paired-skills
    - writing-paired-skills-vs-writing-pattern-skills
    - review-trigger
    - conversation-vs-review

prefix:
  - { kind: file,   path: ../../e2e/AGENTS.md,                    cache: true }
  - { kind: file,   path: ./profile.md,                           cache: true }
  - { kind: system, path: ./disclosure.md,                        cache: true }
  - { kind: system, path: ../skills/using-general/SKILL.md,       cache: true }

conversation:
  - { role: user, path: "prompts/discovery/{{ case }}.md" }
  - { role: assistant }
```

`disclosure.md` is the routing surface: the verbatim `description:` frontmatter of `writing-skills`, `writing-paired-skills`, `writing-pattern-skills`, `review`, and `conversation`. `using-general/SKILL.md` follows it as the bootstrap routing skill. Neither appears in the invocation or baseline prefix, so `disclosure.md` does not affect the falsification arm.

`invocation.yaml`:

```yaml
name: invocation
model: claude-sonnet-4-6

matrix:
  skill:
    - writing-skills
    - writing-paired-skills
    - writing-pattern-skills
    - review
    - conversation

prefix:
  - { kind: file,   path: ../../e2e/AGENTS.md,                    cache: true }
  - { kind: file,   path: ./profile.md,                           cache: true }
  - { kind: system, path: ../skills/using-general/SKILL.md,       cache: true }
  - kind: system
    path: "../skills/{{ skill }}/SKILL.md"
    cache: true

conversation:
  - { role: user, path: "prompts/invocation/{{ skill }}.md" }
  - { role: assistant }
```

`baseline.yaml`: identical matrix to `invocation.yaml`, prefix drops both `kind: system` SKILL.md entries (the routing skill *and* the per-case skill), keeps `AGENTS.md` and `profile.md`.

```yaml
name: baseline
model: claude-sonnet-4-6

matrix:
  skill:
    - writing-skills
    - writing-paired-skills
    - writing-pattern-skills
    - review
    - conversation

prefix:
  - { kind: file, path: ../../e2e/AGENTS.md, cache: true }
  - { kind: file, path: ./profile.md,        cache: true }

conversation:
  - { role: user, path: "prompts/invocation/{{ skill }}.md" }
  - { role: assistant }
```

### `profile.md`

Short and falsification-clean: declares the harness purpose and the axis profile, names neither any `general:*` skill identifier nor any skill heading verbatim.

```markdown
# general/e2e/profile.md

This directory tests the `general` skill plugin. The harness runs the
full axis profile: discovery, invocation, and baseline.
```

### `ci.sh`

Copied from `ailly_two/e2e/patterns-eval/ci.sh` with these changes:

1. `expected_count()` table: `discovery=5`, `invocation=4`, `baseline=4`.
2. `repo_root="$(cd "${project_dir}/../.." && pwd)"` — the e2e dir is two levels under the repo root, one level deeper than patterns-eval's repo-root layout.
3. Ailly is invoked through an overridable `AILLY` variable — `AILLY="${AILLY:-<ailly_two>/target/debug/ailly_two}"` — used as `${AILLY} -p "${project_dir}" assemble <suite>`. This points at the locally built `ailly_two` binary (no `cargo run` rebuild per call) and is overridable to a packaged `ailly` in CI.
4. A first step regenerates `disclosure.md`: `bash evals/scripts/gen_disclosure.sh` before `assemble discovery`, so the discovery surface reflects the live skill frontmatter.

The falsification grep enforces the convention: neither `e2e/AGENTS.md` nor `general/e2e/profile.md` may contain a `general:<skill>` identifier. The grep is:

```bash
if grep -E 'general:(conversation|dispatching-parallel-agents|review|using-general|writing-paired-skills|writing-pattern-skills|writing-skills)' \
     "${repo_root}/e2e/AGENTS.md" "${project_dir}/profile.md"; then
  echo "FAIL: AGENTS.md or profile.md contains a general:<skill> identifier" >&2
  exit 1
fi
```

### Check scripts

All four `evals/scripts/check_*.py` are written in full (decision 2), following the patterns-eval checker contract via a shared `_checker_utils.py`: read the candidate from stdin, apply the ordered structural rules listed per-case above, exit 0 when every rule holds, else print one single-line reason to stdout and exit 1 — never write stderr (an empty-stdout/non-empty-stderr exit is recorded as `Errored`, a crashed checker, not a `Fail`). Each rule traces 1:1 to a structural property of the skill body so a reworded skill that drops the property is what the checker notices. The scripts parse Markdown output (frontmatter blocks, headings, fenced code) rather than a single source dialect, because the general skills' artifacts are themselves Markdown.

`gen_disclosure.sh` regenerates `disclosure.md` by concatenating the YAML frontmatter (the lines between the first two `---` fences) of each candidate `../skills/<name>/SKILL.md`, headed by a `==> <name>/SKILL.md <==` banner, matching the patterns-eval disclosure format.

### Evals

`evals/discovery.yaml`, `evals/invocation.yaml`, `evals/baseline.yaml`. The invocation and baseline files are identical (per the blueprint's "Falsification convention"). The discovery file holds one entry per case with two `text_contains`/`text_not_contains` assertions plus one `judge` assertion per paired-blur case (the trigger cases get `text_contains` plus a single judge).

Pattern for each discovery case:

```yaml
- name: writing-skills-vs-writing-pattern-skills
  assertions:
    - { type: text_contains, value: "general:writing-pattern-skills" }
    - { type: text_not_contains, value: "general:writing-skills" }
    - type: judge
      prompt: |
        The answer selects general:writing-pattern-skills because the
        prompt names the Alexandrian-form patterns-plugin template
        (Quick Reference, Before / After). It does not recommend
        general:writing-skills.
```

The `text_not_contains` on `general:writing-skills` is brittle because `writing-skills` is a substring of `writing-pattern-skills` and `writing-paired-skills`. The blueprint's convention assumes the full prefixed form `general:writing-skills` is the assertion target, which avoids substring collisions — the prefixed identifiers do not overlap. The implementer must keep the `general:` prefix in every assertion value. The blueprint already names this as the convention; no new wrinkle here, but flagging it because the three writing-* names invite the mistake.

Pattern for each invocation case mirrors patterns-eval's:

```yaml
- name: writing-skills
  assertions:
    - { type: script, runtime: python, script: { path: evals/scripts/check_writing_skills.py } }
    - type: judge
      prompt: |
        The SKILL.md has YAML frontmatter with name: and description:
        fields. The description begins with "Use when" and names
        triggering conditions only — no workflow summary. The body
        has a recognisable section structure (Overview, When to Use,
        Common Mistakes).
    - { type: tokens, metric: total, op: "<", value: 6000 }
```

## Alternatives

**Inlining a `writing-skills-baseline` case as in the blueprint.** Rejected. The blueprint listed five discovery cases including a `writing-skills-baseline` ("I want to add a general-purpose SKILL.md → writing-skills"). The three paired-blur cases already test the catch-all property by negation: if `writing-skills` over-claims, the blurs fail. Adding a fourth writing-* case (the all-three-foils-against-the-default one) inflates the matrix without adding falsification signal, because the default is not where the description-space drift happens. Replacing the catch-all case with the third paired-blur (`writing-paired-skills-vs-writing-pattern-skills`) keeps the case count at five and gives the harness the full edge-coverage of the triangle.

**Separate fixture files for the paired-split and review cases.** Rejected. The mixed SKILL.md (paired-split case) and the PR diff (review case) are each short enough to inline in the prompt body. A `fixtures/` directory adds a path to manage and a second source of drift between the prompt and the assertion target. Inlining keeps every invocation case self-contained.

**One check script per discovery case.** Rejected. Discovery scoring is well-served by `text_contains` + `judge`; structural Python adds no signal because the model's output is a short identifier, not an artifact.

**Judge-only invocation arms.** Rejected for the same reason patterns-eval rejected it: a well-crafted prompt can talk the judge into a "yes" without producing the structural artifact. Script + judge + token budget is the working pattern.

**Loading every `general:*` SKILL.md into the invocation prefix.** Rejected. The blueprint specifies loading `using-general` plus the one named skill per case. Loading the full plugin would let the model cross-cite skills the harness is not testing, blurring whether a pass reflects the named skill or the plugin as a whole.

## Summary

A new `general/e2e/` harness with five discovery prompts (three of them paired-blur cases that pairwise separate `writing-skills`, `writing-paired-skills`, and `writing-pattern-skills`), four invocation prompts (each loading exactly one of the four cross-section skills plus `using-general`), and matching baseline assemblies. The harness inherits its file layout from `ailly_two/e2e/patterns-eval/`; it uses the shared `e2e/AGENTS.md` plus a short `profile.md`. The four check scripts are written in full, and the falsification gate is enforced in `ci.sh`.

**Resolved at finalization** (see Implementation Decisions): concrete Python check-script bodies are written now (not placeholders); discovery loads a live-regenerated `disclosure.md`; Ailly runs via the `ailly_two` binary; skills are vendored under `context/` (refreshed each run) because Ailly's VFS clamps `..` at the project root, so live `../skills/...` prefix paths do not resolve.

**Deferred decisions.**

- The exact 30-line "mixed cadence" SKILL.md inlined into the `writing-paired-skills` invocation prompt. **Required for the harness to assemble**, not optional polish. Authored during implementation; the constraint is that it must have two genuine cadences but no built-in answer (no contract block, no cadence clauses).
- The exact ~25-line PR diff inlined into the `review` invocation prompt. **Required for the harness to assemble**, not optional polish. Authored during implementation; the constraint is at least two real reviewable issues (scope creep, missing test, ambiguous behaviour) so the rubric assertion has signal.
- Token budget calibration. The blueprint allows the budget to be tuned after the first run; the values here (6000–8000 total) mirror patterns-eval's numbers and may move.
- Whether the `text_not_contains` assertion on `general:writing-skills` should be replaced with a more specific regex (e.g., word-boundary). The prefixed identifier already avoids substring collision in practice; flagging in case implementation surfaces a false positive.
- Whether to keep `dispatching-parallel-agents` permanently out of the matrix or revisit when ailly grows tool-call assertion support. Out of scope for this harness.
- Model-version sweep strategy and a repo-level CI workflow that calls each plugin's `ci.sh`. Both are blueprint-level deferrals, not specific to this harness.

## Results (run 2026-06-03, claude-sonnet-4-6)

The harness is implemented under `general/e2e/` and runs green end-to-end via `general/e2e/ci.sh`. Both required properties are demonstrated. Five invocation cases (the four cross-section skills plus `conversation`).

| Metric | Value | Target | Pass |
|---|---|---|---|
| Discovery pass rate | 15/15 = 1.00 | ≥ 0.9 | ✓ |
| Invocation pass rate | 15/15 = 1.00 | ≥ 0.8 | ✓ |
| Baseline pass rate | 7/15 = 0.47 | low | — |
| **Falsification gap** | **0.53** | ≥ 0.5 | ✓ |
| Comparison buckets | improved 8, regressed 0, unchanged_pass 7, unchanged_fail 0 | improved>0, regressed==0 | ✓ |

**Property 1 (discovery).** All five cases route to the correct `general:*` skill on every `text_contains` / `text_not_contains` / `judge` assertion, including the three paired-blur cases and the `conversation` vs `review` boundary.

**Property 2 (invocation > baseline).** Eight assertions improved (failed baseline, passed with skill), none regressed: `writing-skills` (script+judge), `writing-paired-skills` (script+judge), `writing-pattern-skills` (script+judge), `review` (script), `conversation` (judge). The `review` judge is a partial null — a capable model writes an acceptable review unaided, so the skill's measurable contribution on `review` is the named-criteria rubric the script catches (baseline named 0 of the four criteria; the skilled arm named ≥ 2). On `conversation`, the skill made the model pause and ask the single most-blocking clarifying question first, where the baseline front-loaded a long analysis and buried its clarifying question last; the judge catches that, the light script passes both arms.

**Run-to-run variance.** The binding criterion is the gate (`improved > 0 && regressed == 0`), which held on every run (e.g. a subsequent fresh run scored improved 6, regressed 0, baseline 8/15). The headline falsification gap fluctuates roughly 0.40–0.58 with model sampling; discovery and the gate are stable. This is inherent to LLM evaluation, not harness instability — `regressed` was 0 on every run.

**Findings worth carrying to the other plugin harnesses** (also in `TASKS.md`):

1. **Ailly VFS clamps `..` at the project root.** Live `../skills/...` prefix paths do not resolve. Vendoring under `context/` via `evals/scripts/vendor.sh` (refreshed each `ci.sh` run, git-ignored) keeps the eval scoring current skill text.
2. **`tokens metric: total` is arm-asymmetric** (it includes the larger invocation prefix), so it can only regress, never improve. Use `metric: output`.
3. **The model hallucinates `write_file` tool calls** under `e2e/AGENTS.md` when asked to "produce files"; the artifact lands in escaped JSON no checker can parse. A "no tools, write inline" clause on the invocation prompts (applied to both arms) fixes it — an output-channel constraint, not answer-coaching.

The feature-test (the `ci.sh` user story) and the 6-step plan that greened it were tracked in this session folder's `feature-test.md` and `plan.md` (git-ignored scratch); their substance is captured above and in `ci.sh`.

## Reproduce

```sh
AILLY=/path/to/ailly_two/target/debug/ailly_two bash general/e2e/ci.sh
```

Requires `general/e2e/.env` (copied from `ailly_two/.env`) or `ANTHROPIC_API_KEY`.
