# Using feature flags

## Overview

Putting a feature behind a flag has a fixed shape: one named flag, one decision point, both code paths tested, and a removal plan.
The hard part is restraint.
A flag checked in many places, fused to its decision logic, becomes permanent.
Fowler's rule is to keep the Toggle Point separate from the Toggle Router (the decision logic), and to keep toggle points few.

This skill assumes the flag harness from the configuring-feature-flags pattern (`references/patterns/configuring-feature-flags.md`) is already in place.
This includes an injected evaluation port, a fail-safe default, a naming convention, and an owner-and-expiry inventory.
It reads through that port and does not set any of it up.

## When to use

- A feature-step or change should reach the codebase before it reaches users.
- An experiment needs two code paths, chosen per user or per request.
- An operational switch, an emergency stop or circuit breaker, must flip without a deploy.
- A capability should be visible only to certain users or cohorts.

**When NOT to use:** choosing the provider, the naming convention, the fail-safe default, or the environment resolution.
That setup is once-per-project and belongs in the configuring-feature-flags pattern (`references/patterns/configuring-feature-flags.md`).
For a whole multi-feature project's release gate, see `developer/skills/ailly/references/shapes/project/release-flags.md` instead of adding a flag per step.

## Core pattern

Read the flag once, at one toggle point, and branch there.
The default path is today's behavior.
The targeting, the Toggle Router, stays in the provider behind the injected port.

```
// one toggle point, at the edge of the new path
if flags.enabled("release.checkout.new-flow", default=false, context):
    newCheckout()
else:
    currentCheckout()        // the default branch is today's behavior
```

- Name the flag per the convention, and record its owner and expiry in the inventory.
- Default to current behavior, so a provider outage keeps production unchanged.
- Keep one toggle point.
  Funnel the decision to a single place and pass the result down rather than re-reading the flag.
- Test both branches.
  A flag doubles the states, and both ship.
- Plan removal.
  A release or experiment flag is temporary.
  Delete the flag and its dead branch once the decision is permanent.

For complete examples, see [`using-feature-flags/typescript.md`](using-feature-flags/typescript.md), [`using-feature-flags/python.md`](using-feature-flags/python.md), and [`using-feature-flags/rust.md`](using-feature-flags/rust.md).

## Quick reference

| Category | Lifespan | Dynamism | Remove when |
|---|---|---|---|
| release | Short | Static per deploy | The feature is fully rolled out. |
| experiment | Short to medium | Per request or user | The experiment concludes. |
| ops | Medium to long | Dynamic emergency stop | Retire the capability. May be permanent. |
| permission | Long or permanent | Per user | Rarely. It encodes an entitlement. |

## Common mistakes

- **Scattered toggle points.**
  Checking one flag in ten places makes it un-removable.
  Funnel the decision to one point and pass the result down.
- **Coupling the point to the router.**
  Hard-coding `if user.plan == premium` at the branch fuses the toggle point to its logic.
  Read a named flag and let the provider hold the targeting.
- **A default that flips current behavior.**
  A flag defaulting to the new path ships the unfinished feature on a provider outage.
  Default to today's behavior.
- **Testing one branch.**
  The off path and the on path both ship.
  Test both, and use pairwise testing for interacting flags rather than every 2^N combination.
- **No removal plan.**
  A short-lived flag with no expiry becomes debt.
  Record the expiry at creation and delete the flag and its dead branch once the decision is permanent.
- **Reaching for a vendor SDK.**
  Importing the provider at the call site breaks the single entry point.
  Read the injected port.

## Composes with

- **the configuring-feature-flags pattern (`references/patterns/configuring-feature-flags.md`)**: the setup partner.
  It installs the evaluation port, the naming convention, and the fail-safe default this skill relies on.
- **the type-states pattern (`references/patterns/type-states.md`)**: when a flag gates a lifecycle change, model the two states as types rather than re-reading the flag downstream.
- **the parse-dont-validate pattern (`references/patterns/parse-dont-validate.md`)**: read the flag once at the boundary into a typed decision rather than threading the raw flag through the domain.
- **`developer/skills/ailly/references/shapes/project/release-flags.md`**: the project loop's single release gate, for hiding a whole project rather than one feature.
