# Design: program-management/using — status-transition and sub-issue-linking rules

*2026-07-03*

## Purpose

`references/abilities/program-management/using.md` currently under-specifies two per-session behaviors that the first live Stellar Commander session exposed: (1) it never says when to move the tracker's board card between Todo -> In Progress -> Done, and (2) it tells rule 4 to "link to the parent Epic" without saying *when* a sub-issue discovered mid-build must be linked, or how GitHub's linking endpoint's id-type quirk should be routed. Both gaps let an agent defer or skip work a human reviewer would expect to already be done, so this closes them directly in prose, matching the closed-form worked example in `configuring.md`'s capability table.

## Prior Art

- `configuring.md`'s capability table already publishes the two capabilities in question — `Link parent/child` (GitHub `sub_issue_write`; else parent field write) and `Transition status` (Jira `transitionJiraIssue`; else status field write) — so this design adds *trigger* language to `using.md`, not new capability rows.
- `using.md` rule 5 already names the default phase-representation strategy (ticking the task's checklist); the new status-transition language extends that same rule rather than adding a new numbered rule, keeping "record phase progress" as the single home for all phase-progress side effects.
- `using.md`'s Capability Routing section is already the documented home for "how to call the capability table" mechanics (e.g., the Not-Available routing signal); the GitHub id-type caveat belongs there, confirmed in research's Resolved Decisions.

## User Journey and Metrics

**Journey:** During a development session with GitHub configured as the active tracker, an agent (a) creates a child task discovered mid-build and links it as a sub-issue of the parent Epic in the same step it creates the task — not deferred to cleanup — using the child's database id via a JSON body, not `gh api -F`; and (b) moves the board card to **In Progress** at the first commit to the session branch (Research phase start) and to **Done** when Cleanup completes and the issue closes, both routed through the existing status-field-write capability when no dedicated transition tool exists.

**Metric (source-level, since this is a documentation feature):** `using.md`'s rule 4 states the "link immediately at creation" trigger; rule 5 states both board-column triggers tied to phase boundaries; the Capability Routing section states the GitHub id-type/`-F` caveat. The feature test encodes all three as a single passing contract check once the rules are in place.

## Specification

Three prose additions to `developer/skills/ailly/references/abilities/program-management/using.md`, no changes to `configuring.md` (research confirmed its capability table already covers both rows):

1. **Rule 4 (Create/label tasks)** gains a sentence: link each child issue as a sub-issue of its parent **immediately when the child is created**, not deferred to cleanup, using the existing link-parent/child capability (field-write fallback unchanged).
2. **Rule 5 (Record phase progress)** gains two trigger sentences, conditioned on the configured tracker exposing a status field (Not-Available routes to the existing fallback pattern otherwise):
   - Move the board card to **In Progress** when the Research phase begins (first commit to the session branch).
   - Move the board card to **Done** when the Cleanup phase completes and the issue closes.
3. **Capability Routing** gains a GitHub-specific routing note: the sub-issue endpoint takes the child's **database id** (an integer), not its issue number; `gh api -F` sends values as strings and is unreliable for this field, so route the call through `gh api --input -` with a JSON heredoc body instead.

No new capability-table rows, no new files, no code. The one feature test is a source-level contract check (matching the existing pattern in `developer/tests/test_subagent_model_mandate.py` and `test_research_note_paths.py`) that reads `using.md` and asserts all three additions are present with the right conditioning language. It is RED today because none of the three exist yet.

## Alternatives

- **Add new capability-table rows in `configuring.md` instead of prose in `using.md`.** Rejected: research confirmed the two rows (`Link parent/child`, `Transition status`) already exist and already note the GitHub/Jira asymmetry; the gap is purely about *when* the practice skill calls them, which is `using.md`'s job, not the wiring reference's.
- **Put the GitHub id-type caveat inline in rule 4** instead of Capability Routing. Rejected per research's resolved decision: rule 4 should stay tracker-agnostic like the rest of the numbered list; Capability Routing is `using.md`'s existing, established home for tracker-specific call mechanics.
- **Detect "first commit to the session branch" programmatically in the phase runner** rather than asserting it as a coordinator-emitted trigger. Left open per research (a plan/build-level mechanism question, not a wording question); this design only prescribes the trigger's *name and condition* in prose, not its detection mechanism, since the reference file is prose, not code.

## Summary

`using.md` rule 4 gets an immediate-linking sentence, rule 5 gets two board-column triggers conditioned on the tracker's status field, and Capability Routing gets a GitHub id-type/`-F` caveat. `configuring.md` is untouched. The single feature test is a source-level contract check against `using.md`'s text, currently RED.

No Open Artifact Decisions: the one artifact this design touches — the feature test's path — follows the already-established `developer/tests/test_<topic>.py` source-contract-test convention (see `test_research_note_paths.py`, `test_subagent_model_mandate.py`, `test_quick_loop_review_retention.py`), so it is derived, not invented.

**Feature test:** `developer/tests/test_status_transition_and_subissue_linking.py`
