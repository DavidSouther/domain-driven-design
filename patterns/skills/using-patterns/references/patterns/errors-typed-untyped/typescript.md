# Typed and untyped errors in TypeScript

Every language has its own way to handle errors. The pattern is always the same: types at library edges, strings at app edges, with translation between. The details differ by language. Use what fits your language. Don't copy error patterns from other languages.

A shared scenario runs through every example: a `users` library that fetches a user by id, and an app that exposes that library through an HTTP handler.

### Library, typed error

A discriminated union with a literal `kind` field is the idiomatic typed error. The compiler exhausts the cases at the call site through `switch` or `if` narrowing. A plain `Result<T, E>` shape avoids the conflation of "throwable Error" with "domain failure."

```ts
// users/errors.ts
export type FetchError =
  | { kind: "Network"; cause: Error }
  | { kind: "NotFound"; userId: string }
  | { kind: "Parse"; field: string; raw: string };

export type Result<T, E> =
  | { ok: true; value: T }
  | { ok: false; error: E };

// users/fetch.ts
import type { FetchError, Result } from "./errors";

export async function fetchUser(id: string): Promise<Result<User, FetchError>> {
  let res: Response;
  try {
    res = await fetch(`/users/${id}`);
  } catch (cause) {
    return { ok: false, error: { kind: "Network", cause: cause as Error } };
  }
  if (res.status === 404) {
    return { ok: false, error: { kind: "NotFound", userId: id } };
  }
  const raw = await res.json();
  if (typeof raw.email !== "string") {
    return { ok: false, error: { kind: "Parse", field: "email", raw: String(raw.email) } };
  }
  return { ok: true, value: raw as User };
}
```

Callers must manage every variant, and the compiler reports an error if a new variant appears without a corresponding `switch` scenario. Libraries such as `neverthrow` or `ts-results` provide an ergonomic `Result` type with combinators if hand-rolling the union becomes tedious.

### Application, stringly error

The HTTP handler does not return `Result`. Its caller is a human reading a response body or a log line. Throw `Error` with the full context formatted into the message.

```ts
// http/users.ts
import { fetchUser } from "../users/fetch";

app.get("/users/:id", async (req, reply) => {
  const result = await fetchUser(req.params.id);
  if (result.ok) return reply.send(result.value);

  switch (result.error.kind) {
    case "NotFound":
      return reply.status(404).send(`User ${result.error.userId} does not exist.`);
    case "Network":
      log.error(`fetch user ${req.params.id}: network failure`, { cause: result.error.cause });
      return reply.status(502).send("Upstream user service is unreachable. Try again shortly.");
    case "Parse":
      log.error(`fetch user ${req.params.id}: malformed payload`, result.error);
      return reply.status(502).send("Upstream returned an unexpected response.");
  }
});
```

The library's typed variants drive the translation. The app's response strings are the user-facing surface.

### Translation rules

- Never `throw` a `FetchError`. Throwing a discriminated union erases the type at the catch site, where it becomes `unknown`.
- Never `JSON.stringify` a typed error and ship the result as the human message. Format each variant deliberately.
- When wrapping for `instanceof Error` consumers (legacy code, logging libraries), wrap once at the boundary: `new Error("load user X failed: 503", { cause: result.error })`.
