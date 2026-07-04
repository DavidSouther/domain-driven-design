# Implementation Plan: program-management/using — status-transition and sub-issue-linking rules

**Feature test:** `developer/tests/test_status_transition_and_subissue_linking.py`
**User story:** As an agent running a development session with GitHub configured as the tracker, I link a discovered sub-issue to its parent the moment I create it (not at cleanup) and move the board card through In Progress/Done at the right phase boundaries, per the rules `using.md` prescribes.
**Steps:**
- [x] Step 0: API surface area (N/A — documentation-only change)
- [x] Step 1: Rule 4 — immediate sub-issue linking
- [x] Step 2: Rule 5 — board-column triggers
- [x] Step 3: Capability Routing — GitHub id-type/`-F` caveat

## Step 0: API surface area

**No new types or function signatures.** This feature is a prose-only change to one reference file (`developer/skills/ailly/references/abilities/program-management/using.md`); design.md's Specification is explicit that it introduces "No new capability-table rows, no new files, no code." There is no domain model, entity, or service to stub — Step 0 is a decision record, not code: the change surface is three sentences/clauses added to existing numbered-list items and one existing `##` section in an existing markdown file. Patterns-using-patterns beat is skipped for the same reason (no type/API surface exists to apply newtype/domain-objects/type-states to); this is recorded here rather than silently omitted so the builder doesn't go looking for a Step 0 diff that doesn't exist.

No skills to load during build: research.md's Libraries & Skills section confirms no library, framework, or agentic skill surface is touched beyond the `developer:ailly` package already in scope.

## Step 1: Rule 4 — immediate sub-issue linking

**Enables:** feature-test check T1 (rule 4 must say sub-issues are linked immediately when the child issue is created, and must say this is not deferred to cleanup).

Extend `using.md` rule 4 ("Create/label tasks for features and bugs...") with a clause: link each child issue as a sub-issue of its parent **immediately when the child is created**, not deferred to cleanup, using the existing link-parent/child capability (the field-write fallback stays unchanged for trackers without a dedicated tool). Keep the sentence tracker-agnostic — no GitHub-specific mechanics here; those belong in Capability Routing (Step 3).

**Tests**

Run the feature test after this edit; T1's checks on rule 4 (`numbered_item(text, 4)` containing "immediately", "creat*", "cleanup", and "not deferred"/"defer") should pass. T2 and T3 will still fail — expected, since rule 5 and Capability Routing are untouched.

- Edge case: rule 4's numbered-item regex must still match — do not restructure rule 4 into a nested list or split it into sub-items, since the test locates it as a single `4. **...**` block up to `5. **...**`.
- Edge case: the word "cleanup" must appear in rule 4's own text (not merely a cross-reference), and "not deferred" or "defer" must appear alongside it.

**Implementation Outline**

Edit one line in `using.md`'s Practice Read/Write Rules, rule 4, appending a clause after the existing "link to the parent Epic via the link capability (field-write fallback where no dedicated tool exists)" sentence — do not touch rules 1-3 or 5-8.

## Step 2: Rule 5 — board-column triggers

**Enables:** feature-test check T2 (rule 5 must name "In Progress" tied to Research-phase-start/first-commit, "Done" tied to Cleanup completing, and both conditioned on "status field").

Extend `using.md` rule 5 ("Record phase progress...") with two trigger sentences:
- Move the board card to **In Progress** when the Research phase begins (first commit to the session branch).
- Move the board card to **Done** when the Cleanup phase completes and the issue closes.

Both triggers are conditioned on the configured tracker exposing a status field (the phrase "status field" must appear in rule 5's text); where no status field exists, route through the existing Not-Available/field-write fallback pattern already established in Capability Routing — do not re-describe that fallback inline in rule 5.

**Tests**

Run the feature test; T2's checks on rule 5 (`numbered_item(text, 5)` containing "in progress", "research" + "commit", "done", "cleanup", "status field") should pass, alongside T1 still passing from Step 1.

- Edge case: "Done" and "cleanup" must co-occur in language that ties them together (not just both appearing anywhere in rule 5) — write the Done sentence so it names Cleanup completing as its trigger, not as an incidental mention.
- Edge case: keep rule 5's existing default ("tick the task's checklist") intact — the two new sentences are additions, not replacements.

**Implementation Outline**

Edit one line in `using.md`'s Practice Read/Write Rules, rule 5, appending the two trigger sentences after the existing "the default is to tick the task's checklist" clause — do not touch rules 1-4 or 6-8.

## Step 3: Capability Routing — GitHub id-type/`-F` caveat

**Enables:** feature-test check T3 (the `## Capability Routing` section must contrast "database id" against "issue number", call out `gh api -F`'s string coercion, and prescribe `gh api --input -` with a JSON heredoc).

Add a GitHub-specific paragraph or bullet to the existing `## Capability Routing` section: the sub-issue endpoint (`POST /repos/:owner/:repo/issues/:parent/sub_issues`) takes the child's **database id** (an integer) — not its issue number — as `sub_issue_id`; `gh api -F` sends field values as strings, which is unreliable for this integer field, so route the call through `gh api --input -` with a JSON heredoc body instead of `-F`.

**Tests**

Run the full feature test; all three checks (T1, T2, T3) should now pass, and `main()` should print `PASS: status-transition and sub-issue-linking rules hold` and exit 0.

- Edge case: the new paragraph must land inside the `## Capability Routing` section as matched by the test's `section()` helper (between the `## Capability Routing` heading and the next `##` heading, i.e. before `## Degradation (no tracker configured)`) — do not append it after the next `##` boundary.
- Edge case: use the literal substrings the test checks case-insensitively: "database id" (or "database identifier"), "issue number", "-f" (as in `gh api -F`), and "--input". Write the prose naturally but make sure each literal appears.

**Implementation Outline**

Append one paragraph to `using.md`'s existing `## Capability Routing` section, after the existing "Not-Available... routing signal" paragraph and before the section boundary — do not create a new `##` heading; this is a caveat within the existing section per design.md's Alternatives (rejected: putting it in rule 4 instead).
