# Builder: TypeScript reference

```typescript
class HttpRequest {
  private constructor(
    readonly method: string,
    readonly url: string,
    readonly headers: Record<string, string>,
    readonly body: string | undefined,
    readonly timeoutMs: number,
  ) {}

  static builder(method: string, url: string): HttpRequestBuilder {
    return new HttpRequestBuilder(method, url);
  }
}

class HttpRequestBuilder {
  private headers: Record<string, string> = {};
  private body: string | undefined;
  private timeoutMs = 5000;

  constructor(private readonly method: string, private readonly url: string) {}

  withHeader(key: string, value: string): this {
    this.headers[key] = value;
    return this;
  }

  withBody(body: string): this { this.body = body; return this; }

  withTimeout(ms: number): this {
    if (ms <= 0) throw new Error("timeout must be positive");
    this.timeoutMs = ms;
    return this;
  }

  build(): HttpRequest {
    if (!this.url.startsWith("https://"))
      throw new Error("url must use HTTPS");
    return new HttpRequest(this.method, this.url, { ...this.headers }, this.body, this.timeoutMs);
  }
}

const req = HttpRequest.builder("POST", "https://api.example.com/orders")
  .withHeader("Content-Type", "application/json")
  .withBody(JSON.stringify(order))
  .withTimeout(30000)
  .build();
```

Key details:
- The builder supplies required fields (`method`, `url`) at creation time, not in `build()`.
- `build()` performs cross-field validation before constructing the object.
- The builder copies headers (`{ ...this.headers }`) so re-using the builder does not alias state.
- The private constructor guarantees the builder validates every `HttpRequest`.
