# Using feature flags in TypeScript

One toggle point reads the injected `Flags` port and branches. The default branch is today's behavior. The targeting stays in the provider behind the port. The test exercises both branches.

```ts
// checkout.ts — one toggle point, at the edge of the new path
import type { Flags, FlagContext } from "./flags"; // installed by configuring-feature-flags

export function checkout(flags: Flags, ctx: FlagContext, cart: Cart): Receipt {
  if (flags.enabled("release.checkout.new-flow", false, ctx)) {
    return newCheckout(cart);
  }
  return currentCheckout(cart); // the default branch is today's behavior
}
```

```ts
// checkout.test.ts — both states ship, so both states are tested
import { checkout } from "./checkout";

class FakeFlags {
  constructor(private readonly on: boolean) {}
  enabled(_key: string, _default: boolean, _ctx: FlagContext): boolean {
    return this.on;
  }
}

const ctx = { environment: "test" };

test("flag off runs the current flow", () => {
  expect(checkout(new FakeFlags(false), ctx, cart).via).toBe("current");
});

test("flag on runs the new flow", () => {
  expect(checkout(new FakeFlags(true), ctx, cart).via).toBe("new");
});
```

When the new flow is fully rolled out, delete the flag, the `if`, and `currentCheckout`, leaving `checkout` as a direct call.
