---
name: using-program-management
description: Use when reading the next task or writing work back to the team's program-management system during a development session, by selecting the next task, creating and labeling tasks, linking parent/child, recording deferred work, and replicating long-lived docs, following the contract recorded by configuring-program-management and degrading to TASKS.md when no tracker is configured. Applies every development session, never to set up the wiring.
---

# Using Program Management

## Overview

The per-session partner for [`developer:configuring-program-management`](../configuring-program-management/SKILL.md).  It reads the contract that skill recorded in `DEVELOPMENT.md`, selects the next task from the configured tracker, creates and labels tasks, links parent/child, records phase progress, and writes deferred work back. On Project acceptance it replicates long-lived notes to the document system as docs.

Three artifact types are defined: **notes** (always-local working files in `.ailly/developer/`), **tasks** (the configured tracker; fallback `TASKS.md`), and **docs** (the configured document system; Project-shape only). The tracker and docs layer on top of the notes floor only when configured, and degrade independently to `TASKS.md` and local notes when not.

Setup, MCP install, OAuth/SSO handshakes, and recording the term mapping belong to `developer:configuring-program-management`. This skill consumes the contract that skill publishes; it never re-teaches the wiring.

## When to Use / When NOT to Use

**Use when:** during a development session you need to read the next task, create or label a task, link it to its parent, record phase progress, write deferred work back, or publish an accepted Project's docs.

**Do NOT use** for setup. Detecting trackers, installing an MCP, completing OAuth, or recording the term mapping is one-time wiring → [`developer:configuring-program-management`](../configuring-program-management/SKILL.md).

## Practice Read/Write Rules

Read the three types. The notes tier is always active; the task and doc tiers layer on top only when configured, and degrade independently.

1. **Notes (always).** In-flight working artifacts live in `.ailly/developer/<date>-<topic>/`. This artifacat needs no contract, is never blocked, and is unaffected by whether a tracker or doc system exists.  Everything below layers on top of it.
2. **Read the contract** from the `## Program Management` section of `DEVELOPMENT.md`. If that section is absent, or its **Active tracker** is unset or `none`, use `TASKS.md` for the task tier (today's behavior) and stop layering. Notes still apply.
3. **Select next task** via the tracker, then map it to the topic using the recorded nouns.
4. **Create/label tasks** for features and bugs using the recorded labels, and link to the parent Epic via the link capability (field-write fallback where no dedicated tool exists).
5. **Record phase progress** per the recorded strategy as phases advance (the default is to tick the task's checklist).
6. **Write deferred work** at cleanup as labeled tasks/comments under the right parent (Note → Task). This is `TASKS.md` today when no tracker is configured.
7. **Publish on Project acceptance** (Note → Doc): when the topic is a Project and the doc-system target is set, replicate the accepted notes to the document system and mark them `completed:`. Feature/bug notes are not published; they stay local and are removed at cleanup.
8. **Never re-teach setup.** A "before you start, confirm the tracker is configured…" preface is a contract bug. The wiring skill owns setup; widen its contract rather than prefacing this skill.

## Capability Routing

The capabilities — their inputs, returns, and conditions — are the capability table published by [`developer:configuring-program-management`](../configuring-program-management/SKILL.md).  Read that table for the schema; this section covers only how to route against it. Every capability is keyed by the active tracker's MCP and is conditional on that MCP being authenticated.

MCP capabilities are asymmetric. First-class parent/child linking exists only in GitHub (`sub_issue_write`); dedicated status transitions exist only in Jira (`transitionJiraIssue`). Where no dedicated tool exists, express both as field writes on the task.

A capability whose MCP did not authenticate returns the typed result reused verbatim from the `research` family:

```
{ result: "not-available", capability: "<name>", reason: "<why>" }
```

Treat Not-Available as a **routing signal, not an error**: route the task tier to the `TASKS.md` fallback and keep notes local. Do not retry the capability.

## Degradation (no tracker configured)

When `DEVELOPMENT.md` has no `## Program Management` section, or its **Active tracker** is unset or `none`:

- **Tasks** falls back to `TASKS.md` — today's behavior, unchanged: next task selected from `TASKS.md`, deferred work written back to it.
- **Docs** has no publish target; accepted Project notes stay local.
- **Notes** is unaffected. Working files in `.ailly/developer/` are written exactly as when a tracker is configured; the floor never degrades.

## Composes With

- **[`developer:configuring-program-management`](../configuring-program-management/SKILL.md)** — the wiring partner. Publishes the contract this skill consumes; owns tracker detection, MCP install, OAuth/SSO, and the term mapping.
- **`developer:ailly`** — the coordinator defers next-task selection and deferred-work writing here when a tracker is configured.
- **The cleanup phase** (`developer:ailly cleanup`, `references/phases/cleanup.md`) — defers deferred-work write-back and Project doc publication here at the end of a topic.
- **[the internal sources setup reference](../../../research/skills/using-research/references/configuring/internal.md)** (`research:using-research`, `references/configuring/internal.md`) — owns the MCP transport and auth for the same tracker MCPs.
