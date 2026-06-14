# Flag Categories

Feature flags are categorized by lifespan, evaluation dynamism, and the action that ends them. The category is encoded in the first segment of the flag key and determines how the harness and the inventory treat the flag.

## Summary

| Category | Key prefix | Lifespan | Dynamism | Fail-safe default | Ends when |
|---|---|---|---|---|---|
| release | `release.` | Short (days to weeks) | Static per deploy | `false` | Feature fully rolled out or rolled back. |
| experiment | `experiment.` | Short to medium | Per request or per user | `false` (control) | Experiment concludes and a winner is chosen. |
| ops | `ops.` | Medium to long, some permanent | Dynamic, no deploy required | `true` (on) | Capability retired. May be permanent. |
| permission | `permission.` | Long or permanent | Per user or per cohort | `false` | Policy decision. Rarely removed. |

## release

A release flag hides a feature that is not yet safe to expose to all users. It is evaluated statically: it is either on or off for the whole environment on a given deploy. When the feature is stable, delete the dead code path and then remove the flag.

- Evaluate at startup or per environment, not per request.
- Fail-safe default is `false` (current behavior). A provider outage keeps the old path live.
- Short lifetime enforced by CI expiry. A release flag that lives past its expiry is a deferred decision, not a feature.
- Owner: the engineer or team that shipped the feature.

Example key: `release.checkout.new-flow`

## experiment

An experiment flag supports A/B tests, canary runs, or multivariate experiments. Evaluation varies per request or per user so the provider can assign cohorts. When the experiment concludes and a winner is chosen, delete the losing code path and make the winning path permanent.

- Evaluate per request, passing the user or session identifier in the evaluation context.
- Fail-safe default is `false` (the control variant). An unreachable provider returns the control.
- Short to medium lifetime. An experiment with no recorded end date is already debt.
- Owner: the product team running the experiment. They read the data and end it.

Example key: `experiment.checkout.two-step-flow`

## ops

An ops flag is a kill switch or circuit breaker. It must be flippable without a deploy, which requires a provider that supports live evaluation rather than a static config file. Ops flags protect capabilities that can fail or overload under production conditions.

- Evaluate per request; the provider evaluates a live ruleset.
- Fail-safe default is `true` (the capability is on). Turning it off is a deliberate operator action. Treating an unreachable provider as a kill is an unintended outage.
- Medium to long lifetime. Some ops flags do not expire: a global maintenance-mode switch is permanent infrastructure.
- Owner: the on-call team or SRE responsible for the protected capability.

Example key: `ops.payments.stripe-integration`

## permission

A permission flag encodes an entitlement: a user, tier, or cohort allowed to access a capability. It is evaluated per user, driven by the user's attributes in the context, not by a release state or experiment. Permission flags are long-lived because they represent policy rather than a transient gate.

- Evaluate per request with the user identifier in the evaluation context.
- Fail-safe default is `false` (no access). An unreachable provider must not grant access inadvertently.
- Long or permanent lifetime. Removal is a policy decision, not cleanup.
- Owner: the product or security team responsible for the entitlement.

Example key: `permission.checkout.early-access`

## Choosing a Category

When a flag does not fit cleanly:

- A release flag that lives longer than a sprint belongs in `ops`.
- A permission that varies by experiment cohort: use `experiment` while the test runs, then convert the winner to `permission`.
- An ops kill switch that also varies per user: two flags composing at one toggle point (one `ops`, one `permission`).

When uncertain, prefer `release` for new code, `ops` for live safety controls, and `permission` for entitlements.
