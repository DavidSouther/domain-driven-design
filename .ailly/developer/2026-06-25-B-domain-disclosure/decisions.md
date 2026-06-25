# Quick-loop: Progressive-Disclosure Design Questions Applied to the Domain Plugin

*2026-06-25. Quick-loop (gates auto-cleared). Branch `progressive_disclosure`.*

Applies the same design questions from `2026-06-25-A-progressive-disclosure` to the
`domain` plugin and records the decisions. The project research listed domain as out of
scope ("already conditionally loaded; no pressure"); this confirms that under the design
questions rather than asserting it, and applies the smaller moves the lens does surface.

## The design questions, answered for domain

- **Concurrent-choice count / token share.** 7 skills (using-domain, domain-model,
  ubiquitous-language, glossary, contracts-and-invariants, arrow-of-maturity,
  domain-review), ~330 always-on tokens. Far under the 30-50 routing ceiling; token
  share negligible. No token or routing pressure. (`domain-review-workspace` is scratch
  scaffolding, not a skill.)
- **Already progressive?** Yes. `using-domain` is conditionally loaded: "Not loaded
  during implementation, as the domain knowledge has already been summarized in the
  prompt." The whole plugin is gated off during the dominant phase already.
- **Mechanism-mismatch taxonomy.** No style overlay (unlike characters). The five
  activity leaves (domain-model, ubiquitous-language, glossary, contracts-and-invariants,
  arrow-of-maturity) are triggered capabilities with reference depth: native skill fit.
  using-domain is routing/coordination: native bootstrap fit. domain-review is the one
  triggered-isolated-artifact case (a critique document) and is ALREADY wired as a
  composable specialist in `general:review` (PR #13); no further move.
- **Patterns analogy?** No. Patterns collapsed because 19 always-on descriptions
  expressed ONE design-time decision used together in one beat, with a built-in red case.
  Domain's leaves are distinct activities invoked at DIFFERENT beats (model vs name vs
  contracts vs maturity vs review). This is the research-shaped case ("you only ever want
  one at a time, never all"), where collapsing loses native direct routing and gains
  nothing.

## Decisions

**1. Do NOT collapse the domain leaves into one router.** Domain is the research-shaped
case, not the patterns-shaped case: distinct one-at-a-time activities, 7 choices / ~330
tokens under the ceiling, already conditionally loaded off during implementation. A
collapse would degrade a working routing surface to chase a non-existent number. Confirms
the project research's out-of-scope finding under the design questions.

**2. No deferral move available.** Domain has no `configuring-*`/bootstrap-pair leaves to
defer (the research analog). using-domain is the only bootstrap and is already
conditionally loaded.

**3. domain-review stays a skill and a composable review specialist.** Already the
correct mechanism (PR #13). No change.

**4. Apply the two small correctness moves the lens DOES surface** (both open in the
`domain/e2e` TASKS notes; the domain analog of patterns' discriminator-sharpening):
  - **(a) Reconcile the `ddd:` prefix to `domain:` in the using-domain routing table.**
    The Level-1 routing surface named `ddd:<skill>` but the manifest namespace is
    `domain:<skill>`, so the named identifiers did not resolve. Capability-discoverability
    depends on correct Level-1 identifiers. The `domain/e2e` discovery evals already
    accept both prefixes, so this is safe. Done here.
  - **(b) Strengthen the glossary-gate routing row.** The glossary's own description says
    "ALL other DDD skills must invoke this skill before introducing terminology," but the
    routing table only sent "ambiguous/synonymous" terms to glossary, so a term-INTRODUCING
    modeling prompt routed to domain-model first (the `domain/e2e` "glossary-gate: NOT
    ENFORCED" finding). The row now routes any term introduction/naming/change to glossary
    first, syncing the routing table to the skill's stated contract. Done here.

## What changed

- `domain/skills/using-domain/SKILL.md`: routing table prefixes `ddd:` -> `domain:`;
  glossary row broadened to enforce the glossary-first gate on term introduction, plus a
  one-line gate note above the table.

## Verification (quick-loop "green")

- using-domain routing table contains zero `ddd:` identifiers and six `domain:` rows.
- The glossary row covers term introduction, not only ambiguity.
- `domain/e2e` discovery evals accept both prefixes, so the change does not regress them;
  a live `domain/e2e/ci.sh` run (no `ailly` binary/key here, standing deferral) would
  confirm the glossary-gate finding flips to ENFORCED. Recorded as a follow-up.

## Deferred

- Reconcile `ddd:` -> `domain:` in the individual skill BODIES too (this pass fixed the
  routing surface only; bodies still use `ddd:` in prose cross-references). Low-risk,
  larger surface; do in a dedicated pass with a live `domain/e2e` run.
- Tighten the `domain/e2e` glossary-gate discovery case to assert ENFORCED now that the
  routing row enforces it.
