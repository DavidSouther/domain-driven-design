---
name: writing-paired-skills
description: Use when two skills cover the same topic at different cadences — one rare-but-recurring task that assembles a harness (configures, scaffolds, bootstraps, idempotent) and one frequent task that operates within the harness (every log line, every TDD cycle, every new term). Applies when a single skill is growing two distinct cadences in its body, when a frequent skill is acquiring a "before you start, configure..." section, or when two existing skills cover the same topic but neither references the other and the contract between them is implicit.
---

# Writing Paired Skills

## Overview

Some topics carry two cadences inside one body of practice. Setting up a logging pipeline happens once per process; emitting a log record happens millions of times. Initializing a project happens once per environment; running a TDD cycle happens every step. Establishing a glossary happens once per bounded context; checking the glossary before introducing a term happens every term. The two cadences want two skills, joined by a small explicit contract.

A **paired skill** is two SKILL.md files about the same topic, written together. One is the **wiring** (rare, idempotent, source of truth for the harness). The other is the **practice** (frequent, scoped to one call site, assumes the wiring holds). The contract between them is short, scannable, and published by the wiring skill; the practice skill cites it rather than re-teaching it.

**Background:** Use `general:writing-skills` for the underlying authoring methodology (CSO, TDD-of-documentation, frontmatter rules, RED-GREEN-REFACTOR with subagents). When the pair lives in the patterns plugin specifically, also use `general:writing-pattern-skills` for the Alexandrian template. This skill only documents what is specific to the pair.

## When to Use

- A single skill body is growing two distinct cadences. A "configure once" preamble keeps appearing before the per-call instructions; readers under time pressure skip past it; the skill drifts past the size where Claude reliably loads it.
- A frequent skill is growing a "before you start, make sure you have …" section. The setup belongs in a partner; the practice skill should not have to teach it.
- Two skills already exist for the same topic, but neither references the other. The contract between them — what the practice skill may assume the wiring has installed — is implicit and drifts silently.
- A topic crosses a posture boundary that twelve-factor or Composition Root would name: wiring near the entry point versus practice inside library code; build versus run; Day-1 deploy versus Day-2 operate.

## Roles

### Wiring

The rare-but-recurring half. Runs once per process, once per environment, once per change to the harness. It is **idempotent**: running it on an already-configured system either confirms the configuration or surfaces drift, but never destroys state. It is the **source of truth** for whatever it installs — the global subscriber, the toolchain layout, the glossary file.

The wiring skill is the place to return when the system changes. The skill body names the triggers: toolchain change, environment change, library upgrade, suspected drift. Re-running checks that the contract still holds.

### Practice

The frequent half. Runs every time the relevant work happens — every log emit, every TDD cycle, every new term. It is **scoped to one call site** and **assumes the wiring holds**. The practice skill cites the wiring as a prerequisite, not as a step. Its body never repeats the wiring instructions.

The practice skill carries the warning Beck attaches to practices: a practice without the wiring it depends on is rote. If a reader can use the practice skill without the wiring being in place, the contract was wrong.

## Role Assignment

For an emerging pair, test each half against the cadence questions:

| Question | If "yes" | If "no" |
|---|---|---|
| Does the work run once per process, environment, or change? | Wiring. | Probably practice. |
| Does the work run every emit, every cycle, every term? | Practice. | Probably wiring. |
| Does running the work twice need to be safe? | Wiring (idempotent). | Could be either. |
| Does the work assume something is already installed? | Practice. | Probably wiring. |
| Is the work the source of truth for a harness, file, or registry? | Wiring. | Practice. |

When both halves answer the same way to several questions, the pair is probably one skill, not two. When the answers diverge cleanly, the assignment is the diverging axis.

## Frontmatter Conventions

The frontmatter is where the pair announces itself to Claude's skill selector. Each description carries a **cadence** and a **scope**, and each description points at its partner under "When NOT to use".

### Wiring description

Open with "Use when" and the assembly triggers, then close with the cadence and scope: "applies once at process start, never inside library code", "applies when bootstrapping or revising the toolchain for a project", "applies once per bounded context, never inside a domain operation". The cadence is what prevents Claude from loading this skill at every emit site.

```yaml
# Wiring frontmatter (configuring-logging)
description: Use when bootstrapping a service's logging pipeline — selecting a
  subscriber/registry, layering formatter/filter/enricher/exporter, attaching
  resource attributes, wiring W3C trace propagators, choosing head- or
  tail-based sampling, configuring redaction as defense-in-depth, and arranging
  graceful shutdown flush. Applies once at process start, never inside library
  code.
```

### Practice description

Open with "Use when" and the recurring trigger: "applies every time code emits a log record", "applies when implementing a plan step", "applies before introducing a new term". The recurring trigger is what makes Claude load this skill at the call site.

```yaml
# Practice frontmatter (emitting-logs)
description: Use when writing log call sites in domain or application code —
  choosing a severity, attaching structured fields with semantic-convention
  keys, scoping spans to units of work, recording errors with their full chain
  at a single boundary, and naming business events. Applies every time code
  emits a log record.
```

### Cross-reference under "When NOT to use"

Each skill's body carries a "When NOT to use" line that points at the partner by name:

> "When NOT to use: to set up the pipeline, attach resource attributes, install propagators, or configure exporters. Those belong in `patterns:configuring-logging`."

> "When NOT to use: inside a library crate, request handler, or any code reachable more than once. Libraries emit; they do not configure."

The cross-reference is symmetric. The wiring skill names the practice skill as the place for the per-call-site work; the practice skill names the wiring skill as the place for the setup. "Composes With" is an acceptable second location for the cross-reference when the partner is one of several related skills, but the "When NOT to use" placement is preferred because that is where Claude reads when deciding whether to load the alternative.

## The Contract

The contract is a short, scannable statement of what downstream code may assume once the wiring has been run. It is the **API between the pair**. It lives in the wiring skill — either as a small block near the top labelled "Contract" or "After this skill runs …", or as the last paragraph of the Overview. The practice skill cites the contract; it does not restate it.

A good contract is concrete and short. The logging pair's contract reads, in effect:

> *After `patterns:configuring-logging` has run, callers may assume: a single global subscriber is installed; resource attributes (`service.*` or `process.*`) are attached at the resource layer; the W3C `traceparent` propagator is wired so that the active span's `TraceId` and `SpanId` flow to every record; the exporter receives records; a flush is registered at shutdown.*

A reader of `patterns:emitting-logs` can then rely on those assumptions: the emit site does not name a destination, does not re-attach resource attributes, does not manage propagation, and does not flush. Every one of those would be a contract violation, and the skill body says so.

**Drift signal.** If the practice skill grows a "first, make sure you have …" paragraph, the contract has gone stale or the wiring skill has dropped something. Either the wiring needs to do more, or the contract needs to be widened to name the new assumption. The practice skill should never have to teach the wiring.

## Re-Verification

The wiring skill is the **return address** when the system changes. The skill body lists the triggers that mean re-running is due:

- A toolchain change (Rust edition bump, Python version upgrade, Node major).
- An environment change (new deployment target, new orchestrator, new collector).
- A library upgrade that touches the wired interface (a new `tracing` major, a new OTel version).
- A suspected drift, surfaced by a record missing a resource attribute or a propagation gap.

Re-running checks that the **contract still holds**. The wiring skill names what to re-verify and how. The practice skill does not list these triggers; if a reader of the practice skill spots one, they switch to the wiring skill.

## Worked Example: The Logging Pair

The two existing examples in this repository are the working models the meta-skill draws from. The **logging pair** is the primary example because both halves are already published, the contract is legible, and the cross-references are symmetric.

| Concern | `patterns:configuring-logging` (Wiring) | `patterns:emitting-logs` (Practice) |
|---|---|---|
| Cadence | Once at process start. | Every call site. |
| Scope | Application bootstrap; never inside library code. | Domain and application code. |
| Idempotent? | Yes. Re-runs confirm or surface drift. | N/A; every call is a new record. |
| Source of truth for … | The subscriber registry, resource attributes, propagator, exporter, flush. | The per-event fields, the severity, the `EventName`. |
| Contract published? | Yes (subscriber installed; resource attributes attached; `traceparent` wired; flush registered). | N/A; the practice consumes the contract. |
| Cross-reference | "When NOT to use" names `emitting-logs` as the call-site partner. | "When NOT to use" names `configuring-logging` as the setup home. |
| Re-verify triggers | Library upgrade, environment change, drift. | None; defer to the partner. |

The developer-plugin pair (`developer:initialize` ↔ `developer:red-green-refactor`) is the second exemplar: a project-scaffolding wiring skill and a per-step TDD-cycle practice skill. The cadence asymmetry is the same, the role names map cleanly, and the contract (a green test runner, a hook layout, a clean working tree) is the harness `red-green-refactor` consumes every cycle. A reader who has internalized the logging pair can read the developer pair as the same shape in a different domain.

## Quick Reference

| Concern | Wiring | Practice |
|---|---|---|
| Cadence | Once per process / environment / change | Every emit / cycle / call site |
| Posture | Near the entry point (12-Factor build, Composition Root) | Inside the application or library |
| Idempotent | Required | Not applicable |
| Re-runnable | Yes; surfaces drift | One-shot per call |
| Frontmatter cadence clause | "Applies once at process start, never inside library code" | "Applies every time code emits a log record" |
| Contract | Publishes it | Cites it |
| Cross-reference location | "When NOT to use" → practice | "When NOT to use" → wiring |
| Re-verification triggers | Toolchain / environment / library / drift | None; defer to wiring |
| Body forbids | Per-call emission details | Setup instructions |

## Common Mistakes

- **One mega-skill per topic.** Folding wiring into practice and letting readers skim past the parts that do not apply this run. The practice skill is loaded constantly; weight in it is paid every conversation. Split the cadences.
- **Two skills with no contract.** The cross-reference is present but no statement names what the practice may assume after the wiring runs. The contract drifts silently and the practice skill grows a "first, make sure you have …" section. Publish the contract in the wiring skill; cite it from the practice skill.
- **Wiring skill that is not idempotent.** A bootstrap that destroys existing state on re-run cannot serve as a re-verification return address. Make running it safe; on a configured system it confirms, it does not overwrite.
- **Practice skill that re-teaches the wiring.** A "before you start, configure …" section in the practice skill is the drift signal. Move the section into the wiring skill and have the practice skill cite the contract.
- **Asymmetric cross-reference.** The practice names the wiring but the wiring does not name the practice. Claude loads the wiring at a call site, has no pointer to the right skill for the call site, and stays in the wiring skill. Cross-reference in both directions.
- **Cadence omitted from the frontmatter.** A description that does not say "once at process start" or "every time code emits a record" leaves Claude no way to pick the right half. Put the cadence clause in the description.
- **Pair invented for symmetry.** Some skills genuinely stand alone; manufacturing a partner is overhead without payoff. Apply the "When NOT to use" tests before splitting.
- **Re-verification triggers buried.** The triggers that mean "re-run the wiring" belong in the wiring skill body and need to be scannable. A reader who suspects drift should find them on first read.

## Composes With

- **`general:writing-skills`** — the underlying authoring methodology (CSO, TDD-of-documentation, frontmatter rules) that this skill specialises for paired skills. Run a baseline pressure scenario on each half of a pair before writing either skill; the wiring half and the practice half typically fail in different ways without their respective skills.
- **`general:writing-pattern-skills`** — when the pair lives in the patterns plugin, both halves also follow the Alexandrian template documented there. This skill adds the pairing conventions on top.
- **`general:review`** — review a fresh pair as a unit, not one half at a time. The contract, the cross-references, and the cadence clauses are pair-level properties.
- **`patterns:bootstrap-and-service`** — the code-level analog of the cadence split. Bootstrap is where wiring is invoked; the service is where practice runs. The pairing of skills mirrors the pairing of code locations.
