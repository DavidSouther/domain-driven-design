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

Intent review runs by default at the **draft gate**, before the human clears the marker. It is a
**recommended default**, not an enforcement: the developer may invoke it earlier, or dismiss it
entirely. The mechanism is still experimental; promoting it from a dismissible soft default to a
harder-to-skip primary mechanism is deferred until real usage shows the questions are
consistently worth the developer's time.

Intent review **never clears** a draft gate, merge gate, or Closing Bell — not an autonomous
gate-clearer, unlike long-loop's research-and-decide reviewer, which does auto-clear. It
**supplements** the human's existing draft-gate review; it does not replace the human as the
gate-clearer. In long-loop mode, the coordinator's existing research-and-decide reviewer still
owns auto-clearing; intent review's questions may be an *input* that reviewer consults, but
intent review itself never clears anything.

Dispatch is always **cold**: a memory-less, freshly dispatched reviewer with no access to the
current session's own reasoning trail, reading the artifact fresh — the same fresh-eyes
isolation long-loop's reviewer already uses, not the same agent reflecting on its own in-session
work.

## Recording: the `reviews/` Folder

Reuse **long-loop**'s dispatch shape and dated-block *entry* format (see
`references/shapes/long-loop.md`), but do not write entries in place into the artifact under
review. Review is one piece of feedback, and feedback resolves into an edit or a closed note, not
a standing unresolved section living forever inside the primary artifact.

Instead, every session tree gains a `reviews/` folder, sibling to the existing `research/`
folder (i.e. `.ailly/developer/<session>/reviews/`). Intent review notates each question there as
a dated entry, in long-loop's entry format, adapted for posing rather than deciding. Once the
human answers a question — by revising the artifact, replying, or dismissing it — that entry is
marked **resolved** and **closed** in place; it does not remain an open item inside `design.md`,
`plan.md`, or any other artifact under review.

## The Original-Prompt Anchor

There is no single mandated source for "the original prompt." Intent review reads whichever
anchor is genuinely available and most faithful to the original ask, best effort:

- a named `.ailly/prompts/<name>` file, when the invocation supplies one; otherwise
- the session's own `research.md` **Topic and Intent** section (or an equivalent durable record
  of the original request) as fallback.

The `.ailly/prompts/` convention is used when present; it is not formalized as a convention that
must exist. Whichever source is actually read, the Topic and Intent section must carry the
original request as an exact, verbatim quote, not a paraphrase, since it serves either directly
or as the fallback anchor (see `references/phases/research.md`'s Topic and Intent instruction).
