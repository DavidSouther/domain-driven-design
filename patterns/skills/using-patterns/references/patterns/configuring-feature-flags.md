# Configuring feature flags

## Overview

Assemble a feature-flag system once at the composition root as a single evaluation entry point. The rest of the code reads through it. The setup fixes the decisions every flag inherits. These are: which provider backs evaluation, what a flag resolves to when the provider is unreachable, how you name and own flags, and when they expire. Code against a vendor-neutral interface: the CNCF OpenFeature standard or a thin internal `Flags` port. This ensures the provider is swappable and no call site imports a vendor SDK.

This skill is the general flag harness. One app of this harness is the project loop's single release gate, which hides a whole multi-feature project until its Closing Bell completes. For details, see `developer/skills/ailly/references/shapes/project/release-flags.md`.

## When to use

- Standing up flags in a project for the first time, with no evaluation entry point yet.
- Adding a flag provider, or replacing one, while keeping call sites unchanged.
- Reviewing a provider or SDK change, the default-value policy, or the stale-flag CI check.
- A flag has appeared with no owner, no expiry, or a name that does not say what it gates.

**When NOT to use:** putting an individual feature behind a flag, choosing its category, or writing its toggle point. That is per-flag work and belongs in the using-feature-flags pattern (`references/patterns/using-feature-flags.md`). Running this skill at a call site installs a second evaluation path and breaks the single-entry-point contract.

## Contract

After this skill has run, a call site may assume:

- A single flag-evaluation entry point is reachable from the composition root (an OpenFeature client, or an injected `Flags` port), so no call site imports a vendor SDK.
- Every flag resolves to a fail-safe default when the provider is unreachable or the key is unknown, and that default is the current production behavior.
- Flag keys follow the project naming convention, and each flag has an owner and an expiry recorded in the inventory.
- The entry point resolves the environment (local, CI, staging, production) and passes it in the evaluation context so call sites do not read it.
- A stop-switch path exists for ops flags, reachable without a deploy.
- CI fails when a flag outlives its recorded expiry.

the using-feature-flags pattern (`references/patterns/using-feature-flags.md`) relies on these assumptions and cites this contract rather than restating it.

## Core pattern

The composition root builds one evaluation client and injects it. Call sites read through it. The decision logic, what Fowler calls the Toggle Router, lives behind the entry point, so the call site is only a read.

```
// composition root, once
provider = selectProvider(environment)      // vendor SDK or in-house, chosen here only
flags    = featureClient(provider)          // vendor-neutral facade (OpenFeature or a port)
flags.onUnreachable = RETURN_DEFAULT        // unknown or unreachable resolves to current behavior

inject(flags).into(services)                // services receive the port, not the SDK
```

For complete examples, see [`configuring-feature-flags/typescript.md`](configuring-feature-flags/typescript.md), [`configuring-feature-flags/python.md`](configuring-feature-flags/python.md), and [`configuring-feature-flags/rust.md`](configuring-feature-flags/rust.md).

## Quick reference

| Decision | Default and guidance |
|---|---|
| Interface | Vendor-neutral OpenFeature client or an internal `Flags` port. Never a vendor SDK at a call site. |
| Default value | Fail-safe, equal to current production behavior. An unreachable provider returns the default. |
| Naming | `<category>.<area>.<intent>`, with owner and expiry recorded in the inventory. |
| Categories | release (short, static), experiment (short, per-request), ops (medium, stop switch), permission (long, per-user). See [`configuring-feature-flags/categories.md`](configuring-feature-flags/categories.md) for full guidance on each. |
| Environment | Resolved at the entry point, passed in the evaluation context. |
| Kill switch | Ops flags flip without a deploy. |
| Stale-flag policy | A maximum lifetime (for example 90 days). CI fails past the expiry. |
| Provider | flagd, Unleash, Flagsmith, LaunchDarkly, or Flipt, fronted by OpenFeature. |

## Re-verification

Re-run this skill, and confirm the contract still holds, when:

- You upgrade the provider or its SDK, or the project switches providers.
- The OpenFeature spec or the internal port changes.
- A new environment or deployment target appears.
- A flag turns up with no owner or expiry, or CI reports a flag past its lifetime. Both are drift.

## Common mistakes

- **Vendor SDK at the call site.** Importing LaunchDarkly or Unleash directly couples every toggle point to one vendor. Put the vendor behind the OpenFeature client or an internal port, and have call sites read the port.
- **Default that is not the current behavior.** A flag whose off-state differs from production turns a provider outage into a surprise change. The default must be what production does today.
- **No owner and no expiry.** A flag without both is a future stale flag. Record them at creation and let CI fail past the date.
- **A name that does not say what it gates.** `flag_1234` tells a reader nothing. Encode category, area, and intent so a stale flag is obvious on sight.
- **Environment resolved at the call site.** Reading `if env == prod` next to a flag scatters environment logic. Resolve the environment once at the entry point and pass it in the context.

## Composes with

- **the using-feature-flags pattern (`references/patterns/using-feature-flags.md`)** — the call-site partner. This skill installs the evaluation entry point and the conventions. That skill puts one feature behind one flag at one toggle point. Run them together.
- **the bootstrap-and-service pattern (`references/patterns/bootstrap-and-service.md`)** — the composition root that skill describes injects the entry point built here.
- **the parse-dont-validate pattern (`references/patterns/parse-dont-validate.md`)** — the evaluation context crosses a boundary, so parse it into a typed shape rather than threading raw values inward.
- **`developer/skills/ailly/references/shapes/project/release-flags.md`** — the project loop's single release gate is one app of this harness.
