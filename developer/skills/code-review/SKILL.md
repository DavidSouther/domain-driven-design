---
name: code-review
description: Use when finishing a task, before claiming work is complete, or after producing a diff — to verify changes are correct, minimal, and conform to the stated requirements.
---

# Code Review

## Overview

An LLM agent cannot accumulate shared understanding the way a human team does. Every session starts cold. What code review means for an agent is therefore different: it is not knowledge transfer, it is **spec conformance verification**. The goal is to catch what the author-frame missed by deliberately adopting a critic-frame before declaring done.

## When to Use

- After completing any implementation task, before reporting it complete.
- Before committing or opening a pull request.
- When a diff feels large — that feeling is the signal to split, not ship.

**When NOT to use:** Exploratory spikes or throwaway scripts where correctness is not the goal.

## The Size Rule

**Keep every change as small as the task permits.** This is not style preference — it is a reliability property. Human reviewers catch 70–90% of defects in diffs under 400 lines; detection degrades sharply beyond that threshold. The same upper bound applies to agent self-review: large diffs exceed the regime where verification is trustworthy.

If a diff has grown large:
1. Identify the smallest coherent subset that is independently correct.
2. Extract it as its own change and review it in isolation.
3. Repeat until all changes are in independently reviewable units.

Never change behavior and structure simultaneously. Refactoring and feature work are separate commits.

## Self-Review Process

Adopt a **critic frame** — read the diff as if you are a skeptic who did not write it and is trying to find a reason to reject it.

Check against the spec, not against your intentions:

| Question | What to look for |
|----------|-----------------|
| Does the diff implement what was asked? | Compare to the stated requirements, not to what you remember intending. |
| Does it change only what was asked? | Flag any unrelated modifications — scope creep is a defect. |
| Does it change behavior and structure together? | If yes, split the commit. |
| Are there missing cases? | What inputs or states does this code not handle that the spec implies it should? |
| Does anything silently break existing behavior? | Check call sites and downstream consumers of anything modified. |

## Refactoring Specifically

When the task is refactoring:

- No behavior changes. If the tests had to change to match new behavior, the commit is not a refactor.
- Incremental: one structural change per commit, verified by tests that pass before and after.
- The right size: a refactor diff large enough to obscure intent should be split further.

## What Replaces Shared Understanding

Human teams use code review to build a collective mental model. Agents do not accumulate this. The equivalent artifact is the **written spec** — bounded context documents, decision records, requirement statements. When in doubt about whether a change is correct, the question is: "does this conform to the spec?" not "does this feel right to me?" If no spec exists, produce a short one before reviewing the code.

## Common Mistakes

- **Reviewing from author-frame.** You know what you meant to do, so you read past gaps. Explicitly reframe: what would a skeptic find wrong here?
- **Approving large diffs.** Size is a proxy for verification quality. A large diff that "looks fine" has not been reviewed — it has been scanned.
- **Conflating refactor and feature.** Any diff that touches both structure and behavior cannot be reviewed as one unit. Split it.
- **Checking style instead of correctness.** Style is mechanical and can be automated. Focus review attention on logic, coverage of the spec, and unintended side effects.
