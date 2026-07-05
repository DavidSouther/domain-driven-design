/ailly adopt the following vale.sh rules, exactly. Quickloop the specific details for adding it to the repo, with github action integration and local execution instructions.

# Vale.sh Rules for domain-driven-design Repository

## Overview

Vale.sh is a style linter for prose. This ruleset targets the DDD repository's writing style to enforce clarity, directness, and consistency. Rules align with documented preferences: eliminate filler, reduce em-dashes, remove sycophancy, and tighten sentence structure.

## Installation

1. Create `.vale.ini` in the repository root:
```ini
[*.md]
BasedOnStyles = Google, Joblint
StylesPath = styles
Vocab = DDD

[*.md]
# Severity levels: suggestion, warning, error
TokenIgnores = ((?:\\$|\\*)?\{[A-Za-z_]+\})

# DDD custom rules
Rules = DDD.EmDashes, DDD.Parentheticals, DDD.Filler, DDD.Sycophancy, DDD.PassiveVoice, DDD.Nominalizations, DDD.Consistency, DDD.TechnicalClarity
```

2. Run: `vale sync` to pull Google and Joblint styles, then add custom rules below.

---

## Custom Rule: DDD.EmDashes

**Problem:** Em-dashes pad sentences. Prefer periods or commas.

**File:** `styles/DDD/EmDashes.yml`

```yaml
---
name: EmDashes
description: Flag em-dashes; prefer periods or commas for clarity.
message: "Replace em-dash with a period (new sentence) or comma (continuation). Em-dashes add filler."
link: "https://github.com/DavidSouther/domain-driven-design"
level: warning
scope: text
regex: '(\s|[a-z])\s+—\s+'
action:
  name: replaceAll
  params:
    - name: replace
      value: ' . '
    - name: exception
      value: 'Keep if essential for clarity between two independent clauses; otherwise split.'
```

---

## Custom Rule: DDD.Parentheticals

**Problem:** Excessive parenthetical asides disrupt flow. Limit to one per sentence; consider footnotes for long asides.

**File:** `styles/DDD/Parentheticals.yml`

```yaml
---
name: Parentheticals
description: Flag sentences with multiple parenthetical asides.
message: "This sentence has {{ count }} parenthetical asides. Limit to one per sentence; consider rewriting."
link: "https://github.com/DavidSouther/domain-driven-design"
level: warning
scope: sentence
regex: '\([^)]+\)[^.!?]*\([^)]+\)'
action:
  name: edit
```

Also flag overly long parentheticals (>50 chars):

```yaml
---
name: LongParenthetical
description: Parenthetical exceeds 50 characters; consider a new sentence.
message: "This parenthetical is {{ length }} characters. Break into a new sentence for clarity."
link: "https://github.com/DavidSouther/domain-driven-design"
level: suggestion
scope: text
regex: '\([^)]{50,}\)'
action:
  name: edit
```

---

## Custom Rule: DDD.Filler

**Problem:** Filler phrases add noise. Flag and suggest removal.

**File:** `styles/DDD/Filler.yml`

```yaml
---
name: Filler
description: Flag filler words and phrases that add no information.
message: "Remove '{{ match }}' — it adds no information."
link: "https://github.com/DavidSouther/domain-driven-design"
level: warning
scope: text

swap:
  "quite a few": "many"
  "a number of": "several"
  "in some sense": ""
  "to some extent": ""
  "sort of": ""
  "kind of": ""
  "seems to": ""
  "appears to": ""
  "arguably": ""
  "in many ways": ""
  "one might say": ""
  "it could be argued": ""
  "as a matter of fact": "in fact"
  "for the most part": "mostly"
  "at the end of the day": ""
  "when all is said and done": ""
  "in point of fact": "in fact"
  "various": "specific [term]"
```

---

## Custom Rule: DDD.Sycophancy

**Problem:** Avoid warm-for-warmth's-sake language: "great," "wonderful," excessive positivity.

**File:** `styles/DDD/Sycophancy.yml`

```yaml
---
name: Sycophancy
description: Flag sycophantic or artificially warm language.
message: "Remove '{{ match }}' — it adds warmth without content."
link: "https://github.com/DavidSouther/domain-driven-design"
level: warning
scope: text

swap:
  "great question": "question"
  "excellent point": "point"
  "wonderful example": "example"
  "lovely insight": "insight"
  "beautiful": ""
  "amazing": "remarkable" # only if truly uncommon
  "awesome": "valuable"
  "wonderful": ""
  "glad to": "will"
  "happy to": "will"
  "delighted to": "will"
  "I really": "I"
  "very unique": "unique"
  "truly": "" # often filler; keep only in superlatives
  "really": "" # usually filler
  "certainly": "" # in formal writing, often unnecessary
  "definitely": "" # usually filler
```

---

## Custom Rule: DDD.PassiveVoice

**Problem:** Passive voice obscures agency. Flag systematic passive constructions.

**File:** `styles/DDD/PassiveVoice.yml`

```yaml
---
name: PassiveVoice
description: Passive voice obscures agency. Use active voice.
message: "Passive: '{{ match }}'. Rewrite in active voice: subject + verb + object."
link: "https://github.com/DavidSouther/domain-driven-design"
level: suggestion
scope: text

regex: '\b(is|are|was|were|be|being|been)\s+\w+(ed|en)\b'
action:
  name: edit
  params:
    - name: suggestion
      value: "Use active voice. Who is performing the action?"
```

Example conversions:
- "Artifacts are produced by each phase." → "Each phase produces an artifact."
- "The pattern should be applied when…" → "Apply the pattern when…"

---

## Custom Rule: DDD.Nominalizations

**Problem:** Nominalizations (verb → noun) create static prose. Prefer verbs.

**File:** `styles/DDD/Nominalizations.yml`

```yaml
---
name: Nominalizations
description: Nominalization creates static prose. Use the verb form.
message: "Replace '{{ match }}' with its verb form for clarity and directness."
link: "https://github.com/DavidSouther/domain-driven-design"
level: suggestion
scope: text

swap:
  "the creation of": "create"
  "the determination of": "determine"
  "the development of": "develop"
  "the implementation of": "implement"
  "the introduction of": "introduce"
  "the elimination of": "eliminate"
  "the selection of": "select"
  "the identification of": "identify"
  "the design of": "design"
  "the analysis of": "analyze"
  "the addition of": "add"
  "the removal of": "remove"
  "the consideration of": "consider"
  "the evaluation of": "evaluate"
  "in isolation": "in isolation" # OK here, not a nominalization
  "isolation": "isolated" # only if nominalization is clear
```

---

## Custom Rule: DDD.Consistency

**Problem:** Inconsistent terminology breaks flow and confuses readers.

**File:** `styles/DDD/Consistency.yml`

```yaml
---
name: TermConsistency
description: Inconsistent terminology. Use the canonical term consistently.
message: "Use '{{ canonical }}' instead of '{{ match }}' for consistency."
link: "https://github.com/DavidSouther/domain-driven-design"
level: warning
scope: text

swap:
  "feature-test": "feature test"
  "feature_test": "feature test"
  "featuretest": "feature test"
  "feature-branch": "feature branch"
  "feature_branch": "feature branch"
  "DDD": "Domain-Driven Design" # or keep DDD if already established
  "bounded context": "bounded context" # not "context" alone
  "Bounded Context": "bounded context" # lowercase in prose
  "ubiquitous language": "ubiquitous language" # not "common language"
  "value object": "value object" # not "value-object" in prose
  "value-object": "value object"
  "domain service": "domain service" # not "domain-service" in prose
  "domain-service": "domain service"
  "Unit of Work": "unit of work" # pattern name, lowercase in prose
  "Unit-of-Work": "unit of work"
  "red-green-refactor": "red-green-refactor" # keep hyphenated as phase name
  "RedGreenRefactor": "red-green-refactor"
```

---

## Custom Rule: DDD.TechnicalClarity

**Problem:** Technical writing must define jargon on first use.

**File:** `styles/DDD/TechnicalClarity.yml`

```yaml
---
name: TechnicalJargon
description: Define technical terms on first use. Acronyms need expansion.
message: "First mention of '{{ match }}' should include definition or expansion."
link: "https://github.com/DavidSouther/domain-driven-design"
level: suggestion
scope: text

# This is a softer rule: flag patterns that need human review
regex: '\b(CQRS|OODA|SDLC|SKILL|PATTERN|ARTIFACT)\b'
action:
  name: edit
  params:
    - name: note
      value: "Check if this acronym is defined in context or earlier in the document."
```

---

## Custom Rule: DDD.SentenceLength

**Problem:** Long sentences (>30 words) become hard to parse. Flag for review.

**File:** `styles/DDD/SentenceLength.yml`

```yaml
---
name: SentenceLength
description: Sentence exceeds 30 words. Consider splitting into two.
message: "This sentence is {{ length }} words. Break into shorter sentences for clarity."
link: "https://github.com/DavidSouther/domain-driven-design"
level: suggestion
scope: sentence
regex: '^.{180,}(?<!\.)$' # ~30 words ≈ 180 chars
action:
  name: edit
```

---

## Custom Rule: DDD.WordChoice

**Problem:** Some words are more precise than others in technical writing.

**File:** `styles/DDD/WordChoice.yml`

```yaml
---
name: PreciseWordChoice
description: Imprecise word choice. Use the more specific term.
message: "Replace '{{ match }}' with '{{ suggestion }}' for precision."
link: "https://github.com/DavidSouther/domain-driven-design"
level: suggestion
scope: text

swap:
  "thing": "the specific object or concept" # This is vague
  "stuff": "content or data" # Too informal
  "case": "scenario or situation" # More precise
  "sometimes": "in [specific condition]" # Be specific
  "usually": "in most cases" # Be measurable
  "often": "frequently" # More specific
  "maybe": "possibly" or rephrase # Avoid hedge words
  "basically": "" # Usually filler
  "essentially": "" # Usually filler
  "component": "[specific type: module, class, service]" # Be precise
  "handle": "process, execute, manage" # More specific
  "support": "[specific capability]" # Vague
  "allow": "enable" # More active
  "help": "facilitate, enable, support" # More specific
  "work with": "use, integrate, compose" # More specific
```

---

## Custom Rule: DDD.RedundantPhrases

**Problem:** Some phrases say the same thing twice.

**File:** `styles/DDD/Redundancy.yml`

```yaml
---
name: RedundantPhrases
description: Redundant phrasing. Remove the duplicate meaning.
message: "Remove '{{ match }}' — it repeats information already stated."
link: "https://github.com/DavidSouther/domain-driven-design"
level: warning
scope: text

swap:
  "and also": "and"
  "but however": "but"
  "end result": "result"
  "final outcome": "outcome"
  "join together": "join"
  "each and every": "each"
  "one or more": "one or more" # OK, but flag in context
  "any and all": "all"
  "throughout the entire": "throughout"
  "in the event that": "if"
  "in the case where": "when"
  "at the time when": "when"
  "at this point in time": "now"
  "for the purpose of": "to"
  "in order to": "to"
```

---

## Usage in CI/CD

Add to GitHub Actions `.github/workflows/vale.yml`:

```yaml
name: Vale Lint

on: [push, pull_request]

jobs:
  vale:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - uses: errata-ai/vale-action@reviewdog
        with:
          files: 'README.md,**/*.md'
          fail_on_error: false # warnings don't fail; errors do
          reporter: github-pr-review
```

---

## Notes

1. **Severity Levels:**
   - `error` — Must fix before merge (broken grammar, consistency violations)
   - `warning` — Should fix (style infractions, filler)
   - `suggestion` — Consider (nominalization, sentence length)

2. **Exceptions:** The rules above are starting points. Some sentences *need* em-dashes or long structures; use `<!-- vale off -->` / `<!-- vale on -->` to suspend locally.

3. **Scope:** These rules are strongest for skill descriptions, less strict for code comments or YAML frontmatter.

4. **Integration:** Vale pairs well with:
   - **Prettier** (code formatting)
   - **Proselint** (prose linting)
   - **Alex** (biased language detection)

5. **Baseline:** Run `vale --generate-config` to create a base `.vale.ini`, then customize.

---

## Suggested Reading

- Microsoft Manual of Style: Conciseness chapter
- Strunk & White, *Elements of Style*: "Vigorous writing is concise"
- Technical Writing course (Google): Clear, simple prose