# Intent review

> This ability runs when each `developer:ailly` phase reaches the draft gate. It uses the active harness's isolation path and reviews alongside `general:review`. There is no standalone `developer:intent-review` skill.

## Intent alignment gap

An alignment gap happens when Ailly's research, design, plan, or code doesn't match what the user wanted.

Each of Ailly's five phases builds a "theory of the program" from its work. But this theory can drift from the user's intent. Intent review works **backward** from that original request through the phase artifacts. It checks if the theory has drifted from the original intent. It generates falsifiable questions of the form:

> As [designed / planned / implemented], the program **[X]**. The original request asked
> for **[Y]**. Do they align?

Every question is a falsifiable claim about behavior paired with a quote or paraphrase of the
original request. Never include a vague quality judgment like "is this good code?"

Before raising a candidate question, cross-reference it against the *entire* original request. Also check against the artifact's own "Open Artifact Decisions" or deferred-decisions section, dropping any candidate the request or artifact already resolves elsewhere. Skipping this dedup discipline causes the mechanism to over-generate shallow, already-settled questions instead of surfacing genuine drift.

## The four categories and the research-phase variant

Categorize each question by where the divergence entered, using these four labels:

- **Research gap**
- **Design assumption**
- **Plan scope**
- **Implementation surprise**

The Research phase gets a distinct variant, instead focusing on whether the research leaves any **blind spots**: **gaps** the current research's own frame has made invisible.
Its question form:

> Inside the frame now built, what becomes invisible to notice as missing? The original
> request implies [Z]; research oriented around [W]. What has orienting on [W] made
> invisible?

## Draft-gate timing and the never-clears invariant

Intent review runs as part of artifact review when reaching the **draft gate**, before the human clears the marker. It is a
**recommended default**, not an enforcement: the developer may invoke it earlier, or dismiss it entirely. Where `general:review` may immediately apply edits, intent review surfaces questions that require user feedback before incorporating.

Intent review **never clears** a draft gate, merge gate, or Closing Bell. It is not an autonomous
gate-clearer, unlike long-loop's research-and-decide reviewer, which does auto-clear. It
**supplements** the human's existing draft-gate review without replacing the human's authority.
In long-loop mode, the coordinator's research-and-decide reviewer still owns auto-clearing.
Intent review's questions may inform that reviewer's decision, but intent review itself never
clears anything.

Dispatch is always **cold**: a memory-less, freshly dispatched reviewer with no access to the
current session's own reasoning trail, reading the artifact fresh. This is the same fresh-eyes
isolation used throughout Ailly, not the same agent reflecting on its own in-session
work.

## Recording

Intent review notates its questions by using `general:review`'s `reviews/` folder convention. Dated entries get resolved and closed once the human answers them, never written in place into the artifact under review. See that skill for the mechanism.

## The original-prompt anchor

There is no single mandated source for "the original prompt." Intent review reads whichever
anchor is genuinely available and most faithful to the original ask, best effort:

- a named `.ailly/prompts/<name>` file, when the invocation supplies one; otherwise
- the session's own `research.md` **Topic and Intent** section (or an equivalent durable record
  of the original request) as fallback.

Apply the `.ailly/prompts/` convention when present; do not formalize it as mandatory.
Whichever source is actually read, the Topic and Intent section must carry the original request
as an exact, verbatim quote, not a paraphrase. It serves either directly or as the fallback
anchor (see `references/phases/research.md`'s Topic and Intent instruction).
