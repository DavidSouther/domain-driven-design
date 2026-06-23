---
name: using-program-management
description: Use when reading the next task or writing work back to the team's program-management system during a development session, by selecting the next task, creating and labeling tasks, linking parent/child, recording deferred work, and replicating long-lived docs, following the contract recorded by configuring-program-management and degrading to TASKS.md when no tracker is configured. Applies every development session, never to set up the wiring.
---

# Using Program Management

## Overview

The per-session partner for
[`developer:configuring-program-management`](../configuring-program-management/SKILL.md).
It reads the contract that skill recorded in `DEVELOPMENT.md`, selects the next
task from the configured tracker, creates and labels tasks, links parent/child,
records phase progress, and writes deferred work back. On Project acceptance it
replicates long-lived notes to the document system as docs.

Three artifact tiers are read in order: **notes** (always-local working files in
`.ailly/developer/`), **tasks** (the configured tracker; fallback `TASKS.md`),
and **docs** (the configured document system; Project-shape only). The tracker
and doc tiers layer on top of the notes floor only when configured, and degrade
independently to `TASKS.md` and local notes when not.

Setup, MCP install, OAuth/SSO handshakes, and recording the term mapping belong
to `developer:configuring-program-management`. This skill consumes the contract
that skill publishes; it never re-teaches the wiring.

## When to Use / When NOT to Use

**Use when:** during a development session you need to read the next task,
create or label a task, link it to its parent, record phase progress, write
deferred work back, or publish an accepted Project's docs.

**Do NOT use** for setup. Detecting trackers, installing an MCP, completing
OAuth, or recording the term mapping is one-time wiring →
[`developer:configuring-program-management`](../configuring-program-management/SKILL.md).

## Practice Read/Write Rules

Read the three tiers in order. The notes tier is always active; the task and doc
tiers layer on top only when configured, and degrade independently.

1. **Notes (always).** In-flight working artifacts live in
   `.ailly/developer/<date>-<topic>/`. This tier needs no contract, is never
   blocked, and is unaffected by whether a tracker or doc system exists.
   Everything below layers on top of it.
2. **Read the contract** from the `## Program Management` section of
   `DEVELOPMENT.md`. If that section is absent, or its **Active tracker** is
   unset or `none`, use `TASKS.md` for the task tier (today's behavior) and stop
   layering. Notes still apply.
3. **Select next task** via the tracker, then map it to the topic using the
   recorded nouns.
4. **Create/label tasks** for features and bugs using the recorded labels, and
   link to the parent Epic via the link capability (field-write fallback where
   no dedicated tool exists).
5. **Record phase progress** per the recorded strategy as phases advance (the
   default is to tick the task's checklist).
6. **Write deferred work** at cleanup as labeled tasks/comments under the right
   parent (Note → Task). This is `TASKS.md` today when no tracker is configured.
7. **Publish on Project acceptance** (Note → Doc): when the topic is a Project
   and the doc-system target is set, replicate the accepted notes to the
   document system and mark them `completed:`. Feature/bug notes are not
   published; they stay local and are removed at cleanup.
8. **Never re-teach setup.** A "before you start, confirm the tracker is
   configured…" preface is a contract bug. The wiring skill owns setup; widen
   its contract rather than prefacing this skill.

## Capability Routing

Capabilities are named in the contract published by
`developer:configuring-program-management`, keyed by the active tracker's MCP.
Every row is conditional on that MCP being authenticated.

| Capability | Tier | Inputs | Returns | Conditional |
|---|---|---|---|---|
| Select next task | tasks | optional team/label/status filter | highest-priority open task with id, title, labels | available when configured |
| Create task | tasks | title, body, labels, optional parent | new task id | available when configured |
| Link parent/child | tasks | child id, parent id | confirmation | GitHub `sub_issue_write`; else parent field write |
| Transition status | tasks | task id, target state | confirmation | Jira `transitionJiraIssue`; else status field write |
| Record phase progress | tasks | task id, phase, state | confirmation | per phase-representation strategy |
| Write deferred work | tasks | title/body, labels, optional parent | new task/comment id | available when configured |
| Publish long-lived doc | docs | doc path, doc-system target | published URL | doc-system target not `none`, Project shape |

MCP capabilities are asymmetric. First-class parent/child linking exists only in
GitHub (`sub_issue_write`); dedicated status transitions exist only in Jira
(`transitionJiraIssue`). Where no dedicated tool exists, express both as field
writes on the task.

A capability whose MCP did not authenticate returns the typed result reused
verbatim from the `research` family:

```
{ result: "not-available", capability: "<name>", reason: "<why>" }
```

Treat Not-Available as a **routing signal, not an error**: route the task tier
to the `TASKS.md` fallback and keep notes local. Do not retry the capability.

## Degradation (no tracker configured)

When `DEVELOPMENT.md` has no `## Program Management` section, or its **Active
tracker** is unset or `none`:

- **Task tier** falls back to `TASKS.md` — today's behavior, unchanged: next
  task selected from `TASKS.md`, deferred work written back to it.
- **Doc tier** has no publish target; accepted Project notes stay local.
- **Notes tier is unaffected.** Working files in `.ailly/developer/` are written
  exactly as when a tracker is configured; the floor never degrades.

## Composes With

- **[`developer:configuring-program-management`](../configuring-program-management/SKILL.md)** —
  the wiring partner. Publishes the contract this skill consumes; owns tracker
  detection, MCP install, OAuth/SSO, and the term mapping.
- **`developer:ailly`** — the coordinator defers next-task selection and
  deferred-work writing here when a tracker is configured.
- **`developer:cleanup`** — defers deferred-work write-back and Project doc
  publication here at the end of a topic.
- **[`research:configuring-internal`](../../../research/skills/configuring-internal/SKILL.md)** —
  owns the MCP transport and auth for the same tracker MCPs.
