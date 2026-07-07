# Arrow of maturity

**Trigger:** architecture reviews, persistence changes, scaling discussions, or when architecture causes friction.

For full stage descriptions, see `../../../references/arrow-of-maturity-stages.md`.

## Stages

| Stage | Name | Move here when |
|-------|------|-------------------|
| 0 | Prototype / Data Engineering | Exploring feasibility; minimal software lifecycle needed |
| 1 | Straight-Through Handler | First real code; pure CRUD with minimal business logic |
| 2a | Domain Model | Business logic accumulates; concepts need names |
| 2b | Extracted Repository | You need to swap or test persistence in isolation |
| 2c | Aggregates & Units of Work | Multi-entity operations with transactional integrity |
| 3 | Event-Sourced Microservices | Production scaling pressures; SLA requirements; time dimension matters |

## Rules

- **Move quickly from Stage 1 to 2a.** Once business logic appears, concepts need names. Do not remain in straight-through handlers.
- **Extract a Repository (2b) before production.** Required for long-term codebase health. Also move to 2b as soon as you need to swap persistence implementations or test domain logic without hitting a real database.
- **Introduce Aggregates and Unit of Work (2c) conservatively.** Add the aggregate when you discover domain operations, not speculatively. Stages 2b and 2c can live side by side, with only some operations relying on aggregates while others continue to use their entities and value objects.
- **Do NOT rush to Stage 3.** Only genuine production scaling pressure or the need to model the dimension of time justifies event-sourced microservices. Moving to event sourced does require changing substantial portions of the external API, and is difficult to do piecemeal.
- **Advance only when the current stage creates genuine friction.**

## Output

Provide:
1. **Current stage**: which stage the codebase is at and the evidence
2. **Signal**: the friction or trigger that justifies advancing (or the reason to stay)
3. **Next concrete step**: the specific refactoring or architectural change to make next (if advancing)
