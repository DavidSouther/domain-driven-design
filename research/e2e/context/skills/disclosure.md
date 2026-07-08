==> archaeology/SKILL.md <==
---
name: archaeology description: Use when a research question asks why code changed over time, who introduced a behavior, when a feature was added or removed, or what motivated a past decision.
Applies to questions about deleted code, renamed files, reverted changes, or the historical rationale behind current implementation.
Does not apply to questions about current codebase state or dependency structure.
---

==> books/SKILL.md <==
---
name: books description: Use when a research question targets a citable book — ISBN-keyed editions, public-domain full text, technical reference content (O'Reilly), the user's own library (Kindle, Apple Books, Calibre, Zotero), or aggregated public-domain digital libraries.
Applies every time a research question targets books.
---

==> codebase/SKILL.md <==
---
name: codebase description: Use when performing research on the current codebase — finding where a symbol is defined, discovering all call sites of a function, understanding a type's structure, tracing interface implementations, or answering any question about what the code does right now at the checked-out commit.
---

==> dependencies/SKILL.md <==
---
name: dependencies description: Use when answering questions about a project's declared dependencies, library versions, package constraints, module requirements, or third-party imports — and the dependency source is not already loaded in context.
---

==> domain/SKILL.md <==
---
name: domain description: Use when a research question is about the conceptual model of the problem space — entities, bounded contexts, ubiquitous language, invariants, or DDD maturity — rather than how code implements those concepts.
Applies when `domain:` skills are loaded or when domain artifacts exist in the codebase.
Does not apply to implementation questions (use `research:codebase`) or to questions answerable only from external sources (use `research:public`).
---

==> internal/SKILL.md <==
---
name: internal description: Use when research requires searching internal organizational documents, communication channels, wikis, tickets, or any non-public source — Slack threads, Confluence pages, ADRs, Linear issues, Notion docs, Google Drive files, GitHub issues/PRs.
Not for public internet or codebase searches.
---

==> papers/SKILL.md <==
---
name: papers description: Use when a research question targets an academic paper, preprint, or citation — DOI lookup, DOI→OA-PDF retrieval, topic search across OpenAlex / Semantic Scholar / DBLP, citation graphs, ArXiv preprints, PubMed biomedical literature, or Wiley journal content.
Applies every time a research question targets academic papers, preprints, or citations.
---

==> public/SKILL.md <==
---
name: public description: Use when a research question requires publicly available information — external library documentation, language specifications, API references, community knowledge, or any topic not contained in the local codebase or internal documents.
Applies when the answer lives on the public internet and must be fetched via web search or URL retrieval.
Does not apply to codebase structure questions (use `research:codebase`) or internal document questions (use `research:internal`).
---

==> using-research/SKILL.md <==
---
name: using-research description: Bootstrap skill for research.
Loaded at session start to establish when to invoke each research skill.
---
