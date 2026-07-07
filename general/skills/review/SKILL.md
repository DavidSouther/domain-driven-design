---
name: review
description: Use when an agent finishes work, before marking a task done, or after an edit.
---

A review is not one rubric. It is a set of independent review skills for your artifact. Compose the applicable reviewers, dispatch them in parallel, converge their findings, fix, and re-evaluate. This skill includes the base reviewer and finds specialists that match your artifact.

## Journey

1. **Compose.** Read the artifact and the available review skills, and assemble the set of reviewers that apply. The base four-criterion reviewer (below) is always in the set. Add a specialist when the artifact matches that specialist's `description`: for example `developer:clean-comments-review` when reviewing code with DocBlocks or inline comments, or `domain:using-domain` when a domain model, its objects, or its ubiquitous language changed. The model decides selection from the available skills, not a maintained table, so the skill automatically composes in any newly installed specialist.
2. **Dispatch.** Run each composed reviewer in parallel, each in its own subagent with isolated context so the lenses do not cross-contaminate (see `general:dispatching-agents`). The base reviewer writes its rubric from the criteria below and evaluates against it. A specialist produces its own critique document; that document is its findings. Do not prompt a specialist to write a rubric first. Below six reviewers, dispatch with static parallel `Agent` calls. At six or more, use a dynamic workflow that pipelines the assembled list.
3. **Converge (mandatory).** One subagent collects every reviewer's findings and performs three steps in order: **verify** each candidate against the actual artifact (read the code, trace the claim) and drop what does not hold; **deduplicate** findings that more than one reviewer raised; **severity-rank** the survivors. The fix pass receives a verified, deduplicated, ranked list, never a flat dump.
4. **Fix.** A separate subagent addresses the ranked findings. Evaluation never emits edits; fixing is always a different agent.
5. **Re-evaluate** and flag any remaining issues to the user. Repeated LLM editing risks attractor states, so handing the residue to the user mitigates that.

When the environment has no tools or file system (a self-contained review prompt), perform this inline. Build the rubric from the base criteria and evaluate the artifact against it. List the verified findings ranked by severity and stop short of editing.

## Base reviewer

The four criteria below are the always-present member of every composed set. They are the floor of every review, regardless of which specialists compose in. The base rubric lifts each criterion's diagnostic into concrete checks.

- **Correctness** ensures claims match the sources, citations, and evidence available. Flag fabricated or unsupported assertions for review. Treat every concrete statement as a claim to verify rather than trust: file paths, identifiers, environment variables, API and function signatures, URLs, version numbers, and quoted values are the details most frequently invented to look plausible. Trace each load-bearing statement to its source by reading the code, running the command, or citing the document, and flag any you cannot trace. A confident tone is not evidence. Words like "should" or "probably" frequently stand in for a check that the author never ran.
- **Completeness** ensures the work fully addresses what the user requested. Nothing important is missing or glossed over. Check both directions. Map each requirement in the request to the place the work satisfies it, and flag any requirement with no matching artifact. Flag the reverse too. Work that answers no requirement represents unrequested scope. Gaps frequently hide in unhappy paths: error handling, empty or boundary inputs, and failure modes the happy path skips. A gap acknowledged and deferred with a note is acceptable. A gap left silent is not.
- **Clarity** ensures no filler terms or weasel words. Jargon is acceptable when the context is appropriate. Vague hedges are not. Tone is professional but cordial. Favor complete, clear sentences and clauses, and read atypical punctuation as a symptom of where that fails. When an em-dash, colon, semicolon, parenthetical aside, or comma splice fuses two independent ideas, buries the subject behind qualifiers, or smuggles a list of full clauses into prose, the sentence structure is weak. Flag the entire sentence and its paragraph for restructuring, not just the punctuation. A colon introducing a real list and a parenthetical carrying a genuine cross-reference are not crutches.
- **Conciseness** requires tightening longer passages without losing meaning. Defer to correctness and clarity first, and do not shorten everything. Look for the tells of padding: a trailing clause that only restates the subject, an intensifier that adds nothing, a summary that repeats what a detail already said, or a clause kept for rhythm. Cut what does not change the meaning. Necessary depth is not padding.

## Recording the `reviews/` folder

A reviewer that poses falsifiable questions rather than deciding or editing directly notates
its findings instead of writing them in place into the artifact under review. Ailly's
`developer/skills/ailly/references/abilities/intent-review.md` is one such reviewer. Feedback resolves
into an edit or a closed note; it does not become a standing unresolved section living forever
inside the primary artifact.

Reuse long-loop's dispatch shape and dated-block entry format
(`developer/skills/ailly/references/shapes/long-loop.md`), adapted for posing rather than
deciding. In a session-folder harness such as Ailly's, this lands in a `reviews/` folder sibling
to the session's `research/` folder (`.ailly/developer/<session>/reviews/`); notate each finding
there as a dated entry. Once the human answers a finding, mark that entry **resolved** and **closed** in place. This can happen by revising the artifact, replying, or dismissing it. It does not remain an open item inside the artifact under review.

## Common mistakes

- Skipping convergence: handing the fix pass a flat, unverified, unranked list. Verify against the artifact, deduplicate, and severity-rank first.
- Prompting a specialist to write a rubric instead of consuming its critique. The specialist's critique document is already its findings.
- Treating the review as a single rubric instead of a composed set, so orthogonal concerns get a thinner pass than a dedicated reviewer would give them.
- Dropping the base reviewer from the set, so the artifact ships without the four-criterion floor.
- Running a dynamic workflow below the six-reviewer threshold where static `Agent` calls would do.
- Combining evaluation and editing into one pass. These happen in separate agents, to reduce context bloat.
- Claiming the task is complete before the review cycle finishes.
- Treating a punctuation mark as the defect. Swapping a flagged em-dash for a colon or semicolon papers over the same weak structure. Restructure the sentence instead.
