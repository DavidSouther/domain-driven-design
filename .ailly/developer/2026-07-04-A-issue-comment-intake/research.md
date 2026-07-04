# Research: A thread-digest research mode — full-fetch, organize, refine-or-drop any discussion thread

## Topic and Intent

This topic has two layers, and the primary deliverable is now the general one.

**(a) Primary — a general thread-digest research + review mode.** Whenever research encounters a
discussion thread — a GitHub issue/PR comment chain, a Slack thread, a Linear/Jira comment log, a
web forum, a Reddit/HN discussion, a mailing-list archive — it should be able to dispatch a
dedicated digestion of that thread rather than either ignoring it or dumping it raw into context.
The mode has three passes: (1) **full fetch** of the whole thread — tens, dozens, in extreme cases
hundreds of posts/comments, not a truncated first page; (2) an **organize** pass that sorts the raw
fetch into claims and viewpoints (who said what, where they agree or conflict, what merely restates
vs. what is new); (3) a **refine** pass that distills that organization down to what is actually
relevant to the calling research task — explicitly permitted to conclude *there is no signal here*
and drop the thread entirely, rather than always surfacing something. The user's framing:

> On any tracker, the newest comments frequently carry the *live* scope — clarifications,
> re-scoping, "actually this needs…" — while the body may or may not have edits… Comments may
> distract as much as they clarify. When research finds a thread, it should dispatch a subagent to
> work through that thread several times to understand its relevance, signals, and noise.

That is the thing Design must build: a reusable capability for turning a long, noisy thread into a
task-relevant digest (or a justified drop), applicable wherever a thread is found.

**(b) Secondary / motivating instance — the narrow GitHub #37/#29 comment-fetch fix.** The topic
originated from GitHub issue #37: Ailly task intake read only an issue's `title + body` and not its
comments, so scope-changing follow-up comments were silently dropped. The concrete instance: issue
#29's body reads as a small prose soft-block change, but a later owner comment reframes it as an e2e
benchmarking effort across ~16 models spanning 4 providers; the overnight quickloop fetched only
`title + body` (via `gh issue list --json number,title,body,labels`), so neither the coordinator nor
the #29 research runner saw the comment, and the resulting PR #34 shipped a prose diff with no
per-model data. This evidence trail is still true and still the motivating case — but the fix is now
framed as **the first concrete consumer of the general thread-digest mode**, not the whole topic. The
narrow wiring (route tracker intake through a full-thread fetch) is what feeds pass (1); the digest
mode is what then makes passes (2) and (3) worth having instead of a raw dump the coordinator must
re-read every time.

## Search/Expand

General lens — the class of failure and how it is handled elsewhere:

- **The "handle vs. object" truncation.** The failure is generic: an input arrives as a *handle*
  to a richer object (an issue number → its whole thread; a file path → its directory of
  siblings; a task id → its parent, linked docs, and prior comments; a session slug → its
  `research/` folder), and the agent consumes the cheapest literal field of that handle instead of
  hydrating the object. Issue-body-without-comments is one instance; the same shape recurs across
  the repo (see below).
- **Comments carry live scope, but they are noisy — hence three passes, not one read.** On any
  tracker or forum, the newest comments frequently carry the *live* scope — clarifications,
  re-scoping, "actually this needs…" — while the body may or may not have been edited to keep
  abreast of the conversation. Fetching body-only reads the task without any of that commentary,
  which is sometimes right and sometimes exactly the miss #29 demonstrates. But the naive opposite
  fails too: a flat full-dump of a long thread is expensive and distracting (comments distract as
  much as they clarify), and a single one-shot summary of the dump risks flattening away the one
  "actually this needs…" reframing that mattered. So the capability wants **three distinct passes
  with different jobs**: a full fetch that misses nothing, an organize pass that separates
  who-claims-what and restated-vs-new so the reframing is visible as its own item, and a refine
  pass that keeps only what bears on the calling task — or drops the thread when it finds no signal.
  The three-pass shape is what lets the mode be both complete (pass 1) and cheap-to-consume (pass 3)
  at once, which neither body-only nor full-dump achieves alone.
- **Nearby-context misses already litter this repo.** `.ailly/developer/TASKS.md` records loose
  ends that are themselves the same pattern: a plan reference pointing at a nonexistent
  `.ailly/prompts/plan-use-patterns.md`; a stale research folder describing a removed
  `model-per-phase.md`. These corroborate the general class (they are evidence, not in-scope work).
- **The source layer already supports the fix.** `research:internal`'s contract already returns
  comments for GitHub/Linear/Jira/Notion fetches (see Libraries & Skills). The miss was
  procedural: the orchestration hand-rolled a minimal `--json ...,body` query instead of routing
  through the full-thread fetch that already exists.

Full detail in `research/codebase.md` and `research/internal.md`.

General lens — public prior art for this class of problem:

- **One established name for this shape, from DDD.** Martin Fowler's
  Event Notification vs. Event-Carried State Transfer distinction names exactly the
  handle-vs-object seam: an Event Notification "doesn't carry much data... often just some ID
  information and a link back to the sender that can be queried for more information," and the
  pattern only works if the consumer reliably calls back for the full record before acting —
  a consumer that stops at the thin fields is treating a notification as if it were the full
  state transfer. Issue #37's bug is that shape: an issue number is a notification, `title +
  body` is its thin payload, and the full thread is the state the consumer must call back for.
  A second, independent community naming ("Thin Events / Rich APIs") corroborates the same split.
- **HATEOAS confirms bare-handle consumption is the industry-common failure, not an aberration.**
  REST's own hypermedia constraint calls for link-following over bare-ID consumption, yet an
  empirical survey found fewer than a fifth of real-world web APIs implement it — bare-handle
  consumption is the norm the constraint was written against, matching the "lazy and literal by
  default" framing rather than contradicting it.
- **The standard AI-coding-agent benchmark bakes in the exact same body/comments split.**
  SWE-bench (arXiv:2310.06770), the dominant public benchmark every major open-source coding
  agent (SWE-agent, mini-SWE-agent, OpenHands) reports scores against, defines `problem_statement`
  ("the issue title and body") and `hints_text` ("comments made on the issue... prior to the
  solution PR's first commit") as two separate schema fields, with comments held back by default
  to prevent solution leakage. This is strong evidence the seam is a known, industry-wide one —
  not idiosyncratic to this repo — though the benchmark's rationale for the split is leakage
  control, not an endorsement of dropping comments as good practice.
- **Production agents are already moving the other way.** GitHub's own Copilot coding agent
  states it "incorporates context from related issues or PR discussions" on pickup, and the
  open-source Open SWE framework explicitly assembles "the full issue (title, description,
  comments)" before a run starts for issue-origin tasks (while windowing PR-comment fetches to
  since-the-last-mention, to avoid unbounded replay on follow-ups). Both are live, public
  precedent for "full thread on first read" being the correct, already-adopted intake shape for
  a real agent — matching this task's narrow fix, not just theorizing it.
- **Field research came back thin on one angle.** Requirements-volatility/scope-creep is a large
  academic literature, but nothing specifically studies "issue-tracker comments carry live scope
  while the body reflects only filing-time intent" as its own phenomenon; the SWE-bench schema
  split is the closest corroboration found, and it is tooling evidence, not a requirements-
  engineering study. GitHub's webhook "best practices" doc was checked specifically for a stated
  "don't trust the payload, refetch the full resource" rule and does not contain one (it covers
  signature verification and delivery timing only) — noted as a dead end rather than stretched.

General lens — public prior art for the thread-digest capability (the primary layer):

- **The three-pass shape is the established long-content summarization pattern.** LangChain's
  `map_reduce` and `refine` summarization chains name exactly this: `map_reduce` distills each chunk
  independently then combines the partials (recursively collapsing if still too large) — the
  full-fetch → per-chunk-organize → combine shape — while `refine` walks chunks carrying a running
  summary. The proposed passes map onto this vocabulary: organize is a map over the thread, refine-
  or-drop is a reduce with a relevance filter [20][21].
- **Recursive/hierarchical summarization is academically validated, with a hallucination caution.**
  OpenAI's *Recursively Summarizing Books with Human Feedback* (arXiv:2109.10862) decomposes content
  that exceeds any context window into sections, summarizes each, and recursively summarizes the
  summaries [22] — direct precedent for the staged distillation. A 2025 follow-up, *Context-Aware
  Hierarchical Merging* (arXiv:2502.00977), finds naive chunk-then-merge pipelines **hallucinate at
  the merge step** and that re-injecting source context reduces it [23]. This is a load-bearing
  design constraint: the refine pass must stay anchored to the raw fetch, or it invents the "actually
  this needs…" it was meant to preserve.
- **Discussion-thread summarization is its own studied sub-problem, and argument mining helps.**
  ConvoSumm (ACL 2021) benchmarks thread summarization across NYT comments, StackExchange, W3C
  mailing lists, and Reddit, and shows that **argument mining improves thread summarization** [24] —
  direct evidence for the organize-into-claims middle pass over a flat summary. EmailSum (ACL 2021)
  corroborates that thread digestion is harder than prose summarization and that automatic metrics
  correlate weakly with human judgment on threads [25]. Argument mining over discussion threads
  (AMPERSAND, EMNLP 2019; IAM, ACL 2022) and stance detection with an explicit "no viewpoint / NONE"
  label (SemEval-2016 Task 6) are benchmarked NLP operations that back the organize pass and the
  refine pass's power to conclude "no signal" [27][28][29].
- **Shipping tooling already does full-fetch → digest on real threads.** Discourse AI ships
  "summarize this topic" for mega-threads [30]; the trIAge bot analyzes and replies in-thread on
  GitHub/GitLab issues and PRs [31]; and Simon Willison's "summarizing Hacker News themes with
  Claude" is a concrete hand-built three-pass pipeline — fetch the full thread via API, flatten it,
  then prompt for themes-with-quotes surfacing opposing viewpoints on 300+-comment threads [32].
- **The "drop the whole thread, no signal" decision came back genuinely thin.** No canonical paper
  names "conclude a thread carries no signal and drop it" as its own task; the closest are
  per-comment relevance classifiers and comment-ranking work seen only as search snippets. Recorded
  as a real gap: Design should treat "no signal, drop it" as a decision it introduces, anchored on
  the SemEval "NONE" precedent, not as an inherited best practice.

Full detail on the external search — both passes — in `research/public.md`.

## Libraries & Skills

This task edits **skill/reference markdown inside this repo's own `developer/skills/ailly/` and
`research/skills/` packages** — there is no external third-party library or framework, and no
`node_modules`/package surface. The "skills to load" are therefore this repo's own authoring and
contract skills.

> **Before doing any work in this feature, load these skills via the active harness's
> skill-loading mechanism:**
> - **`general:writing-skills`** — the underlying authoring methodology (CSO, TDD-of-documentation,
>   frontmatter, RED-GREEN-REFACTOR of docs) for every edit to a SKILL.md or reference file.
> - **`general:writing-paired-skills`** — because the primary edit sites are the paired
>   `program-management/configuring.md` (contract/wiring) + `program-management/using.md`
>   (per-session practice); a contract-shape change and a read-rule change must land together and
>   keep the contract explicit.
> - **`research:using-research`** and its two source contracts —
>   **`research:internal`** (`research/skills/using-research/references/configuring/internal.md`,
>   GitHub/tracker/Slack fetches returning `body, comments` / `thread or canvas contents`) and
>   **`research:public`** (`.../configuring/public.md`, `WebSearch`/`WebFetch` returning forum and
>   discussion pages). The thread-digest mode **operates on what these contracts already return**;
>   it needs no new fetch capability. Do not re-teach or re-implement fetching — cite these contracts.
> - **`general:dispatching-agents`** — its **Agent Prompt Structure** section is the home for how
>   the three passes are dispatched: three sequential subagent briefs (or one subagent running three
>   passes), each with a focused, self-contained scope and a structured hand-off. Cite it; do not
>   re-teach dispatch.
> - **`general:review`** — its Intent Review "blind spot" variant is the existing hook the narrow
>   consumer extends for "a comment postdates and reframes the scoping."

**Placement of the new capability — recommendation.** The research package already has the exact
precedent for a *shared technique reference that practice skills cite rather than reimplement*:
`research/references/jeopardy.md` (query-variant expansion) and `research/references/falsify.md`
(dispatch-a-subagent-per-hypothesis) are both plain reference files under `research/references/`,
cited from `research:using-research` and from the per-source configuring contracts (see
`configuring/public.md`'s "Composes With", which lists both). Neither is a standalone skill. The
thread-digest mode is the same shape — a cross-cutting technique invoked from multiple practice
skills (`research:internal` for tracker/Slack threads, `research:public` for forums/Reddit/HN/
mailing lists) — so the recommendation is a **new sibling `research/references/thread-digest.md`**
alongside those two, cited from `using-research` and from the internal/public configuring contracts'
"Composes With", not a new skill and not per-skill duplicated prose. This keeps the fetch contracts
(what a source returns) cleanly separated from the digest technique (what to do with a thread once
fetched), mirroring how `jeopardy.md`/`falsify.md` sit beside — not inside — the source configs.

No published external agentic skill (SKILL.md / MCP) is relevant here beyond the repo's own; the
omission is a finding, not a gap — the fetch capability already lives in `research:internal` /
`research:public`, and the digest technique is new in-repo work, not an off-the-shelf import.

## Falsification/Refine

Specific lens — right-sizing:

- **Size: this is no longer a pure bugfix — it is a small feature (a new cross-cutting research
  capability) plus a narrow bugfix consumer.** Say it plainly: the previous draft sized this as a
  bugfix-shaped doc/contract change. The refinement changes that. The primary deliverable — a
  reusable thread-digest technique with three specified passes, invoked from multiple practice
  skills — is a **small feature**: it introduces a new named capability (a new reference file and
  the citations wiring it into `research:internal`/`research:public`), not just corrected wording in
  existing files. The secondary deliverable — routing tracker intake through a full-thread fetch —
  remains **bugfix-shaped** and is the first consumer of the feature. Best handled as a small
  feature that *ships with* its first consumer, not two separate efforts.
- **Off-the-shelf?** The *fetch* half is already off-the-shelf: `research:internal` returns
  `body, comments`, `research:public` returns forum/discussion pages. Nothing new must be built to
  *read* a thread. But the *digest* half — the organize-into-claims and refine-or-drop passes — is
  genuinely new authored guidance; no existing repo reference does it. So this is not "wire two call
  sites and stop"; it is "author one new technique reference, then wire the narrow consumer to it."
- **Smallest version that still meets both layers:**
  1. **The feature (primary):** a new `research/references/thread-digest.md` specifying the three
     passes — (1) full fetch of the whole thread via the already-contracted source fetch; (2) an
     organize pass sorting the raw fetch into claims/viewpoints (who said what, agree/conflict,
     restated-vs-new); (3) a refine pass distilling to task-relevant signal, explicitly permitted to
     drop the thread as no-signal. Cited from `research:using-research` and from the
     internal/public configuring contracts' "Composes With", exactly as `jeopardy.md`/`falsify.md`
     are. Passes dispatched per `general:dispatching-agents` Agent Prompt Structure.
  2. **The consumer (secondary, bugfix-shaped):** the three coordinated tracker-intake edits from the
     prior draft, now *pointing at* the new reference — (a) `program-management/configuring.md`
     "Select next task" returns `body, comments` not just `id, title, labels`; (b)
     `program-management/using.md` gains a read rule "on selection, fetch the full thread and, when
     it is long/noisy, run it through `thread-digest` before scoping," symmetric to its write-back
     rule 6; (c) `phases/research.md` gains a tracker-origin step that fetches the full thread and,
     past a size signal, digests it via the new reference, extending the step-6 blind-spot review to
     flag a comment that postdates and reframes the scoping.
- **Falsification of "the capability is missing":** partly refuted, partly upheld. The *fetch*
  capability is present (internal.md rows for GitHub/Linear/Notion, public.md rows for WebFetch) —
  so no new transport is needed. But the *digest* capability is genuinely absent: a grep across
  `research/`, `developer/`, and `general/` finds no organize-then-refine thread-processing guidance
  (codebase.md). So the honest split is: fetch exists, digest does not — the feature is the digest.
- **What triggers three-pass digestion vs. a plain read?** A **sizing signal** should gate it: a
  short thread (a handful of comments) is read inline; a long/noisy one (tens to hundreds) is worth
  the three-pass dispatch. Recommend a **comment/post-count threshold** as the trigger, defaulting
  to plain-read below it and digest above it, with a manual override. The exact number is left as an
  open question for Design (see Resolved Decisions) — grounded loosely by ConvoSumm/EmailSum thread
  sizes (single-digit-to-low-tens email/forum threads still warranted dedicated summarization work)
  and by the Willison HN precedent operating on 300+-comment threads, but not pinned to a citation.
- **Refine — keep the general principle bounded, now folded into the feature.** The prior draft's
  "hydrate the handle / use nearby context" principle survives but as the *motivation* for the
  feature, not a separate sweeping mandate: when an input is a handle to a richer object (an issue
  number → its thread), hydrate the object before acting. Fowler's Event Notification vs.
  Event-Carried State Transfer names this seam and the thread-digest reference can borrow the
  phrasing — "call back to the rich object before acting" — rather than minting a vague
  "always-use-all-context" rule no agent can operationalize.

## Scope

**In scope for design — primary (the feature):**

- **Author the thread-digest capability**, most likely as a new `research/references/thread-digest.md`
  sibling to `jeopardy.md`/`falsify.md` (placement is an open question, but this is the recommended
  location). It specifies the three passes: full fetch → organize into claims/viewpoints → refine to
  task-relevant signal or drop as no-signal.
- **Wire it into the practice skills that encounter threads** by citation, not duplication: add it to
  `research:using-research` and to the `configuring/internal.md` and `configuring/public.md`
  "Composes With" sections, so `research:internal` (tracker/Slack threads) and `research:public`
  (forums/Reddit/HN/mailing lists) invoke it against what their fetch contracts already return.
- **Specify the trigger** — a size signal (comment/post count threshold) that selects plain-read for
  short threads and the three-pass digest for long/noisy ones — and how a "no signal, drop it"
  outcome is recorded.
- **Reference `general:dispatching-agents`** for the three-pass dispatch shape; do not re-teach dispatch.

**In scope for design — secondary (the first consumer, bugfix-shaped):**

- Wire the existing full-thread fetch into the two places a tracker item is read: next-task
  selection (`program-management` configuring contract + using read rule) and Research-phase
  tracker-origin topics (`phases/research.md`), routing long threads through the new digest reference.
- Make "fetch the full thread" the mandated intake read; forbid the truncated `title + body`
  (or `--json ...,body`) shortcut when a topic originates from a tracker item.
- Extend the Research phase's step-6 blind-spot review to flag a comment that postdates and
  materially reframes the initial scoping (issue #29 is the worked example).
- Cite `research:internal`/`research:public` contracts for the fetch; do not re-teach fetching.

**Out of scope:**

- Building the model-benchmarking eval suite that issue #29's comment actually asks for (that is
  #29's own follow-up work, not this topic).
- Reopening/redoing PR #34 or the Fable-5 soft-block.
- **Building new fetch transports or changing any source's capability set** — the fetch half already
  exists in `research:internal`/`research:public`; this task adds the digest technique, not new
  plumbing or MCP tools.
- The unrelated TASKS.md loose ends (stale plan reference, stale research folder) — cited only as
  evidence of the pattern.
- A broad, unoperationalizable "consider everything" process mandate (the digest mode is the bounded
  operationalization; the vague version stays out).

## Resolved Decisions

**Answered by research:**

- *Is the thread-fetch capability missing?* No. `research:internal` already returns
  `body, comments, diff threads` for GitHub, `issue body, comments` for Linear/Jira, and thread
  contents for Slack; `research:public` returns forum/discussion pages via `WebFetch`. The digest
  mode operates on what these already return — no new fetch transport is needed.
- *Is the digest capability missing?* Yes. A grep across `research/`, `developer/`, and `general/`
  finds no organize-then-refine thread-processing guidance (codebase.md). This absence is the
  feature to build; it is not an off-the-shelf import.
- *Is there an established shape to borrow?* Yes. LangChain `map_reduce`/`refine`, recursive
  summarization (Wu et al.), and argument-mining-improves-thread-summarization (ConvoSumm) all
  validate the three-pass shape; the hierarchical-merge hallucination caution (Ou & Lapata) says the
  refine pass must stay anchored to the raw fetch. Details in `research/public.md`.
- *Where exactly is the body-only truncation (the consumer bug)?* Two contracted call sites plus one
  ad hoc path: (1) `program-management` "Select next task" returns only `id, title, labels`;
  (2) `phases/research.md` has no tracker-origin full-thread step; (3) the overnight quickloop used a
  raw `gh issue list --json ...,body` query. Details in `research/codebase.md`.
- *Is there an existing hook for the "reframing comment" flag?* Yes — `research.md` step 6's
  `general:review` blind-spot Intent Review, but it fires against the prompt already passed in, so it
  only helps if the thread is fetched and digested first.

**Open for the human:**

1. **Placement of the new capability.** Recommendation: a new `research/references/thread-digest.md`
   sibling to `jeopardy.md`/`falsify.md`, cited (not duplicated) from `research:using-research` and
   the internal/public configuring contracts. Confirm, or prefer another home (e.g. inside
   `research:using-research` directly, or a standalone skill — research argues against both, since
   the two existing cross-cutting techniques are plain references).
2. **The size threshold that triggers three-pass digestion.** Research recommends a comment/post
   count threshold (plain-read below, digest above) but cannot ground the exact number from prior
   art — ConvoSumm/EmailSum studied single-digit-to-low-tens threads, Willison's precedent runs on
   300+. Pick the number (and whether it is a hard threshold or a heuristic with manual override).
3. **How "no signal, drop it" gets recorded.** When the refine pass concludes a thread carries no
   relevant signal, does it write a one-line "digested, no signal" note into the session's
   `research/` notes (auditable drop), silently drop it, or surface a short "considered and dropped"
   line to the human? No prior art names this decision (a genuine gap), so it is a design call.
4. **Feature-vs-bugfix shape and packaging.** Research resizes this as a **small feature** (the
   digest technique) that ships **with** its first **bugfix-shaped** consumer (tracker intake).
   Confirm they land together in one session, or split the feature and the consumer into two.
5. **Is the intake mandate a hard rule or a check-with-degrade?** Given `research:internal` returns
   Not-Available when a source is unauthenticated, a check-with-degrade (warn and proceed, like the
   model check) likely fits better than a hard gate that blocks until the full thread is fetched —
   confirm. Applies to both the fetch step and whether digestion is mandatory or best-effort.
6. **Blind-spot flag strength.** When a postdating comment reframes scope, should Research just
   *note* it in Resolved Decisions, or *halt* and force a human/refine pass? (Issue #37's third
   suggestion says "flag"; this asks how loud.)

## Sources

[1] `research/skills/using-research/references/configuring/internal.md`, GitHub/Linear/Notion fetch contract rows returning `body, comments`. Local checkout, accessed 2026-07-04.
[2] `developer/skills/ailly/references/abilities/program-management/configuring.md`, "Select next task" capability row. Local checkout.
[3] `developer/skills/ailly/references/abilities/program-management/using.md`, Practice Read/Write Rules 1-8. Local checkout.
[4] `developer/skills/ailly/references/phases/research.md`, Behavior steps 2/6/7. Local checkout.
[5] `developer/skills/ailly/SKILL.md`, "Next Task", Quick-loop, Long-loop sections. Local checkout.
[6] `general/skills/dispatching-agents/SKILL.md`, "Agent Prompt Structure". Local checkout.
[7] `general/skills/writing-paired-skills/SKILL.md`, paired configuring/using contract. Local checkout.
[8] `.ailly/developer/TASKS.md`, stale-reference/stale-folder entries as evidence of the pattern. Local checkout.
[9] M. Fowler. "What do you mean by 'Event-Driven'?" 2017-01-05. [Online]. Available: https://martinfowler.com/articles/201701-event-driven.html
[10] p-ssanders. "thin-events-rich-apis" integration pattern reference. GitHub. [Online]. Available: https://github.com/p-ssanders/thin-events-rich-apis
[11] GitHub, Inc. "Webhook events and payloads." GitHub Docs. [Online]. Available: https://docs.github.com/en/webhooks/webhook-events-and-payloads
[12] GitHub, Inc. "Best practices for using webhooks." GitHub Docs. [Online]. Available: https://docs.github.com/en/webhooks/using-webhooks/best-practices-for-using-webhooks
[13] R. Fielding. "Chapter 5: Representational State Transfer (REST)." Doctoral dissertation, UC Irvine. [Online]. Available: https://ics.uci.edu/~fielding/pubs/dissertation/rest_arch_style.htm
[14] "RESTful or RESTless -- Current State of Today's Top Web APIs." arXiv:1902.10514. [Online]. Available: https://arxiv.org/pdf/1902.10514
[15] Princeton NLP. "SWE-bench: Can Language Models Resolve Real-World GitHub Issues?" arXiv:2310.06770, ICLR 2024. [Online]. Available: https://arxiv.org/pdf/2310.06770
[16] Princeton NLP. "princeton-nlp/SWE-bench" dataset README, `problem_statement`/`hints_text` field definitions. Hugging Face. [Online]. Available: https://huggingface.co/datasets/princeton-nlp/SWE-bench/blob/main/README.md
[17] GitHub, Inc. "Assigning and completing issues with coding agent in GitHub Copilot." GitHub Blog. [Online]. Available: https://github.blog/ai-and-ml/github-copilot/assigning-and-completing-issues-with-coding-agent-in-github-copilot/
[18] LangChain, Inc. "GitHub Integration," Open SWE documentation. DeepWiki. [Online]. Available: https://deepwiki.com/langchain-ai/open-swe/2.3-github-integration
[19] "Causes and Mitigation Practices of Requirement Volatility in Agile Software Development." MDPI Informatics 11(1):12. [Online]. Available: https://www.mdpi.com/2227-9709/11/1/12
[20] LangChain. "How to summarize text through parallelization (map-reduce)." LangChain docs. [Online]. Available: https://python.langchain.com/docs/how_to/summarize_map_reduce/
[21] LangChain. "load_summarize_chain (chain_type: stuff / map_reduce / refine)." LangChain API reference. [Online]. Available: https://api.python.langchain.com/en/latest/chains/langchain.chains.summarize.chain.load_summarize_chain.html
[22] J. Wu, L. Ouyang, D. M. Ziegler, N. Stiennon, R. Lowe, J. Leike, and P. Christiano. "Recursively Summarizing Books with Human Feedback." arXiv:2109.10862, 2021. [Online]. Available: https://arxiv.org/abs/2109.10862
[23] L. Ou and M. Lapata. "Context-Aware Hierarchical Merging for Long Document Summarization." arXiv:2502.00977, 2025. [Online]. Available: https://arxiv.org/abs/2502.00977
[24] A. R. Fabbri, F. Rahman, I. Rizvi, B. Wang, H. Li, Y. Mehdad, and D. Radev. "ConvoSumm: Conversation Summarization Benchmark and Improved Abstractive Summarization with Argument Mining." ACL 2021. [Online]. Available: https://aclanthology.org/2021.acl-long.535/
[25] S. Zhang, A. Celikyilmaz, J. Gao, and M. Bansal. "EmailSum: Abstractive Email Thread Summarization." ACL 2021, arXiv:2107.14691. [Online]. Available: https://arxiv.org/abs/2107.14691
[26] "Improving Online Forums Summarization via Hierarchical Unified Deep Neural Network." arXiv:2103.13587, 2021 (search-derived; full text not fetched). [Online]. Available: https://arxiv.org/abs/2103.13587
[27] T. Chakrabarty, C. Hidey, S. Muresan, K. McKeown, and A. Hwang. "AMPERSAND: Argument Mining for PERSuAsive oNline Discussions." EMNLP 2019. [Online]. Available: https://arxiv.org/abs/2004.14677
[28] L. Cheng, L. Bing, R. He, Q. Yu, Y. Zhang, and L. Si. "IAM: A Comprehensive and Large-Scale Dataset for Integrated Argument Mining Tasks." ACL 2022. [Online]. Available: https://arxiv.org/abs/2203.12257
[29] S. Mohammad, S. Kiritchenko, P. Sobhani, X. Zhu, and C. Cherry. "SemEval-2016 Task 6: Detecting Stance in Tweets." SemEval 2016. [Online]. Available: https://aclanthology.org/S16-1003/
[30] Discourse. "Discourse AI — Summarize." Discourse Meta. [Online]. Available: https://meta.discourse.org/t/discourse-ai-summarize/262711
[31] trIAge lab. "trIAge — AI triage for GitHub/GitLab issues, discussions, and PRs." GitHub. [Online]. Available: https://github.com/trIAgelab/trIAge
[32] S. Willison. "Summarizing Hacker News discussion themes with Claude and LLM." Simon Willison's TILs. [Online]. Available: https://til.simonwillison.net/llms/claude-hacker-news-themes
[Internal] GitHub issue DavidSouther/domain-driven-design#37 (body; empty comment thread). `gh issue view 37`. Accessed 2026-07-04.
[Internal] GitHub issue DavidSouther/domain-driven-design#29 (body; owner comment 2026-07-03T22:12:07Z listing ~16 models). `gh issue view 29 --json title,body,comments`. Accessed 2026-07-04.
[Internal] GitHub pull request DavidSouther/domain-driven-design#34 (CLOSED; file list, no per-model data). `gh pr view 34 --json files,title,state`. Accessed 2026-07-04.
