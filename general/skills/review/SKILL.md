---
name: review
description: Use when preparing a final work product for handoff, before claiming a task is complete.
---

A review is not one rubric. It composes independent reviewers for the final artifact in front of it: `general:c3-review` is always present, and specialists compose in when the artifact matches them. Dispatch the reviewers in parallel, converge their findings, fix, and re-evaluate.

## Journey

1. **Compose.** Read the final artifact and the available review skills. Dispatch one isolated subagent that invokes `general:c3-review`; it is always in the set. Add a specialist when its `description` matches the final artifact — for example `developer:clean-comments-review` when reviewing code with DocBlocks or inline comments, or `domain:using-domain` when a domain model, its objects, or its ubiquitous language changed. Selection is model-decided from the available skills, not a maintained table, so a newly installed specialist is composed in with no edit here.
2. **Dispatch.** Run each composed reviewer in parallel, each in its own subagent with isolated context so the lenses do not cross-contaminate (see `general:dispatching-agents`). C3's subagent collects feedback per `general:c3-review`; a specialist produces its own critique document. Those documents are their findings — do not prompt a specialist to write a rubric first. Below six reviewers, dispatch with static parallel `Agent` calls. At six or more, use a dynamic workflow that pipelines the assembled list.
3. **Converge (mandatory).** One subagent collects every reviewer's findings and performs three steps in order: **verify** each candidate against the actual artifact (read the code, trace the claim) and drop what does not hold; **deduplicate** findings that more than one reviewer raised; **severity-rank** the survivors. The fix pass receives a verified, deduplicated, ranked list, never a flat dump.
4. **Fix.** A separate subagent addresses the ranked findings. Evaluation never emits edits; fixing is always a different agent.
5. **Re-evaluate** and flag any remaining issues to the user. Repeated LLM editing risks attractor states, so handing the residue to the user mitigates that.

After initial convergence, dispatch a separate cold challenger and fresh final verifier under `general:c3-review`'s High-severity challenge protocol. C3 and any specialists run only to prepare a final artifact for handoff; Intent review is the continuous, every-phase-or-stage mechanism for an evolving Ailly artifact instead.

When the environment has no tools or file system (a self-contained review prompt), apply the `general:c3-review` rubric inline, list verified findings ranked by severity, and stop short of editing.

## Recording: the `reviews/` Folder

A reviewer that poses falsifiable questions rather than deciding or editing directly — Ailly's
`developer/skills/ailly/references/abilities/intent-review.md` is one such reviewer — notates
its findings instead of writing them in place into the artifact under review. Feedback resolves
into an edit or a closed note; it does not become a standing unresolved section living forever
inside the primary artifact.

Reuse long-loop's dispatch shape and dated-block entry format
(`developer/skills/ailly/references/shapes/long-loop.md`), adapted for posing rather than
deciding. In a session-folder harness such as Ailly's, this lands in a `reviews/` folder sibling
to the session's `research/` folder (`.ailly/developer/<session>/reviews/`); notate each finding
there as a dated entry. Once the human answers a finding — by revising the artifact, replying, or
dismissing it — mark that entry **resolved** and **closed** in place. It does not remain an open
item inside the artifact under review.

## Pi Workflow

Under pi, run Dispatch and Converge (steps 2 and 3 above) with the `review_run` tool (`.pi/extensions/review-subagent/`) instead of relying on the orchestrating model to remember both. One call spawns an isolated `general:c3-review` subprocess plus any `specialists` you name in parallel, then always runs a dedicated convergence subprocess against the raw findings before returning anything: convergence cannot be skipped because it is not a separate step the calling model has to remember, it is inside the tool call. If it returns a High-severity finding, the caller separately dispatches C3's cold challenger and final verifier; `review_run` evaluates and converges only. Composition (step 1: which specialists apply) stays your call, same as skill selection in `research:using-research`; fix (step 4) and re-evaluate (step 5) stay separate turns.

Name specialists in `specialists` the way pi knows them — by frontmatter `name` (`"clean-comments-review"`, `"using-domain"`), not this document's `<plugin>:<skill>` prose form (accepted too, but only the part after the colon is used). `review_run` resolves each name by searching the calling project's own `.pi/skills`/`.agents/skills` first, then this package's skills, then user-global skills — pi's own discovery precedence. That is what keeps "a newly installed specialist is composed in with no edit here" true for a project that installs this package: a project can write its own brand-new specialist skill under its own `.pi/skills/`, or pull one from a different installed pi package, and pass its name straight through with no change to this skill or to `review_run` itself.

```
review_run({
  artifactPath: "src/session/manager.ts",
  specialists: ["clean-comments-review"],
  model: "<the model general/skills/dispatching-agents/model-selection.md recommends>"
})
```

## Common Mistakes

- Skipping convergence: handing the fix pass a flat, unverified, unranked list. Verify against the artifact, deduplicate, and severity-rank first.
- Prompting a specialist to write a rubric instead of consuming its critique. The specialist's critique document is already its findings.
- Treating the review as a single rubric instead of a composed set, so orthogonal concerns get a thinner pass than a dedicated reviewer would give them.
- Dropping `general:c3-review` from the set, so the final artifact ships without the C3 floor.
- Running a dynamic workflow below the six-reviewer threshold where static `Agent` calls would do.
- Combining evaluation and editing into one pass. These happen in separate agents, to reduce context bloat.
- Claiming the task is complete before the review cycle finishes.
- Treating a punctuation mark as the defect. Swapping a flagged em-dash for a colon or semicolon papers over the same weak structure. Restructure the sentence instead.
