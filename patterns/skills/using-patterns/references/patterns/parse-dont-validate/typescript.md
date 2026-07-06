# Parse, don't validate, TypeScript reference

```typescript
// BAD: boolean guard must be repeated at every call site
function isValidEmail(s: string): boolean {
  return /^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(s);
}

function sendWelcome(email: string) {
  if (!isValidEmail(email)) throw new Error("invalid email"); // repeated everywhere
  smtp.send(email, "Welcome!");
}

// GOOD: parse once at the boundary; the type carries the proof
type Email = string & { readonly _brand: unique symbol };

function parseEmail(raw: string): Email {
  if (!/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(raw))
    throw new UserError(`"${raw}" is not a valid email address`);
  return raw as Email;
}

// Domain functions accept Email — illegal to pass an unvalidated string
function sendWelcome(email: Email) {
  smtp.send(email, "Welcome!"); // no guard needed; the type is the proof
}

// Parsing happens exactly once, at the HTTP boundary
app.post("/register", (req, res) => {
  const email = parseEmail(req.body.email); // throws with a user-friendly message
  sendWelcome(email);
});
```
