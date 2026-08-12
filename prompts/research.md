---
description: Answer a research question via research:using-research's routing, dispatched through research_dispatch
argument-hint: "<question>"
---
Read `research/skills/using-research/SKILL.md` and pick the research skill(s) that fit this question from its routing table (dispatch more than one in parallel when the question spans, e.g., "why does this exist and what does it do" style combinations). Then call the `research_dispatch` tool with those skill name(s) and this question, rather than assembling subagent dispatch or notes-folder paths by hand.

Question: $ARGUMENTS
