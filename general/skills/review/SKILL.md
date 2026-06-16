---
name: review
description: Used when an agent is finishing a work product, before claiming a task is complete, or after completing an editing pass.
---

A review is a **composition of independent review skills** assembled to fit the artifact to be reviewed. The skill composes the applicable reviewers, dispatches them in parallel, converges their findings, uses the findings to decide on edits, and then re-evaluates. The skill has a default reviewer looking for correctness, completeness, clarity, and conciseness which is always applied; specialist skills (e.g. `developer:clean-comments-review`) are discovered and composed in when the artifact matches them.

Parallel fan-out ensures composing independent reviewers. Once the set is assembled, members share no state, so they dispatch concurrently and a convergence stage reconciles their findings.

## Journey

- [ ] **Compose.** Read the artifact and name the domains of concern it carries (code correctness, comment longevity, prose clarity, citation accuracy, security, domain modeling, and so on). The base four-criterion reviewer (below) is always in the set. Pick the specialists in a routing subagent:
  1. **Enumerate candidates.** List the skills installed and available to you. A *review skill* is one whose description says it critiques or evaluates a finished work product and reports findings, rather than one that builds or modifies. Today the repo ships one such specialist, `developer:clean-comments-review` (comment and DocBlock longevity); treat the list as open, since others may be installed.
  2. **Match by domain.** Compose in a specialist when its description's trigger matches a domain the artifact actually carries. An artifact with concerns in more than one domain (code correctness *and* comment longevity, prose clarity *and* citation accuracy) gets a reviewer per domain.
  3. **Exclude the rest.** Skip a specialist whose trigger the artifact does not meet. Composing in a reviewer with nothing to look for spends an agent to produce noise.

  This is model-decided selection against the live skill list, not a maintained table, so a newly installed specialist is composed in with no edit to this skill.
- [ ] **Dispatch (fan out).** Run each composed reviewer in parallel, each in its own subagent with isolated context and its own lens. The base reviewer builds its rubric from the criteria below and evaluates against it. A specialist emits its own critique document; that document *is* its findings. Do not prompt a specialist to write a rubric first. Below six composed reviewers, dispatch with static parallel `Agent` calls. At six or more, use a dynamic workflow that pipelines the assembled list.
- [ ] **Converge (mandatory).** One convergence subagent collects all findings and performs three steps in order: **verify** each candidate against the actual artifact (read the code, trace the claim, quote the line) and drop what does not hold; **deduplicate** and indicate findings raised by more than one reviewer; **severity-rank** the survivors. Hand the fix pass a verified, deduplicated, ranked list.
- [ ] **Fix.** In a separate subagent, address the ranked findings. Evaluation never emits edits; fixing is its own agent.
- [ ] **Re-evaluate** after fixing, and flag any further issues to the user for their review. Repeated LLM editing risks entering attractor states, so asking the user to take over mitigates that risk.

## Base Reviewer Criteria

The base reviewer covers four criteria. They are the floor of every review regardless of which specialists were composed in. Lift each diagnostic into concrete checks.

- **Correctness** ensures claims match the sources, citations, and evidence available. Flag fabricated or unsupported assertions for review. Treat every concrete statement as a claim to verify rather than trust: file paths, identifiers, environment variables, API and function signatures, URLs, version numbers, and quoted values are the details most often invented to look plausible. Trace each load-bearing statement to its source by reading the code, running the command, or citing the document, and flag any that cannot be traced. A confident tone is not evidence. Words like "should" or "probably" often stand in for a check that was never run.
- **Completeness** ensures the work fully addresses what was requested. Nothing important is missing or glossed over. Check both directions. Map each requirement in the request to the place the work satisfies it, and flag any requirement with no matching artifact. Flag the reverse too. Work that answers no requirement is unrequested scope. Gaps often hide in unhappy paths: error handling, empty or boundary inputs, and failure modes the happy path skips. A gap acknowledged and deferred with a note is acceptable. A gap left silent is not.
- **Clarity** ensures no filler terms or weasel words. Jargon is acceptable when the context is appropriate. Vague hedges are not. Tone is professional but cordial. Favor complete, clear sentences and clauses, and read atypical punctuation as a symptom of where that fails. When an em-dash, colon, semicolon, parenthetical aside, or comma splice fuses two independent ideas, buries the subject behind qualifiers, or smuggles a list of full clauses into prose, the sentence structure is weak. Flag the entire sentence and its paragraph for restructuring, not just the punctuation. A colon introducing a real list and a parenthetical carrying a genuine cross-reference are not crutches.
- **Conciseness** ensures longer passages are tightened without losing meaning. Defer to correctness and clarity first, and do not shorten everything. Look for the tells of padding: a trailing clause that only restates the subject, an intensifier that adds nothing, a summary that repeats what a detail already said, or a clause kept for rhythm. Cut what does not change the meaning. Necessary depth is not padding.

## Common Mistakes

- Treating the review as a single rubric instead of a composed set of independent reviewers.
- Dropping the base reviewer from the composed set, so an artifact ships without the four-criterion floor.
- Prompting a specialist to write a rubric instead of consuming its critique document directly.
- Skipping convergence and handing the fix pass a flat, unverified, unranked list.
- Running a dynamic workflow below the six-reviewer threshold when static parallel dispatch would do.
- Combining evaluation and editing into one pass. These should happen in separate agents, to reduce context bloat.
- Claiming the task is complete before the review cycle finishes.
- Treating a punctuation mark as the defect. Swapping a flagged em-dash for a colon or semicolon papers over the same weak structure. Restructure the sentence instead.

