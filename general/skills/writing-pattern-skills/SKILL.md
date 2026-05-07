---
name: writing-pattern-skills
description: Use when authoring a new skill for the patterns plugin, or when revising an existing pattern skill so it conforms to the plugin's conventions. Applies when a recurring design pressure needs to be captured as a named, reusable pattern, including its frontmatter, section structure, and the references directory layout.
---

# Writing Pattern Skills

## Overview

A pattern skill captures one named, reusable solution to a recurring design pressure. The patterns plugin follows a reduced Alexandrian form, refined by Fowler in *Patterns of Enterprise Application Architecture* and Evans in *Domain-Driven Design*: a name, the forces that call for it, the solution itself, and its relationships to neighbouring patterns. Every skill in `patterns/skills/` is shaped by that template, so a reader can scan any of them and know where to look for the answer.

This skill describes that template, and the editorial choices that keep the catalog coherent. Use it before opening a new SKILL.md in the patterns plugin.

**Background:** Use `general:writing-skills` for the underlying authoring methodology (CSO, TDD-of-documentation, frontmatter rules). This skill assumes those practices and only documents what is specific to the patterns plugin.

## When to Use

- A recurring design pressure is named in industry literature (GoF, DDD, Fowler, Alexis King, Kent Beck) and a skill should make it discoverable to Claude.
- An emergent pattern in this codebase has matured enough to deserve a reusable name.
- An existing pattern skill needs to be brought into conformance with the catalog's structure.
- A new language reference (`references/<lang>.md`) is being added to an existing pattern.

**When NOT to use:** Authoring a non-pattern skill (a technique, a workflow, a reference). Use `general:writing-skills` directly. Likewise, project-specific conventions belong in CLAUDE.md, not in a pattern skill.

## The Canonical Pattern Skill Template

```markdown
---
name: pattern-name
description: Use when [the design pressure that calls for this pattern]. Applies when [the symptoms a reader would recognise]. [One sentence on what becomes possible once the pattern is in place.]
---

# Pattern Name

## Overview
[Two or three sentences: what the pattern is, the core principle, and the named source if one exists.]

## When to Use
- [Triggering condition, phrased as a recognisable symptom.]
- [Another condition.]
- [...]

**When NOT to use:** [Cases where a simpler construct is preferable.]

## Core Pattern
[Before / After framing, or a numbered solution sketch. One short, language-agnostic code block.]

For complete examples, see [`references/typescript.md`](references/typescript.md), [`references/python.md`](references/python.md), and [`references/rust.md`](references/rust.md).

## Quick Reference
| Column | Column |
|--------|--------|
| ... | ... |

## Common Mistakes
- **Concise name of the misstep.** One or two sentences on the corrective action.

## Composes With
- **`patterns:other-skill`** — how the two patterns reinforce each other.
```

## Anatomy of Each Section

### Frontmatter

The `name` matches the folder name exactly, in lowercase with hyphens. The `description` opens with **Use when** and names the design pressure in language a reader would recognise from the symptoms in their own code, not from the pattern's name. Industry-standard pressure terms work well: "scattered null checks", "stringly typed values", "many-parameter constructor", "ORM rows leaking into domain logic". The description states the conditions; it never summarises the steps.

### Overview

Open by naming the pattern in plain terms, state the core principle in one sentence, and cite the original source when a canonical one exists. Readers reach for pattern skills under time pressure, so the first paragraph must answer "is this the right pattern for my situation". A second paragraph, if needed, distinguishes this pattern from a near-neighbour (Repository vs DAO, Builder vs options-object, Aggregate vs cluster of entities).

### When to Use

Each bullet is a symptom, written so a reader scanning the list recognises their current situation. Triggering symptoms travel further than abstract criteria: "two domain identifiers share the same primitive type" beats "type ambiguity". Close with **When NOT to use** so the catalog also teaches restraint. Patterns that are universally applicable still have boundaries; name them.

### Core Pattern

The shape that has worked best across the catalog is **Before / After**, where the before shows the design pressure in unmistakable terms and the after shows the resolved form. Keep the inline code block to roughly fifteen lines, in whichever language reads most clearly for the example, and treat it as illustrative rather than complete. Full, runnable examples belong in the references directory.

When a pattern is procedural (like Triangulate) or the Before / After framing distorts the shape, use a short numbered sequence of steps with the smallest illustrative code under each step.

End the section with a single sentence pointing to the language-specific reference files.

### Quick Reference

A table that a reader can scan in five seconds. Common columns: domain concept to type, situation to action, implementation variant to purpose. The table earns its place by being faster to consume than re-reading the prose, so it should hold concrete entries rather than restated principles.

### Common Mistakes

Each entry is a bolded misstep followed by the corrective move, framed as guidance toward the right action. "**Public constructor alongside the builder.** Make the product constructor private and expose only `static builder(...)`." This section is brief, four to six entries, because it is a safety net rather than the centre of the skill.

### Composes With

The patterns plugin is a network, not a list. Every pattern names the neighbours it reinforces, with a short clause on why they pair: "**`patterns:newtype`** — the return type of a parser is a newtype." Cross-references use the `plugin:skill` form. When a pattern composes with skills outside the plugin (`developer:red-green-refactor`, for instance), include them too.

## File Layout

```
patterns/skills/<pattern-name>/
  SKILL.md
  references/
    typescript.md
    python.md
    rust.md
```

Most skills carry the three-language reference triplet. The languages are deliberate: TypeScript for object-oriented and structural typing, Python for dynamic typing and class-based DDD, Rust for ownership and algebraic data types. A pattern that lacks a faithful expression in one of these languages can omit that file, but the default is to write all three.

When the pattern is small and procedural (`triangulate`), or the code is so short that a references directory would be ceremony, keep the code inline in SKILL.md and skip the directory entirely.

The references files are complete, runnable examples with imports and supporting types. They show the pattern at work, not toy snippets. Each file opens with the same structural shape across languages, so a reader fluent in one can map the pattern onto another.

## Voice and Style

Patterns are documented in the third person, in the present tense, as ongoing practice rather than a one-time fix. The tone is reference-grade: complete sentences, technical vocabulary used precisely, no exclamation marks, no encouragement language. Examples are concrete and named (`UserId`, `OrderId`, `Email`, `Cents`) so the pattern lands as a thing applied to real domains rather than an abstract shape.

When citing prior art, name the source: Alexis King for parse-don't-validate, Evans for Aggregate and Repository, Fowler for Unit of Work, the GoF for Builder. A short attribution gives the reader a thread to pull on.

## Quick Reference

| Section | Purpose | Length |
|---------|---------|--------|
| Frontmatter | Discoverability for Claude | Description under 500 chars |
| Overview | Identify the pattern and its core principle | 2 or 3 sentences |
| When to Use | Recognise the symptoms | 3 to 6 bullets plus "When NOT" |
| Core Pattern | Show the shape | One short code block plus pointers |
| Quick Reference | Scannable lookup | Single table |
| Common Mistakes | Catch the close-but-wrong forms | 4 to 6 bolded entries |
| Composes With | Map the neighbourhood | 2 to 4 cross-references |

## Common Mistakes

- **Description summarises the workflow.** Naming the steps in the description leads Claude to follow the description and skip the body. Keep the description to triggering symptoms only.
- **Frontmatter exceeds the 500-character soft cap.** Long descriptions crowd other skills out of Claude's selection view. Trim until the symptoms are dense and singular.
- **One-language reference.** Shipping only the language the author was thinking in deprives readers fluent in another. Default to all three; omit only when the pattern has no faithful expression in that language.
- **Composes With as a flat list.** Naming neighbours without explaining why they reinforce each other. Each entry pairs the partner skill with one short clause on the composition.
- **Restated principles in the Quick Reference.** A table that paraphrases the prose has not earned its place. Concrete entries — section names, file paths, length budgets — beat restated rules.
- **Skipping `general:writing-skills`.** The TDD-of-documentation methodology (RED-GREEN-REFACTOR with subagents) belongs to that skill. This one only documents the patterns plugin's specifics; do not duplicate them here.

## Composes With

- **`general:writing-skills`** — the underlying authoring methodology (CSO, TDD-of-documentation, naming, frontmatter rules) that this skill specialises for the patterns plugin.
- **`patterns:using-patterns`** — the bootstrap and routing skill that names every pattern in the catalog. Add a row to its situation table whenever a new pattern skill is published, so the new skill becomes reachable from the workflow.
- **`general:review`** — run a review pass against a fresh draft before committing, especially the Common Mistakes and Composes With sections, which are easy to under-fill.
