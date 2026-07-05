# Intent Review

> Ability referenced by each `developer:ailly` phase at its draft gate. Invoked through the active harness's isolation path and as one reviewer for `general:review`. There is no standalone `developer:intent-review` skill.

## Intent Alignment Gap

The alignment gap occurs when the research, design, plan, or implementation developed across Ailly's phases differ from the expectations and intent of the user.
Ailly's five phases each accumulate a "theory of the program" across their artifacts, but
that theory may drift from the user's original request, which precedes all of them. Intent review works **backward** from that
original prompt through the accumulated phase artifacts,
checking whether the theory built up along the way has quietly drifted from what was actually
asked for. It generates falsifiable questions of the form:

> As [designed / planned / implemented], the program will **[X]**. The original request asked
> for **[Y]**. Do they align?

Every question is a falsifiable claim about behavior paired with a quote or paraphrase of the
original request — never a vague quality judgment like "is this good code?"

Before raising a candidate question, cross-reference it against the *entire* original request
and against the artifact's own
existing "Open Artifact Decisions" or deferred-decisions section, dropping any candidate the
request or the artifact already resolves elsewhere. Skipping this dedup discipline causes the
mechanism to over-generate shallow, already-settled questions instead of surfacing genuine
drift.

## The Four Categories, and the Research-phase Variant

Categorize each question by where the divergence entered, using these four labels:

- **Research gap**
- **Design assumption**
- **Plan scope**
- **Implementation surprise**

The Research phase gets a distinct variant, instead focusing on whether the research leaves any **blind spots**: **gaps** the current research's own frame has made invisible.
Its question form:

> Inside the frame we have now built, what would we no longer notice is missing? The original
> request implies [Z]; our research oriented around [W]. What has orienting on [W] made
> invisible?

## Draft-Gate Timing and the Never-Clears Invariant

Intent review runs as part of artifact review when reaching the **draft gate**, before the human clears the marker. It is a
**recommended default**, not an enforcement: the developer may invoke it earlier, or dismiss it entirely. Where `general:review` may immediately apply edits, intent review surfaces questions that require user feedback before incorporating.

Intent review **never clears** a draft gate, merge gate, or Closing Bell. It is not an autonomous
gate-clearer, unlike long-loop's research-and-decide reviewer, which does auto-clear. It
**supplements** the human's existing draft-gate review; it does not replace the human as the
gate-clearer. In long-loop mode, the coordinator's existing research-and-decide reviewer still
owns auto-clearing; intent review's questions may be an input that reviewer consults, but
intent review itself never clears anything.

Dispatch is always **cold**: a memory-less, freshly dispatched reviewer with no access to the
current session's own reasoning trail, reading the artifact fresh — the same fresh-eyes
isolation used throughout Ailly, not the same agent reflecting on its own in-session
work.

## Recording

Intent review notates its questions using `general:review`'s `reviews/` folder convention —
dated entries, resolved and closed once the human answers them, never written in place into the
artifact under review. See that skill for the mechanism.

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
