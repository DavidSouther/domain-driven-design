# Using program management

> Coordinator reference loaded by `developer:ailly` for **per-session** task I/O
> when you configure a tracker. The bootstrap-vs-per-use partner is the
> configuring reference (`references/abilities/program-management/configuring.md`), which
> sets up the wiring once. There is no standalone `developer:using-program-management`
> skill.

## Overview

The per-session partner of the [configuring reference](configuring.md). It reads the contract that reference recorded in `DEVELOPMENT.md` and selects the next task from the configured tracker. It creates and labels tasks, links parent/child issues, records phase progress, and writes deferred work back. On Project acceptance it replicates long-lived notes to the document system as docs.

We define three artifact types. **Notes** are always-local working files in `.ailly/developer/`. **Tasks** use the configured tracker with fallback to `TASKS.md`. **Docs** use the configured document system for Project-shape only. The tracker and docs layer on top of the notes floor only when configured. Each degrades independently to `TASKS.md` and local notes when the tier is not configured.

Setup, MCP install, OAuth/SSO handshakes, and recording the term mapping belong to the [configuring reference](configuring.md). This reference consumes the contract that reference publishes; it never re-teaches the wiring.

## When to use / when NOT to use

**Use when:** you need to read the next task, create or label tasks, or link them to their parents during a development session. Also use when you need to record phase progress, write deferred work back, or publish an accepted Project's docs.

**Do NOT use** for setup. Detecting trackers, installing an MCP, completing OAuth, or recording the term mapping is one-time wiring → the [configuring reference](configuring.md).

## Practice read/write rules

Read the three types. The notes tier is always active; the task and doc tiers layer on top only when configured, and degrade independently.

1. **Notes (always).** In-flight working artifacts live in `.ailly/developer/<date>-<topic>/`. These artifacts need no contract and face no barriers to use. A tracker or doc system does not affect them. Everything below layers on top of these notes.
2. **Read the contract** from the `## Program Management` section of `DEVELOPMENT.md`. If that section is absent, or its **Active tracker** is unset or `none`, use `TASKS.md` for the task tier (today's behavior) and stop layering. Notes still apply.
3. **Select next task** via the tracker, then fetch the full thread (body plus every comment) and route it through `thread-digest` before mapping the task to a topic using the recorded nouns. If the tracker's fetch capability returns Not-Available for full-thread content, warn and proceed with body-only context rather than blocking task selection.
4. **Create/label tasks** for features and bugs using the recorded labels, and link to the parent Epic via the link capability. Use field-write as fallback where no dedicated tool exists. When you discover a sub-issue mid-build, link it to its parent immediately when you create the child issue using the same link capability. Do not defer this to cleanup.
5. **Record phase progress** per the recorded strategy as phases advance (the default is to tick the task's checklist). Where the configured tracker exposes a status field, also move the board card between columns at these phase boundaries: to **In Progress** when the Research phase begins (first commit to the session branch), and to **Done** when the Cleanup phase completes and the issue closes. Where no status field exists, route through the existing Not-Available/field-write fallback instead of skipping the transition.
6. **Write deferred work** at cleanup as labeled tasks/comments under the right parent (Note → Task). This defaults to `TASKS.md` today when you have not configured a tracker.
7. **Publish on Project acceptance** (Note → Doc): when the topic is a Project and the doc-system target is set, replicate the accepted notes to the document system and mark them `completed:`. Feature/bug notes are not published; they stay local, and you remove them at cleanup.
8. **Never re-teach setup.** A "before you start, confirm you configured the tracker…" preface is a contract bug. The wiring skill owns setup; widen its contract rather than prefacing this skill.

## Capability routing

The [configuring reference](configuring.md) publishes a capability table that lists each capability with its inputs, returns, and conditions. Read that table for the schema; this section covers routing only. Each capability requires the active tracker's MCP as its key and works only when that MCP is authenticated.

MCP capabilities are asymmetric. First-class parent/child linking (`sub_issue_write`) exists only in GitHub. Dedicated status transitions (`transitionJiraIssue`) exist only in Jira. Where no dedicated tool exists, express both as field writes on the task.

A capability whose MCP did not authenticate returns the typed result reused verbatim from the `research` family:

```
{ result: "not-available", capability: "<name>", reason: "<why>" }
```

Treat Not-Available as a **routing signal, not an error**: route the task tier to the `TASKS.md` fallback and keep notes local. Do not retry the capability.

## Degradation (no tracker configured)

When `DEVELOPMENT.md` has no `## Program Management` section, or its **Active tracker** is unset or `none`:

- **Tasks** falls back to `TASKS.md` — today's behavior, unchanged: next task selected from `TASKS.md`, deferred work written back to it.
- **Docs** has no publish target; accepted Project notes stay local.
- **Notes** remain unaffected. You write working files in `.ailly/developer/` exactly the same way whether or not you configure a tracker. The floor never degrades.

## Composes with

- **[the configuring reference](configuring.md)** — the wiring partner. Publishes the contract this reference consumes; owns tracker detection, MCP install, OAuth/SSO, and the term mapping.
- **`developer:ailly`** — the coordinator defers next-task selection and deferred-work writing here when you configure a tracker.
- **The cleanup phase** (`references/phases/cleanup.md`) defers deferred-work write-back and Project doc publication at the end of a topic.
- **[the internal sources setup reference](../../../../../research/skills/using-research/references/configuring/internal.md)** (see `research:using-research` and `references/configuring/internal.md`) owns the MCP transport and auth for the same tracker MCPs.
