# Research: program-management/using — status-transition and sub-issue-linking rules

*2026-07-03*

## Topic and Intent

Issue #22 asks that `references/abilities/program-management/using.md` prescribe two things it currently omits:

1. When to move the project board card between Todo -> In Progress -> Done (rule 5, Record phase progress), tied to the configured tracker's status field.
2. When sub-issues discovered during build should be linked to their parent (rule 4, Create/label tasks) — immediately at creation, not deferred to cleanup — plus a Capability Routing note that GitHub's sub-issue REST endpoint needs the child's database id (an integer), not its issue number, and that `gh api -F` is the wrong tool for that value.

## Search/Expand

This is a documentation-only change to one reference file (`using.md`) plus its already-published sibling contract (`configuring.md`). No new library, service, or runtime dependency is introduced. The general-lens question is "how do other tracker integrations phrase status-transition and parent/child-linking rules" — answered directly by GitHub's own REST/CLI docs and the `cli/cli` issue tracker, not by a broader field survey:

- GitHub's sub-issues REST endpoints (`POST/DELETE /repos/{owner}/{repo}/issues/{issue_number}/sub_issues`, and reprioritize) all key off `sub_issue_id`, documented as "The id of the sub-issue to add" — i.e., the issue's database id, not its issue number [1].
- `gh api`'s `-F/--field` flag documents automatic type conversion for bare integers, `true`/`false`/`null` [2], but multiple open `cli/cli` issues show this conversion is unreliable in practice for specific fields/endpoints, including sub-issue linking itself (HTTP 500 and 404 reports with no confirmed root cause in the threads) [3][4]. Given the documented-vs-observed mismatch, the safe, unambiguous fix — and the one the issue author already prescribes — is to bypass `-F` entirely and send a pre-built JSON body via `--input -` (a heredoc), which removes the type-coercion question altogether [2].
- Community scripts that automate sub-issue linking independently confirm the "fetch the database id first, then use it" pattern (e.g., resolving `.id` via a separate lookup call before the link call) [5].
- For status transitions, GitHub Projects v2 has no dedicated "transition" verb (unlike Jira's `transitionJiraIssue`, already named in `configuring.md`); the field-write fallback is `gh project item-edit --field-id <status-field-id> --single-select-option-id <option-id>`, which requires resolving both ids via `gh project field-list` first [6]. This matches the row already published in `configuring.md`: *"Transition status ... Jira `transitionJiraIssue`; else status field write."* No new capability needs to be invented — rule 5 just needs to say when to call the existing field-write capability.

## Libraries & Skills

No library or framework surface is touched. This is a change to two markdown reference files inside `developer/skills/ailly/references/abilities/program-management/` (`using.md`, and possibly a routing-table note in `configuring.md`). No agentic skill exists for "editing Ailly's own reference docs" beyond the `developer:ailly` skill package itself already in scope, and none needs to be loaded for this change. GitHub CLI/API usage is exercised directly via `gh`/`gh api`; there is no MCP tool wrapper for sub-issue linking in this repo today (only Jira has a dedicated `transitionJiraIssue`-style tool per `configuring.md`; GitHub's own linking is already scoped as a field-write / REST call, not an MCP tool call).

## Falsification/Refine

- **Size:** a bug/small-feature-shaped documentation fix — two rules extended in one file (`using.md`), plus a cross-check that `configuring.md`'s existing capability table already supports both rules without needing new rows. Not project-shaped; no new phase, no new file layout.
- **Off-the-shelf:** no tool substitutes for this — it is prescriptive text in Ailly's own reference, not executable code.
- **Smallest version that meets intent:** edit rule 4 to add "link the child as a sub-issue immediately on creation" (with the GitHub REST/id caveat folded into Capability Routing, not rule 4 itself, since Capability Routing is where MCP/tool mechanics already live); edit rule 5 to add the two board-column triggers (Research-phase-start -> In Progress, Cleanup-complete -> Done), conditioned on the tracker's status field per the existing Not-Available/field-write pattern. No changes to `configuring.md`'s capability table are strictly required — the "Link parent/child" and "Transition status" rows already exist and already note the GitHub/Jira asymmetry; `using.md`'s Capability Routing section is the right place to add the id-type caveat, since that section already explains *how* to route against the published capability table.
- Confirmed via `gh project list --owner DavidSouther` that this repo has a real configured board ("Stellar Commander", `PVT_kwHOAAecGM4Bb0nr`) — the issue's "first Stellar Commander session" reference is this project, not a hypothetical, so the status-transition rule has a concrete tracker to describe.

## Scope

**In for design:**
- Extend `using.md` rule 4 (Create/label tasks) with: link each child issue as a sub-issue immediately at creation time, not deferred to cleanup.
- Extend `using.md` rule 5 (Record phase progress) with: move the board card to In Progress on first commit to the session branch (Research phase start); move it to Done when Cleanup completes and the issue closes. Both conditioned on the configured tracker exposing a status field (Not-Available routing applies otherwise, per the existing pattern).
- Extend `using.md`'s Capability Routing section with a note: GitHub's sub-issue endpoint takes the child's database id (integer), not its issue number; `gh api -F` is unreliable for sending that id as an integer, so use `gh api --input -` with a JSON heredoc instead.

**Out for design:**
- No changes to `configuring.md`'s capability table rows (they already cover "Link parent/child" and "Transition status" with the GitHub/Jira asymmetry noted) — design should confirm this and only touch `configuring.md` if it finds a genuine gap, not by default.
- No changes to any other ability/reference.
- No implementation of the actual sub-issue-linking or status-transition calls in this session (that is Build's job in a future feature, not this docs change) — Ailly's own program-management rules do not yet have code/tests to exercise; this is prose-only.

## Resolved Decisions

- **Resolved:** Tracker in scope is GitHub Projects v2 (confirmed live board "Stellar Commander" exists in this repo/org). Status-transition wording should be generic (keyed to "the configured tracker's status field") but the Capability Routing caveat is GitHub-specific, matching the issue's ask.
- **Resolved:** The id-type caveat belongs in Capability Routing, not restated inside rule 4, because Capability Routing is `using.md`'s existing home for "how to call the capability table," and rule 4 should stay tracker-agnostic like the rest of the numbered list.
- **Resolved:** No new capability-table rows are needed in `configuring.md`; both "Link parent/child" and "Transition status" rows already exist there. Design should treat `configuring.md` as out of scope unless it finds otherwise.
- **Open for design/human judgment:** exact wording/placement of the two new sentences in rule 4 and rule 5 (kept for design, not research, since it's a phrasing decision informed by the existing prose style of `using.md`).
- **Open for design/human judgment:** whether "first commit to the session branch" should be detected by the phase runner itself (e.g., checking `git log` on the session branch) or simply asserted as a trigger the coordinator emits when entering Research — this is a design/plan-level mechanism question, not a research one.

## Sources

[1] GitHub Docs, "REST API endpoints for sub-issues," https://docs.github.com/en/rest/issues/sub-issues (parameter description for `sub_issue_id`: "The id of the sub-issue to add").
[2] GitHub CLI Manual, "gh api," https://cli.github.com/manual/gh_api (`-F/--field` type-conversion rules; `--input` pre-built JSON body behavior).
[3] cli/cli Issue #10378, "gh api call to add sub-issue fails with HTTP/2.0 500 Internal Server Error," https://github.com/cli/cli/issues/10378.
[4] cli/cli Issue #12258, "`gh api` return 404 Not Found when adding sub_issues," https://github.com/cli/cli/issues/12258.
[5] joshjohanning/github-misc-scripts, `gh-cli/add-sub-issue-to-issue.sh`, https://github.com/joshjohanning/github-misc-scripts/blob/main/gh-cli/add-sub-issue-to-issue.sh (fetches each issue's database id via a separate lookup before linking).
[6] GitHub CLI Manual, "gh project item-edit," https://cli.github.com/manual/gh_project_item-edit (`--field-id` / `--single-select-option-id` status field write pattern).
