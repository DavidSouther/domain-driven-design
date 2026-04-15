# Builder — Code Reference

Code examples for the `patterns:builder` skill. Referenced by `patterns/skills/builder/SKILL.md`.

---

## TypeScript

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
- Required fields (`method`, `url`) are supplied at builder-creation time, not in `build()`.
- `build()` performs cross-field validation before constructing the object.
- Headers are copied (`{ ...this.headers }`) so re-using the builder does not alias state.
- The private constructor guarantees every `HttpRequest` was validated by the builder.

---

## Python

```python
from dataclasses import dataclass, field
from typing import Optional

@dataclass
class HttpRequest:
    method: str
    url: str
    headers: dict[str, str]
    body: Optional[str]
    timeout_ms: int

    @classmethod
    def builder(cls, method: str, url: str) -> "HttpRequestBuilder":
        return HttpRequestBuilder(method, url)


class HttpRequestBuilder:
    def __init__(self, method: str, url: str) -> None:
        self._method = method
        self._url = url
        self._headers: dict[str, str] = {}
        self._body: Optional[str] = None
        self._timeout_ms = 5000

    def with_header(self, key: str, value: str) -> "HttpRequestBuilder":
        self._headers[key] = value
        return self

    def with_body(self, body: str) -> "HttpRequestBuilder":
        self._body = body
        return self

    def with_timeout(self, ms: int) -> "HttpRequestBuilder":
        if ms <= 0:
            raise ValueError("timeout must be positive")
        self._timeout_ms = ms
        return self

    def build(self) -> HttpRequest:
        if not self._url.startswith("https://"):
            raise ValueError("url must use HTTPS")
        return HttpRequest(
            method=self._method,
            url=self._url,
            headers=dict(self._headers),   # copy — reusing builder doesn't alias
            body=self._body,
            timeout_ms=self._timeout_ms,
        )


req = (
    HttpRequest.builder("POST", "https://api.example.com/orders")
    .with_header("Content-Type", "application/json")
    .with_body('{"id": "ord-1"}')
    .with_timeout(30_000)
    .build()
)
```

---

## Rust

Rust's ownership model makes the consuming builder pattern natural: calling `build()` moves the builder, preventing any further mutation.

```rust
use std::collections::HashMap;

pub struct HttpRequest {
    method: String,
    url: String,
    headers: HashMap<String, String>,
    body: Option<String>,
    timeout_ms: u64,
}

pub struct HttpRequestBuilder {
    method: String,
    url: String,
    headers: HashMap<String, String>,
    body: Option<String>,
    timeout_ms: u64,
}

impl HttpRequest {
    pub fn builder(method: impl Into<String>, url: impl Into<String>) -> HttpRequestBuilder {
        HttpRequestBuilder {
            method: method.into(),
            url: url.into(),
            headers: HashMap::new(),
            body: None,
            timeout_ms: 5_000,
        }
    }
}

impl HttpRequestBuilder {
    pub fn with_header(mut self, key: impl Into<String>, value: impl Into<String>) -> Self {
        self.headers.insert(key.into(), value.into());
        self
    }

    pub fn with_body(mut self, body: impl Into<String>) -> Self {
        self.body = Some(body.into());
        self
    }

    pub fn with_timeout(mut self, ms: u64) -> Result<Self, String> {
        if ms == 0 {
            return Err("timeout must be positive".into());
        }
        self.timeout_ms = ms;
        Ok(self)
    }

    pub fn build(self) -> Result<HttpRequest, String> {
        if !self.url.starts_with("https://") {
            return Err("url must use HTTPS".into());
        }
        Ok(HttpRequest {
            method: self.method,
            url: self.url,
            headers: self.headers,   // ownership moved — no aliasing possible
            body: self.body,
            timeout_ms: self.timeout_ms,
        })
    }
}

let req = HttpRequest::builder("POST", "https://api.example.com/orders")
    .with_header("Content-Type", "application/json")
    .with_body(r#"{"id":"ord-1"}"#)
    .with_timeout(30_000)?
    .build()?;
```
