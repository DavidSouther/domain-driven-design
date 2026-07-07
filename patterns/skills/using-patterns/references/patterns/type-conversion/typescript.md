# Type conversion - TypeScript reference

TypeScript has no built-in `From` or `Into` traits, so you supply the discipline through convention. Use static `from` and `tryFrom` methods on the target class or namespace. Total conversions never throw. Partial conversions either throw a typed error or return a discriminated `Result`.

## Total: `static from`

```typescript
type Brand<T, B> = T & { readonly __brand: B };
export type Cents   = Brand<number, "Cents">;
export type Dollars = Brand<number, "Dollars">;

export const Cents = (n: number): Cents => {
  if (!Number.isInteger(n) || n < 0) throw new Error(`invalid Cents: ${n}`);
  return n as Cents;
};

export const Dollars = {
  from(c: Cents): Dollars {
    return (c / 100) as Dollars;
  },
};

const d: Dollars = Dollars.from(Cents(2599));
```

## Partial: `static tryFrom`

`Email` is a partial conversion: a raw string may not be a valid email. The constructor stays private; the only public construction paths are `tryFrom` and `parse`. Two return shapes are idiomatic. Choose one per project and stay consistent.

```typescript
export class Email {
  private constructor(private readonly value: string) {}

  // Result-shaped return. Caller pattern-matches the discriminated union.
  static tryFrom(raw: string): Email | EmailError {
    if (!raw) return { kind: "Empty" };
    if (!raw.includes("@")) return { kind: "MissingAt" };
    return new Email(raw);
  }

  // Throw a typed error. Caller wraps in try/catch at the boundary.
  static parse(raw: string): Email {
    if (!raw) throw new EmailFormatError(raw, "Empty");
    if (!raw.includes("@")) throw new EmailFormatError(raw, "MissingAt");
    return new Email(raw);
  }

  toString(): string { return this.value; }
}

export type EmailError =
  | { kind: "Empty" }
  | { kind: "MissingAt" };

export class EmailFormatError extends Error {
  constructor(readonly raw: string, readonly reason: "Empty" | "MissingAt") {
    super(`bad email (${reason}): ${raw}`);
  }
}
```

You consume the result-shaped variant by pattern-matching on the union:

```typescript
const result = Email.tryFrom(req.body.email);
if ("kind" in result) {
  return reply.status(400).send(`bad email: ${result.kind}`);
}
sendWelcome(result);
```

Both factories call `new Email(raw)` from inside a static method, so the private constructor is reachable without an `as` cast.

## Generic acceptance

Function overloads accept multiple convertible inputs while the body narrows once.

```typescript
export function charge(amount: Cents): void;
export function charge(amount: number): void;
export function charge(amount: Cents | number): void {
  const cents: Cents = typeof amount === "number" ? Cents(amount) : amount;
  /* ... */
}

charge(Cents(500));
charge(500);
```

## Lifecycle reshape

```typescript
interface DraftOrder  { readonly id: OrderId; readonly customer: CustomerId; readonly total: Cents; }
interface PlacedOrder extends DraftOrder { readonly placedAt: Date; }

export const PlacedOrder = {
  fromDraft(draft: DraftOrder, placedAt: Date): PlacedOrder {
    return { ...draft, placedAt };
  },
};
```

The spread operator copies the fields of `draft` directly, without extraction and rewrapping. The branded values flow through.

## Anti-patterns

```typescript
// Wrong: `as` cast at the call site bypasses the constructor.
const id = raw as OrderId;

// Wrong: a single `Email.from` that sometimes throws and sometimes does not.
//        Total and partial must not share a name.
Email.from(req.body.email); // throws on bad input

// Wrong: extract-and-rewrap.
const newId = (draft.id as string) as OrderId;
```

## Single canonical direction

Implement one direction. If `Cents` to `Dollars` is canonical, the reverse gets a named method that surfaces the rounding:

```typescript
export const Cents = {
  // ... constructor above ...
  fromDollarsRounded(d: Dollars): Cents {
    return Cents(Math.round((d as number) * 100));
  },
};
```
