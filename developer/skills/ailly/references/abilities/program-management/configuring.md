# Configuring Program Management

> Coordinator reference loaded by `developer:ailly` for the **one-time** tracker
> setup. The bootstrap-vs-per-use partner is the using reference
> (`references/abilities/program-management/using.md`), which runs every session. There is
> no standalone `developer:configuring-program-management` skill.

## Overview

This reference creates the development details that the [using reference](using.md) checks when performing project management tasks. Development produces three kinds of artifact — **tasks** (short-lived work items that belong in the team's issue tracker), **docs** (durable research/design/plan artifacts that belong in the team's document system on acceptance), and **notes** (in-flight working files that stay local in `.ailly/developer/`). This reference configures the two *optional* homes: the active tracker for tasks and the doc-system target for docs. The notes tier always uses local files (`./ailly` folder) and only needs configuration to override that default location.

These details provide a natural language bridge between the development teams' tools and process and Ailly's internal workflows. Ailly does not build or vendor a tracker; she uses the MCP servers already reachable through the internal sources setup reference (`research:using-research`, `references/configuring/internal.md`). This skill probes each tracker and document-system MCP, has the user pick one active tracker, records the details in `DEVELOPMENT.md`, and smoke-tests that the tracker answers.

Re-running on a configured project confirms the contract or detects that surfaces drift — most often an expired token or a renamed label. It never destroys state: it only **records** or **updates** the details, it never recreates them from scratch.

## When to Use / When NOT to Use

**Use when:**

- Standing up a fresh checkout for the first time and the [using reference](using.md) has no tracker to call.
- Adding or switching the active tracker, wiring a document system, completing an OAuth/SSO handshake, or recording the team's term mapping.
- Re-verifying after a re-verification trigger (see below) fires.

**Do NOT use** inside a development session. The per-session partner is the [using reference](using.md); tracker detection, MCP install, auth handshakes, and recording the term mapping happen here, once per project — not at a per-session call site.

## Details (published to `DEVELOPMENT.md`)

The details lives in `DEVELOPMENT.md` **only** — a single home that is both human-facing and agent-readable. After the configuring reference has run, the using reference may assume `DEVELOPMENT.md` contains a `## Program Management` section naming:

- **Active tracker (tasks home):** exactly one value that uniquely identifies a project management MCP. Known trackers are `{ linear, jira, github, notion, none }`, resolved at configure time even when several MCPs authenticate. When unset or `none`, the task tier degrades to `TASKS.md`.
- **Term mapping:** the team's outward nouns for each Ailly tier.

  | Ailly concept | Default tracker concept | Team's noun (recorded) |
  |---|---|---|
  | Project (multi-feature topic) | Epic / parent issue | _e.g._ "Initiative" |
  | Feature | Task labeled `feature` | _e.g._ "Story" |
  | Bug | Task labeled `bug` | _e.g._ "Defect" |
  | Deferred decision | Task labeled `deferred` / follow-up | _recorded_ |

- **Doc-system target (docs home):** where long-lived research/design docs are replicated on acceptance (a Notion workspace, a Google Drive folder, other installed MCPs), or `none`. Promotion scope is projects-only.
- **Phase-representation strategy:** how Ailly's five phases ride a task that has no native primitive. The default is a **checklist** on the task. A per-tracker override applies where no checklist primitive exists (Jira: a custom field or comment thread; GitHub: a task-list in the issue body).

The capability details the practice skill consumes, keyed by the active tracker's MCP, with every row conditional on that MCP being authenticated:

| Capability | Tier | Inputs | Returns | Notes |
|---|---|---|---|---|
| Select next task | tasks | optional team/label/status filter | highest-priority open task with id, title, labels | — |
| Create task | tasks | title, body, labels, optional parent | new task id | — |
| Link parent/child | tasks | child id, parent id | confirmation | GitHub `sub_issue_write`; else parent field write |
| Transition status | tasks | task id, target state | confirmation | Jira `transitionJiraIssue`; else status field write |
| Record phase progress | tasks | task id, phase, state | confirmation | per phase-representation strategy |
| Write deferred work | tasks | title/body, labels, optional parent | new task/comment id | — |
| Publish long-lived doc | docs | doc path, doc-system target | published URL | only when doc-system target is not `none`, Project shape |

**GitHub `Link parent/child` caveat:** GitHub's sub-issue endpoint (`POST /repos/:owner/:repo/issues/:parent/sub_issues`) takes the child's **database id** (an integer) as `sub_issue_id` — not its issue number. `gh api -F` sends every field value as a string, which is unreliable for this integer field; route the call through `gh api --input -` with a JSON heredoc body instead of `-F`.

Every tracker/doc capability is **conditional**: available only when its MCP is authenticated. A project with no tracker configured is legal and returns Not-Available for every row. The **notes** tier has no row — writing working files to `.ailly/developer/` is never conditional. Conditional capabilities return the typed Not-Available result reused verbatim from the `research` family:

```
{ result: "not-available", capability: "<name>", reason: "<why>" }
```

The practice skill treats Not-Available as a routing signal, not an error.

## Configure Checklist

Walk the checklist top-to-bottom. Each item probes the source's MCP through the [internal sources setup reference](../../../../../research/skills/using-research/references/configuring/internal.md) contract, then records its line and smoke-tests it. **Do not re-teach MCP install or OAuth** — cite that internal setup reference for transport and auth. Record in (or update) `DEVELOPMENT.md`; never recreate it.

**Default**

- [ ] **Tracker detection and selection (tasks home).** Probe each tracker MCP for this project — **Linear**, **Jira**, **GitHub**, **Notion**, or if advertised research others. If more than one authenticates, ask the user to pick **one** active tracker and record it.  Smoke-test: select-next-task returns the contract shape.
- [ ] **Term mapping.** Ask the team's outward nouns for Project/Epic, feature, bug, and the deferred-work label, then record the mapping table. Where the team has no distinct noun, keep the tracker default.

**Priority**

- [ ] **Doc-system target (docs home).** Probe the configured doc-system MCP (**Notion**, **Google Drive**, or other as discovered). Record the publish target, or `none`.  Smoke-test: a no-op resolve of the target workspace/folder.
- [ ] **Phase representation.** Pick the default (checklist) or the per-tracker override (Jira: custom field/comment; GitHub: task-list in the body), then record it.

**Opt-in**

- [ ] **Other trackers / doc systems** the user supplies — same shape: probe, record a contract row, smoke-test, or mark Not-Available.

The notes tier may be configured with a specific top level folder, but otherwise it is the local floor and is assumed present.

## Re-Verification Triggers

Re-run the wiring when any of the following happens. Re-running confirms the contract still resolves; on a configured project it does not destroy state.

- An OAuth token or SSO session expires (the most frequent trigger — commonly a 401 on the next read).
- An API key or PAT rotates (GitHub `GH_TOKEN`, any tracker token).
- The team switches trackers or adds a document system that should sit in the contract.
- A label or noun is renamed, so the recorded term mapping no longer resolves.
- The [using reference](using.md) reports drift: a tracker returned a shape the practice reference did not expect, or a smoke-test that previously passed now fails.

## Composes With

- **[the using reference](using.md)** — the per-session partner. Wiring publishes the contract; practice consumes it.
- **[the internal sources setup reference](../../../../../research/skills/using-research/references/configuring/internal.md)** (`research:using-research`, `references/configuring/internal.md`) — owns the MCP transport and OAuth/SSO handshakes for the same tracker MCPs.  Cite it for install and auth; do not re-teach them here.
- **`developer:ailly`** — the coordinator reads this contract from `DEVELOPMENT.md` to decide whether to defer task I/O to the practice reference.
