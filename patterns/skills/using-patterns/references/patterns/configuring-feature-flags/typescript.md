# Configuring feature flags in TypeScript

The composition root builds one evaluation client behind a vendor-neutral port and injects it.
Call sites receive the port, never a vendor SDK.

```ts
// flags.ts: the vendor-neutral port every call site reads through
export type FlagContext = { environment: string; userId?: string };

export interface Flags {
  enabled(key: string, defaultValue: boolean, ctx: FlagContext): boolean;
}
```

```ts
// fail-safe.ts: an unreachable backing resolves to the default (current behavior)
export class FailSafeFlags implements Flags {
  constructor(private readonly inner: Flags) {}

  enabled(key: string, defaultValue: boolean, ctx: FlagContext): boolean {
    try {
      return this.inner.enabled(key, defaultValue, ctx);
    } catch {
      return defaultValue;
    }
  }
}
```

```ts
// static-flags.ts: a fully runnable backing for local and CI
export class StaticFlags implements Flags {
  constructor(private readonly values: Record<string, boolean> = {}) {}

  enabled(key: string, defaultValue: boolean, _ctx: FlagContext): boolean {
    return key in this.values ? this.values[key] : defaultValue;
  }
}
```

```ts
// bootstrap.ts: built once at the composition root, then injected
export function buildFlags(environment: string): Flags {
  // Production backs the port with a vendor SDK that evaluates a locally cached
  // ruleset (LaunchDarkly, Unleash), or with an OpenFeature client. OpenFeature's
  // server evaluation, client.getBooleanValue(key, default, ctx), is async, so a
  // team using it makes Flags.enabled return Promise<boolean>.
  return new FailSafeFlags(new StaticFlags(loadOverrides(environment)));
}

function loadOverrides(environment: string): Record<string, boolean> {
  return environment === "local" ? { "release.checkout.new-flow": true } : {};
}
```

The flag inventory (key, owner, expiry) lives beside this module, and a CI check fails any flag past its expiry.
