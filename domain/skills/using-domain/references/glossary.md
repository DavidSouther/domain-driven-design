# Glossary

**Trigger:** any time a term lacks definition, is ambiguous, or is potentially synonymous with an existing term.

**ALL other DDD skills must check the glossary before introducing terminology.**

## Process

1. **Check first.** Read `docs/ddd/glossary.md` before introducing a term or asking the user about terminology. If the file does not exist yet, create it with an empty header (`# Glossary\n`) and proceed to step 4 to add the new term.
2. **If the term exists:** Use the canonical name in all documentation, DDD artifacts, and discussion. Reference it exactly as written in the glossary entry heading. Do not introduce alternate spellings or alternate forms anywhere in your work.
3. **If synonymous with an existing term:** Add the new term to the `**Synonyms:**` field of the canonical term's existing glossary entry. Do not create a separate entry for the synonym.
4. **If the term is new:** Add it with a definition, context, and source. Mark as **[DRAFT]** until human-approved.
5. **If the term is ambiguous:** Check whether the glossary already defines the term with a specific context. If so, apply that definition. If the glossary has no entry or the ambiguity remains after checking, present both interpretations to the user and ask them to choose the canonical meaning before adding any entry.

## Glossary file format

File: `docs/ddd/glossary.md`

Each entry uses this format:

```markdown
## <Term>
**Definition:** <clear, precise definition>
**Context:** <bounded context where this term is primary>
**Synonyms:** <term1>, <term2>  *(omit section if none)*
**Source:** <expert conversation | research | codebase>
```

## Rules

- Every entry must include Definition, Context, and Source.
- Include Synonyms only when synonyms exist.
- Mark terms not confirmed by a domain expert **[DRAFT]**.
- Do not remove **[DRAFT]** without explicit human approval.
