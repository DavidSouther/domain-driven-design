We construct `HttpRequest` through a long positional constructor — method, url,
headers, body, timeout — and keep swapping arguments and forgetting required ones,
and sometimes end up with a half-initialized request. Give callers a construction
API where the required fields (method, url) must be supplied up front, the optional
fields (headers, body, timeout) are discoverable, cross-field validation runs once
before the object exists, and there is no way to construct an `HttpRequest` that
skipped validation. Show the construction API and one call site.
