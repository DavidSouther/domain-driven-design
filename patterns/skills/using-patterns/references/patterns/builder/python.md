# Builder — Python Reference

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
