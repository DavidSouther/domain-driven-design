---
name: clean-comments-review
description: Use when reviewing comments in coding artifacts. Produces a critique document, not code edits.
---

# Clean Comments Review

## Overview

Review comments for whether they explain durable intent and invariants to the right reader. The artifact is a critique document, not a code rewrite.

Comments explain why this exists, what contract callers may rely on, what invariant must be preserved, or why an unusual choice is correct.
A comment explains what the code, signatures, type names, editor navigation, and git history cannot say clearly enough.

## Comments Explain Intent and Invariants

The review’s core question is: what can this comment tell a future reader that the code and tools cannot?

Good comments name durable things: intent, invariants, contracts, constraints, tradeoffs, surprising decisions, compatibility requirements, and domain meaning.
They remain useful after code moves, files are renamed, callers change, helper functions are rearranged, and the original project plan is forgotten.

## Public DocBlocks Serve External Readers

A public DocBlock addresses someone using the symbol without reading its implementation. It should explain why the symbol exists, what behavior callers may rely on, and any constraints that shape correct use.

A public DocBlock can include module-level intent, stable contracts, important edge cases, and worked examples.
It should trust the reader’s tools for signatures, parameter names, return types, definitions, and reference searches.

## Internal Comments Preserve Maintainer Judgment

An internal comment addresses a future maintainer who can read the code, jump to definitions, find usages, and inspect history.
Its job is to preserve judgment that would otherwise be lost: why this path is surprising but intentional, what invariant the next edit must protect, or what external constraint shaped the implementation.

The strongest inline comments sit near the decision they explain and survive a caller reshuffle.

## Comments Trust the Tooling

Treat the editor and repository as part of the reader’s context.
Signatures, types, field names, visibility, cfg attributes, definitions, references, blame, and file history are already available.

A comment like “split out of restir.wgsl” is history.
A comment like “this layout must remain byte-compatible with the ReSTIR shader buffer” is an invariant.
A comment like “used by testing_events.rs” is a reference search.
A comment like “the test harness and production path must share this gather rule” may be a contract if that shared rule is the important thing to preserve.

## Output Format

Produce a critique document. For each comment or comment group:

1. Identify the audience: public DocBlock or internal maintainer note.
2. State the durable intent or invariant the comment should carry.
3. Assess whether the current comment serves that purpose.
4. Recommend an action: keep, reduce to intent, rewrite around the invariant, or remove.

The review artifact names the problem and the desired shape of the comment; it does not edit the code directly.

## Review Signals

- **Durable intent:** Keep comments that explain why the code exists, what must remain true, or what contract readers may rely on.
- **Audience fit:** Shape public DocBlocks around caller contracts and internal comments around maintainer judgment.
- **Tooling duplication:** Reduce comments that repeat signatures, field names, type names, obvious control flow, or LSP-findable relationships.
- **Usage-site drift:** Replace “called by,” “used from,” and fixture-provenance prose with the stable rule those usages depend on, if one exists.
- **History breadcrumbs:** Replace “split out of,” “originally part of,” feature IDs, design-doc links, and TDD notes with the current invariant, or remove them.
- **Over-complete prose:** Prefer the smallest comment that preserves the intent a future reader cannot recover from code alone.