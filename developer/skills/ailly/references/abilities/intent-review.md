# Intent Review

## When to Consult This

Consult this reference at a moment, the way `thinking.md` and `refactor.md` are consulted — not
as a phase, and not folded into any single phase body.

## The Backwards Method and Question Template

Ailly's five phases each accumulate a "theory of the program" (in Naur's sense) built up across
the artifacts. The one thing that predates all of those artifacts is the user's original
request. Intent review works **backward** from that original prompt through the accumulated
Research, Design, Plan, and Implementation artifacts, checking whether the theory built up along
the way has quietly drifted from what was actually asked for. It generates falsifiable questions
of the form:

> As [designed / planned / implemented], the program will **[X]**. The original request asked
> for **[Y]**. Is that what you intended?

Every question is a falsifiable claim about behavior paired with a quote or paraphrase of the
original request — never a vague quality judgment like "is this good code?"

Before raising a candidate question, cross-reference it against the *entire* original request
(not just the sentence nearest the artifact text under scrutiny) and against the artifact's own
existing "Open Artifact Decisions" or deferred-decisions section, dropping any candidate the
request or the artifact already resolves elsewhere. Skipping this dedup discipline causes the
mechanism to over-generate shallow, already-settled questions instead of surfacing genuine
drift.

## The Four Categories, and the Research-phase Variant

Categorize each question by where the divergence entered, using four labels verbatim from
issue #33:

- **Research gap**
- **Design assumption**
- **Plan scope**
- **Implementation surprise**

The Research phase gets a distinct variant instead, because at that stage there is no downstream
implementation yet to compare against the original ask — the risk is not "did this match
intent" but a **blind spot**: a **gap** the frame the research itself built has made invisible.
Its question form:

> Inside the frame we have now built, what would we no longer notice is missing? The original
> request implies [Z]; our research oriented around [W]. What has orienting on [W] made
> invisible?

## Draft-Gate Timing and the Never-Clears Invariant

## Recording: the `reviews/` Folder

## The Original-Prompt Anchor
