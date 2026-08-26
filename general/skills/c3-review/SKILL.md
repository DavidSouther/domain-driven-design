---
name: c3-review
description: Use when an isolated subagent needs to collect Correctness, Conciseness, and Clarity feedback for a final artifact handoff.
---

# C3 Review

Collect evidence-grounded feedback for a final artifact. C3 means **Correctness**, **Conciseness**, and **Clarity**. It evaluates only: return findings with severity and evidence; do not edit, choose specialists, or converge other reviewers' findings.

## C3 Rubric

- **Correctness:** Treat each load-bearing statement as a claim to verify. Trace file paths, identifiers, environment variables, API signatures, URLs, version numbers, and quoted values to code, command output, or a cited document. Flag unsupported claims. A confident tone is not evidence.
- **Conciseness:** Tighten padding without sacrificing necessary depth. Cut clauses that only restate their subject, empty intensifiers, repeated summaries, and rhythm-only phrasing. Do not shorten material that changes meaning.
- **Clarity:** Flag vague hedges and filler, not appropriate domain jargon. Favor complete, direct sentences. When unusual punctuation fuses independent ideas, buries the subject behind qualifiers, or disguises a list of full clauses, flag the sentence and its paragraph for restructuring rather than swapping punctuation.

## Findings

For each finding, state a stable `findingId`, severity, the claim, and evidence locations in the artifact or its sources. Report only findings that the supplied artifact and evidence support.

## Post-Convergence Cold Challenge Protocol

The isolated C3 collection lane does not run this protocol. After initial convergence, `general:review` or its caller invokes it only if convergence selected a High-severity finding. Select exactly one deterministically: severity first, then stable-id order. If no finding is High severity, do not challenge.

The challenger reads only the finding's `findingId`, claim, and evidence plus the artifact. It returns one counterclaim naming the `findingId`, evidence locations, and a falsification condition that could refute the counterclaim. It does not edit, score, or debate in rounds.

A fresh final verifier reads the original finding, counterclaim, and artifact. For a consequential challenge, evaluate both presentation orders. Report exactly one status: **accepted** when the challenge refutes the finding; **rejected** when it stands; **unresolved** when evidence cannot decide or the orders disagree; or **failed** when the challenger or verifier could not run. Accepted findings are removed from the actionable list. Rejected findings are retained. Unresolved findings escalate to the developer if substantial and otherwise are removed; failed findings are also removed.

## When Not to Use

Do not use C3 for an evolving Ailly artifact's request alignment; use continuous Intent review. Do not use it as a replacement for `general:review`, which composes C3 with applicable specialists and converges the collected feedback.
