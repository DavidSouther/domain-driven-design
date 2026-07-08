# Tasks

- Build `scripts/vale-generate-examples.sh`, the offline LLM-generated example-backfill tier named in design.md Specification item 3.
  It should iterate every Warning/Error rule across the repo's effective style set (`Google`, `Joblint`, `DDD` — `.vale.ini`'s `BasedOnStyles`), skipping any rule already covered by the auto-derived tier (has a `swap:`/`action:` block — `vale-fix.sh`'s `lookup_example` already reads these live, nothing to generate) or already carrying a hand-authored sidecar under `styles/config/examples/` (the two seed files this session shipped — the generator must never overwrite curated content), and dispatch one LLM call per remaining rule (mirroring `vale-fix.sh`'s own `xargs -P 8` pattern) asking it to either write a `bad`/`good`/`note` example in the sidecar schema or emit nothing when the rule's own `message:`/`link:` already states a sufficient correction.
  Output is written to the sidecar path and reviewed/committed like any other content change, never generated or trusted at fix-time.
  Deliberately out of scope for this session's plan (a separate script with its own dispatch/testing needs).
  Also undecided, per design.md's Deferred technical decisions: whether this script should be periodically re-run (e.g., whenever `vale sync` updates a package's rule bodies) or is a one-time backfill — left to whoever builds/runs it next; it's designed to be idempotent (skips rules with an existing sidecar) so re-running is always safe once built.
  See design.md Specification item 3 and plan.md's Risks and Notes in session `2026-07-06-A-vale-examples`.
- Surface worked examples in `vale-check.sh`'s human-facing output too, not just `vale-fix.sh`'s Claude-facing fix prompt.
  Deliberately deferred during design — see design.md's Alternatives (resolved in `research.md`'s draft-gate review) in session `2026-07-06-A-vale-examples`; this session's build targets only the LLM fixer prompt.
- Wire intent review's phase-appropriate variant into the Research and Build draft gates.
  `references/abilities/intent-review.md` and the Design/Plan phase references now name intent review at the two gates issue #33 emphasizes (Design, Plan); the Research and Build gates follow the same soft-default rule by design but were not load-bearing for this feature's primary story and were left unwired.
  See design.md "Deferred technical decisions" in session `2026-07-04-B-intent-review-ooda`.
- Decide whether long-loop's autonomous research-and-decide reviewer (`references/shapes/long-loop.md`) should be updated to *consult* intent-review's `reviews/` entries when present, as an input to its own decisions (it never auto-clears based on them, per the never-clears invariant, but nothing today makes it read them either).
  Explicitly out of scope for the Intent Review OODA Loop feature itself.
  See design.md "Deferred technical decisions" in session `2026-07-04-B-intent-review-ooda`.
- Revisit whether intent review should be promoted from a dismissible "recommended default" to the issue's literal "primary questioning mechanism" framing (harder to skip).
  Shipped as a soft default deliberately for this feature; revisit once real usage shows the questions are consistently worth the developer's time.
  This is also dogfooded intent-review question 3 against this feature's own design, resolved for now as "dismissible, not primary" — see `.ailly/developer/2026-07-04-B-intent-review-ooda/reviews/2026-07-04-design-intent-review.md` (before that session folder was removed at cleanup) or `design.md`'s Deferred technical decisions / Open Artifact Decisions for the full reasoning.

- Extend the answer-leak hygiene gate to also grep the `design-artifacts` pair's prompt (`developer/e2e/prompts/invocation/design-artifacts.md`) for "open artifact" wording.
  Today the hygiene gate only scans `AGENTS.md` and `profile.md`; the prompt sharing both arms is the fragile invariant for the `design-artifacts` eval pair and isn't covered.
  See `.ailly/developer/2026-07-02-D-design-artifact-decisions/plan.md` Risks and Notes.
- Fix the plan phase reference: it points at `.ailly/prompts/plan-use-patterns.md`, which does not exist in this repo.
  The patterns beat currently has to be run by consulting `patterns:using-patterns` directly.
  Recurring note, also seen in session 2026-07-02-C.
- Build the eval suite that gates model adoption per complexity dimension.
  `general/skills/dispatching-agents/model-selection.md`'s Frontier-Model Caution section names this explicitly as future work ("that eval suite is named here as future work; it is not built by this guidance") — today the guidance only states the gating rule, with no suite to run it against.
  See `general/skills/dispatching-agents/model-selection.md` and design.md Specification item 4 in session `2026-07-03-A-subagent-model-guidance`.
- Periodically re-check the "as of 2026-07-03" Principle → Provider example table in `general/skills/dispatching-agents/model-selection.md` against each provider's current alias recommendations, and bump the date stamp when it's re-verified.
  `DEVELOPMENT.md`'s new "Model Guidance Maintenance" section asks Ailly to do this but there is no automation or schedule behind it yet — this entry is the tracking hook until (if ever) it becomes a scheduled check.
  See `DEVELOPMENT.md` "Model Guidance Maintenance".
- Confirm Copilot's and Gemini's own subagent-dispatch calls for a model-selection mechanism (a `model` field or equivalent).
  Neither is confirmed today, so `developer/skills/ailly/references/agents/copilot.md` and `.../gemini.md` degrade to announce-only under the mandate-with-announce rule; once either harness's mechanism is confirmed, its adapter file should be updated to mandate the model directly, matching Claude's `Task` and Codex's `spawn_agent`.
  See design.md "Deliberately deferred" in session `2026-07-03-A-subagent-model-guidance`.
- Look at `.ailly/research/2026-07-03-A-llm-model-selection/` — an older, separate research-session folder (not this session's own `.ailly/developer/2026-07-03-A-subagent-model-guidance/`), flagged during this session's build phase as possibly-stale debris.
  Its `codebase.md` describes the phase-by-provider table from the now-removed `developer/skills/ailly/references/checks/model-per-phase.md`, so its findings are now stale against the current repo.
  Not touched during this cleanup (out of scope for this topic) — a human should decide whether to delete it or fold anything worth keeping into a proper research artifact.
- Detect the "first commit to the session branch" trigger programmatically in the phase runner, rather than leaving it as coordinator-asserted prose. `using.md` rule 5 (session `2026-07-03-C-status-subissue-linking`, closes #22) now prescribes moving the board card to In Progress at that trigger and to Done when Cleanup completes and the issue closes, but design.md's Alternatives left the detection *mechanism* open as a plan/build-level question, not a wording one — the rule only names and conditions the trigger, it doesn't say how a phase runner would observe "first commit" or "issue closes" and fire the transition automatically.
- Specify a structural quoting/attribution convention for fetched comment text reproduced into later written notes, so a downstream phase or a doc-publish step cannot mistake an attacker's embedded text for project prose.
  `research/references/thread-digest.md` line 36 explicitly defers this, leaving the exact convention to the call site that adopts it, against that site's own note format; indirect prompt injection (Greshake et al.) is the real motivating risk behind this deferral, though thread-digest.md itself carries no citation for that work.
  A call site adopting thread-digest (e.g. a new research-phase consumer) will need concrete guidance on how to quote fetched text without risk of misattribution.
  This work belongs in a new reference or as an extended section in `research/references/thread-digest.md` itself (a follow-up to session `2026-07-04-A-issue-comment-intake`).
- Add the e2e invocation case for the `page-objects` pattern (issue #27, optional fast-follow deliberately deferred out of the Build phase — the reference and routing table shipped without it, mirroring `configuring-feature-flags`/`using-feature-flags`, two already-shipped patterns with no e2e case).
  Four pieces, following the existing sibling patterns' shape under `patterns/e2e/`:
  - `patterns/e2e/prompts/invocation/page-objects.md` — an invocation prompt that puts a model in a situation calling for the page-objects discriminator (a UI screen/console driven repeatedly across acceptance tests with selector/wait duplication), matching the shape of e.g. `patterns/e2e/prompts/invocation/arrange-act-assert.md`.
  - `patterns/e2e/evals/scripts/check_page_objects.py` — a structural checker (matching `patterns/e2e/evals/scripts/check_arrange_act_assert.py`'s shape) verifying the model's response names the page-objects pattern, keeps assertions out of the page object, and uses verb-phrase method naming.
  - A new entry in `patterns/e2e/evals/invocation.yaml` wiring the prompt to the checker.
  - A new entry in `patterns/e2e/assemblies/invocation.yaml` adding the case to the invocation assembly run.
  - See `patterns/e2e/evals/scripts/_checker_utils.py` for shared checker helpers already in use by sibling checks.
