# NewType: TypeScript reference

Branded types erase at runtime, zero performance overhead.

```typescript
// Before: primitives leak domain intent
function transfer(fromAccount: string, toAccount: string, amount: number): void { /* ... */ }
// Compiles silently even when arguments are swapped:
transfer(toId, fromId, amountInCents);

// After: branded types make the mistake unrepresentable
type AccountId = string & { readonly _brand: "AccountId" };
type Cents     = number & { readonly _brand: "Cents" };

// Constructor is the only sanctioned entry point — validation lives here once.
function makeAccountId(raw: string): AccountId {
  if (!raw.startsWith("acc-")) throw new Error(`Invalid AccountId: ${raw}`);
  return raw as AccountId;
}
function makeCents(raw: number): Cents {
  if (!Number.isInteger(raw) || raw < 0) throw new Error(`Invalid Cents: ${raw}`);
  return raw as Cents;
}

function transfer(from: AccountId, to: AccountId, amount: Cents): void { /* ... */ }

// Type error — plain string is not assignable to AccountId:
transfer("acc-123", "acc-456", 5000);           // TS error

// Correct — construction is explicit:
transfer(makeAccountId("acc-123"), makeAccountId("acc-456"), makeCents(5000));
```
