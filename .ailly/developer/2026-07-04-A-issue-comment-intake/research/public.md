# Public Findings — the general lens on "handle vs. rich object" intake

External/general-lens research for issue #37 (Ailly tracker intake reads body, not comments).
Internal findings (this repo's own skills, issues, PRs) are already complete in `codebase.md`
and `internal.md` and are not repeated here. This file is the outward half of the Dual Lens:
established engineering practice and public prior art for the *class* of problem, not this
repo's instance of it.

## An established name exists one domain over: Event Notification vs. Event-Carried State Transfer

Martin Fowler's event-driven-architecture writeup names almost exactly this shape, one domain
over from issue trackers: in the **Event Notification** pattern, "an event doesn't carry much
data... often just some ID information and a link back to the sender that can be queried for
more information" — the consumer is expected to call back to the source system for the full
state before acting. The opposing pattern, **Event-Carried State Transfer**, embeds the full
state in the event itself precisely so the consumer never has to call back [1].

This is the closest established vocabulary for "a handle (issue number, order ID, entity ID)
is not the object — it is a pointer the consumer must dereference before acting." Fowler's own
framing of the failure mode is structural, not behavioral: Event Notification *works* only if
every consumer reliably calls back for the full record before acting on it; a consumer that
stops at the ID (or, in Ailly's case, at `title + body`) is consuming the notification as if it
were the full state. Issue #37's bug is a plain instance of treating an Event-Notification-shaped
input (an issue number) as if the thin fields already visible on it (`title, body`) were the
complete Event-Carried-State-Transfer payload.

A community reference implementation for the adjacent "Thin Events / Rich APIs" integration
pattern makes the same point independently: published events are deliberately thin (a URL +
timestamp), and the pattern's entire premise is that the consumer "makes a separate API call to
retrieve complete state" rather than trusting the thin payload [2]. Tier 4 (single reference
repo, not a canonical text), but it corroborates Fowler's Tier-1/2 framing with a second,
independent naming of the same shape.

## GitHub's own webhook docs: payloads are explicitly capped/truncated, re-fetch is the documented workaround

GitHub's webhook documentation states plainly that push-event payloads are capped — "for push
events with many commits, only the first 20 commits are included in the payload... use the
GitHub API to fetch the full commit list if you need more" [3]. This is a first-party, narrow
but concrete precedent for the exact shape of this bug: GitHub's own payload design assumes and
documents that consumers must re-fetch the full resource when the thin payload is insufficient,
rather than treating the payload's visible fields as exhaustive. It does not generalize this into
a named "always re-fetch" rule elsewhere in the webhook best-practices doc — that page's
guidance is about payload authenticity (signature verification) and delivery timing, not
completeness [4]. Worth noting as a limit: GitHub's docs stop short of stating the general
principle explicitly; they document the specific truncation, not the class of failure.

## HATEOAS names link-following as the ideal, and confirms bare-ID consumption is the industry-common failure

REST's HATEOAS constraint (Fielding's dissertation, via the uniform-interface constraints) holds
that a client should navigate an API by following links returned in a representation rather than
hard-coding or bare-consuming an ID [5]. The corroborating data point is that this constraint is
also the most commonly *violated* one in practice: an empirical survey of real-world web APIs
found fewer than a fifth provided hypermedia links to related resources at all [6] — i.e., the
industry default is bare-ID/thin-field consumption, not link-following, which matches the
"lazy and literal" failure mode named by the user rather than contradicting it. This is useful as
confirmation that the failure is the norm, not an aberration, rather than as a fix (Ailly's fix
is procedural discipline, not a hypermedia redesign).

## SWE-bench, the standard AI-coding-agent benchmark, bakes this exact split into its own schema

This is the most directly on-point external finding. SWE-bench (Princeton NLP, ICLR 2024;
*"SWE-bench: Can Language Models Resolve Real-World GitHub Issues?"*, arXiv:2310.06770) is the
dominant public benchmark for AI coding agents resolving GitHub issues (SWE-agent, mini-SWE-agent,
OpenHands and others report scores against it). Its task schema defines two *separate* fields for
every task instance: `problem_statement` — "the issue title and body" — and `hints_text` —
"comments made on the issue prior to the creation of the solution PR's first commit" [7][8].
These are tracked as distinct fields precisely so the benchmark can control (and in stricter
variants, withhold) `hints_text` to prevent solution leakage. In other words: the standard,
most-cited public evaluation harness for "can an AI agent resolve a GitHub issue" formalizes
the *same* body/comments split issue #37 names, and its default/most common task framing is
body-only — comments are explicitly a separate, optional-to-include field, not part of the core
task input. This does not mean SWE-bench endorses dropping comments as good practice; it means
the industry's own agent-evaluation standard already treats "body" and "comments" as two
different tiers of context, which corroborates that this is a well-known seam, not an idiosyncratic
gap in this repo. Falsification check: I looked for a stated rationale in the SWE-bench paper for
excluding hints_text by default and found the leakage-prevention framing, not a "comments are
noise" framing — so this finding supports "the seam is real and well-known," not "excluding
comments is best practice."

## Public coding agents that ship in production treat the fuller thread as correct

Two production-facing counter-examples, in the other direction, show the field moving toward
full-thread intake once the concern is a real deployed agent rather than a leakage-controlled
benchmark:

- **GitHub Copilot's own coding agent** (the first-party product): its announcement blog states
  the agent "incorporates context from related issues or PR discussions" when picking up an
  assigned issue [9]. The public docs and blog do not spell out whether this includes every
  comment on the issue itself, so treat this as directional corroboration rather than a precise
  technical confirmation — a real limit surfaced by this search, not a stretch to paper over.
- **Open SWE** (LangChain's open-source coding-agent framework) assembles, for GitHub-issue-origin
  tasks, "the full issue (title, description, comments)... before the agent starts," and separately
  windows *PR* review-comment fetches to "all comments since the most recent `@openswe` mention"
  to avoid replaying entire PR histories on every nudge [10]. This is a live, public agent
  framework encoding exactly the intake rule this repo's fix proposes for tracker-origin topics:
  full thread on first read, not just the initial field — while still avoiding unbounded replay
  for iterative follow-ups.

## Where the field research came back thin

- I found extensive academic literature on **requirements volatility / requirements churn / scope
  creep** as a general software-engineering-research topic [11], but nothing specifically studying
  "issue-tracker comment threads carry live scope while the body reflects only filing-time intent"
  as its own named phenomenon or empirical finding. The closest adjacent framing (SWE-bench's
  problem_statement/hints_text split, above) is evidence of the seam existing in tooling, not a
  requirements-engineering study of it. Treat this angle as corroborated only indirectly — do not
  cite it as if a dedicated study exists.
- GitHub's webhook "best practices" page, searched specifically for a stated "don't trust the
  payload, always fetch the full resource" rule, does not contain one — its best-practices
  guidance is about signature verification and delivery robustness, not payload completeness [4].
  I looked because it seemed like the most likely place for GitHub to state the rule explicitly;
  it isn't there, so I'm not citing it as if it were.

## Second pass: staged/hierarchical summarization of long threads (the thread-digest capability)

The refined topic scopes a general **thread-digest** capability — full fetch of a whole thread,
then an organizing pass into claims/viewpoints, then a refining pass that distills to what the
calling task needs or drops the thread. This second search looked specifically for prior art on
staged/hierarchical summarization and on claims-extraction-then-relevance-filtering over long
discussion threads. It is genuinely on-point and, unlike the requirements-volatility angle above,
came back well-supported.

### The three-pass shape is the standard long-content summarization pattern

- **LangChain's `map_reduce` and `refine` summarization chains** are the canonical named form of
  "you cannot stuff the whole thread into one prompt, so distill in stages." `stuff` concatenates
  everything into one call (fails past the context window); **`map_reduce`** summarizes each chunk
  independently (map) then combines the partial summaries (reduce), recursively collapsing if the
  combined set is still too large — the "full fetch → per-chunk distill → combine" shape directly;
  **`refine`** walks chunks sequentially carrying a running summary it updates with each new chunk
  [12][13]. This is the closest established engineering vocabulary for the proposed three passes:
  the organize pass is a map, the refine-or-drop pass is a reduce with a relevance filter.
- **Recursive/hierarchical summarization is validated academically.** OpenAI's *Recursively
  Summarizing Books with Human Feedback* (Wu et al., arXiv:2109.10862, 2021) decomposes a book into
  small sections, summarizes each, then recursively summarizes the summaries — direct precedent for
  hierarchically distilling content that exceeds any single context window [14]. A more recent
  caution, *Context-Aware Hierarchical Merging for Long Document Summarization* (Ou & Lapata,
  arXiv:2502.00977, 2025), finds that naive chunk-then-merge pipelines **hallucinate at the merge
  step**, and that re-injecting source context during merging reduces this [15] — a direct warning
  for the organize→refine passes: the distilling pass must stay anchored to the raw fetch, or it
  invents the "actually this needs…" it was meant to preserve.

### Discussion-thread summarization is its own studied sub-problem (not just prose summarization)

- **ConvoSumm** (Fabbri et al., ACL 2021) is the most on-point finding: a benchmark of crowd
  summaries across four *thread* genres (NYT comments, StackExchange, W3C email lists, Reddit), and
  it shows that **argument mining improves thread summarization** [16]. That is direct evidence for
  the middle pass: organizing a thread into claims/arguments first produces a better distillation
  than summarizing the flat dump — exactly the two-stage split the design proposes.
- **EmailSum** (Zhang et al., ACL 2021, arXiv:2107.14691) is an abstractive email-thread
  summarization dataset and finds ROUGE/BERTScore correlate only weakly with human judgment on
  threads [17] — corroborating that thread digestion is harder than document summarization and that
  a naive one-shot summary is a poor fit, motivating distinct passes. Forum-specific extractive
  work exists too (*Improving Online Forums Summarization via Hierarchical Unified Deep Neural
  Network*, arXiv:2103.13587, 2021) [18] — cited as directional; its full text was not fetched.

### Claims/viewpoints extraction and "no-signal, drop it" have prior art, but the drop-decision is thin

- **Argument mining over discussion threads** is established: AMPERSAND (Chakrabarty et al., EMNLP
  2019) mines argument components and the *relations* between them in Reddit ChangeMyView threads —
  who-claims-what and where they target each other [19]; IAM (Cheng et al., ACL 2022) defines
  Claim Extraction with Stance Classification as one joint task over ~70k sentences [20]. Both
  support the organize pass as a real, benchmarked NLP operation, not a hand-wave.
- **Stance / agreement-disagreement** classification is standard: SemEval-2016 Task 6 classifies
  text as FAVOR / AGAINST / **NONE** toward a target [21] — and the explicit "NONE / no viewpoint"
  label is the small precedent for the refine pass's power to conclude a comment carries no signal.
- **The explicit "distill-to-relevant-or-drop the whole thread" decision came back thin.** No
  single canonical paper names "decide a thread carries no signal and drop it entirely" as its own
  task; the closest are per-comment relevance-classification and comment-ranking work seen only as
  search snippets, not fetched — recorded as a genuine gap, not stretched. The drop decision is a
  sound engineering choice but is under-studied as a named problem; treat it as a design decision
  to specify, not a cited best practice.

### Shipping tooling already does full-fetch → digest on real threads

- **Discourse AI — Summarize** ships a "summarize this topic/channel" feature for mega-threads
  across pluggable model providers [22]: live product precedent that forum-thread digestion is a
  real, shipped capability, not a research toy.
- **trIAge** (2023–2026) analyzes GitHub/GitLab issues, discussions, and PRs and replies in-thread
  with categorization and duplicate detection [23] — a direct analog to a triage-and-digest bot on
  the exact tracker surface this repo's narrow fix targets.
- **Simon Willison's "Summarizing Hacker News themes with Claude"** is the most concrete three-pass
  engineering precedent found: fetch the *full* thread via the Algolia API, flatten it, then prompt
  a model to "summarize the themes… including quotes," surfacing opposing viewpoints on 300+-comment
  threads [24]. It is essentially the proposed full-fetch → organize-viewpoints → distill pipeline,
  hand-built, in the wild.

**Falsification note on this pass.** The strong, verifiable anchors are LangChain map_reduce/refine
[12][13], Wu et al. recursive summarization [14], the merge-hallucination caution [15], ConvoSumm
[16], and the Willison worked example [24]. The weaker, search-snippet-only leads (the forum
extractive paper [18], per-comment relevance classifiers, the HN-summarizer tools other than
Willison's) are recorded as directional and were not independently fetched. The genuine gap is a
named "drop the whole thread" task — it does not appear to exist as a studied problem, so the
design should treat "no signal, drop it" as a decision it introduces rather than one it inherits.

### Third pass: safety of digesting untrusted, multi-participant content

The first two passes above establish prior art for summarization *quality*. This third, separate
search looked for prior art on *safety*: every pass in a thread-digest capability feeds text
written by arbitrary thread participants directly into an LLM's context, which is a different
concern from whether the resulting summary reads well.

- **Indirect prompt injection is the named attack class this concern belongs to.** Greshake,
  Abdelnabi, Mishra, Endres, Holz, and Fritz, *"Not What You've Signed Up For: Compromising
  Real-World LLM-Integrated Applications with Indirect Prompt Injection"* (AISec '23, arXiv:2302.12173)
  [25] is the foundational paper naming *indirect* prompt injection: an attacker plants instructions
  in content the model will later retrieve or process, exploiting the blurred line between data and
  instructions. The paper demonstrates real compromises of deployed systems (Bing's GPT-4-powered
  Chat, code-completion engines) via exactly this mechanism, and states plainly that "effective
  mitigations of these emerging threats are currently lacking" as of publication. A subagent that
  fetches a whole multi-participant thread into its own context is a direct instance of this
  pattern: every participant's message is an untrusted channel of the kind this paper shows can
  hijack the consuming model. This is the citation for *why* an Untrusted Content concern applies to
  a thread-digest capability at all, not an optional hardening afterthought.
- **A named architectural mitigation exists, and it reuses the same map-reduce shape already cited
  for quality.** Beurer-Kellner, Buesser, Creţu, Debenedetti, Dobos, Fabian, Fischer, Froelicher,
  Grosse, Naeff, Ozoani, Paverd, Tramèr, and Volhejn, *"Design Patterns for Securing LLM Agents
  against Prompt Injections"* (arXiv:2506.08837, 2025) [26], analyzed via Willison's write-up
  (simonwillison.net, 2025-06-13) [also 26], catalogs architectural patterns whose shared invariant
  is: once an agent ingests untrusted input, it must be structurally impossible for that input to
  trigger consequential actions. Two patterns are directly on point: the **Dual LLM** pattern, where
  a privileged coordinator never observes untrusted tokens directly and a quarantined LLM returns
  only symbolic references (`$VAR1`, `$VAR2`) standing in for processed results; and the **LLM
  Map-Reduce** pattern, where independent sub-agents each process a slice of untrusted data and
  return only a tightly constrained output (a boolean, a score, an enum value), which a privileged
  controller then safely aggregates — explicitly the same shape as the map_reduce chain already
  cited at [12] for summarization quality, now applied for safety instead. This is the architectural
  precedent for the tool-scoping mitigation named in this design: a quarantined digest subagent that
  reads the raw thread but returns only a distilled, action-free summary to the privileged caller.
- **The genuine gap, stated plainly rather than papered over.** Dedicated red-team literature on
  prompt injection is dominated by single-document or single-email attack surfaces (this is what
  [25] itself demonstrates, and what benchmarks such as AgentDojo and InjecAgent represent). A
  follow-up search for a benchmark specifically red-teaming a *multi-party conversation thread
  summarizer* against an adversarial participant's own message returned general red-teaming and
  multi-turn adversarial-evaluation work (e.g. the ART benchmark, Gray Swan's prompt-injection
  benchmark), but nothing that squarely tests this shape: a participant embedding an instruction in
  their own thread message specifically to manipulate the digest another party will read. Adjacent
  agent-to-agent conversation-safety benchmarks test a different concern (agent behavior across
  turns, not injection via a fellow participant's content), and shipped products (e.g. Slack's
  generic "AI Guardrails" marketing) publish no technical detail on defending a produced summary
  against this specific manipulation. State this plainly: a dedicated benchmark for this exact shape
  does not appear to exist yet. This is a real gap in the field, not a best practice to cite as if
  solved.

**Sources**

[1] M. Fowler. "What do you mean by 'Event-Driven'?" 2017-01-05 (accessed 2026-07-04). [Online]. Available: https://martinfowler.com/articles/201701-event-driven.html
[2] p-ssanders. "thin-events-rich-apis: Reference implementation of the 'Thin Events / Rich APIs' integration pattern." GitHub (accessed 2026-07-04). [Online]. Available: https://github.com/p-ssanders/thin-events-rich-apis
[3] GitHub, Inc. "Webhook events and payloads." GitHub Docs (accessed 2026-07-04). [Online]. Available: https://docs.github.com/en/webhooks/webhook-events-and-payloads
[4] GitHub, Inc. "Best practices for using webhooks." GitHub Docs (accessed 2026-07-04). [Online]. Available: https://docs.github.com/en/webhooks/using-webhooks/best-practices-for-using-webhooks
[5] R. Fielding. "Chapter 5: Representational State Transfer (REST)." Doctoral dissertation, UC Irvine (accessed 2026-07-04). [Online]. Available: https://ics.uci.edu/~fielding/pubs/dissertation/rest_arch_style.htm
[6] "RESTful or RESTless -- Current State of Today's Top Web APIs." arXiv:1902.10514 (accessed 2026-07-04). [Online]. Available: https://arxiv.org/pdf/1902.10514
[7] Princeton NLP. "SWE-bench: Can Language Models Resolve Real-World GitHub Issues?" arXiv:2310.06770, ICLR 2024 (accessed 2026-07-04). [Online]. Available: https://arxiv.org/pdf/2310.06770
[8] Princeton NLP. "princeton-nlp/SWE-bench README — dataset schema (`problem_statement`, `hints_text` field definitions)." Hugging Face (accessed 2026-07-04). [Online]. Available: https://huggingface.co/datasets/princeton-nlp/SWE-bench/blob/main/README.md
[9] GitHub, Inc. "Assigning and completing issues with coding agent in GitHub Copilot." GitHub Blog (accessed 2026-07-04). [Online]. Available: https://github.blog/ai-and-ml/github-copilot/assigning-and-completing-issues-with-coding-agent-in-github-copilot/
[10] LangChain, Inc. "GitHub Integration." Open SWE documentation, DeepWiki (accessed 2026-07-04). [Online]. Available: https://deepwiki.com/langchain-ai/open-swe/2.3-github-integration
[11] "Causes and Mitigation Practices of Requirement Volatility in Agile Software Development." MDPI Informatics 11(1):12 (accessed 2026-07-04). [Online]. Available: https://www.mdpi.com/2227-9709/11/1/12
[12] LangChain. "How to summarize text through parallelization (map-reduce)." LangChain docs (accessed 2026-07-04). [Online]. Available: https://python.langchain.com/docs/how_to/summarize_map_reduce/
[13] LangChain. "load_summarize_chain (chain_type: stuff / map_reduce / refine)." LangChain API reference (accessed 2026-07-04). [Online]. Available: https://api.python.langchain.com/en/latest/chains/langchain.chains.summarize.chain.load_summarize_chain.html
[14] J. Wu, L. Ouyang, D. M. Ziegler, N. Stiennon, R. Lowe, J. Leike, and P. Christiano. "Recursively Summarizing Books with Human Feedback." arXiv:2109.10862, 2021 (accessed 2026-07-04). [Online]. Available: https://arxiv.org/abs/2109.10862
[15] L. Ou and M. Lapata. "Context-Aware Hierarchical Merging for Long Document Summarization." arXiv:2502.00977, 2025 (accessed 2026-07-04). [Online]. Available: https://arxiv.org/abs/2502.00977
[16] A. R. Fabbri, F. Rahman, I. Rizvi, B. Wang, H. Li, Y. Mehdad, and D. Radev. "ConvoSumm: Conversation Summarization Benchmark and Improved Abstractive Summarization with Argument Mining." ACL 2021 (accessed 2026-07-04). [Online]. Available: https://aclanthology.org/2021.acl-long.535/
[17] S. Zhang, A. Celikyilmaz, J. Gao, and M. Bansal. "EmailSum: Abstractive Email Thread Summarization." ACL 2021, arXiv:2107.14691 (accessed 2026-07-04). [Online]. Available: https://arxiv.org/abs/2107.14691
[18] "Improving Online Forums Summarization via Hierarchical Unified Deep Neural Network." arXiv:2103.13587, 2021 (search-derived, full text not fetched; accessed 2026-07-04). [Online]. Available: https://arxiv.org/abs/2103.13587
[19] T. Chakrabarty, C. Hidey, S. Muresan, K. McKeown, and A. Hwang. "AMPERSAND: Argument Mining for PERSuAsive oNline Discussions." EMNLP 2019 (accessed 2026-07-04). [Online]. Available: https://arxiv.org/abs/2004.14677
[20] L. Cheng, L. Bing, R. He, Q. Yu, Y. Zhang, and L. Si. "IAM: A Comprehensive and Large-Scale Dataset for Integrated Argument Mining Tasks." ACL 2022 (accessed 2026-07-04). [Online]. Available: https://arxiv.org/abs/2203.12257
[21] S. Mohammad, S. Kiritchenko, P. Sobhani, X. Zhu, and C. Cherry. "SemEval-2016 Task 6: Detecting Stance in Tweets." SemEval 2016 (accessed 2026-07-04). [Online]. Available: https://aclanthology.org/S16-1003/
[22] Discourse. "Discourse AI — Summarize." Discourse Meta (accessed 2026-07-04). [Online]. Available: https://meta.discourse.org/t/discourse-ai-summarize/262711
[23] trIAge lab. "trIAge — AI triage for GitHub/GitLab issues, discussions, and PRs." GitHub (accessed 2026-07-04). [Online]. Available: https://github.com/trIAgelab/trIAge
[24] S. Willison. "Summarizing Hacker News discussion themes with Claude and LLM." Simon Willison's TILs (accessed 2026-07-04). [Online]. Available: https://til.simonwillison.net/llms/claude-hacker-news-themes
[25] K. Greshake, S. Abdelnabi, S. Mishra, C. Endres, T. Holz, and M. Fritz. "Not What You've Signed Up For: Compromising Real-World LLM-Integrated Applications with Indirect Prompt Injection." Proc. 16th ACM Workshop on Artificial Intelligence and Security (AISec '23), Copenhagen, Denmark, pp. 79-90, arXiv:2302.12173 (verified via arXiv abstract, accessed 2026-07-04). [Online]. Available: https://arxiv.org/abs/2302.12173
[26] L. Beurer-Kellner, B. Buesser, A.-M. Creţu, E. Debenedetti, D. Dobos, D. Fabian, M. Fischer, D. Froelicher, K. Grosse, D. Naeff, E. Ozoani, A. Paverd, F. Tramèr, and V. Volhejn. "Design Patterns for Securing LLM Agents against Prompt Injections." arXiv:2506.08837, 2025 (verified via arXiv abstract; Dual LLM and Map-Reduce pattern details corroborated via S. Willison, "Design Patterns for Securing LLM Agents against Prompt Injections," Simon Willison's Weblog, 2025-06-13, and independent third-party summaries; accessed 2026-07-04). [Online]. Available: https://arxiv.org/abs/2506.08837 and https://simonwillison.net/2025/Jun/13/prompt-injection-design-patterns/
