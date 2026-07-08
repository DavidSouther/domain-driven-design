---
name: clean-comments-review
description: Use when reviewing comments in coding artifacts. Produces a critique document, not code edits.
---

# Clean comments review

## Overview

Review comments to see if they explain intent and key rules to the right reader.
Create a critique document, not code edits.

Comments explain why this exists, what callers can trust, what a future reader must protect, or why a choice is right.
A comment tells readers what code, names, and history alone cannot explain.

## Comments Explain Intent and Invariants

The review’s core question is: what can this comment tell a future reader that the code and tools cannot?

Good comments capture intent, constraints, tradeoffs, and domain meaning.
They stay useful after code moves, names change, and teams forget the original plan.

## Public docblocks serve external readers

A public DocBlock reaches readers by using the symbol.
It explains why it exists, what callers can rely on, and what constraints matter.

A public DocBlock can name intent, contracts, edge cases, and examples.
Trust the reader’s tools for types and signatures.

## Internal comments preserve maintainer judgment

An internal comment speaks to a future maintainer who can read code and check history.
It saves judgment they cannot recover alone.
It explains why a path is right, what invariant the next edit must protect, or what constraint shaped the code.

Strong comments sit near the decision they explain and stay true when callers change.

## Comments trust the tooling

Trust the editor and repository to show readers what they need.
Types, names, visibility, definitions, references, blame, and history are already at hand.

Consider these comment types:

History: “split out of restir.wgsl” Invariant: “this layout must remain byte-compatible with the ReSTIR shader buffer” Reference: “used by testing_events.rs” Contract: “the test harness and production path must share this gather rule”

## Output format

Produce a critique document.
For each comment or comment group:

1. Identify the audience: public DocBlock or internal note.
2. Name the intent or invariant the comment should carry.
3. Check if the current comment serves that goal.
4. Suggest an action: keep, simplify, rewrite, or remove.

The review document names the problem and suggests how the comment should change.
It does not edit code.

## Review signals

- **Durable intent:** Keep comments that explain why code exists or what readers must protect.
- **Audience fit:** Write for callers (public) or maintainers (internal).
- **Tooling duplication:** Remove comments that repeat signatures, names, or control flow.
- **Usage-site drift:** Replace call lists with the stable rule they depend on.
- **History breadcrumbs:** Remove “split out of” or “originally from” notes.
- **Over-complete prose:** Use the smallest comment that saves future readers from guessing.