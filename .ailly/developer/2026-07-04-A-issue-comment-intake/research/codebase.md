# Codebase Findings — where a tracker item is read, and where comments are dropped

Investigation of this repo's own `developer/skills/ailly/` and `research/skills/` reference
files, tracing every place an issue or task is read into a phase runner's context.

## The comment-fetch capability already exists at the source layer

`research:internal`'s published contract already returns comments for every tracker
fetch capability. In `research/skills/using-research/references/configuring/internal.md`
(the contract table, lines 22-27):

- **GitHub issue/PR fetch** — `repo + number` → **`body, comments, diff threads where exposed`**
- **Linear/Jira fetch** — `issue id` → **`issue body, comments, linked documents`**
- **Confluence/Notion fetch** — `page id or URL` → **`page body (and comments where exposed)`**

So the ability to read the full thread is not missing from the research stack. The bug is
that the two call sites that actually select/scope a tracker item never route through this
fetch contract — they read a truncated `title + body` (or less) and stop.

## Gap 1 — program-management "Select next task" truncates to id/title/labels

`developer/skills/ailly/references/abilities/program-management/configuring.md` publishes the
capability table the using reference consumes. The **Select next task** row (line 48):

| Capability | Inputs | Returns |
|---|---|---|
| Select next task | optional team/label/status filter | highest-priority open task with **id, title, labels** |

The returned shape is `id, title, labels` — it does not even include the body, let alone
comments. Nothing downstream re-hydrates the full thread. `using.md`'s read rules (rule 3,
"Select next task via the tracker, then map it to the topic using the recorded nouns") stop
at selection; there is no "then fetch the full thread (body + comments) before scoping" step.
`using.md` rule 6 covers *writing* deferred work back as tracker comments, but there is no
symmetric rule about *reading* the comment thread. This is exactly the gap issue #37 names:
`program-management/using.md` "has no rule about reading the full issue thread."

## Gap 2 — the Research phase never routes a tracker-origin topic through the internal fetch

`developer/skills/ailly/references/phases/research.md` Behavior section:

- Step 2 (Expand) tells the runner to gather "adjacent internal libraries and docs" — nearby
  context in the *library* sense, but not the comment thread of the very issue that spawned
  the topic.
- Step 7 (Cite the wiring contract) points at `research:using-research` / `references/configuring/<source>.md`
  for source setup, but nothing in the phase says: *when the topic originates from a tracker
  item, fetch that item's full thread (body + comments) via `research:internal` and fold the
  comments into the Expand/Refine context alongside the body.*
- Step 6 (Review) composes `general:review`'s Intent Review "blind spot" variant against the
  user's initial prompt. This is the closest existing hook for "a comment reframed the task,"
  but it fires against the prompt the coordinator already passed in — if the comment was never
  fetched, its content is not in the prompt, so the blind-spot check cannot catch it.

## Gap 3 — the ad hoc/quickloop path bypasses the contract entirely

Issue #37's evidence: the overnight session fetched context with
`gh issue list --state open --json number,title,body,labels` and passed only `title + body`
into each phase runner. That raw `gh` call sidesteps the `research:internal` GitHub fetch
capability that *already* returns comments. So even where the capability exists, the
orchestration reached past it for a hand-rolled minimal query. The coordinator `SKILL.md`
"Next Task" section (line 247-256) and the quickloop/long-loop shapes give no directive that
a tracker-origin topic must be hydrated through the full-thread fetch before a phase runner
sees it.

## Nothing anywhere states the general "read the whole artifact, not the first field" rule

Grep across `developer/skills`, `general/skills`, `research/skills` for
`nearby | adjacent context | too literal | full thread | fold in | surrounding context` returns
no governing guidance — only incidental hits ("commands are literal" in a graphviz doc, "string
literals" in the codebase skill). The `general:dispatching-agents` SKILL.md "Agent Prompt
Structure" section teaches focused, self-contained briefs but says nothing about hydrating a
handle (issue number, file path, task id, prior-session slug) into its surrounding context
before handing it off. This is the general failure class the user named: agents "do exactly the
thing asked, without using the obvious nearby context."

## Existing hooks a fix could extend rather than invent

- `research.md` step 6 already runs a blind-spot Intent Review — the natural place to add "a
  comment postdates and reframes the scoping" flagging, *if* the comments are fetched first.
- `program-management/using.md` "Practice Read/Write Rules" already enumerates read rules 1-8;
  a "read the full thread on selection" rule slots in beside rule 3.
- `configuring.md`'s "Select next task" contract row is the single edit that would carry
  `body, comments` into the returned shape, matching the `research:internal` fetch it sits next to.
- The paired-skill structure (`configuring.md` + `using.md`) means a contract change and a
  read-rule change must land together; `general:writing-paired-skills` governs that pairing.

## TASKS.md corroborates the "nearby context is easy to miss" pattern (not in-scope work)

`.ailly/developer/TASKS.md` records loose ends that are themselves instances of missed nearby
context: a plan phase reference pointing at `.ailly/prompts/plan-use-patterns.md` that does not
exist; a stale research folder `.ailly/research/2026-07-03-A-llm-model-selection/` describing a
now-removed `model-per-phase.md`. These are evidence of the same class (context sitting adjacent
that an agent walked past), not tasks to fix here.

## Note on the PR #34 evidence

Issue #37 describes PR #34 as a "two-file prose diff." As checked out now, PR #34 (CLOSED)
touched 6 paths — three session artifacts, `developer/skills/ailly/SKILL.md`,
`general/skills/dispatching-agents/model-selection.md`, and one test
`developer/tests/test_fable5_softblock.py`. The soft-block landed in `model-selection.md` /
`SKILL.md`, not in `model-per-phase.md` (which no longer exists — it was removed, per a TASKS.md
entry). The substance of #37's claim is unaffected: PR #34 delivered a prose soft-block guardrail
and contained **no e2e runs and no per-model data**, so it did not address the #29 comment's real
ask (empirical baselines across ~16 models). The literal body was satisfied; the comment's scope
was not.

**Sources**

[1] `research/skills/using-research/references/configuring/internal.md`, GitHub/Linear/Notion fetch contract rows (lines 22-27). Local checkout.
[2] `developer/skills/ailly/references/abilities/program-management/configuring.md`, capability table "Select next task" row (line 48). Local checkout.
[3] `developer/skills/ailly/references/abilities/program-management/using.md`, Practice Read/Write Rules 1-8 (lines 24-35). Local checkout.
[4] `developer/skills/ailly/references/phases/research.md`, Behavior steps 2, 6, 7 (lines 28, 32, 33). Local checkout.
[5] `developer/skills/ailly/SKILL.md`, "Next Task" section (lines 247-256), Quick-loop / Long-loop shapes (lines 210-237). Local checkout.
[6] `general/skills/dispatching-agents/SKILL.md`, "Agent Prompt Structure" (lines 105-128). Local checkout.
[7] `general/skills/writing-paired-skills/SKILL.md`, paired configuring/using contract (lines 1-20). Local checkout.
[8] `.ailly/developer/TASKS.md`, stale-reference and stale-folder entries. Local checkout.
