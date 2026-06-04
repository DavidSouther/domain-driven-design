# research-eval

A regression harness for the `research` skill plugin, built with
[Ailly](https://github.com/davidsouther/ailly). It scores two independent
failure surfaces of a `SKILL.md` edit:

- **Discovery** — does the `description:` frontmatter still route the model to
  the right skill? Sweeps 10 routing cases over the concatenated descriptions of
  all eleven research skills (`context/skills/disclosure.md`) plus the
  `using-research` bootstrap. Asserts which skill the model names.
- **Invocation** — once a skill body is loaded, does the output exhibit the
  conventions the skill teaches? Sweeps all 10 non-bootstrap skills (`codebase`,
  `archaeology`, `configuring-papers`, `configuring-books`, `papers`, `books`,
  `dependencies`, `domain`, `internal`, `public`). Each case mixes a structural
  Python checker, an LLM judge, and a token budget.

The invocation axis is run as an A/B falsification comparison against a
**baseline** arm with no skill body loaded, over identical prompts. The gate is
`improved > 0 && regressed == 0`: the skill must help on at least one assertion
the baseline failed, and break nothing the baseline passed.

## Layout

```
AGENTS.md                     constitution + falsification narrative (prefix position 0)
context/AGENTS.md             neutral candidate-project context (invocation + baseline)
context/skills/disclosure.md  routing table — all 11 live descriptions (discovery surface)
context/skills/<name>/        the skills under test, vendored verbatim
assemblies/{discovery,invocation,baseline}.yaml
prompts/{discovery,invocation}/<case>.md
evals/{discovery,invocation,baseline}.yaml
evals/scripts/check_<skill>.py   structural checkers (+ shared _md.py)
ci.sh                         assemble -> run -> eval -> report, with the gate
```

## Running

`ci.sh` needs the Ailly binary and an Anthropic key. Point it at the binary with
`AILLY_BIN` (or its repo with `AILLY_HOME`), and drop the key in a project
`.env` (`ANTHROPIC_API_KEY=...`) or export it.

```sh
./ci.sh
```

`assemble` runs without a model; `run`, `eval`, and `report` call the model. The
script asserts the conversation counts, that every assistant slot was filled,
that a per-run report landed, and finally that the baseline-vs-invocation
comparison clears the falsification gate.

## What the harness exercises, and what it does not

`ailly run` fills one assistant turn per conversation with a single model
completion and **no live tool execution**. Every case is therefore a text task:
the model writes the research note or configuration plan it would produce, and
the assertions score the *structure and convention* the skill teaches — the
research-note path, the IEEE Sources block, the `## Timeline`, the four-stage
per-source wiring, the typed Not-Available routing signal. Because nothing is
fetched, external-transport credentials (Crossref mailto, Open Library
User-Agent, internal-source tokens) change nothing about the produced text, so
there is no per-case credential gating — see `AGENTS.md`.

## Reading the result

`report <baseline-id> <invocation-id>` writes a comparison markdown sorting
every paired assertion into `improved` / `regressed` / `unchanged_pass` /
`unchanged_fail`. A null result (an assertion that fails on both arms) is a true
statement about the model, not a defect — do not weaken a checker to manufacture
a pass. See the design doc at
`docs/developer/2026-05-29-G-research-e2e/design.md` for the build
reconciliation and the committed results.
