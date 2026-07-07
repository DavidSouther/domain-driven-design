---
name: using-domain
description: Bootstrap and routing skill for Domain-Driven Design. Loaded when brainstorming, researching, or designing, to decide which domain ability applies.
---

# Domain-driven design workflow

You are working in a project that uses Domain-Driven Design. This skill routes you to the
right ability. During brainstorming, research, and design, read the situation, name the
matching ability, and open its reference under `references/<name>.md` for the full details
(trigger, process, and output).

**Glossary-first gate:** before introducing, naming, or changing any domain term, apply
the glossary ability (`references/glossary.md`) first. All other domain abilities defer to
it for terminology.

Each row below states the discriminator that selects the ability and the reference that
holds it. Match the situation in the left column, then read the reference in the right
column. Do not apply all abilities upfront; start with the one that addresses the immediate
situation.

## Routing table

| Situation (discriminator) | Ability and reference |
|---------------------------|-----------------------|
| Introducing, naming, or changing a single domain term, entity, operation, or concept. Check whether it already exists, record its definition, resolve a synonym against an existing entry, or pin down an ambiguous term. | glossary, `references/glossary.md` |
| Developing the whole language for a bounded context. Research candidate terms, categorize which questions go to domain experts via Ask vs Confirm, and populate the glossary in bulk. | ubiquitous-language, `references/ubiquitous-language.md` |
| Starting a new project, service, subdomain, or bounded context. Identify subdomains, draw context boundaries, and classify each as Core, Generic, or Supporting. | domain-model, `references/domain-model.md` |
| Designing an API boundary, service interface, or domain operation signature. Specify input/output contracts and the invariants that must always hold at the edge. | contracts-and-invariants, `references/contracts-and-invariants.md` |
| Evaluating architecture, adding persistence, or feeling scaling/friction pressure. Assess the current architectural stage and the signal that justifies advancing. | arrow-of-maturity, `references/arrow-of-maturity.md` |

## Discriminators that are easy to confuse

These pairs route to different abilities. State the discriminator before choosing.

- **glossary vs ubiquitous-language.** Pinning down a single term (its definition, a
  synonym to fold into an existing entry, or an ambiguity between two readings of one word,
  such as a `customer`-vs-`account` drift) routes to glossary (`references/glossary.md`).
  Developing the whole language of a bounded context (researching many candidate terms at
  once and routing questions to domain experts) routes to ubiquitous-language
  (`references/ubiquitous-language.md`). One term: glossary. The whole context's
  vocabulary: ubiquitous-language. The glossary-first gate still applies: ubiquitous-language
  defers to glossary for each term it confirms.

- **domain-model vs contracts-and-invariants.** Carving a problem space into subdomains and
  drawing the boundaries between bounded contexts routes to domain-model
  (`references/domain-model.md`). Specifying the operation signatures, preconditions, and
  always-true rules at an existing context's edge routes to contracts-and-invariants
  (`references/contracts-and-invariants.md`). Boundaries first (domain-model), then the
  contract across one boundary (contracts-and-invariants).

- **domain-model vs arrow-of-maturity.** A question about what the concepts are and where
  the boundaries go routes to domain-model (`references/domain-model.md`). A question about
  how far the architecture should advance (when to extract a repository, introduce
  aggregates, or move to event sourcing) routes to arrow-of-maturity
  (`references/arrow-of-maturity.md`). A purely architectural/scaling question that adds no
  new business concept is arrow-of-maturity, not domain-model.

## Change cadence gate

This gate applies to DDD artifact files under `docs/ddd/` (domain model, glossary, and
context files), not to these skill files.

Any proposed change to `docs/ddd/` requires explicit human approval before humans finalize it.

- You may introduce and commit changes as **[DRAFT]** without human review.
- Use a git branch for DDD changes when possible.
- Do not finalize domain changes by removing **[DRAFT]** labels without explicit human sign-off.
- Plan for longer review cycles before finalizing domain changes; they happen at a substantially lower cadence than feature work.

Do not apply all abilities upfront. Start with the one that addresses the immediate
situation, name it, and read its reference.
