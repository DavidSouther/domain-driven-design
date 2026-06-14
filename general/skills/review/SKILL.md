---
name: review
description: Used when an agent is finishing a work product, before claiming a task is complete, or after completing an editing pass.
---

Review work before declaring it done by building a task-specific rubric, evaluating against it, and editing to address gaps.

## Checklist

- [ ] Prepare an evaluation rubric for the review. Include the criteria below, lifting each criterion's diagnostic into concrete checks, plus any task-specific concerns (e.g., code correctness, citation accuracy, format requirements).
- [ ] In a subagent, evaluate the work against the rubric. For each criterion, describe what fails and why, with the line and a quote. Do not suggest edits in the subagent's output.
- [ ] In a second subagent, address the issues the reviewer identified.
- [ ] Re-evaluate after fixing, and flag any further issues to the user for their review. Repeated LLM editing risks entering attractor states, so asking the user to take over mitigates that risk.

## Review Criteria

- **Correctness** ensures claims match the sources, citations, and evidence available. Flag fabricated or unsupported assertions for review. Treat every concrete statement as a claim to verify rather than trust: file paths, identifiers, environment variables, API and function signatures, URLs, version numbers, and quoted values are the details most often invented to look plausible. Trace each load-bearing statement to its source by reading the code, running the command, or citing the document, and flag any that cannot be traced. A confident tone is not evidence. Words like "should" or "probably" often stand in for a check that was never run.
- **Completeness** ensures the work fully addresses what was requested. Nothing important is missing or glossed over. Check both directions. Map each requirement in the request to the place the work satisfies it, and flag any requirement with no matching artifact. Flag the reverse too. Work that answers no requirement is unrequested scope. Gaps often hide in unhappy paths: error handling, empty or boundary inputs, and failure modes the happy path skips. A gap acknowledged and deferred with a note is acceptable. A gap left silent is not.
- **Clarity** ensures no filler terms or weasel words. Jargon is acceptable when the context is appropriate. Vague hedges are not. Tone is professional but cordial. Favor complete, clear sentences and clauses, and read atypical punctuation as a symptom of where that fails. When an em-dash, colon, semicolon, parenthetical aside, or comma splice fuses two independent ideas, buries the subject behind qualifiers, or smuggles a list of full clauses into prose, the sentence structure is weak. Flag the entire sentence and its paragraph for restructuring, not just the punctuation. A colon introducing a real list and a parenthetical carrying a genuine cross-reference are not crutches.
- **Conciseness** ensures longer passages are tightened without losing meaning. Defer to correctness and clarity first, and do not shorten everything. Look for the tells of padding: a trailing clause that only restates the subject, an intensifier that adds nothing, a summary that repeats what a detail already said, or a clause kept for rhythm. Cut what does not change the meaning. Necessary depth is not padding.

## Common Mistakes

- Skipping the rubric and reviewing without any criteria.
- Combining evaluation and editing into one pass. These should happen in separate agents, to reduce context bloat.
- Claiming the task is complete before the review cycle finishes.
- Treating a punctuation mark as the defect. Swapping a flagged em-dash for a colon or semicolon papers over the same weak structure. Restructure the sentence instead.

