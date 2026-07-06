# Builder Rust reference

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
