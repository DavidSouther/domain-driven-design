---
name: review
description: Used when an agent is finishing a work product, before claiming a task is complete, or after completing an editing pass.
---

Review work before declaring it done by building a task-specific rubric, evaluating against it, and editing to address gaps.

## Checklist

- [ ] Prepare an evaluation rubric for the review. Include the criteria below plus any task-specific concerns (e.g., code correctness, citation accuracy, format requirements).
- [ ] In a subagent, evaluate the work against the rubric. Describe what does not meet each criterion and why. Do not suggest edits in the subagent's output.
- [ ] In a second subagent, address any issues identified by the reviewer.

## Review Criteria

- **Correctness** ensures claims match the sources, citations, and evidence available. Flag fabricated or unsupported assertions for review.
- **Completeness** ensures the work fully addresses what was requested. Nothing important is missing or glossed over.
- **Clarity** ensures no filler terms or weasel words. Jargon is acceptable when appropriate; vague hedges are not. Tone is professional but cordial.
- **Conciseness** ensures longer passages are tightened without losing meaning. Defer to correctness and clarity first; do not shorten everything.

## Common Mistakes

- Skipping the rubric and reviewing without any criteria.
- Combining evaluation and editing into one pass. These should happen in separate agents, to reduce context bloat.
- Claiming the task is complete before the review cycle finishes.

