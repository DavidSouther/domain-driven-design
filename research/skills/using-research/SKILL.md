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
| What book covers this topic? Find an ISBN? Quote from a book? | `research:books` |
| What paper says X? Cite this DOI? What cites this paper? | `research:papers` |

## Configuring Sources

Source wiring is a once-per-environment setup task, not a per-query research move, so it lives as on-demand references rather than always-on skills. When bootstrapping or revising a source stack on a fresh checkout — probing MCP servers, falling back to HTTP, installing marketplace plugins, completing OAuth/SSO handshakes, setting auth env vars and contact details, and smoke-testing each capability against its published contract — read the matching setup reference and follow it. Each reference publishes the capability contract the per-query skill above consumes. Do NOT run these inside a research session.

| Setting up sources for | Read |
|---|---|
| Books (ISBN lookup, full text, O'Reilly, personal libraries) | `references/configuring/books.md` |
| Codebase language servers (pyright/pylsp, rust-analyzer, tsserver) | `references/configuring/codebase.md` |
| Internal authenticated sources (Slack, Notion, Linear, GitHub, Drive) | `references/configuring/internal.md` |
| Academic papers (Crossref, OpenAlex, ArXiv, PubMed, Wiley) | `references/configuring/papers.md` |
| Public web (WebSearch/WebFetch policy, augmentation provider) | `references/configuring/public.md` |

## Jeopardy! Search (all skills)

Every research skill applies Jeopardy! search: before issuing any query, generate 3–5 variants (synonyms, different phrasings, casing variants, related concepts) and run each. See `research/references/jeopardy.md` for background.

## Falsification (oppositional research)

When a claim is load-bearing, when the user asks "are you sure?", or when the evidence so far is entirely confirming, run a falsification pass before reporting a conclusion. Restate the claim as a universal, negate it into 3 to 5 concrete falsifiable hypotheses, and dispatch a subagent per hypothesis to search specifically for the negation. A single counterexample refutes the original; absence of counterexamples only fails to refute it. See `research/references/falsify.md` for procedure and limits.

## Research Notes Convention

Before dispatching search subagents, choose the research note folder:

- Standalone research uses `.ailly/research/YYYY-MM-DD-A-<topic>/`.
- Research that is part of an Ailly development task uses the task session's `.ailly/developer/<session-slug>/research/` folder when the caller provides it.

Create that folder before dispatching. Each skill writes its findings to `<skill-name>.md` in that folder, with a `**Sources**` section listing every resource consulted. In text references to sources should use a loose IEEE style. See `references/citations.md` when formatting those sections for more details.

## Combining Skills

Most research questions benefit from more than one skill. Dispatch them in parallel and synthesize the findings:

- "Why does this dependency exist and what does it actually do?" → `dependencies` + `archaeology`
- "What does the domain say this should be, and is the code correct?" → `domain` + `codebase`
- "Is this pattern documented anywhere internally or publicly?" → `internal` + `public`
