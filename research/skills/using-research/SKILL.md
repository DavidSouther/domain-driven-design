---
name: using-research
description: Bootstrap skill for research. Loaded at session start to establish when to invoke each research skill.
---

<SUBAGENT-STOP>
If you were dispatched as a subagent to execute a specific task, skip this skill.
</SUBAGENT-STOP>

# Research Skills Workflow

You are working in a project with structured research skills. When asked a research question, select the appropriate skill based on the nature of the question.

| Question type | Invoke |
|---------------|--------|
| Why did this code change? Who introduced it? When was it added or removed? | `research:archaeology` |
| What does this code do right now? Where is a symbol defined or used? | `research:codebase` |
| What version of a dependency is used? What does a package provide or require? | `research:dependencies` |
| What does this concept mean in the domain? How are domain terms defined? | `research:domain` |
| What do internal documents (Slack, Confluence, Linear, Notion) say about this? | `research:internal` |
| What does the public internet say? What do official docs or forums say? | `research:public` |

## Jeopardy! Search (all skills)

Every research skill applies Jeopardy! search: before issuing any query, generate 3–5 variants (synonyms, different phrasings, casing variants, related concepts) and run each. See `research/references/jeopardy.md` for background.

## Research Notes Convention

Before dispatching search subagents, create `docs/research/YYYY-MM-DD-<topic>/`. Each skill writes its findings to `<skill-name>.md` in that folder, with a `**Sources**` section listing every resource consulted.

## Combining Skills

Most research questions benefit from more than one skill. Dispatch them in parallel and synthesize the findings:

- "Why does this dependency exist and what does it actually do?" → `dependencies` + `archaeology`
- "What does the domain say this should be, and is the code correct?" → `domain` + `codebase`
- "Is this pattern documented anywhere internally or publicly?" → `internal` + `public`
